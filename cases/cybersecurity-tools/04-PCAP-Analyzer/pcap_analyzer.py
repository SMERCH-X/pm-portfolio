import argparse,json
from collections import defaultdict
from datetime import datetime,timezone
def analyze_packets(rows,port_threshold=15,syn_threshold=100):
 ports=defaultdict(set); syn=defaultdict(int)
 for row in rows:
  src=row.get('src')
  if not src: continue
  if row.get('dst_port') is not None: ports[src].add(int(row['dst_port']))
  if row.get('tcp_syn') and not row.get('tcp_ack'): syn[src]+=1
 alerts=[]
 for src,seen in ports.items():
  if len(seen)>=port_threshold: alerts.append({'severity':'medium','type':'possible_port_scan','source_ip':src,'unique_destination_ports':len(seen)})
 for src,count in syn.items():
  if count>=syn_threshold: alerts.append({'severity':'high','type':'possible_syn_flood','source_ip':src,'syn_packets':count})
 return alerts
def load_pcap(path):
 """Read classic PCAP (Ethernet linktype 1) without third-party dependencies.

 Supports untagged Ethernet, IPv4 and IPv6 TCP without IPv6 extension headers.
 Does not support PCAPNG, VLAN tags, or other link-layer formats.
 """
 import ipaddress
 import struct
 from pathlib import Path
 with Path(path).open('rb') as stream:
  header=stream.read(24)
  if len(header)!=24: raise ValueError('Invalid or truncated PCAP header')
  magic=header[:4]
  if magic in (b'\xd4\xc3\xb2\xa1',b'\x4d\x3c\xb2\xa1'): endian='<'
  elif magic in (b'\xa1\xb2\xc3\xd4',b'\xa1\xb2\x3c\x4d'): endian='>'
  else: raise ValueError('Unsupported capture format (expected classic PCAP, not PCAPNG)')
  network=struct.unpack(endian+'I',header[20:24])[0]
  if network!=1: raise ValueError('Only Ethernet PCAP (linktype 1) is supported')
  rows=[]
  while True:
   record=stream.read(16)
   if not record: break
   if len(record)!=16: raise ValueError('Truncated PCAP packet header')
   incl_len=struct.unpack(endian+'I',record[8:12])[0]
   if incl_len>16*1024*1024: raise ValueError('Unreasonably large captured packet')
   packet=stream.read(incl_len)
   if len(packet)!=incl_len: raise ValueError('Truncated PCAP packet data')
   if len(packet)<14: continue
   ethertype=int.from_bytes(packet[12:14],'big')
   if ethertype==0x0800:
    if len(packet)<34 or packet[14]>>4!=4: continue
    ihl=(packet[14]&15)*4
    if ihl<20 or len(packet)<14+ihl+14 or packet[23]!=6: continue
    # Non-initial IPv4 fragments do not carry a TCP header.
    if int.from_bytes(packet[20:22],'big')&0x1fff: continue
    src=str(ipaddress.IPv4Address(packet[26:30])); offset=14+ihl
   elif ethertype==0x86dd:
    if len(packet)<14+40+14 or packet[14]>>4!=6 or packet[20]!=6: continue
    src=str(ipaddress.IPv6Address(packet[22:38])); offset=54
   else: continue
   port=int.from_bytes(packet[offset+2:offset+4],'big')
   flags=packet[offset+13]
   rows.append({'src':src,'dst_port':port,'tcp_syn':bool(flags&2),'tcp_ack':bool(flags&16)})
  return rows
def main():
 p=argparse.ArgumentParser(description='Offline PCAP triage for basic TCP attack patterns.'); p.add_argument('pcap'); p.add_argument('--port-threshold',type=int,default=15); p.add_argument('--syn-threshold',type=int,default=100); p.add_argument('--json',dest='json_file'); a=p.parse_args()
 if a.port_threshold < 1 or a.syn_threshold < 1: p.error('thresholds must be positive')
 try: rows=load_pcap(a.pcap)
 except (OSError,ValueError) as e: p.error(str(e))
 out=json.dumps({'file':a.pcap,'packets_analyzed':len(rows),'analyzed_at':datetime.now(timezone.utc).isoformat(),'alerts':analyze_packets(rows,a.port_threshold,a.syn_threshold)},indent=2); print(out)
 if a.json_file: open(a.json_file,'w').write(out+'\n')
if __name__=='__main__': main()
