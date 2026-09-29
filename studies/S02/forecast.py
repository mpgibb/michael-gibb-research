"""Point-in-time cycle features and coherent joint forecast scenarios."""
import numpy as np
from scipy.stats import rankdata
from sklearn.ensemble import HistGradientBoostingRegressor


def features(y,price,meta,calendar,origin):
    if origin<365:raise ValueError('Insufficient history')
    history=y[:,:origin]
    columns=[]
    for width in [7,14,28,56,84,182,364]:
        window=history[:,-width:];columns.extend([window.mean(axis=1),window.std(axis=1),(window==0).mean(axis=1)])
    columns.extend([history[:,-1],history[:,-7],history[:,-28],history[:,-28:].sum(axis=1)/(1+history[:,-56:-28].sum(axis=1)),price[:,origin-1]])
    date=calendar.iloc[origin-1]
    for value in [date.month,date.wday,origin/365]:columns.append(np.repeat(float(value),len(meta)))
    for key in ['item_id','store_id','dept_id','cat_id','state_id']:
        columns.append(np.asarray([sorted(meta[key].unique()).index(value) for value in meta[key]],float))
    return np.column_stack(columns)


def training(y,price,meta,calendar,origin,config):
    origins=range(max(config['min_history'],origin-config['training_window']),origin-config['horizon']+1,config['training_stride'])
    x=np.concatenate([features(y,price,meta,calendar,o) for o in origins]);target=np.concatenate([y[:,o:o+config['horizon']].sum(axis=1) for o in origins])
    return x,target


def fit_quantiles(y,price,meta,calendar,origin,leaves,config):
    x,target=training(y,price,meta,calendar,origin,config);future=features(y,price,meta,calendar,origin)
    categorical=[False]*(x.shape[1]-5)+[True]*5
    predictions=[]
    for q in config['quantiles']:
        model=HistGradientBoostingRegressor(loss='quantile',quantile=q,max_leaf_nodes=leaves,max_iter=config['iterations'],learning_rate=.05,l2_regularization=1,early_stopping=False,categorical_features=categorical,random_state=config['seed']).fit(x,target)
        predictions.append(model.predict(future))
    raw=np.column_stack(predictions)
    # Rearrangement is fixed in advance and removes quantile crossing without examining target outcomes.
    return np.maximum(np.sort(raw,axis=1),0),int(np.any(np.diff(raw,axis=1)<0,axis=1).sum()),len(target)


def baseline(y,origin,kind):
    return y[:,origin-7:origin].sum(axis=1)*4 if kind=='seasonal_7' else y[:,origin-28:origin].sum(axis=1)


def joint_quantile_scenarios(quantiles,residuals,draws,seed,independent=False):
    rng=np.random.default_rng(seed);ranks=(rankdata(residuals,axis=0,method='average')-.5)/len(residuals)
    indices=rng.integers(0,len(residuals),size=(draws,len(quantiles))) if independent else rng.integers(0,len(residuals),size=(draws,1))
    u=ranks[indices,np.arange(len(quantiles))]
    q10,q50,q90=quantiles.T
    low=np.maximum(0,q10-(q50-q10)*.25);high=q90+(q90-q50)*.25
    knots=[low,q10,q50,q90,high];levels=np.array([0,.1,.5,.9,1.])
    out=np.zeros_like(u)
    for j in range(4):
        mask=(u>=levels[j])&(u<levels[j+1]);fraction=(u-levels[j])/(levels[j+1]-levels[j]);out=np.where(mask,knots[j]+fraction*(knots[j+1]-knots[j]),out)
    return np.maximum(out,0)


def aggregation(meta):
    groups=[('bottom',str(i),[i]) for i in range(len(meta))]
    for level,key in [('store','store_id'),('category','cat_id')]:
        groups.extend((level,str(value),np.flatnonzero(meta[key].to_numpy()==value).tolist()) for value in sorted(meta[key].unique()))
    groups.append(('total','selected assortment',list(range(len(meta)))))
    matrix=np.zeros((len(groups),len(meta)))
    for i,(_,_,indices) in enumerate(groups):matrix[i,indices]=1
    return groups,matrix


def scales(history):
    blocks=history.shape[1]//28
    totals=history[:,-blocks*28:].reshape(len(history),blocks,28).sum(axis=2)
    differences=np.diff(totals,axis=1)
    return np.maximum(np.sqrt(np.mean(differences**2,axis=1)),1),np.maximum(np.mean(np.abs(differences),axis=1),1)


def pinball(actual,prediction,q):
    error=actual-prediction
    return np.maximum(q*error,(q-1)*error)
