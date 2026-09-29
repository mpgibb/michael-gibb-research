"""Customer purchase models with explicit latent-state and spend assumptions."""
import numpy as np
from scipy.optimize import minimize
from scipy.special import betaln, gammaln, roots_jacobi
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor

from studies.S03.ingest import CONFIG, feature_matrix


def fit_positive(objective, starts, bounds):
    runs=[]
    for initial in starts:
        result=minimize(lambda theta: objective(np.exp(theta)),np.log(initial),method='L-BFGS-B',bounds=np.log(bounds),options={'maxiter':3000,'ftol':1e-11,'gtol':1e-6})
        runs.append(result)
    valid=[r for r in runs if r.success and np.isfinite(r.fun)]
    if not valid:raise RuntimeError('Population likelihood did not converge')
    best=min(valid,key=lambda r:r.fun);p=np.exp(best.x)
    info={'objective':float(best.fun),'converged_starts':len(valid),'attempted_starts':len(starts),'iterations':int(best.nit),'boundary_parameters':[i for i,(value,bound) in enumerate(zip(p,bounds)) if np.isclose(value,bound[0],rtol=.001) or np.isclose(value,bound[1],rtol=.001)]}
    return p,info


class BGNBD:
    @staticmethod
    def log_terms(params,x,tx,age):
        r,alpha,a,b=params
        common=gammaln(r+x)-gammaln(r)+r*np.log(alpha)+betaln(a,b+x)-betaln(a,b)
        live=-(r+x)*np.log(alpha+age)
        dead=np.full(len(x),-np.inf);positive=x>0
        dead[positive]=np.log(a)-np.log(b+x[positive]-1)-(r+x[positive])*np.log(alpha+tx[positive])
        return common,live,dead

    def fit(self,history):
        x,tx,age=[history[col].to_numpy(float) for col in ['frequency','tx','age']]
        def objective(p):
            common,live,dead=self.log_terms(p,x,tx,age)
            return -np.mean(common+np.logaddexp(live,dead))
        bounds=np.array([[.01,50],[.001,5000],[.01,100],[.01,1000]])
        self.params,self.fit_info=fit_positive(objective,[[.5,10,1,3],[1,20,.5,2],[.2,1,2,5]],bounds)
        return self

    def predict(self,frame,nodes=64):
        x,tx,age,h=[frame[col].to_numpy(float) for col in ['frequency','tx','age','horizon']];h=h/7
        r,alpha,a,b=self.params
        _,live,dead=self.log_terms(self.params,x,tx,age)
        alive=np.exp(live-np.logaddexp(live,dead));expected=np.empty(len(x))
        for frequency in np.unique(x):
            mask=x==frequency
            roots,weights=roots_jacobi(nodes,b+frequency-1,a-1)
            p=(roots+1)/2;weights=weights/weights.sum()
            integrand=-np.expm1(-(r+frequency)*np.log1p(h[mask,None]*p/(alpha+age[mask,None])))/p
            expected[mask]=alive[mask]*(integrand@weights)
        purchase=alive*(-np.expm1(-(r+x)*np.log1p(h/(alpha+age))))
        if not (np.isfinite(expected).all() and (expected>=0).all() and (purchase>=0).all() and (purchase<=1).all()):raise ValueError('Invalid BG/NBD prediction')
        return {'count':expected,'purchase':purchase,'alive':alive}


class GammaGamma:
    def fit(self,history):
        eligible=history.frequency>0
        x=history.loc[eligible,'frequency'].to_numpy(float);m=history.loc[eligible,'repeat_mean_spend'].to_numpy(float)/100
        if len(x)<20 or (m<=0).any():raise ValueError('Insufficient positive repeat-spend histories')
        def objective(params):
            p,q_minus_one,gamma=params;q=1+q_minus_one
            log=gammaln(p*x+q)-gammaln(p*x)-gammaln(q)+q*np.log(gamma)+p*x*np.log(x)+(p*x-1)*np.log(m)-(p*x+q)*np.log(gamma+x*m)
            return -np.mean(log)
        mean=m.mean();bounds=np.array([[.02,100],[.001,100],[.00001,1e6]])
        self.params,self.fit_info=fit_positive(objective,[[6,3,mean/2],[2,1,mean/2],[1,.5,mean/2]],bounds)
        return self

    def posterior(self,frame):
        p,q_minus_one,gamma=self.params;x=frame.frequency.to_numpy(float);m=frame.repeat_mean_spend.to_numpy(float)/100
        return p,1+q_minus_one+p*x,gamma+x*m

    def predict(self,frame):
        p,shape,rate=self.posterior(frame)
        return 100*p*rate/(shape-1)


def predictive_distribution(bg,gg,frame,prediction,seed,draws):
    rng=np.random.default_rng(seed);n=len(frame)
    output={k:np.zeros(n) for k in ['count_lower','count_upper','spend_lower','spend_upper','simulated_count_mean']}
    masses=np.zeros((n,6));r,alpha,a,b=bg.params
    for start in range(0,n,100):
        stop=min(start+100,n);f=frame.iloc[start:stop];shape=(len(f),draws)
        x=f.frequency.to_numpy(float)[:,None];age=f.age.to_numpy(float)[:,None];h=f.horizon.to_numpy(float)[:,None]/7
        lam=rng.gamma(r+x,1/(alpha+age),size=shape);p=rng.beta(a,b+x,size=shape)
        proposed=rng.poisson(lam*h);geometric=np.full(shape,np.inf);regular=(p>0)&(p<1)
        u=np.maximum(rng.random(shape),np.finfo(float).tiny)
        geometric[regular]=np.floor(np.log(u[regular])/np.log1p(-p[regular]))+1;geometric[p>=1]=1
        counts=np.minimum(proposed,geometric).astype(int)
        counts*=rng.random(shape)<prediction['alive'][start:stop,None]
        spend_shape,posterior_shape,posterior_rate=gg.posterior(f)
        rate=rng.gamma(posterior_shape[:,None],1/posterior_rate[:,None],size=shape)
        spend=100*rng.gamma(spend_shape*counts,1/rate)
        for label,values in [('count',counts),('spend',spend)]:
            low,high=np.quantile(values,[.05,.95],axis=1,method='inverted_cdf');output[label+'_lower'][start:stop]=low;output[label+'_upper'][start:stop]=high
        output['simulated_count_mean'][start:stop]=counts.mean(axis=1)
        for k in range(6):masses[start:stop,k]=((counts==k) if k<5 else (counts>=5)).mean(axis=1)
    output['count_distribution']=masses
    return output


class HurdleBoosting:
    def __init__(self,leaves):self.leaves=leaves
    def fit(self,frame):
        x=feature_matrix(frame);count=frame.future_count.to_numpy(float);positive=count>0
        common=dict(max_iter=CONFIG['boosting_iterations'],learning_rate=.05,l2_regularization=1,max_leaf_nodes=self.leaves,min_samples_leaf=30,early_stopping=False,random_state=CONFIG['seed'])
        self.classifier=HistGradientBoostingClassifier(**common).fit(x,positive)
        self.excess=HistGradientBoostingRegressor(loss='poisson',**common).fit(x[positive],count[positive]-1)
        self.spend=HistGradientBoostingRegressor(loss='gamma',**common).fit(x[positive],frame.future_spend.to_numpy(float)[positive]/count[positive],sample_weight=count[positive])
        return self
    def predict(self,frame):
        x=feature_matrix(frame);probability=self.classifier.predict_proba(x)[:,1];count=probability*(1+self.excess.predict(x));value=self.spend.predict(x)
        return {'count':count,'purchase':probability,'spend_per_purchase':value,'spend':count*value}


def recent_rule(frame):
    count=frame.past90_count.to_numpy(float)*frame.horizon.to_numpy(float)/90
    spend=np.divide(frame.past90_spend.to_numpy(float),frame.past90_count.to_numpy(float),out=frame.mean_spend.to_numpy(float).copy(),where=frame.past90_count.to_numpy(float)>0)
    return {'count':count,'purchase':-np.expm1(-count),'spend_per_purchase':spend,'spend':count*spend}


class RFMRule:
    def fit(self,frame):
        self.cells={}
        for h in CONFIG['horizons_days']:
            f=frame[frame.horizon==h];prior_count=f.future_count.mean();prior_prob=(f.future_count>0).mean();prior_spend=f.future_spend.sum()/f.future_count.sum()
            for group in f.rfm.unique():
                s=f[f.rfm==group];n=len(s);count=(s.future_count.sum()+20*prior_count)/(n+20);prob=((s.future_count>0).sum()+20*prior_prob)/(n+20);spend=(s.future_spend.sum()+10*prior_spend)/(s.future_count.sum()+10)
                self.cells[(h,group)]=(count,prob,spend)
            self.cells[(h,None)]=(prior_count,prior_prob,prior_spend)
        return self
    def predict(self,frame):
        values=np.array([self.cells.get((h,g),self.cells[(h,None)]) for h,g in zip(frame.horizon,frame.rfm)])
        return {'count':values[:,0],'purchase':values[:,1],'spend_per_purchase':values[:,2],'spend':values[:,0]*values[:,2]}


def interval_quantile(scores,level=.9):
    ordered=np.sort(scores);index=min(len(scores)-1,int(np.ceil((len(scores)+1)*level))-1)
    return ordered[index]


def empirical_bands(prediction,horizons,quantiles):
    result={}
    for target in ['count','spend']:
        center=prediction[target];scale=np.sqrt(center+1) if target=='count' else np.maximum(center,1)
        q=np.array([quantiles[int(h)][target] for h in horizons]);low=np.maximum(0,center-q*scale);high=center+q*scale
        if target=='count':low=np.floor(low);high=np.ceil(high)
        result[target+'_lower']=low;result[target+'_upper']=high
    return result


def break_even(cost,margin,spend_per_purchase):
    if not 0<=cost<=5 or not .1<=margin<=.5 or spend_per_purchase<=0:raise ValueError('Unsupported campaign assumption')
    return cost/(margin*spend_per_purchase)
