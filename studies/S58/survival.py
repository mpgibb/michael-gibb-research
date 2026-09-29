"""Discrete survival accounting with training-only workflow feature mappings."""
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier

CAT=['stage','last_activity','last_lifecycle']
BASE=['age_days','last_gap_days','max_gap_days','mean_gap_days','offers_created','prefix']


def survival_from_hazard(hazard):
    hazard=np.asarray(hazard,float)
    if hazard.ndim!=2 or np.any((hazard<0)|(hazard>1)):raise ValueError('Invalid hazards')
    return np.column_stack([np.ones(len(hazard)),np.cumprod(1-hazard,axis=1)])


def summarize_survival(survival):
    s=np.asarray(survival);cdf=1-s[:,1:];cdf[:,-1]=1
    return {'mean':s[:,:-1].sum(axis=1),'late_14':s[:,14],
            'lower':np.argmax(cdf>=.1,axis=1)+1,'upper':np.argmax(cdf>=.9,axis=1)+1}


def kaplan_meier(frame):
    days=frame.risk_days.to_numpy();event=frame.event_day.to_numpy();weight=frame.weight.to_numpy()
    hazard=[]
    for day in range(1,31):
        risk=weight[days>=day].sum();hazard.append(weight[event==day].sum()/risk if risk else 0)
    return survival_from_hazard(np.asarray(hazard)[None,:])[0]


def baseline_survival(train,test,stage=False):
    pooled=kaplan_meier(train)
    if not stage:return np.tile(pooled,(len(test),1))
    groups={key:kaplan_meier(group) for key,group in train.groupby(['stage','age_band']) if len(group)>=50}
    return np.asarray([groups.get((r.stage,r.age_band),pooled) for r in test.itertuples()])


class FeatureMap:
    def __init__(self,frame,reduced=False):
        self.reduced=reduced;self.numeric=['age_days'] if reduced else BASE+[c for c in frame if c.startswith(('activity:','lifecycle:')) and frame[c].sum()>0]
        self.categories=['stage'] if reduced else CAT
        self.levels={key:{value:i for i,value in enumerate(sorted(frame[key].unique()))} for key in self.categories}
    def transform(self,frame):
        columns=[frame[c].fillna(0).to_numpy(float) if c in frame else np.zeros(len(frame)) for c in self.numeric]
        columns += [frame[key].map(self.levels[key]).fillna(-1).to_numpy(float) for key in self.categories]
        return np.column_stack(columns)
    def categorical(self):return [False]*len(self.numeric)+[True]*len(self.categories)+[False]


def expand_risk(frame,features):
    indices=np.repeat(np.arange(len(frame)),frame.risk_days.to_numpy(int));day=np.concatenate([np.arange(1,int(n)+1) for n in frame.risk_days])
    x=np.column_stack([features[indices],day]);target=(frame.event_day.to_numpy()[indices]==day).astype(int);weights=frame.weight.to_numpy()[indices]
    return x,target,weights


def fit_hazard(train,test,leaves,seed,reduced=False):
    mapping=FeatureMap(train,reduced);features=mapping.transform(train);x,y,weight=expand_risk(train,features)
    model=HistGradientBoostingClassifier(max_leaf_nodes=leaves,max_iter=120,learning_rate=.05,l2_regularization=10,early_stopping=False,categorical_features=mapping.categorical(),random_state=seed)
    model.fit(x,y,sample_weight=weight)
    future=mapping.transform(test);idx=np.repeat(np.arange(len(test)),30);days=np.tile(np.arange(1,31),len(test));risk=np.column_stack([future[idx],days]);hazard=model.predict_proba(risk)[:,1].reshape(len(test),30)
    return survival_from_hazard(hazard),{'risk_rows':len(y),'event_intervals':int(y.sum()),'features':mapping.numeric+mapping.categories+['future_day'],'categories':mapping.levels,'max_leaves':leaves,'reduced_history':reduced}
