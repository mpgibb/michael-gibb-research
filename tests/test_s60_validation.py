"""Reject malformed arguments before any simulated tool can be called."""
import unittest,importlib.util
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'studies/S60/tool_validation.py';spec=importlib.util.spec_from_file_location('validation',p);V=importlib.util.module_from_spec(spec);spec.loader.exec_module(V)
S={'change':{'type':'object','properties':{'id':{'type':'string'},'status':{'type':'string','enum':['open','closed']},'items':{'type':'array','items':{'type':'string'}}},'required':['id','status']}}
class ToolValidationTests(unittest.TestCase):
 def test_valid(self):self.assertTrue(V.validate_call('change','{"id":"x","status":"open"}',S)['valid'])
 def test_unknown_tool(self):self.assertEqual(V.validate_call('delete',{},S)['reason'],'unknown_tool')
 def test_unknown_argument(self):self.assertFalse(V.validate_call('change',{'id':'x','status':'open','extra':1},S)['valid'])
 def test_type_and_enum(self):
  for obj in [{'id':True,'status':'open'},{'id':'x','status':'other'},{'id':'x','status':'open','items':[1]}]:self.assertFalse(V.validate_call('change',obj,S)['valid'])
 def test_duplicate_and_nonfinite_json(self):
  for text in ['{"id":"x","id":"y","status":"open"}','{"id":NaN,"status":"open"}']:
   self.assertEqual(V.validate_call('change',text,S)['reason'],'invalid_json')
 def test_missing_and_nonobject(self):
  self.assertFalse(V.validate_call('change',{'id':'x'},S)['valid']);self.assertEqual(V.validate_call('change','[]',S)['reason'],'non_object_arguments')
 def test_schema_is_not_mutated(self):
  V.validate_call('change',{'id':'x','status':'open'},S);self.assertNotIn('additionalProperties',S['change'])
