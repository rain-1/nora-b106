#!/usr/bin/env python3
"""Audit resolved DT/Kconfig, signed-image vectors, and factory flash ranges."""
from pathlib import Path
import pickle,sys,json,struct,re,hashlib,subprocess
from intelhex import IntelHex
from cryptography.hazmat.primitives import serialization
from elftools.elf.elffile import ELFFile
ROOT=Path(__file__).resolve().parents[2];B=ROOT/'build/firmware';FW=ROOT/'firmware';OUT=FW/'dist'
sys.path.insert(0,str(B/'workspace/zephyr/scripts/dts/python-devicetree/src'))
sys.path.insert(0,str(FW/'tools'))
from usb_update import check_image

def cfg(name):
 return dict(line.strip().split('=',1) for line in (B/name/'zephyr/.config').read_text().splitlines() if line.startswith('CONFIG_') and '=' in line)
a=cfg('app');b=cfg('bootloader');edts={}
for name,c in [('app',a),('bootloader',b)]:
 e=pickle.load((B/name/'zephyr/edt.pickle').open('rb'));edts[name]=e
 assert c['CONFIG_CLOCK_CONTROL_NRF_K32SRC_RC']=='y'
 assert c['CONFIG_CLOCK_CONTROL_NRF_K32SRC_500PPM']=='y'
 assert c['CONFIG_CLOCK_CONTROL_NRF_K32SRC_RC_CALIBRATION']=='y'
 assert c.get('CONFIG_SOC_NRF53_CPUNET_ENABLE')!='y'
 assert c['CONFIG_NRF_APPROTECT_USE_UICR']=='y'
 assert e.label2node['hfxo'].props['load-capacitance-femtofarad'].val==20000
 assert e.label2node['lfxo'].status=='disabled'
 for label,offset,length in [('boot_partition',0,0x30000),('slot0_partition',0x30000,0x60000),('slot1_partition',0x90000,0x60000),('storage_partition',0xf0000,0x10000)]:
  n=e.label2node[label];assert (n.regs[0].addr,n.regs[0].size)==(offset,length),(name,label,n.regs)
 for label in ['uart0','uart1','qspi','nfct']:
  assert e.label2node[label].status=='disabled',(name,label)
 assert e.label2node['usbd'].status=='okay'
for k in ['CONFIG_BOOT_SERIAL_CDC_ACM','CONFIG_BOOT_SERIAL_BOOT_MODE','CONFIG_BOOT_SERIAL_PIN_RESET','CONFIG_BOOT_SERIAL_NO_APPLICATION','CONFIG_BOOT_VALIDATE_SLOT0','CONFIG_BOOT_SIGNATURE_TYPE_ECDSA_P256']:
 assert b[k]=='y',k
assert b['CONFIG_BOOT_SERIAL_WAIT_FOR_DFU_TIMEOUT']=='8000'
assert b.get('CONFIG_BOOT_SERIAL_ENTRANCE_GPIO')!='y'
assert a['CONFIG_USB_DEVICE_STACK_NEXT']=='y' and a['CONFIG_CDC_ACM_SERIAL_ENABLE_AT_BOOT']=='y'
assert a['CONFIG_RETENTION_BOOT_MODE']=='y' and a['CONFIG_GPIO_GET_CONFIG']=='y'
assert edts['app'].chosen_node('zephyr,code-partition')==edts['app'].label2node['slot0_partition']
assert edts['bootloader'].chosen_node('zephyr,code-partition')==edts['bootloader'].label2node['boot_partition']
actual=[]
for gp in edts['app'].get_node('/zephyr,user').props['gpios'].val:
 port=0 if 'gpio0' in gp.controller.labels else 1
 assert gp.data['flags']==0
 actual.append(f'P{port}.{gp.data["pin"]:02}')
expected=[v.split('_')[0] for k,v in json.loads((ROOT/'design.json').read_text())['gpio_header'].items() if int(k)>=3]
assert actual==expected,(actual,expected)
data=check_image(OUT/'nora-app.signed.bin');header=struct.unpack_from('<H',data,8)[0]
with (B/'app/zephyr/zephyr.elf').open('rb') as f:
 elf=ELFFile(f);vectors=next(s for s in elf.iter_sections() if s.name=='rom_start');assert vectors['sh_addr']==0x30000
 # Zephyr's header padding is already present. Signing must not add another one.
 raw=IntelHex(str(B/'app/zephyr/zephyr.hex'));assert raw[0x30200:0x30208].tobinarray().tobytes()==data[header:header+8]
factory=IntelHex(str(OUT/'nora-factory.hex'));boot=IntelHex(str(OUT/'nora-bootloader.hex'));signed=IntelHex(str(OUT/'nora-app.signed.hex'))
assert all(0<=s<e<=0x30000 or 0x30000<=s<e<=0x90000 for s,e in factory.segments())
assert all(x<0x30000 for x in boot.addresses())
public=serialization.load_pem_public_key((FW/'keys/development.pub.pem').read_bytes()).public_bytes(serialization.Encoding.DER,serialization.PublicFormat.SubjectPublicKeyInfo)
assert public in boot.tobinarray().tobytes(),'Bootloader does not contain the supplied signing public key'
assert signed.minaddr()==0x30000
assert signed.tobinarray().tobytes()==data
report={'result':'passed','hardware_tested':False,'signed_application_bytes':len(data),'gpio_header':actual,'factory_hex_ranges':factory.segments(),'bootloader_bytes':len(boot.addresses()),'checks':['Both images: calibrated RC LFCLK and 20 pF HFXO','GPIO mapping matches PCB J3; no DK GPIO/peripheral assumptions','USB recovery request/reset/power-on window configured','Application and bootloader use matching partitions','Signature headers and Cortex-M vectors occupy expected addresses','Factory HEX excludes UICR, network flash, storage and secondary slot','Bootloader contains the supplied development public key']}
(OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
