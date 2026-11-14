import argparse,json,re
from collections import defaultdict
from datetime import datetime,timedelta
from pathlib import Path
PATTERNS=[('failed',re.compile(r'^(?P<ts>\S+)\s+(?P<host>\S+)\s+sshd(?:\[\d+\])?: Failed password for (?:invalid user )?(?P<user>\S+) from (?P<ip>[0-9a-fA-F:.]+)')),('invalid_user',re.compile(r'^(?P<ts>\S+)\s+(?P<host>\S+)\s+sshd(?:\[\d+\])?: Invalid user (?P<user>\S+) from (?P<ip>[0-9a-fA-F:.]+)')),('accepted',re.compile(r'^(?P<ts>\S+)\s+(?P<host>\S+)\s+sshd(?:\[\d+\])?: Accepted \S+ for (?P<user>\S+) from (?P<ip>[0-9a-fA-F:.]+)'))]
def parse_line(line):
 for kind,pat in PATTERNS:
  m=pat.search(line.strip())
  if m:
   try: datetime.fromisoformat(m['ts'].replace('Z','+00:00'))
   except ValueError: return None
   return {'timestamp':m['ts'],'host':m['host'],'username':m['user'],'source_ip':m['ip'],'event':kind}
 return None
def analyze(events,threshold=5,window_minutes=10):
 grouped=defaultdict(list)
 for e in events:
  if e.get('event') == 'failed':
   try: grouped[e['source_ip']].append(datetime.fromisoformat(e['timestamp'].replace('Z','+00:00')))
   except (KeyError,ValueError): pass
 alerts=[]; window=timedelta(minutes=window_minutes)
 for ip,stamps in grouped.items():
  stamps.sort(); left=0
  for right,stamp in enumerate(stamps):
   while stamp-stamps[left]>window: left+=1
   count=right-left+1
   if count>=threshold:
    alerts.append({'severity':'high','type':'ssh_bruteforce_suspected','source_ip':ip,'attempts':count,'window_minutes':window_minutes,'first_seen':stamps[left].isoformat(),'last_seen':stamp.isoformat()}); break
 return alerts
def main():
 p=argparse.ArgumentParser(description='Analyze SSH authentication logs for repeated failures.')
 p.add_argument('logfile',type=Path); p.add_argument('--threshold',type=int,default=5); p.add_argument('--window',type=int,default=10); p.add_argument('--json',type=Path); a=p.parse_args()
 
 if a.threshold < 1 or a.window <= 0: p.error('--threshold must be >= 1 and --window must be > 0')
 try: lines=a.logfile.read_text(encoding='utf-8',errors='replace').splitlines()
 except OSError as exc: p.error(str(exc))
 events=[e for line in lines if (e:=parse_line(line))]
 out=json.dumps({'events_parsed':len(events),'alerts':analyze(events,a.threshold,a.window)},indent=2); print(out)
 if a.json: a.json.write_text(out+'\n')
if __name__=='__main__': main()
