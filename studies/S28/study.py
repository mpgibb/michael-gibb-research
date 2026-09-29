"""Chronological, pre-call subscription-response evaluation."""
from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import platform
import sys
import zipfile

import numpy as np
import pandas as pd
import scipy
import sklearn
from scipy.special import expit, logit
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, SplineTransformer, StandardScaler
from threadpoolctl import threadpool_limits

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from research_program.evaluation import binary_metrics, calibration_bins, circular_block_indices, interval, ranked_selection
from research_program.io import ROOT, data_dir, download, provenance, sha256, write_json
from research_program.validate import validate_result

HERE = Path(__file__).resolve().parent
CONFIG = json.loads((HERE / 'config.json').read_text())
NUMERIC = ['campaign_prior', 'previous', 'prior_days', 'ever_contacted']
CATEGORICAL = ['contact', 'month', 'day_of_week', 'poutcome']
EXTRA = ['job', 'marital', 'education', 'default', 'housing', 'loan']


def ingest() -> pd.DataFrame:
    directory = data_dir('S28')
    archive = download(CONFIG['archive_url'], directory / 'bank-marketing.zip', CONFIG['archive_sha256'], 2_000_000)
    with zipfile.ZipFile(archive) as outer:
        with zipfile.ZipFile(io.BytesIO(outer.read('bank-additional.zip'))) as inner:
            content = inner.read('bank-additional/bank-additional-full.csv')
    if hashlib.sha256(content).hexdigest() != CONFIG['csv_sha256']:
        raise ValueError('CSV content changed')
    data = pd.read_csv(io.BytesIO(content), sep=';')
    if len(data) != 41188 or not set(data.y.unique()) == {'yes', 'no'}:
        raise ValueError('Unexpected source population')
    return data


def features(data: pd.DataFrame, expanded=False) -> pd.DataFrame:
    x = data[CATEGORICAL + ['previous']].copy()
    x['campaign_prior'] = data.campaign - 1
    x['ever_contacted'] = (data.pdays != 999).astype(float)
    x['prior_days'] = data.pdays.where(data.pdays != 999, np.nan)
    if expanded:
        x['age'] = data.age
        for column in EXTRA: x[column] = data[column]
    if set(CONFIG['excluded']) & set(x.columns) or 'y' in x or 'campaign' in x:
        raise ValueError('Unavailable feature in model matrix')
    if (x.campaign_prior < 0).any(): raise ValueError('Invalid campaign count')
    return x


def split_boundaries(n):
    return int(n * CONFIG['development_end']), int(n * CONFIG['calibration_end'])


def model(family, setting, expanded=False):
    numeric = NUMERIC + (['age'] if expanded else [])
    categorical = CATEGORICAL + (EXTRA if expanded else [])
    steps = [('impute', SimpleImputer(strategy='median', keep_empty_features=True))]
    if family == 'additive':
        steps += [('spline', SplineTransformer(n_knots=5, degree=3, include_bias=False, extrapolation='linear'))]
    steps += [('scale', StandardScaler())]
    preprocessor = ColumnTransformer([('numeric', Pipeline(steps), numeric), ('categorical', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical)], sparse_threshold=0)
    if family == 'boosting':
        learner = HistGradientBoostingClassifier(max_iter=200, learning_rate=.05, max_leaf_nodes=int(setting), l2_regularization=1, early_stopping=False, random_state=CONFIG['seed'])
    else:
        learner = LogisticRegression(C=setting, max_iter=2000, solver='lbfgs', random_state=CONFIG['seed'])
    return Pipeline([('preprocessing', preprocessor), ('model', learner)])


def calibrate(raw, y, evaluation_raw):
    raw = np.asarray(raw)
    fitted = LogisticRegression(C=1e6, max_iter=2000).fit(logit(np.clip(raw, 1e-6, 1-1e-6)).reshape(-1,1), y)
    probability = fitted.predict_proba(logit(np.clip(evaluation_raw,1e-6,1-1e-6)).reshape(-1,1))[:,1]
    return np.clip(probability,1e-6,1-1e-6)


def rule_score(data):
    return ((data.poutcome == 'success').astype(float) * 3 + (data.pdays != 999).astype(float) + 1 / (1 + data.pdays.clip(0,999)) - .01 * np.minimum(data.campaign - 1,20)).to_numpy()


def conditional_metrics(y, p, selections, ids):
    yt, pt = y[ids], p[ids]
    metric = binary_metrics(yt, pt)
    for capacity, selected in selections.items():
        use = selected[ids]
        metric[f'precision_{capacity}'] = float(yt[use].mean()) if use.any() else 0.0
        metric[f'capture_{capacity}'] = float(yt[use].sum() / max(yt.sum(),1))
    return metric


def main():
    version = provenance('S28')
    data = ingest(); x = features(data); y = (data.y == 'yes').astype(int).to_numpy()
    n = len(data); train_end, calibration_end = split_boundaries(n)
    evaluation_y = y[calibration_end:]; test_n = len(evaluation_y)
    folds = [(int(n*a),int(n*b)) for a,b in CONFIG['tuning_folds']]
    tuning, chosen, fitted_models = [], {}, {}
    predictions = {'random': np.repeat(y[train_end:calibration_end].mean(), test_n)}
    rule = rule_score(data)
    rule_calibrator = LogisticRegression(C=1e6,max_iter=2000).fit(rule[train_end:calibration_end,None], y[train_end:calibration_end])
    predictions['business_rule'] = rule_calibrator.predict_proba(rule[calibration_end:,None])[:,1]
    for family, grid in CONFIG['candidates'].items():
        scores = []
        for setting in grid:
            fold_scores=[]
            for end, validation_end in folds:
                candidate=model(family,setting).fit(x.iloc[:end],y[:end])
                loss=log_loss(y[end:validation_end], candidate.predict_proba(x.iloc[end:validation_end])[:,1])
                fold_scores.append(loss)
            scores.append(float(np.mean(fold_scores)))
            tuning.append({'model':family,'setting':setting,'fold_log_loss':fold_scores,'mean_log_loss':scores[-1]})
        chosen[family] = grid[int(np.argmin(scores))]
        learner = model(family,chosen[family]).fit(x.iloc[:train_end],y[:train_end])
        fitted_models[family] = learner
        raw = learner.predict_proba(x.iloc[train_end:])[:,1]
        predictions[family] = calibrate(raw[:calibration_end-train_end],y[train_end:calibration_end],raw[calibration_end-train_end:])
        print(f'Completed {family} development/calibration; frozen configuration {chosen[family]}',flush=True)
    selected_family = min(CONFIG['candidates'],key=lambda family:min(t['mean_log_loss'] for t in tuning if t['model']==family))
    expanded_x=features(data,expanded=True)
    expanded=model('boosting',chosen['boosting'],expanded=True).fit(expanded_x.iloc[:train_end],y[:train_end])
    raw=expanded.predict_proba(expanded_x.iloc[train_end:])[:,1]
    predictions['boosting_richer_features']=calibrate(raw[:calibration_end-train_end],y[train_end:calibration_end],raw[calibration_end-train_end:])
    bootstrap=list(circular_block_indices(test_n,CONFIG['bootstrap_block'],CONFIG['bootstrap_repetitions'],CONFIG['seed']))
    metrics, frontier, calibration, periods, bootstrap_store = [], [], [], [], {}
    specs=[{'id':'random','label':'Random allocation','specification':'Constant probability from the preceding calibration cohort; analytical expected selection results.'},{'id':'business_rule','label':'History and recency rule','specification':'Previous success, prior contact and recency; sigmoid calibrated on preceding cohort.'}]
    for family in CONFIG['candidates']:
        specs.append({'id':family,'label':{'logistic':'Regularized logistic','additive':'Additive spline logistic','boosting':'Gradient boosting'}[family],'specification':{'selected_configuration':chosen[family],'selected_by_development':family==selected_family,'features':'pre-call operational only','calibration':'disjoint chronological sigmoid'}})
    specs.append({'id':'boosting_richer_features','label':'Boosting with richer attributes','specification':'Sensitivity only; adds demographic and loan/default fields; same frozen complexity.'})
    for name,p in predictions.items():
        # The ranking rule uses its declared score, even if probability calibration reverses it under a distribution shift.
        ranking = rule[calibration_end:] if name=='business_rule' else p
        selections = {c:ranked_selection(ranking,c) for c in CONFIG['capacities']}
        samples=[]
        for indices in bootstrap:
            sampled=conditional_metrics(evaluation_y,p,selections,indices)
            if name=='random':
                for c in CONFIG['capacities']:
                    sampled[f'precision_{c}']=float(evaluation_y[indices].mean())
                    sampled[f'capture_{c}']=int(test_n*c)/test_n
            samples.append(sampled)
        bootstrap_store[name]=samples
        for key,value in binary_metrics(evaluation_y,p).items():
            metrics.append({'name':key,'model':name,'estimate':value,'unit':'natural-log units' if key=='log_loss' else 'fraction','split':'final chronological holdout',**interval([s[key] for s in samples])})
        for c,selected in selections.items():
            count=int(selected.sum())
            captured=float(evaluation_y.sum()*count/test_n) if name=='random' else int(evaluation_y[selected].sum())
            row={'model':name,'capacity':c,'selected':count,'responses':captured,'precision':captured/count,'capture':captured/evaluation_y.sum(),'precision_interval':interval([s[f'precision_{c}'] for s in samples]),'capture_interval':interval([s[f'capture_{c}'] for s in samples]),'kind':'analytical expectation' if name=='random' else 'observed selected contacts'}
            frontier.append(row)
        calibration.extend({'model':name,**b} for b in calibration_bins(evaluation_y,p))
        for period,idx in enumerate(np.array_split(np.arange(test_n),4),1):
            capacity=ranked_selection(ranking[idx],CONFIG['primary_capacity'])
            periods.append({'model':name,'period':period,'source_row_start':calibration_end+int(idx[0])+1,'source_row_end':calibration_end+int(idx[-1])+1,'n':len(idx),'events':int(evaluation_y[idx].sum()),'log_loss':log_loss(evaluation_y[idx],p[idx]),'precision_at_20_percent':float(evaluation_y[idx].mean()) if name=='random' else float(evaluation_y[idx][capacity].mean())})
    delta = binary_metrics(evaluation_y,predictions[selected_family])['log_loss'] - binary_metrics(evaluation_y,predictions['business_rule'])['log_loss']
    sensitivity=[]
    for block in [CONFIG['bootstrap_block'],*CONFIG['bootstrap_sensitivity_blocks']]:
        draws=[log_loss(evaluation_y[idx],predictions[selected_family][idx])-log_loss(evaluation_y[idx],predictions['business_rule'][idx]) for idx in circular_block_indices(test_n,block,CONFIG['bootstrap_repetitions'],CONFIG['seed'])]
        sensitivity.append({'block_length':block,'model':selected_family,'metric':'log_loss_difference_vs_business_rule','estimate':delta,**interval(draws)})
    profile_hash=pd.util.hash_pandas_object(data.drop(columns=['y','duration']),index=False)
    overlap=profile_hash.iloc[calibration_end:].isin(set(profile_hash.iloc[:calibration_end])).to_numpy()
    novel=~overlap
    duplicate_sensitivity=[{'model':name,'n':int(novel.sum()),**binary_metrics(evaluation_y[novel],p[novel])} for name,p in predictions.items()]
    audit={'rows':n,'columns':list(data.columns),'exact_rows_repeated':int(data.duplicated().sum()),'test_profiles_seen_before':int(overlap.sum()),'missing_categorical':{c:int((data[c]=='unknown').sum()) for c in data.select_dtypes('object').columns if c!='y'},'not_previously_contacted':int((data.pdays==999).sum()),'primary_features':list(x.columns),'excluded_columns':CONFIG['excluded'],'category_novelty':{c:int((~x.iloc[calibration_end:][c].isin(x.iloc[:train_end][c])).sum()) for c in CATEGORICAL},'boundaries_zero_based_exclusive':{'development_end':train_end,'calibration_end':calibration_end,'final_end':n}}
    result={'schema_version':'1.0','study_id':'S28','run_id':'S28-'+version['code_version'][:8]+'-'+CONFIG['csv_sha256'][:8],**version,'evaluated_on':CONFIG['evaluated_on'],'data':{'source_url':'https://archive.ics.uci.edu/dataset/222/bank+marketing','release':CONFIG['release'],'sha256':CONFIG['csv_sha256'],'license':'CC BY 4.0, as listed by UCI','citation':'Moro, Rita & Cortez (2014), Bank Marketing, UCI, doi:10.24432/C5K306','coverage':'May 2008–November 2010; individual exact dates unavailable'},'target':{'label':'Recorded term-deposit subscription','estimand':'Response probability among observed campaign contacts; not incremental effect','prediction_cutoff':'Immediately before the recorded current call','horizon':'Campaign outcome as recorded; fixed follow-up duration unavailable','unit':'contact/example'},'cohort':f'Source-ordered final rows {calibration_end+1}–{n}; exact calendar dates and person identifiers unavailable.','samples':{'total':n,'train':train_end,'calibration':calibration_end-train_end,'test':test_n,'events':{'train':int(y[:train_end].sum()),'calibration':int(y[train_end:calibration_end].sum()),'test':int(evaluation_y.sum())}},'models':specs,'metrics':metrics,'uncertainty':'500 paired circular moving-block bootstrap draws, 100 source-ordered test records per block; conditional on fixed fitted models. Block lengths 50/200 are sensitivity checks.','assumptions':['Source row order is chronological as documented by UCI.','Operational history fields describe information preceding the current call under the source definitions.','Scenario response values and contact costs are user assumptions, not observed financial outcomes.'],'limitations':['Single bank, historical observed-contact population; no randomized no-contact comparison.','No stable customer IDs or exact call dates; dependence and repeated contacts cannot be fully resolved.','Calibrated probabilities can fail under later campaign shifts. Bootstrap intervals do not include model-retraining uncertainty.','Economic indicator release vintages cannot be verified, so all five are excluded.','Matching anonymized profiles do not establish matching people. Independent technical review is pending.'],'tables':{'audit':audit,'tuning':tuning,'selected_model':selected_family,'capacity_frontier':frontier,'calibration':calibration,'periods':periods,'block_sensitivity':sensitivity,'novel_profile_sensitivity':duplicate_sensitivity,'scenario_ranges':CONFIG['economic_scenario']},'software':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,'pandas':pd.__version__,'scikit-learn':sklearn.__version__}}
    validate_result(result)
    write_json(HERE/'results/result.json',result)
    # Individual predictions remain in the external cache for auditing, never in public exports.
    pd.DataFrame({'source_row':np.arange(calibration_end+1,n+1),'outcome':evaluation_y,**predictions}).to_csv(data_dir('S28')/'heldout-predictions.csv',index=False,lineterminator='\n')
    print(json.dumps({'selected':selected_family,'samples':result['samples'],'log_loss_delta':sensitivity[0]}),flush=True)


if __name__=='__main__':
    with threadpool_limits(limits=2): main()
