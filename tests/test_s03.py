"""Tests of transaction grain, information timing and purchase-model identities."""
import unittest
import numpy as np
import pandas as pd
from scipy.special import hyp2f1
from studies.S03 import ingest,models,study
from sklearn.metrics import mean_poisson_deviance,log_loss,brier_score_loss


class CustomerModelChecks(unittest.TestCase):
 def test_sheet_overlap_is_separate_from_repeated_lines(self):
  row=dict(zip(ingest.COLUMNS,['1','A','Item',1,pd.Timestamp('2010-12-02'),10.,1.,'UK']))
  a=pd.DataFrame([row,row]);b=pd.DataFrame([row,row,row]);self.assertEqual(len(ingest.combine_sheets([a,b])),1);self.assertEqual(len(ingest.combine_sheets([a,b],True)),3)
 def test_positive_purchase_and_signed_return_separation(self):
  frame=pd.DataFrame({'Invoice':['1','2','C3','4'],'Quantity':[1,2,-1,1],'Price':[10.,10.,10.,10.],'Customer ID':[1.,1.,1.,np.nan],'InvoiceDate':pd.to_datetime(['2010-01-01']*4)})
  events,net=ingest.prepare_events(frame);self.assertEqual(len(events),1);self.assertEqual(events.spend.iloc[0],30);self.assertEqual(net.net_spend.iloc[0],20)
 def test_cutoff_and_horizon_boundaries_exclude_future_features(self):
  e=pd.DataFrame({'customer':['a']*5,'date':pd.to_datetime(['2010-01-01','2010-01-15','2010-02-01','2010-03-02','2010-03-03']),'spend':[10.,20.,30.,40.,50.]});n=e.rename(columns={'spend':'net_spend'})
  s=ingest.snapshots(e,n,'2010-02-01');r=s[s.horizon==30].iloc[0]
  self.assertEqual(r.purchase_days,2);self.assertEqual(r.total_spend,30);self.assertEqual(r.future_count,2);self.assertEqual(r.future_spend,70)
  e2=e.copy();e2.loc[e2.date>=pd.Timestamp('2010-02-01'),'spend']=9999
  s2=ingest.snapshots(e2,n,'2010-02-01');np.testing.assert_equal(ingest.feature_matrix(s),ingest.feature_matrix(s2))
 def test_bgnbd_quadrature_matches_closed_form_and_a_one(self):
  f=pd.DataFrame({'frequency':[0.,2.,8.],'tx':[0.,10.,25.],'age':[20.,20.,30.],'horizon':[90.,90.,60.]})
  bg=models.BGNBD()
  for a in [.5,1.,2.]:
   bg.params=np.array([.6,5.,a,3.]);p=bg.predict(f,64);fine=bg.predict(f,128);np.testing.assert_allclose(p['count'],fine['count'],rtol=1e-8,atol=1e-10)
   self.assertEqual(p['alive'][0],1.);self.assertTrue(np.all(p['purchase']<=np.minimum(1,p['count'])))
   if a!=1:
    x=f.frequency.to_numpy();age=f.age.to_numpy();h=f.horizon.to_numpy()/7;r,alpha,_,b=bg.params
    expected=(a+b+x-1)/(a-1)*(1-((alpha+age)/(alpha+age+h))**(r+x)*hyp2f1(r+x,b+x,a+b+x-1,h/(alpha+age+h)))*p['alive']
    np.testing.assert_allclose(p['count'],expected,rtol=1e-7)
 def test_predictive_simulation_matches_purchase_expectation(self):
  f=pd.DataFrame({'frequency':[0.,3.],'tx':[0.,10.],'age':[20.,20.],'horizon':[90.,90.],'repeat_mean_spend':[0.,50.]})
  bg=models.BGNBD();bg.params=np.array([.6,5.,.8,3.]);gg=models.GammaGamma();gg.params=np.array([3.,2.,1.]);p=bg.predict(f);sim=models.predictive_distribution(bg,gg,f,p,91,60000)
  np.testing.assert_allclose(sim['simulated_count_mean'],p['count'],atol=.02);np.testing.assert_allclose(1-sim['count_distribution'][:,0],p['purchase'],atol=.01);np.testing.assert_allclose(sim['count_distribution'].sum(axis=1),1)
  self.assertTrue(np.all(sim['spend_lower']<=sim['spend_upper']))
 def test_gamma_gamma_mean_uses_repeat_count_and_finite_prior(self):
  gg=models.GammaGamma();gg.params=np.array([2.,3.,4.]);f=pd.DataFrame({'frequency':[0.,5.],'repeat_mean_spend':[0.,100.]});np.testing.assert_allclose(gg.predict(f),[800/3,1800/13])
 def test_calibration_partition_is_customer_stable(self):
  a=ingest.validation_selection(['a','b','a']);self.assertEqual(a[0],a[2])
 def test_finite_sample_interval_and_break_even_units(self):
  self.assertEqual(models.interval_quantile(np.arange(10),.9),9);self.assertEqual(models.break_even(1,.2,50),.1)
  with self.assertRaises(ValueError):models.break_even(1,0,50)

 def test_metric_components_match_independent_reference(self):
  f=pd.DataFrame({'future_count':[0.,1.,4.],'future_spend':[0.,20.,70.]})
  p={'count':np.array([.2,1.2,3.]),'purchase':np.array([.1,.8,.9]),'spend':np.array([3.,30.,60.])}
  got=study.score(f,p)
  self.assertAlmostEqual(got['count_poisson_deviance'],mean_poisson_deviance(f.future_count,p['count']))
  self.assertAlmostEqual(got['purchase_log_loss'],log_loss(f.future_count>0,p['purchase']))
  self.assertAlmostEqual(got['purchase_brier'],brier_score_loss(f.future_count>0,p['purchase']))
  self.assertAlmostEqual(got['spend_ratio'],93/90)
 def test_rolling_training_requires_completed_labels_and_reserved_customers(self):
  ids=[str(i) for i in range(100)];kept=next(i for i in ids if ingest.validation_selection([i])[0]);reserved=next(i for i in ids if not ingest.validation_selection([i])[0])
  data={'2010-09-01':pd.DataFrame({'customer':[kept,kept],'label_end':pd.to_datetime(['2011-03-01','2011-03-02'])}), '2010-12-01':pd.DataFrame({'customer':[kept,reserved],'label_end':pd.to_datetime(['2011-03-01']*2)}), '2011-03-01':pd.DataFrame({'customer':[kept],'label_end':pd.to_datetime(['2011-06-01'])})}
  got=ingest.permitted_training(data,'2011-03-01');self.assertEqual(len(got),2);self.assertTrue((got.customer==kept).all());self.assertEqual(got.label_end.max(),pd.Timestamp('2011-03-01'))


if __name__=='__main__':unittest.main()
