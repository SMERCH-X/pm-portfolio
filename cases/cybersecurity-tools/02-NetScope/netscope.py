import argparse,concurrent.futures,json,socket
from pathlib import Path
from datetime import datetime,timezone
COMMON=[21,22,23,25,53,80,110,143,443,445,3306,3389,5432,8080,8443]
def parse_ports(spec):
 ports=set()
 for part in spec.split(','):
  if '-' in part:
   lo,hi=map(int,part.split('-',1))
   if lo>hi: raise ValueError('Invalid port range')
   ports.update(range(lo,hi+1))
  else: ports.add(int(part))
 if not ports or min(ports)<1 or max(ports)>65535: raise ValueError('Ports must be 1..65535')
 if len(ports)>2048: raise ValueError('Maximum 2048 ports per run')
 return sorted(ports)
def scan_port(host,port,timeout):
 try:
  with socket.create_connection((host,port),timeout=timeout): return {'port':port,'state':'open'}
 except OSError: return {'port':port,'state':'closed_or_filtered'}
def scan(host,ports,timeout=.5,workers=32):
 with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool: return sorted(pool.map(lambda p:scan_port(host,p,timeout),ports),key=lambda x:x['port'])
def main():
 p=argparse.ArgumentParser(description='TCP connect scanner for explicitly authorized assets.'); p.add_argument('target'); p.add_argument('--ports',default=','.join(map(str,COMMON))); p.add_argument('--timeout',type=float,default=.5); p.add_argument('--workers',type=int,default=32); p.add_argument('--json',dest='json_file'); a=p.parse_args()
 if not .05<=a.timeout<=5: p.error('--timeout must be 0.05..5 seconds')
 if not 1<=a.workers<=64: p.error('--workers must be 1..64')
 try: socket.getaddrinfo(a.target,None,type=socket.SOCK_STREAM); ports=parse_ports(a.ports)
 except (ValueError,OSError) as e: p.error(str(e))
 out=json.dumps({'target':a.target,'scanned_at':datetime.now(timezone.utc).isoformat(),'results':scan(a.target,ports,a.timeout,a.workers)},indent=2); print(out)
 if a.json_file: Path(a.json_file).write_text(out+'\n',encoding='utf-8')
if __name__=='__main__': main()
