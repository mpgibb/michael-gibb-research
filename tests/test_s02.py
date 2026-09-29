import importlib.util
from pathlib import Path
import unittest
import numpy as np
import pandas as pd
from research_program.io import ROOT


def module(name):
    spec=importlib.util.spec_from_file_location('s02_'+name,ROOT/'studies/S02'/f'{name}.py');value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value

inv=module('inventory');forecast=module('forecast')


class InventoryStudyTests(unittest.TestCase):
    def test_stock_flow_conserves_units(self):
        demand=np.array([[2,5,3],[0,0,1]])
        initial=np.array([3,1]);order=np.array([4,2])
        r=inv.replay(demand,initial,order,1,.1,2)
        np.testing.assert_allclose(initial+order,demand.sum(axis=1)-r['lost_units']+r['ending_stock'])
        np.testing.assert_allclose(r['cost'],.1*r['holding_unit_days']+2*r['lost_units'])

    def test_order_cannot_serve_demand_before_arrival(self):
        r=inv.replay([[5,0,0]],[0],[5],1,0,1)
        self.assertEqual(r['lost_units'][0],5);self.assertEqual(r['ending_stock'][0],5)

    def test_hindsight_matches_exhaustive_feasible_orders(self):
        rng=np.random.default_rng(12)
        for lead in [0,1,3]:
            for holding,penalty in [(.01,1),(.8,.5),(0,1)]:
                demand=rng.integers(0,6,(6,7));initial=rng.integers(0,4,6);maximum=rng.integers(0,16,6)
                chosen,r=inv.hindsight(demand,initial,maximum,lead,holding,penalty)
                for i in range(6):
                    costs=[inv.replay(demand[i:i+1],initial[i:i+1],[q],lead,holding,penalty)['cost'][0] for q in range(maximum[i]+1)]
                    self.assertAlmostEqual(r['cost'][i],min(costs),places=8)
                    self.assertLessEqual(chosen[i],maximum[i]);self.assertGreaterEqual(chosen[i],0)

    def test_future_sales_and_prices_do_not_change_features(self):
        n=2;y=np.ones((n,450));price=np.ones_like(y);meta=pd.DataFrame({c:['A','B'] for c in ['item_id','store_id','dept_id','cat_id','state_id']});cal=pd.DataFrame({'month':np.ones(450),'wday':np.ones(450)})
        a=forecast.features(y,price,meta,cal,400);y[:,400:]=10000;price[:,400:]=10000
        np.testing.assert_array_equal(a,forecast.features(y,price,meta,cal,400))
        config={'min_history':365,'training_window':730,'horizon':28,'training_stride':7}
        _,target=forecast.training(y,price,meta,cal,400,config)
        np.testing.assert_array_equal(target,np.repeat(28,len(target)))

    def test_scenarios_and_aggregations_are_coherent(self):
        meta=pd.DataFrame({'store_id':['A','B','A','B'],'cat_id':['X','X','Y','Y']})
        groups,A=forecast.aggregation(meta);q=np.array([[1,2,3],[2,3,7],[0,1,3],[4,7,11]])
        scenarios=forecast.joint_quantile_scenarios(q,np.arange(40).reshape(10,4),100,1)
        aggregate=scenarios@A.T
        self.assertEqual(scenarios.shape,(100,4));self.assertTrue((scenarios>=0).all())
        np.testing.assert_allclose(aggregate[:,-1],scenarios.sum(axis=1))
        np.testing.assert_allclose(aggregate[:,4]+aggregate[:,5],aggregate[:,-1])
        np.testing.assert_allclose(aggregate[:,6]+aggregate[:,7],aggregate[:,-1])

    def test_pinball_is_asymmetric_and_zero_for_exact_forecast(self):
        self.assertEqual(forecast.pinball(10,10,.9),0)
        self.assertAlmostEqual(forecast.pinball(10,8,.9),1.8)
        self.assertAlmostEqual(forecast.pinball(10,12,.9),.2)


if __name__=='__main__':unittest.main()
