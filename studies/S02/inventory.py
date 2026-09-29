"""One-cycle stock accounting and exact feasible hindsight comparator."""
import numpy as np


def replay(demand,initial,order,lead,holding,penalty):
    demand=np.asarray(demand,float);stock=np.asarray(initial,float).copy();order=np.asarray(order,float)
    if (demand<0).any() or (stock<0).any() or (order<0).any():raise ValueError('Negative inventory inputs')
    lost=np.zeros_like(stock);held=np.zeros_like(stock)
    for day in range(demand.shape[1]):
        if day==lead:stock+=order
        served=np.minimum(stock,demand[:,day]);stock-=served
        lost+=demand[:,day]-served;held+=stock
    return {'cost':held*holding+lost*penalty,'lost_units':lost,'holding_unit_days':held,'ending_stock':stock}


def hindsight(demand,initial,maximum_order,lead,holding,penalty):
    maximum_order=np.floor(maximum_order).astype(int)
    if (maximum_order<0).any():raise ValueError('Infeasible storage')
    lo=np.zeros(len(initial),int);hi=maximum_order.copy()
    # Discrete convex costs: find the first nonnegative forward difference.
    while np.any(lo<hi):
        mid=(lo+hi)//2
        delta=replay(demand,initial,mid+1,lead,holding,penalty)['cost']-replay(demand,initial,mid,lead,holding,penalty)['cost']
        take=(lo<hi)&(delta< -1e-10);stay=(lo<hi)&~take
        lo[take]=mid[take]+1;hi[stay]=mid[stay]
    return lo,replay(demand,initial,lo,lead,holding,penalty)
