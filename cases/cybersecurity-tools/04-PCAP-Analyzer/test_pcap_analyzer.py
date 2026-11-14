import unittest
from pcap_analyzer import analyze_packets
class Tests(unittest.TestCase):
 def test_scan(self):
  rows=[{'src':'192.0.2.5','dst_port':p,'tcp_syn':True,'tcp_ack':False} for p in range(1,20)]
  self.assertEqual(analyze_packets(rows,15)[0]['type'],'possible_port_scan')
 def test_syn_flood(self):
  rows=[{'src':'192.0.2.9','dst_port':443,'tcp_syn':True,'tcp_ack':False} for _ in range(101)]
  self.assertTrue(any(x['type']=='possible_syn_flood' for x in analyze_packets(rows,syn_threshold=100)))
if __name__=='__main__': unittest.main()

class FileTests(unittest.TestCase):
 def test_sample_pcap(self):
  from pcap_analyzer import load_pcap
  from pathlib import Path
  rows=load_pcap(Path(__file__).with_name('sample.pcap'))
  self.assertEqual(len(rows),4)
  self.assertEqual(rows[0]['src'],'192.0.2.5')
  self.assertEqual(len(analyze_packets(rows,port_threshold=3,syn_threshold=4)),2)
