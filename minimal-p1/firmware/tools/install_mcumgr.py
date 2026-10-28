#!/usr/bin/env python3
"""Build the pinned Apache mcumgr CLI locally on Linux x86_64."""
from pathlib import Path
import hashlib,urllib.request,tarfile,subprocess,os,platform
ROOT=Path(__file__).resolve().parents[2];B=ROOT/'build/firmware';FW=ROOT/'firmware'
if (platform.system(),platform.machine())!=('Linux','x86_64'):raise SystemExit('Use the manual Go build in firmware/host-tools/README.md on other platforms.')
out=FW/'host-tools/linux-amd64';out.mkdir(parents=True,exist_ok=True)
if (out/'mcumgr').exists():
 subprocess.run([out/'mcumgr','version'],check=True);raise SystemExit(0)
B.mkdir(parents=True,exist_ok=True);go_root=B/'go-sdk';go_root.mkdir(exist_ok=True)
if not (go_root/'go/bin/go').exists():
 p=go_root/'go1.27.3.linux-amd64.tar.gz';urllib.request.urlretrieve('https://go.dev/dl/'+p.name,p)
 with p.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
 if digest!='65efbc80fdc1fa2cd2631cad5b481777a68e8725f34e89f50fc6ac714e379b40':raise SystemExit('Go download checksum failed')
 with tarfile.open(p) as t:t.extractall(go_root,filter='data')
 p.unlink()
env=os.environ.copy();env.update(GOBIN=str(out),GOPATH=str(B/'go-modules'),GOCACHE=str(B/'go-build-cache'),CGO_ENABLED='0',GOTOOLCHAIN='local',PATH=str(go_root/'go/bin')+os.pathsep+env['PATH'])
subprocess.run([go_root/'go/bin/go','install','github.com/apache/mynewt-mcumgr-cli/mcumgr@5c56bd24066c780aad5836429bfa2ecc4f9a944c'],env=env,check=True)
subprocess.run([out/'mcumgr','version'],check=True)
