import unittest
from netscope import parse_ports
class Tests(unittest.TestCase):
 def test_ranges(self): self.assertEqual(parse_ports('22,80,8000-8002'),[22,80,8000,8001,8002])
 def test_bad(self):
  with self.assertRaises(ValueError): parse_ports('0,70000')
  with self.assertRaises(ValueError): parse_ports('1-3000')
if __name__=='__main__': unittest.main()
