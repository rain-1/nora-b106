"""Validate the saved design and export the bare-PCB fabrication package."""
from pathlib import Path
import csv
import hashlib
import json
import subprocess
import zipfile

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'fabrication'
REPORTS=OUT/'reports'
GERBERS=OUT/'gerbers'
for directory in (REPORTS,GERBERS):directory.mkdir(parents=True,exist_ok=True)
def run(*args):subprocess.run(args,cwd=ROOT,check=True)
run('kicad-cli','sch','erc','--exit-code-violations','--format','json','-o',str(REPORTS/'erc.json'),'nora-b106-board.kicad_sch')
run('kicad-cli','pcb','drc','--schematic-parity','--exit-code-violations','--format','json','-o',str(REPORTS/'drc.json'),'nora-b106-board.kicad_pcb')
run('/usr/bin/python3','tools/check_module_ground.py')
# The output directory is dedicated to generated fabrication files.
for old in GERBERS.iterdir():
    if old.is_file():old.unlink()
run('kicad-cli','pcb','export','gerbers','--layers','F.Cu,B.Cu,F.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts','--subtract-soldermask','-o',str(GERBERS)+'/', 'nora-b106-board.kicad_pcb')
run('kicad-cli','pcb','export','drill','--format','excellon','--excellon-separate-th','--excellon-units','mm','-o',str(GERBERS)+'/', 'nora-b106-board.kicad_pcb')
zip_path=OUT/'nora-b106-breakout-revB-gerbers.zip'
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(GERBERS.iterdir()):archive.write(path,path.name)
files=['nora-b106-board.kicad_pcb','nora-b106-board.kicad_sch','nora-b106-board.kicad_pro','hardware/BOM.csv']
manifest={'revision':'B','board_mm':[36,36],'thickness_mm':0.8,'copper_layers':2,'copper_oz':1,'assembly':'self assembly; see hardware/README.md for SWD-only and USB variants','status':'CAD checks passed; physical prototype not yet tested','sha256':{file:hashlib.sha256((ROOT/file).read_bytes()).hexdigest() for file in files},'gerber_zip_sha256':hashlib.sha256(zip_path.read_bytes()).hexdigest()}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Bare-PCB package:',zip_path)
