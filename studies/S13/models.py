"""Training-only sensor processing and sparse/latent/nonlinear comparisons."""
import numpy as np
from sklearn.base import BaseEstimator,TransformerMixin
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.pipeline import Pipeline
from ingest import CONFIG

class SensorProcessor(BaseEstimator,TransformerMixin):
 def __init__(self,indicators=True):self.indicators=indicators
 def fit(self,x,y=None):
  x=np.asarray(x,float); pp=CONFIG['preprocessing']; good=[]
  for j in range(x.shape[1]):
   obs=x[np.isfinite(x[:,j]),j]
   if len(obs) and 1-len(obs)/len(x)<=pp['maximum_missing_fraction'] and np.std(obs)>pp['minimum_standard_deviation'] and np.unique(obs,return_counts=True)[1].max()/len(obs)<pp['maximum_dominant_fraction']:good.append(j)
  if not good:raise ValueError('No eligible sensor columns')
  a=x[:,good]; med=np.nanmedian(a,axis=0); filled=np.where(np.isnan(a),med,a)
  _,keep=np.unique(filled.T,axis=0,return_index=True);keep=np.sort(keep)
  self.columns_=np.asarray(good)[keep];a=x[:,self.columns_];self.median_=np.nanmedian(a,axis=0)
  self.lower_,self.upper_=np.nanquantile(a,pp['clip_quantiles'],axis=0)
  miss=np.isnan(a).mean(axis=0);self.missing_columns_=np.flatnonzero((miss>.005)&(miss<.995)) if self.indicators else np.array([],int)
  self.names_=[f'sensor_{j+1:03}' for j in self.columns_]+[f'sensor_{self.columns_[j]+1:03}_missing' for j in self.missing_columns_]
  raw=self._raw(x);self.keep_=np.std(raw,axis=0)>1e-12;self.names_=np.asarray(self.names_)[self.keep_].tolist();self.scale_=StandardScaler().fit(raw[:,self.keep_]);return self
 def _raw(self,x):
  a=np.asarray(x,float)[:,self.columns_]; values=np.clip(np.where(np.isnan(a),self.median_,a),self.lower_,self.upper_)
  return np.column_stack([values,np.isnan(a[:,self.missing_columns_]).astype(float)])
 def transform(self,x):return self.scale_.transform(self._raw(x)[:,self.keep_])

class CheckedLogistic(LogisticRegression):
 def fit(self,x,y,sample_weight=None):
  super().fit(x,y,sample_weight=sample_weight)
  if np.all(self.coef_==0):
   rate=np.average(y,weights=sample_weight)
   if not 0<rate<1:raise ValueError('Both outcomes required')
   self.intercept_=np.array([np.log(rate/(1-rate))])
  return self

class PCAMonitor:
 def __init__(self,n_components):self.n_components=n_components
 def fit(self,x,y):
  self.pre=SensorProcessor(False).fit(x);a=self.pre.transform(x)
  self.pca=PCA(n_components=self.n_components,svd_solver='full').fit(a[np.asarray(y)==0]);scores=self.score_features(a)
  self.bridge=Pipeline([('scale',StandardScaler()),('logistic',LogisticRegression(C=1,max_iter=2000))]).fit(scores,y);return self
 def score_features(self,a):
  z=self.pca.transform(a);t2=np.sum(z*z/np.maximum(self.pca.explained_variance_,1e-12),axis=1);q=np.mean((a-self.pca.inverse_transform(z))**2,axis=1)
  return np.column_stack([np.log1p(t2),np.log1p(q)])
 def predict_proba(self,x):return self.bridge.predict_proba(self.score_features(self.pre.transform(x)))

def make_model(family,setting,indicators=True):
 if family=='pca_monitor':return PCAMonitor(int(setting))
 if family=='elastic_net':
  clf=CheckedLogistic(C=float(setting),penalty='elasticnet',l1_ratio=CONFIG['elastic_net_l1_ratio'],solver='saga',max_iter=CONFIG['elastic_net_max_iterations'],tol=1e-4,random_state=CONFIG['seed'])
 elif family=='boosting':
  clf=HistGradientBoostingClassifier(max_leaf_nodes=int(setting),max_iter=CONFIG['boosting_iterations'],learning_rate=CONFIG['boosting_learning_rate'],min_samples_leaf=CONFIG['boosting_min_samples_leaf'],l2_regularization=CONFIG['boosting_l2'],early_stopping=False,random_state=CONFIG['seed'])
 else:raise ValueError('Unknown model')
 return Pipeline([('pre',SensorProcessor(indicators)),('model',clf)])

def selected_sensors(model):
 names=model.named_steps['pre'].names_;coef=model.named_steps['model'].coef_[0];return {name[:10] for name,c in zip(names,coef) if abs(c)>1e-6}

def cluster_draws(days,repetitions,seed,block=1):
 days=np.asarray(days);unique=np.unique(days);groups=[np.flatnonzero(days==d) for d in unique];rng=np.random.default_rng(seed)
 for _ in range(repetitions):
  if block==1:picks=rng.integers(0,len(groups),len(groups))
  else:
   starts=rng.integers(0,len(groups),int(np.ceil(len(groups)/block)));picks=np.concatenate([(s+np.arange(block))%len(groups) for s in starts])[:len(groups)]
  yield np.concatenate([groups[j] for j in picks])

def capacity_row(y,p,fraction):
 y=np.asarray(y);k=int(np.floor(len(y)*fraction));indices=np.lexsort((np.arange(len(y)),-np.asarray(p)))[:k];tp=int(y[indices].sum());fp=k-tp;fn=int(y.sum())-tp
 return {'capacity':float(fraction),'inspections':k,'detected_failures':tp,'missed_failures':fn,'unnecessary_inspections':fp,'recall':tp/int(y.sum()),'precision':tp/k if k else None}
