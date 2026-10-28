#!/usr/bin/env python3
"""Upload a signed P1 application with Apache mcumgr; no erase/recover commands."""
from pathlib import Path
import argparse,os,struct,subprocess,sys,time,shutil
ROOT=Path(__file__).resolve().parents[2]
BOOT_VID,BOOT_PID,APP_PID=0x2fe3,0x0004,0x0005

def check_image(path):
    data=Path(path).read_bytes()
    if len(data)<0x208 or len(data)>0x60000:raise ValueError('Not a P1 signed application: invalid file size')
    magic,load,header,protected,size,flags=struct.unpack_from('<IIHHII',data)
    if magic!=0x96f3b83d or load or header!=0x200 or flags or size<8 or header+size+protected+4>len(data):
        raise ValueError('Not a P1 signed application: invalid MCUboot header')
    stack,reset=struct.unpack_from('<II',data,header)
    if not 0x20000000<stack<=0x20070000 or not reset&1 or not 0x30200<=reset<0x90000:
        raise ValueError('Application vectors do not match the P1 flash/RAM layout')
    tlv_magic,tlv_length=struct.unpack_from('<HH',data,header+size+protected)
    if tlv_magic!=0x6907 or tlv_length<4 or header+size+protected+tlv_length!=len(data):
        raise ValueError('Missing or truncated MCUboot signature TLV block')
    return data

def recovery_port(ports,location=None,device=None):
    candidates=[p for p in ports if p.vid==BOOT_VID and p.pid==BOOT_PID]
    if location is not None:candidates=[p for p in candidates if p.location==location]
    elif device is not None:candidates=[p for p in candidates if os.path.realpath(p.device)==os.path.realpath(device)]
    if len(candidates)!=1:raise ValueError('Could not identify exactly one recovery port; specify its --port explicitly')
    return candidates[0].device

def transfer(mcumgr,port,image,reset=True):
    # Argument arrays protect paths/port names; failed upload never triggers reset.
    common=[str(mcumgr),'--conntype','serial','--connstring',f'dev={port},baud=115200','--timeout','60']
    subprocess.run(common+['image','upload',str(image)],check=True)
    if reset:subprocess.run(common+['reset'],check=True)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--port',required=True,help='Application/recovery tty path; close any terminal using it')
    p.add_argument('--enter',action='store_true',help='Send nora dfu to the running application before uploading')
    p.add_argument('--no-reset',action='store_true',help='Remain in recovery after upload')
    p.add_argument('--mcumgr',type=Path)
    p.add_argument('image',nargs='?',type=Path,default=ROOT/'firmware/dist/nora-app.signed.bin')
    a=p.parse_args();data=check_image(a.image)
    mcumgr=a.mcumgr or next((x for x in [ROOT/'firmware/host-tools/linux-amd64/mcumgr',ROOT/'build/firmware/bin/mcumgr'] if x.is_file()),None) or shutil.which('mcumgr')
    if not mcumgr:raise ValueError('Install mcumgr or pass --mcumgr /path/to/mcumgr')
    import serial
    from serial.tools import list_ports
    ports=list(list_ports.comports())
    if a.enter:
        current=next((x for x in ports if os.path.realpath(x.device)==os.path.realpath(a.port)),None)
        if not current or (current.vid,current.pid)!=(BOOT_VID,APP_PID):
            raise ValueError('--enter requires the NORA application USB port (2fe3:0005)')
        if not current.location:raise ValueError('USB physical location unavailable; use nora dfu manually and specify the recovery port')
        with serial.Serial(a.port,115200,timeout=1,write_timeout=2) as s:
            s.dtr=True;time.sleep(.15);s.write(b'\x03\r\nnora dfu\r\n');s.flush()
        deadline=time.monotonic()+15
        while True:
            try:port=recovery_port(list(list_ports.comports()),location=current.location);break
            except ValueError:
                if time.monotonic()>=deadline:raise ValueError('Recovery port did not appear; use manual recovery and specify its port')
                time.sleep(.2)
    else:port=recovery_port(ports,device=a.port)
    print(f'Uploading {a.image} ({len(data)} bytes) to {port}',flush=True)
    transfer(mcumgr,port,a.image.resolve(),reset=not a.no_reset)
    print('Upload complete. Allow 8 seconds for the normal boot window after reset.')

if __name__=='__main__':
    try:main()
    except (ValueError,OSError,subprocess.CalledProcessError) as e:raise SystemExit(str(e))
