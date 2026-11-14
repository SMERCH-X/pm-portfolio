import unittest
from pysentry import scan_source,to_sarif
class Tests(unittest.TestCase):
 def test_dangerous_calls(self):
  ids={x['rule_id'] for x in scan_source('import subprocess\neval(data)\nsubprocess.run(cmd, shell=True)')}
  self.assertTrue({'PY001','PY003'}.issubset(ids))
 def test_secret(self): self.assertIn('PY008',{x['rule_id'] for x in scan_source('api_key = "abcdefghijklmnop"')})
 def test_sarif(self): self.assertEqual(to_sarif([],'x.py')['version'],'2.1.0')
if __name__=='__main__': unittest.main()

class SarifPathsTests(unittest.TestCase):
 def test_per_finding_uri(self):
  findings=[{'rule_id':'PY001','severity':'HIGH','line':2,'message':'eval','file':'example.py'}]
  result=to_sarif(findings,'root')
  self.assertEqual(result['runs'][0]['results'][0]['locations'][0]['physicalLocation']['artifactLocation']['uri'],'example.py')
