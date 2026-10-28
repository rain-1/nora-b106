"""Validate the KiCad 9 working project; optionally export bare-board files."""
from pathlib import Path
import os,shlex,subprocess,json,hashlib,zipfile,sys
r=Path(__file__).resolve().parents[1]
check_only='--check' in sys.argv
out=r/'fabrication';reports=(r/'build/reports') if check_only else (out/'reports');g=out/'gerbers'
reports.mkdir(parents=True,exist_ok=True)
cli=shlex.split(os.environ.get('KICAD_CLI','kicad-cli'))
def run(*args,report=None):
 result=subprocess.run([str(x) for x in args],cwd=r,text=True,capture_output=report is not None,check=True)
 if report is not None:
  report.write_text(result.stdout+result.stderr);print(result.stdout,end='')
run(*cli,'sch','erc','--exit-code-violations','--format','json','-o',reports/'erc.json',r/'nora-minimal.kicad_sch')
run(*cli,'pcb','drc','--schematic-parity','--exit-code-violations','--format','json','-o',reports/'drc.json',r/'nora-minimal.kicad_pcb')
run('/usr/bin/python3',r/'tools/check_module_ground.py',report=reports/'ground-check.txt')
run('/usr/bin/python3',r/'tools/audit_design.py',report=reports/'pad-audit.txt')
run(sys.executable,r/'tools/check_firmware.py','--output',reports/'firmware-compatibility.json')
if check_only:raise SystemExit(0)
g.mkdir(parents=True,exist_ok=True)
for p in g.iterdir():
 if p.is_file():p.unlink()
run(*cli,'pcb','export','gerbers','--layers','F.Cu,B.Cu,F.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts','--subtract-soldermask','-o',str(g)+'/',r/'nora-minimal.kicad_pcb')
run(*cli,'pcb','export','drill','--format','excellon','--excellon-separate-th','--excellon-units','mm','-o',str(g)+'/',r/'nora-minimal.kicad_pcb')
z=out/'nora-square-P3-gerbers.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as a:
 for p in sorted(g.iterdir()):a.write(p,p.name)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files=['nora-minimal.kicad_pcb','nora-minimal.kicad_sch','nora-minimal.kicad_pro','hardware/BOM.csv','design.json']
m={'revision':'P3','board_mm':[49.5,49.5],'thickness_mm':1.6,'layers':2,'copper_oz':1,'export_source':'KiCad 9 Square P3 working project, derived from Backplane-assisted Minimal P1','status':'CAD validation passed; no physical prototype or programming test','sha256':{f:sha(r/f) for f in files},'gerber_zip_sha256':sha(z),'gerber_sha256':{p.name:sha(p) for p in sorted(g.iterdir())}}
(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print('Fabrication package:',z)
