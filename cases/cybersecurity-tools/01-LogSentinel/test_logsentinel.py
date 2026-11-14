import unittest
from logsentinel import parse_line,analyze
class Tests(unittest.TestCase):
 def test_parse(self): self.assertEqual(parse_line('2026-10-10T10:00:00+00:00 h sshd[1]: Failed password for root from 192.0.2.1')['source_ip'],'192.0.2.1')
 def test_bruteforce(self): self.assertEqual(len(analyze([{'timestamp':f'2026-10-10T10:0{i}:00+00:00','source_ip':'192.0.2.1','event':'failed'} for i in range(5)])),1)
if __name__=='__main__': unittest.main()

class EdgeTests(unittest.TestCase):
 def test_invalid_user_not_double_counted(self):
  events=[{'timestamp':'2026-10-10T10:00:00+00:00','source_ip':'192.0.2.1','event':'invalid_user'}]
  self.assertEqual(analyze(events,threshold=1),[])
