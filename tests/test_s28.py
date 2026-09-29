import importlib.util
import unittest
import numpy as np
import pandas as pd
from research_program.io import ROOT

spec=importlib.util.spec_from_file_location('s28',ROOT/'studies/S28/study.py')
study=importlib.util.module_from_spec(spec);spec.loader.exec_module(study)


class SalesTests(unittest.TestCase):
    def test_unavailable_columns_never_reach_features(self):
        data=pd.DataFrame({'contact':['cellular'],'month':['may'],'day_of_week':['mon'],'poutcome':['nonexistent'],'previous':[0],'campaign':[1],'pdays':[999],'duration':[900],'y':['yes'],'euribor3m':[9]})
        x=study.features(data)
        self.assertEqual(x.campaign_prior.iloc[0],0)
        self.assertEqual(x.ever_contacted.iloc[0],0)
        self.assertTrue(np.isnan(x.prior_days.iloc[0]))
        self.assertFalse(set(study.CONFIG['excluded']+['y','campaign']) & set(x.columns))
        changed=data.assign(duration=0,y='no',euribor3m=-20)
        pd.testing.assert_frame_equal(x,study.features(changed))

    def test_splits_have_no_overlap_or_random_shuffle(self):
        a,b=study.split_boundaries(41188)
        self.assertEqual((a,b),(28831,32950))
        self.assertLess(a,b);self.assertLess(b,41188)
        self.assertLessEqual(max(end for _,end in study.CONFIG['tuning_folds']),study.CONFIG['development_end'])

    def test_unknown_categories_are_not_fitted_from_validation(self):
        frame=pd.DataFrame({c:[0,1,2,3]*5 for c in study.NUMERIC})
        for c in study.CATEGORICAL:frame[c]=['known']*20
        model=study.model('logistic',.1).fit(frame,np.array([0,1]*10))
        changed=frame.copy();changed['contact']='new'
        output=model.predict_proba(changed)
        self.assertTrue(np.isfinite(output).all())
        fitted=model.named_steps['preprocessing'].named_transformers_['categorical']
        self.assertNotIn('new',fitted.categories_[0])

    def test_sigmoid_calibration_is_bounded(self):
        p=study.calibrate([.1,.2,.8,.9],[0,0,1,1],[0,.5,1])
        self.assertTrue(((p>0)&(p<1)).all())
        self.assertTrue(np.all(np.diff(p)>0))


if __name__=='__main__':unittest.main()
