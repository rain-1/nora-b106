#!/usr/bin/env python3
"""Build USB recovery + console, sign the app, and create an SWD factory HEX."""
from pathlib import Path
import argparse,os,subprocess,sys,json,hashlib,shutil
ROOT=Path(__file__).resolve().parents[2]
FW=ROOT/'firmware';BUILD=ROOT/'build/firmware';WS=BUILD/'workspace';VENV=BUILD/'venv'
p=argparse.ArgumentParser();p.add_argument('--version',help='Must match usb_bringup/VERSION');args=p.parse_args()
version_fields=dict(line.split('=',1) for line in (FW/'usb_bringup/VERSION').read_text().splitlines() if '=' in line)
version_fields={k.strip():v.strip() for k,v in version_fields.items()}
source_version='.'.join(str(int(version_fields[k])) for k in ['VERSION_MAJOR','VERSION_MINOR','PATCHLEVEL'])+'+'+str(int(version_fields['VERSION_TWEAK']))
if args.version is not None and args.version not in [source_version,source_version.removesuffix('+0')]:raise SystemExit('Update usb_bringup/VERSION first; image and application versions must match.')
args.version=source_version
env=os.environ.copy();env.update(PATH=str(VENV/'bin')+os.pathsep+env['PATH'],ZEPHYR_BASE=str(WS/'zephyr'),ZEPHYR_SDK_INSTALL_DIR=str(BUILD/'zephyr-sdk-1.0.1'),ZEPHYR_TOOLCHAIN_VARIANT='zephyr')
def run(*a):subprocess.run([str(x) for x in a],cwd=WS,env=env,check=True)
if not (VENV/'bin/west').exists():raise SystemExit('Run firmware/tools/setup.py first.')
key=FW/'keys/development.pem'
if not key.exists():raise SystemExit('Development signing key missing; restore it or deliberately install a new bootloader/key pair.')
conf=BUILD/'signing.conf';conf.write_text('CONFIG_BOOT_SIGNATURE_KEY_FILE='+json.dumps(str(key))+'\n')
board='nora_b106_minimal/nrf5340/cpuapp'
run(VENV/'bin/west','build','-b',board,WS/'bootloader/mcuboot/boot/zephyr','-d',BUILD/'bootloader','--','-DBOARD_ROOT='+str(FW),'-DCONF_FILE='+str(FW/'bootloader/prj.conf'),'-DEXTRA_CONF_FILE='+str(conf))
run(VENV/'bin/west','build','-b',board,FW/'usb_bringup','-d',BUILD/'app','--','-DBOARD_ROOT='+str(FW))
out=FW/'dist';out.mkdir(exist_ok=True)
imgtool=WS/'bootloader/mcuboot/scripts/imgtool.py'
for ext in ['bin']:
 run(VENV/'bin/python',imgtool,'sign','--key',key,'--align','4','--header-size','0x200','--slot-size','0x60000','--version',args.version,BUILD/('app/zephyr/zephyr.'+ext),out/('nora-app.signed.'+ext))
run(VENV/'bin/python',imgtool,'verify','--key',key,out/'nora-app.signed.bin')
# Use the build venv for intelhex, even if this script was started by system Python.
merge='''from intelhex import IntelHex
from pathlib import Path
import sys
b=IntelHex(sys.argv[1]);a=IntelHex();a.frombytes(Path(sys.argv[2]).read_bytes(),offset=0x30000);a.write_hex_file(sys.argv[4]);assert b.segments() and a.segments()
assert all(0<=s<e<=0x30000 for s,e in b.segments()),b.segments()
assert all(0x30000<=s<e<=0x90000 for s,e in a.segments()),a.segments()
b.merge(a,overlap="error");b.write_hex_file(sys.argv[3]);print("Factory HEX ranges:",b.segments())'''
run(VENV/'bin/python','-c',merge,BUILD/'bootloader/zephyr/zephyr.hex',out/'nora-app.signed.bin',out/'nora-factory.hex',out/'nora-app.signed.hex')
for src,dst in [('bootloader/zephyr/zephyr.hex','nora-bootloader.hex'),('bootloader/zephyr/zephyr.elf','nora-bootloader.elf'),('app/zephyr/zephyr.elf','nora-app.elf')]:shutil.copyfile(BUILD/src,out/dst)
run(VENV/'bin/python',FW/'tools/validate_build.py')
run(VENV/'bin/python','-m','unittest','discover','-s',FW/'tests','-v')
manifest={'board':board,'app_version':args.version,'zephyr':'v4.4.0','zephyr_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=WS/'zephyr',text=True).strip(),'mcuboot_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=WS/'bootloader/mcuboot',text=True).strip(),'sdk':'1.0.1','sdk_archives_sha256':json.loads((BUILD/'sdk-hashes.json').read_text()),'source_sha256':{str(p.relative_to(FW)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(FW.rglob('*')) if p.is_file() and not any(part in ['dist','host-tools','__pycache__'] for part in p.relative_to(FW).parts)},'status':'Build and static checks only; hardware/USB/SWD not tested','flash':{'boot':[0,0x30000],'primary':[0x30000,0x90000],'secondary':[0x90000,0xf0000],'storage':[0xf0000,0x100000]},'sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir()) if p.is_file() and p.name!='manifest.json'}}
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Ready-to-flash artifacts:',out)
