"""Repeated-trial audit accounting without model calls or outcome invention."""
import unittest,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('s60_audit',ROOT/'studies/S60/publisher_audit.py');M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
def runs(rewards):return [{'task_id':0,'trial':i,'reward':x,'info':{'reward_info':{'reward':x},'user_cost':.1},'traj':[]} for i,x in enumerate(rewards)]
class ReliabilityAuditTests(unittest.TestCase):
 def test_all_k_success_differs_from_at_least_one(self):
  tasks,values,audit=M.analyze_runs(runs([1,1,0,0]));self.assertEqual(values['all_available'][1][0],.5);self.assertAlmostEqual(values['all_available'][2][0],1/6);self.assertEqual(values['all_available'][4][0],0)
 def test_duplicate_repeat_fails(self):
  data=runs([1,1,0,0]);data[3]['trial']=0
  with self.assertRaises(ValueError):M.analyze_runs(data)
 def test_reward_disagreement_fails(self):
  data=runs([1,1,0,0]);data[0]['info']['reward_info']['reward']=0
  with self.assertRaises(ValueError):M.analyze_runs(data)
 def test_missing_cost_is_not_zero(self):
  data=runs([1,1,0,0]);data[0]['info'].pop('user_cost');_,_,audit=M.analyze_runs(data);self.assertIsNone(audit['recorded_user_cost_USD']);self.assertIsNone(audit['complete_api_cost_USD'])
 def test_missing_reward_metadata_retains_failed_trial(self):
  data=runs([1,1,0,0]);data[3]['info']['reward_info']=None;_,values,audit=M.analyze_runs(data)
  self.assertEqual(audit['missing_reward_metadata_rows'],1);self.assertEqual(audit['runs'],4);self.assertEqual(values['all_available'][1][0],.5)
