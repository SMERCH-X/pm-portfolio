import argparse,ast,json,re
from pathlib import Path
RULES={'PY001':('HIGH','Use of eval() can execute attacker-controlled code.'),'PY002':('HIGH','Use of exec() can execute dynamically supplied code.'),'PY003':('HIGH','subprocess call uses shell=True; avoid shell interpretation.'),'PY004':('HIGH','pickle deserialization can execute code; do not load untrusted data.'),'PY005':('MEDIUM','yaml.load() may be unsafe; use yaml.safe_load() for untrusted input.'),'PY006':('MEDIUM','MD5 is unsuitable for security-sensitive hashing.'),'PY007':('MEDIUM','SHA-1 is unsuitable for security-sensitive hashing.')}
SECRET=re.compile(r'''(?i)\b(api[_-]?key|secret|token|password)\b\s*=\s*['"][^'"]{8,}['"]''')
class Visitor(ast.NodeVisitor):
 def __init__(self): self.findings=[]
 def add(self,node,rule):
  sev,msg=RULES[rule]; self.findings.append({'rule_id':rule,'severity':sev,'line':getattr(node,'lineno',1),'message':msg})
 def visit_Call(self,node):
  f=node.func; name=f.id if isinstance(f,ast.Name) else (f'{f.value.id}.{f.attr}' if isinstance(f,ast.Attribute) and isinstance(f.value,ast.Name) else '')
  if name=='eval': self.add(node,'PY001')
  if name=='exec': self.add(node,'PY002')
  if name in ('subprocess.run','subprocess.call','subprocess.Popen') and any(k.arg=='shell' and isinstance(k.value,ast.Constant) and k.value.value is True for k in node.keywords): self.add(node,'PY003')
  if name in ('pickle.load','pickle.loads'): self.add(node,'PY004')
  if name=='yaml.load': self.add(node,'PY005')
  if name=='hashlib.md5': self.add(node,'PY006')
  if name=='hashlib.sha1': self.add(node,'PY007')
  self.generic_visit(node)
def scan_source(source,filename='<memory>'):
 try: tree=ast.parse(source,filename=filename)
 except SyntaxError as e: return [{'rule_id':'PY000','severity':'INFO','line':e.lineno or 1,'message':f'Cannot parse source: {e.msg}'}]
 v=Visitor(); v.visit(tree); found=v.findings
 for n,line in enumerate(source.splitlines(),1):
  if SECRET.search(line): found.append({'rule_id':'PY008','severity':'HIGH','line':n,'message':'Possible hardcoded secret; use environment variables or a secret manager.'})
 return sorted(found,key=lambda x:(x['line'],x['rule_id']))
def to_sarif(results,uri):
 rules=[{'id':k,'shortDescription':{'text':v[1]}} for k,v in RULES.items()]+[{'id':'PY008','shortDescription':{'text':'Possible hardcoded secret.'}}]
 return {'version':'2.1.0','$schema':'https://json.schemastore.org/sarif-2.1.0.json','runs':[{'tool':{'driver':{'name':'PySentry','rules':rules}},'results':[{'ruleId':x['rule_id'],'level':{'HIGH':'error','MEDIUM':'warning','INFO':'note'}.get(x['severity'],'warning'),'message':{'text':x['message']},'locations':[{'physicalLocation':{'artifactLocation':{'uri':x.get('file',uri)},'region':{'startLine':x['line']}}}]} for x in results]}]}
def main():
 p=argparse.ArgumentParser(description='AST-based static security checks for Python source.'); p.add_argument('path',type=Path); p.add_argument('--sarif',type=Path); a=p.parse_args()
 if not a.path.exists(): p.error(f'Path not found: {a.path}')
 paths=[a.path] if a.path.is_file() else sorted(x for x in a.path.rglob('*.py') if not any(part in {'.git','.venv','venv','__pycache__'} for part in x.parts)); allf=[]
 for path in paths:
  for f in scan_source(path.read_text(errors='replace'),str(path)): f['file']=str(path); allf.append(f)
 print(json.dumps({'files_scanned':len(paths),'findings':allf},indent=2))
 if a.sarif: a.sarif.write_text(json.dumps(to_sarif(allf,str(a.path)),indent=2)+'\n')
if __name__=='__main__': main()
