"""Cross-fitted effects and independent profile-cluster policy inference."""
import numpy as np
from scipy.stats import norm
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


def outcome_model(seed,iterations=120):
    return HistGradientBoostingRegressor(max_leaf_nodes=7,max_iter=iterations,learning_rate=.05,l2_regularization=10,early_stopping=False,random_state=seed)


def propensity_model():
    return make_pipeline(StandardScaler(),LogisticRegression(C=1,max_iter=500))


def doubly_robust(y,t,m0,m1,e):
    y,t,m0,m1,e=map(np.asarray,[y,t,m0,m1,e])
    if np.any((e<=0)|(e>=1)):raise ValueError('No treatment overlap')
    return m1-m0+t*(y-m1)/e-(1-t)*(y-m0)/(1-e)


def nuisance_fit(x,y,t,seed):
    return (outcome_model(seed).fit(x[t==0],y[t==0]),outcome_model(seed).fit(x[t==1],y[t==1]),propensity_model().fit(x,t))


def nuisance_predict(models,x):
    m0,m1,propensity=models
    return np.clip(m0.predict(x),1e-6,1-1e-6),np.clip(m1.predict(x),1e-6,1-1e-6),np.clip(propensity.predict_proba(x)[:,1],.05,.95)


def cluster_mean(values,profiles,multiplier=1):
    values=np.asarray(values,float);profiles=np.asarray(profiles)
    if len(values)!=len(profiles) or not np.isfinite(values).all():raise ValueError('Invalid inference arrays')
    _,indices=np.unique(profiles,return_inverse=True);n=len(values);g=int(indices.max())+1
    estimate=values.mean();sums=np.bincount(indices,weights=values-estimate)
    se=np.sqrt(g/(g-1)*np.sum(sums*sums)/(n*n)) if g>1 else 0
    margin=norm.ppf(.975)*se
    return {'estimate':float(estimate*multiplier),'lower':float((estimate-margin)*multiplier),'upper':float((estimate+margin)*multiplier),'confidence':.95,'standard_error':float(se*multiplier),'clusters':g}


def cluster_folds(folds):
    folds=np.asarray(folds)
    return [(np.flatnonzero(folds!=k),np.flatnonzero(folds==k)) for k in range(3)]
