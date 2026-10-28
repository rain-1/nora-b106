#!/usr/bin/env python3
"""Install a pinned, project-local Linux x86_64 firmware build environment."""
from pathlib import Path
import subprocess,sys,os,urllib.request,hashlib,tarfile,platform,shutil,json
ROOT=Path(__file__).resolve().parents[2];FW=ROOT/'firmware';B=ROOT/'build/firmware';WS=B/'workspace';V=B/'venv'
ZREV='684c9e8f32e4373a21098559f748f06915f950c9'
MODULES=['cmsis','cmsis_6','hal_nordic','mcuboot','mbedtls','zcbor']
SDK={'zephyr-sdk-1.0.1_linux-x86_64_minimal.tar.xz':'ca9bc0ff66fafca1dac9d592a36d953cf16d096a9d09b1c0357f021cf9f6a7eb','toolchain_gnu_linux-x86_64_arm-zephyr-eabi.tar.xz':'21b85981cb5a1818d9bc53d82af80f208946ec038b982ff1907287572ed3a634'}
def run(*args,cwd=ROOT,env=None):subprocess.run([str(x) for x in args],cwd=cwd,env=env,check=True)
if platform.system()!='Linux' or platform.machine()!='x86_64':raise SystemExit('This automated setup targets Linux x86_64. Other platforms can use the pinned Zephyr/SDK versions manually.')
for tool in ['git','uv','make','cc','xz']:
 if not shutil.which(tool):raise SystemExit('Required tool missing: '+tool)
B.mkdir(parents=True,exist_ok=True);WS.mkdir(exist_ok=True)
if not (V/'bin/python').exists():run('uv','venv','--python','3.12',V)
run('uv','pip','sync','--python',V/'bin/python',FW/'requirements-build.lock')
env=os.environ.copy();env['PATH']=str(V/'bin')+os.pathsep+env['PATH']
if not (WS/'zephyr/.git').exists():run('git','clone','--depth','1','--branch','v4.4.0','https://github.com/zephyrproject-rtos/zephyr.git',WS/'zephyr')
actual=subprocess.check_output(['git','rev-parse','HEAD'],cwd=WS/'zephyr',text=True).strip()
if actual!=ZREV:raise SystemExit('Existing Zephyr checkout has the wrong revision; it was left unchanged.')
if not (WS/'.west/config').exists():run(V/'bin/west','init','-l',WS/'zephyr',env=env)
run(V/'bin/west','update','--narrow','-o=--depth=1',*MODULES,cwd=WS,env=env)
sdk=B/'zephyr-sdk-1.0.1'
for name,expected in SDK.items():
 marker=sdk/'sdk_version' if name.startswith('zephyr-sdk') else sdk/'gnu/arm-zephyr-eabi/bin/arm-zephyr-eabi-gcc'
 if marker.exists():continue
 downloads=B/'downloads';downloads.mkdir(exist_ok=True);dest=downloads/name
 if not dest.exists():urllib.request.urlretrieve('https://github.com/zephyrproject-rtos/sdk-ng/releases/download/v1.0.1/'+name,dest)
 digest=hashlib.file_digest(dest.open('rb'),'sha256').hexdigest()
 if digest!=expected:raise SystemExit('SDK archive checksum failed: '+name)
 prefix=B if name.startswith('zephyr-sdk') else sdk/'gnu';prefix.mkdir(exist_ok=True)
 with tarfile.open(dest) as t:t.extractall(prefix,filter='data')
 dest.unlink()
if not (sdk/'hosttools/sysroots').exists():run(sdk/'setup.sh','-h',env=env)
(B/'sdk-hashes.json').write_text(json.dumps(SDK,indent=2)+'\n')
print('Toolchain ready. Build with: python3 firmware/tools/build.py')
