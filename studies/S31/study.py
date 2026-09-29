"""Execute the frozen actuarial comparison and export aggregate evidence."""
import json
import platform
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import scipy
import sklearn
from threadpoolctl import threadpool_limits

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from research_program.io import data_dir, provenance, write_json
from research_program.validate import validate_result
from ingest import CONFIG, ingest, split_masks
from models import PremiumModel, deviance_rows, measures, segment_masks

HERE = Path(__file__).resolve().parent
LABELS = {'constant': 'Training portfolio mean', 'glm': 'Poisson–Gamma regression', 'tweedie': 'Direct Tweedie regression', 'boosting': 'Boosted frequency–severity'}
UNITS = {'tweedie_deviance': 'exposure-weighted Tweedie deviance; power 1.5', 'absolute_error': 'EUR per policy-year', 'predicted_observed_loss_ratio': 'ratio'}


def choose_settings(frame, dev, val, geography=True, families=('glm', 'tweedie', 'boosting')):
    rows, settings = [], {}
    for family in families:
        for setting in CONFIG['candidates'][family]:
            model = PremiumModel(family, setting, geography).fit(frame.loc[dev])
            prediction = model.predict(frame.loc[val])
            scores = measures(frame.loc[val, 'Exposure'].to_numpy(float), frame.loc[val, 'Loss'].to_numpy(float), prediction)
            rows.append({'model': family, 'setting': setting, **scores})
            print('validation', 'main' if geography else 'geographic stress', family, setting, scores, flush=True)
        settings[family] = min((row for row in rows if row['model'] == family), key=lambda row: (row['tweedie_deviance'], row['setting']))['setting']
    return settings, rows


def evaluate(frame, predictions, loss_column, seed, repetitions):
    exposure = frame.Exposure.to_numpy(float)
    loss = frame[loss_column].to_numpy(float)
    scores = {name: measures(exposure, loss, p) for name, p in predictions.items()}
    dev = {name: exposure * deviance_rows(loss / exposure, p['premium']) for name, p in predictions.items()}
    abs_error = {name: np.abs(loss - exposure * p['premium']) for name, p in predictions.items()}
    pred_loss = {name: exposure * p['premium'] for name, p in predictions.items()}
    draws = {name: {metric: [] for metric in UNITS} for name in predictions}
    rng = np.random.default_rng(seed)
    for _ in range(repetitions):
        ix = rng.integers(len(frame), size=len(frame))
        denominator, total_loss = exposure[ix].sum(), loss[ix].sum()
        if total_loss <= 0:
            raise ValueError('Bootstrap sample has no loss')
        for name in predictions:
            draws[name]['tweedie_deviance'].append(dev[name][ix].sum() / denominator)
            draws[name]['absolute_error'].append(abs_error[name][ix].sum() / denominator)
            draws[name]['predicted_observed_loss_ratio'].append(pred_loss[name][ix].sum() / total_loss)
    metrics = []
    for name in predictions:
        for metric, unit in UNITS.items():
            low, high = np.quantile(draws[name][metric], [.025, .975])
            metrics.append({'model': name, 'name': metric, 'estimate': scores[name][metric], 'unit': unit, 'split': 'final', 'lower': low, 'upper': high, 'confidence': .95})
    paired = np.asarray(draws['boosting']['tweedie_deviance']) - np.asarray(draws['glm']['tweedie_deviance'])
    low, high = np.quantile(paired, [.025, .975])
    difference = {'comparison': 'boosting minus glm', 'metric': 'tweedie_deviance', 'estimate': scores['boosting']['tweedie_deviance'] - scores['glm']['tweedie_deviance'], 'lower': low, 'upper': high, 'draws': repetitions}
    return metrics, difference


def aggregate(frame, predictions, loss_column, mask):
    exposure = frame.Exposure.to_numpy(float)[mask]
    loss = frame[loss_column].to_numpy(float)[mask]
    claims = frame.ClaimNb.to_numpy(float)[mask]
    total_exposure, total_loss, total_claims = exposure.sum(), loss.sum(), claims.sum()
    result = []
    for name, pred in predictions.items():
        predicted_loss = np.sum(exposure * pred['premium'][mask])
        predicted_claims = np.sum(exposure * pred['frequency'][mask]) if 'frequency' in pred else None
        result.append({'model': name, 'policies': int(mask.sum()), 'claims': int(total_claims), 'exposure_years': total_exposure,
                       'observed_loss_eur': total_loss, 'predicted_loss_eur': predicted_loss,
                       'observed_pure_premium': total_loss / total_exposure, 'predicted_pure_premium': predicted_loss / total_exposure,
                       'observed_frequency': total_claims / total_exposure,
                       'predicted_frequency': predicted_claims / total_exposure if predicted_claims is not None else None,
                       'observed_severity': total_loss / total_claims if total_claims else None,
                       'predicted_severity': predicted_loss / predicted_claims if predicted_claims is not None else None,
                       'predicted_observed_loss_ratio': predicted_loss / total_loss if total_loss else None})
    return result


def segments(frame, predictions, loss_column, seed):
    output = []
    rng = np.random.default_rng(seed)
    for grouping, group, mask in segment_masks(frame, CONFIG['minimum_segment_policies']):
        rows = aggregate(frame, predictions, loss_column, mask)
        exposure = frame.loc[mask, 'Exposure'].to_numpy(float)
        loss = frame.loc[mask, loss_column].to_numpy(float)
        names = list(predictions)
        predicted = np.column_stack([p['premium'][mask] * exposure for p in predictions.values()])
        ratios, observed = [], []
        for _ in range(CONFIG['segment_bootstrap_repetitions']):
            ix = rng.integers(len(loss), size=len(loss))
            total = loss[ix].sum()
            if total <= 0:
                raise ValueError('Segment bootstrap has no claims')
            ratios.append(predicted[ix].sum(axis=0) / total)
            observed.append(total / exposure[ix].sum())
        bounds = np.quantile(ratios, [.025, .975], axis=0)
        observed_low, observed_high = np.quantile(observed, [.025, .975])
        for i, row in enumerate(rows):
            assert row['model'] == names[i]
            output.append({'grouping': grouping, 'group': group, **row, 'ratio_lower': bounds[0, i], 'ratio_upper': bounds[1, i], 'observed_premium_lower': observed_low, 'observed_premium_upper': observed_high})
    return output


def calibration(frame, predictions, loss_column):
    output = []
    for name, p in predictions.items():
        for number, ix in enumerate(np.array_split(np.argsort(p['premium'], kind='stable'), 10), 1):
            mask = np.zeros(len(frame), dtype=bool)
            mask[ix] = True
            output.append({'bin': number, **aggregate(frame, {name: p}, loss_column, mask)[0]})
    return output


def main():
    prov = provenance('S31')
    frame, audit = ingest()
    dev, val, test = split_masks(frame.IDpol)
    fit = dev | val
    metrics, scenarios, private = [], {}, {}
    with threadpool_limits(limits=2):
        settings, tuning = choose_settings(frame, dev, val)
        final = frame.loc[test].reset_index(drop=True)
        private.update(exposure=final.Exposure.to_numpy(float), claims=final.ClaimNb.to_numpy(float), loss=final.Loss.to_numpy(float), capped_loss=final.CappedLoss.to_numpy(float), region=final.Region.astype(str).to_numpy(dtype=str), area=final.Area.astype(str).to_numpy(dtype=str), driver_age=final.DrivAge.to_numpy(float))
        for scenario, loss_column in [('uncapped', 'Loss'), ('capped', 'CappedLoss')]:
            predictions = {}
            for family in LABELS:
                model = PremiumModel(family, settings.get(family)).fit(frame.loc[fit], loss_column)
                predictions[family] = model.predict(final)
                for kind, values in predictions[family].items():
                    private[f'{scenario}_{family}_{kind}'] = values
                print('final fit ready', scenario, family, flush=True)
            ms, delta = evaluate(final, predictions, loss_column, CONFIG['seed'], CONFIG['bootstrap_repetitions'])
            rows = segments(final, predictions, loss_column, CONFIG['seed'] + 1)
            dispersion = []
            for name, p in predictions.items():
                if 'frequency' in p:
                    expected = final.Exposure.to_numpy(float) * p['frequency']
                    dispersion.append({'model': name, 'mean_pearson_count_residual_squared': np.mean((final.ClaimNb.to_numpy(float) - expected)**2 / expected)})
            scenarios[scenario] = {'claim_cap_eur': None if scenario == 'uncapped' else CONFIG['claim_cap_eur'], 'metrics': ms, 'primary_difference': delta, 'segments': rows, 'calibration': calibration(final, predictions, loss_column), 'count_dispersion': dispersion}
            if scenario == 'uncapped':
                metrics = ms
            print('evaluated', scenario, delta, flush=True)
        reserved = frame.Region.astype(str).eq(CONFIG['stress_region']).to_numpy()
        stress_settings, stress_tuning = choose_settings(frame, dev & ~reserved, val & ~reserved, geography=False, families=('glm', 'boosting'))
        stress_frame = frame.loc[reserved].reset_index(drop=True)
        stress_predictions = {}
        for family in ['glm', 'boosting']:
            model = PremiumModel(family, stress_settings[family], geography=False).fit(frame.loc[fit & ~reserved])
            stress_predictions[family] = model.predict(stress_frame)
            for kind, values in stress_predictions[family].items():
                private[f'stress_{family}_{kind}'] = values
        stress_metrics, stress_delta = evaluate(stress_frame, stress_predictions, 'Loss', CONFIG['seed'] + 2, CONFIG['bootstrap_repetitions'])
        private.update(stress_exposure=stress_frame.Exposure.to_numpy(float), stress_loss=stress_frame.Loss.to_numpy(float), stress_claims=stress_frame.ClaimNb.to_numpy(float))
        stress = {'region': CONFIG['stress_region'], 'policies': len(stress_frame), 'claims': int(stress_frame.ClaimNb.sum()), 'development_policies': int((dev & ~reserved).sum()), 'validation_policies': int((val & ~reserved).sum()), 'final_fit_policies': int((fit & ~reserved).sum()), 'region_feature_excluded': True, 'selected_settings': stress_settings, 'tuning': stress_tuning, 'metrics': stress_metrics, 'primary_difference': stress_delta, 'aggregate': aggregate(stress_frame, stress_predictions, 'Loss', np.ones(len(stress_frame), dtype=bool))}
    samples = {'total': len(frame), 'total_claims': int(frame.ClaimNb.sum()), 'test': int(test.sum()), 'test_claims': int(frame.loc[test, 'ClaimNb'].sum()), 'test_claiming_policies': int((frame.loc[test, 'ClaimNb'] > 0).sum())}
    for label, mask in [('development', dev), ('validation', val), ('final_fit', fit)]:
        samples[label] = int(mask.sum())
        samples[label + '_claims'] = int(frame.loc[mask, 'ClaimNb'].sum())
    result = {'schema_version': '1.0', 'study_id': 'S31', 'run_id': f"S31-{prov['code_version'][:8]}-{CONFIG['archive_sha256'][:8]}", **prov, 'evaluated_on': CONFIG['evaluated_on'],
              'data': {'source_url': 'https://doi.org/10.57745/P0KHAG', 'release': 'CASdatasets 1.2-0, Recherche Data Gouv dataset version 1.1, July 12, 2024', 'sha256': CONFIG['archive_sha256'], 'license': 'Etalab Open Licence 2.0 (dataset metadata); GPL >=2 (package code)', 'citation': 'Dutang, C.; Charpentier, A.; Gallic, E. Insurance dataset. Recherche Data Gouv. doi:10.57745/P0KHAG. CASdatasets 1.2-0, file doi:10.57745/ULR0ZA.', 'file_sha256': CONFIG['files']},
              'target': {'label': 'Aggregate historical nominal claim euros per recorded policy-year', 'estimand': 'Conditional expected claim frequency times event-weighted conditional severity, or direct expected pure premium', 'prediction_cutoff': 'Assumed pre-claim policy characteristics; source timestamps cannot independently confirm field timing', 'horizon': 'Recorded exposure duration; approximate source years 2011–2013, no policy dates', 'unit': 'Policy; associated claims allocated together'},
              'cohort': 'SHA-256 policy-held-out final 20%; independent Ile-de-France geographic stress with region omitted from predictors',
              'samples': samples, 'models': [{'id': name, 'label': label, 'specification': 'Training portfolio frequency and severity means' if name == 'constant' else f"Frozen {name}, selected setting {settings[name]}; training-only feature transforms and exposure/claim-count weights. See protocol."} for name, label in LABELS.items()],
              'metrics': metrics, 'uncertainty': 'Paired policy bootstrap: 500 final and geographic-stress draws, 250 per segment; 95% percentile intervals conditional on fitted models and the observed empirical loss tail. No independent-year or catastrophe uncertainty claim.',
              'assumptions': ['Source risk fields are hypothetically available before claims; exact timing and claim-development maturity are not verified.', 'Policy IDs define the sampling unit, but multiple policies may share unobserved drivers or shocks.', 'The capped sensitivity limits each claim to EUR 50000 and changes the estimand; it is not a source contract limit.', 'Expense loading is an explicit 0–50% scenario: estimated pure premium divided by one minus loading.'],
              'limitations': ['Historical French motor data do not validate a current insurance price or rate filing.', 'No policy dates support a temporal holdout or ultimate-claim development model.', 'Nominal euros are not inflation-adjusted and some amounts reflect settlement conventions.', 'Heavy losses and unobserved dependence can make empirical bootstrap intervals too narrow for future risk.', 'Driver age and geography are descriptive benchmark features, not causal effects or a fairness certification.', 'No policyholder eligibility or pricing action is taken; expense scenarios exclude taxes, profit, capital and regulatory constraints.', 'Independent technical review is pending.'],
              'tables': {'audit': audit, 'tuning': tuning, 'selected_settings': settings, 'scenarios': scenarios, 'geographic_stress': stress, 'expense_loadings': CONFIG['expense_loadings']},
              'software': {'python': platform.python_version(), 'numpy': np.__version__, 'pandas': pd.__version__, 'scipy': scipy.__version__, 'sklearn': sklearn.__version__, 'seed': CONFIG['seed']}}
    validate_result(result)
    write_json(HERE / 'results/result.json', result)
    np.savez_compressed(data_dir('S31') / 'verification.npz', **private)
    print(json.dumps({'run': result['run_id'], 'samples': samples, 'settings': settings, 'primary': scenarios['uncapped']['primary_difference'], 'capped': scenarios['capped']['primary_difference'], 'stress': stress_delta}, indent=2), flush=True)


if __name__ == '__main__':
    main()
