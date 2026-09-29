"""Training-only hedonic preprocessing and spatial prediction intervals."""
import numpy as np,pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler,OneHotEncoder
from sklearn.linear_model import Ridge
from sklearn.ensemble import HistGradientBoostingRegressor
from ingest import NUMERIC,CATEGORIES,PHYSICAL,SPATIAL,CONFIG


def predictors(frame):
 f=frame.copy()
 for key in ['char_bldg_sf','char_land_sf']:f[key]=np.log1p(f[key])
 return f


def fit_hedonic(train):
 pre=ColumnTransformer([('numeric',make_pipeline(SimpleImputer(strategy='median',add_indicator=True),StandardScaler()),NUMERIC+SPATIAL),('categorical',OneHotEncoder(handle_unknown='ignore',min_frequency=10),CATEGORIES+['meta_nbhd_code'])])
 model=make_pipeline(pre,Ridge(alpha=10,solver='lsqr'));model.fit(predictors(train),np.log(train.sale_price));return lambda f:model.predict(predictors(f))


def fit_local(train):
 values=train.assign(log_price=np.log(train.sale_price));groups={}
 for c,n in [('meta_nbhd_code',20),('meta_township_name',30)]:
  g=values.groupby(c).log_price.agg(['median','size']);groups[c]=g.loc[g['size']>=n,'median'].to_dict()
 overall=float(values.log_price.median())
 def predict(frame):return np.array([groups['meta_nbhd_code'].get(r.meta_nbhd_code,groups['meta_township_name'].get(r.meta_township_name,overall)) for r in frame.itertuples()])
 return predict


def fit_boosting(train,leaves,reduced=False):
 numeric=NUMERIC if reduced else NUMERIC+SPATIAL;categories=PHYSICAL if reduced else CATEGORIES;maps={c:{x:i for i,x in enumerate(sorted(train[c].unique()))} for c in categories}
 if any(len(m)>255 for m in maps.values()):raise ValueError('Native categorical limit exceeded')
 def transform(f):
  x=predictors(f);return np.column_stack([x[c].to_numpy(float) for c in numeric]+[x[c].map(maps[c]).fillna(-1).to_numpy(float) for c in categories])
 model=HistGradientBoostingRegressor(max_iter=CONFIG['iterations'],learning_rate=.05,max_leaf_nodes=leaves,l2_regularization=10,early_stopping=False,categorical_features=[False]*len(numeric)+[True]*len(categories),random_state=CONFIG['seed']);model.fit(transform(train),np.log(train.sale_price));return lambda f:model.predict(transform(f))


def radius(residuals,coverage):
 x=np.sort(np.asarray(residuals));n=len(x)
 if not n or not 0<coverage<1:raise ValueError('Invalid calibration request')
 k=int(np.ceil((n+1)*coverage))
 if k>n:raise ValueError('Insufficient calibration sample for finite interval')
 return float(x[k-1])


def metrics(y,log_prediction):
 p=np.exp(log_prediction);return {'median_ape_pct':float(np.median(np.abs(p/y-1))*100),'log_rmse':float(np.sqrt(np.mean((log_prediction-np.log(y))**2))),'median_absolute_error_USD':float(np.median(np.abs(p-y))),'median_price_ratio':float(np.median(p/y))}
