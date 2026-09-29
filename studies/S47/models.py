"""Fold-local additive/logistic and boosted models with separate calibration."""
import numpy as np
from scipy.special import expit,logit
from scipy.stats import norm
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer,OneHotEncoder,OrdinalEncoder,SplineTransformer,StandardScaler
from studies.S47.ingest import CONFIG,feature_columns


def make_model(family,setting,variant):
    numeric,categorical=feature_columns(variant)
    if family in ['linear','additive']:
        steps=[('log',FunctionTransformer(np.log1p,feature_names_out='one-to-one'))]
        if family=='additive':steps.append(('spline',SplineTransformer(n_knots=5,degree=3,knots='uniform',include_bias=False,extrapolation='constant')))
        steps.append(('scale',StandardScaler()))
        pre=ColumnTransformer([('numeric',Pipeline(steps),numeric),('category',OneHotEncoder(handle_unknown='ignore',sparse_output=False),categorical)])
        model=LogisticRegression(C=float(setting),max_iter=3000,tol=1e-7,solver='lbfgs')
    elif family=='boosting':
        pre=ColumnTransformer([('numeric','passthrough',numeric),('category',OrdinalEncoder(handle_unknown='use_encoded_value',unknown_value=-1),categorical)])
        model=HistGradientBoostingClassifier(max_leaf_nodes=int(setting),max_iter=CONFIG['boosting_iterations'],learning_rate=.05,min_samples_leaf=20,l2_regularization=1,early_stopping=False,categorical_features=[False]*len(numeric)+[True]*len(categorical),random_state=CONFIG['seed'])
    else:raise ValueError('Unknown family')
    return Pipeline([('pre',pre),('model',model)])


def candidates(family):return CONFIG['boosting_leaves'] if family=='boosting' else CONFIG['regularization_c']


def select(frame,y,groups,family,variant,seed):
    splits=list(StratifiedGroupKFold(CONFIG['inner_folds'],shuffle=True,random_state=seed).split(frame,y,groups));rows=[]
    for setting in candidates(family):
        prediction=np.empty(len(y))
        for train,val in splits:
            if set(groups[train])&set(groups[val]):raise ValueError('Inner group leakage')
            m=make_model(family,setting,variant).fit(frame.iloc[train],y[train]);prediction[val]=m.predict_proba(frame.iloc[val])[:,1]
        rows.append({'setting':setting,'grouped_validation_log_loss':log_loss(y,prediction)})
    return min(rows,key=lambda r:(r['grouped_validation_log_loss'],r['setting']))['setting'],rows


def nested(frame,y,groups,family):
    rows=[]
    for fold,(train,val) in enumerate(StratifiedGroupKFold(CONFIG['outer_folds'],shuffle=True,random_state=CONFIG['seed']+10).split(frame,y,groups)):
        setting,_=select(frame.iloc[train],y[train],groups[train],family,'core',CONFIG['seed']+100+fold);m=make_model(family,setting,'core').fit(frame.iloc[train],y[train]);p=m.predict_proba(frame.iloc[val])[:,1]
        rows.append({'fold':fold,'setting':setting,'training_rows':len(train),'validation_rows':len(val),'validation_log_loss':log_loss(y[val],p)})
    return rows


class CalibrationMap:
    def fit(self,p,y):
        self.model=LogisticRegression(C=1,max_iter=3000,tol=1e-9).fit(logit(np.clip(p,1e-7,1-1e-7))[:,None],y);return self
    def predict(self,p):return self.model.predict_proba(logit(np.clip(p,1e-7,1-1e-7))[:,None])[:,1]


class ComplaintUsageRule:
    def fit(self,frame,y):
        self.median=float(frame['Seconds of Use'].median());self.prior=float(np.mean(y));self.cells={}
        keys=self.keys(frame)
        for k in np.unique(keys):
            s=y[keys==k];self.cells[k]=(s.sum()+20*self.prior)/(len(s)+20)
        return self
    def keys(self,frame):return frame.Complains.to_numpy(int)*2+(frame['Seconds of Use'].to_numpy()<self.median).astype(int)
    def predict(self,frame):return np.array([self.cells.get(k,self.prior) for k in self.keys(frame)])


def capacity(y,p,keys,fraction):
    if not 0<=fraction<=1:raise ValueError('Invalid capacity')
    k=int(np.floor(len(y)*fraction));chosen=np.lexsort((keys,-p))[:k];captured=int(y[chosen].sum());events=int(y.sum())
    return {'capacity':fraction,'contacts':k,'churn_found':captured,'churn_missed':events-captured,'non_churn_contacts':k-captured,'recall':captured/events if events else None,'precision':captured/k if k else None}


def sample_size(control,reduction):
    if not .05<=control<=.4 or not .01<=reduction<=.1 or reduction>=control:raise ValueError('Unsupported experiment assumption')
    intervention=control-reduction;mean=(control+intervention)/2
    per_arm=int(np.ceil((norm.ppf(.975)*np.sqrt(2*mean*(1-mean))+norm.ppf(.8)*np.sqrt(control*(1-control)+intervention*(1-intervention)))**2/reduction**2))
    return {'control_churn':control,'absolute_reduction':reduction,'intervention_churn':intervention,'per_arm':per_arm,'total':2*per_arm,'alpha':.05,'power':.8}


def contrasts(model,calibrator,frame,references):
    values=[]
    for feature,low,high in references:
        a=frame.copy();b=frame.copy();a[feature]=low;b[feature]=high
        effect=np.mean(calibrator.predict(model.predict_proba(b)[:,1])-calibrator.predict(model.predict_proba(a)[:,1]))
        values.append(effect)
    return np.array(values)
