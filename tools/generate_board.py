#!/usr/bin/env python3
"""Generate the NORA-B106 breakout sources. Run with the target editor closed.
Routing is a separate step; never regenerate a manually edited board blindly.
"""
from pathlib import Path
import copy
import csv
import json
import math
import shutil
import sys
import uuid
import sexpdata as sx
import pcbnew as p

ROOT=Path(__file__).resolve().parents[1]
NS=uuid.UUID('2735f9ef-27f4-4762-8c87-acd63bfcddce')
def uid(key): return str(uuid.uuid5(NS,key))
def q(value):return json.dumps(str(value))
def mm(value):return p.FromMM(value)
def vec(x,y):return p.VECTOR2I(mm(x),mm(y))
def key(node):return str(node[0]) if isinstance(node,list) and node else ''
def child(node,name):return next((x for x in node if key(x)==name),None)
def children(node,name):return [x for x in node if key(x)==name]
def write(path,text):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text+'\n')

# Manufacturer UBX-20027119 R13, Table 6. ANT is disconnected in B106.
ROWS='''A1 GND
A2 P0.12
A3 P1.03
A4 P1.00
A5 P0.20
A6 NC
A7 VDD
A8 VDDH
A9 GND
B1 P0.08
B2 GND
B3 P0.11
B4 P1.02
B5 P0.03
B6 P0.01
B7 VDD
B8 GND
B9 VBUS
C1 P0.10
C2 P0.09
C4 P1.01
C5 P0.02
C6 P0.00
C8 P0.22
C9 USB_DP
D1 P0.15
D2 P0.13
D3 P0.07
D7 P0.23
D8 P0.04
D9 USB_DM
E1 P0.18
E2 P0.14
E3 P0.21
E4 GND
E5 GND
E7 P0.06
E8 P0.05
E9 P1.05
F1 P0.17
F2 P0.16
F3 P0.19
F4 GND
F5 GND
F7 P1.07
F8 P1.14
F9 P1.15
G1 P1.06
G2 P0.26
G3 P0.25
G4 P1.04
G5 P1.08
G7 P1.09
G8 P1.12
G9 P1.13
H1 P0.24
H2 SWDIO
H3 P0.27
H7 P0.29
H8 P0.30
H9 P1.11
J1 NC
J2 SWCLK
J3 RESET_N
J4 NC
J5 NC
J7 P1.10
J8 P0.28
J9 P0.31
K1 NC
K2 GND
K3 GND
K5 GND
K7 GND
K8 GND
K9 ANT_NC
L1 GND
L9 GND
M1 GND
M2 GND
M8 GND
M9 GND'''
PIN_NAMES=dict(line.split() for line in ROWS.splitlines())
if len(PIN_NAMES)!=82:raise RuntimeError('Module pin inventory must contain 82 pads')
MODULE_NETS={n:'GND' for n,v in PIN_NAMES.items() if v=='GND'}
MODULE_NETS.update({'A7':'+3V3','B7':'+3V3','A8':'+3V3','B9':'VBUS','H2':'SWDIO','J2':'SWCLK','J3':'RESET_N','C9':'USB_DP','D9':'USB_DM','A5':'LED','D8':'P0.04_AIN0','E8':'P0.05_AIN1','B4':'P1.02_SDA','A3':'P1.03_SCL','G8':'P1.12_TX','G9':'P1.13_RX'})

LIB_CACHE={}
def source_symbol(lib,name):
 if lib not in LIB_CACHE:
  data=sx.load(open('/usr/share/kicad/symbols/'+lib+'.kicad_sym'))
  LIB_CACHE[lib]={x[1]:x for x in data if key(x)=='symbol'}
 node=copy.deepcopy(LIB_CACHE[lib][name]);extends=child(node,'extends')
 if extends:
  base=source_symbol(lib,extends[1]);override={x[1] for x in children(node,'property')}
  node=[node[0],node[1]]+[x for x in node[2:] if key(x)!='extends']+[copy.deepcopy(x) for x in base[2:] if (key(x)=='property' and x[1] not in override) or key(x) not in ('property','embedded_fonts')]
  for sub in children(node,'symbol'):sub[1]=str(sub[1]).replace(str(base[1]),name,1)
 return node

def make_module_symbol():
 pins={1:[],2:[]}
 def pin(num,name,x,y,angle,typ='bidirectional',unit=1):
  pins[unit].append(f'(pin {typ} line (at {x} {y} {angle}) (length 5.08) (name {q(name)} (effects (font (size 0.9 0.9)))) (number {q(num)} (effects (font (size 0.7 0.7)))))')
 for i,num in enumerate(['A7','B7','A8','B9']):pin(num,PIN_NAMES[num],-30.48,20.32-i*5.08,0,'power_in')
 for i,num in enumerate(['H2','J2','J3','C9','D9']):pin(num,PIN_NAMES[num],30.48,20.32-i*5.08,180,'input' if num in ('J2','J3') else 'bidirectional')
 for i,num in enumerate(['A6','J1','J4','J5','K1','K9']):pin(num,PIN_NAMES[num],-30.48,-2.54-i*2.54,0,'no_connect')
 grounds=[n for n,v in PIN_NAMES.items() if v=='GND']
 for i,num in enumerate(grounds):pin(num,'GND' if i==len(grounds)//2 else '',round((i-(len(grounds)-1)/2)*2.54,3),-30.48,90,'power_in')
 gpio=sorted([(v,n) for n,v in PIN_NAMES.items() if v.startswith('P')])
 for i,(name,num) in enumerate(gpio):
  side=i//24;row=i%24
  pin(num,name,-35.56 if side==0 else 35.56,29.21-row*2.54,0 if side==0 else 180,unit=2)
 raw=f'''(symbol "NORA-B106" (pin_names (offset 0.7)) (exclude_from_sim no) (in_bom yes) (on_board yes)
 (property "Reference" "U" (at 0 35.56 0) (effects (font (size 1.27 1.27))))
 (property "Value" "NORA-B106-00B" (at 0 33.02 0) (effects (font (size 1.27 1.27))))
 (property "Footprint" "Breakout:NORA-B106" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
 (property "Datasheet" "https://content.u-blox.com/sites/default/files/NORA-B1_DataSheet_UBX-20027119.pdf" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
 (symbol "NORA-B106_1_1" (rectangle (start -25.4 25.4) (end 25.4 -25.4) (stroke (width 0.254) (type default)) (fill (type background))) {' '.join(pins[1])})
 (symbol "NORA-B106_2_1" (rectangle (start -30.48 33.02) (end 30.48 -33.02) (stroke (width 0.254) (type default)) (fill (type background))) {' '.join(pins[2])}))'''
 return sx.loads(raw)

def module_footprint():
 f=p.FOOTPRINT(None);f.SetFPID(p.LIB_ID('Breakout','NORA-B106'));f.SetAttributes(p.FP_SMD)
 columns={'A':-5.5,'B':-4.4,'C':-3.3,'D':-2.2,'E':-1.1,'F':0,'G':1.1,'H':2.2,'J':3.3,'K':4.4,'L':5.9,'M':7.4}
 for num in PIN_NAMES:
  col,row=num[0],int(num[1]);y=4.4-(row-1)*1.1
  if col in 'EFGJ' and row in (4,5):y=0.55 if row==4 else -0.55
  pad=p.PAD(f);pad.SetNumber(num);pad.SetAttribute(p.PAD_ATTRIB_SMD);pad.SetShape(p.PAD_SHAPE_RECT)
  pad.SetSize(vec(.6,.6));pad.SetPosition(vec(columns[col],y));pad.SetLayerSet(p.LSET.FrontMask())
  layers=p.LSET();[layers.AddLayer(l) for l in (p.F_Cu,p.F_Paste,p.F_Mask)];pad.SetLayerSet(layers)
  pad.SetLocalSolderMaskMargin(mm(.05));f.Add(pad)
 def line(a,b,layer,width=.1):
  x=p.PCB_SHAPE(f);x.SetShape(p.SHAPE_T_SEGMENT);x.SetStart(vec(*a));x.SetEnd(vec(*b));x.SetLayer(layer);x.SetWidth(mm(width));f.Add(x)
 for layer,margin in ((p.F_Fab,0),(p.F_CrtYd,.25)):
  x0,x1,y0,y1=-6.25-margin,8.05+margin,-5.2-margin,5.2+margin
  for a,b in [((x0,y0),(x1,y0)),((x1,y0),(x1,y1)),((x1,y1),(x0,y1)),((x0,y1),(x0,y0))]:line(a,b,layer,.05 if layer==p.F_CrtYd else .1)
 # No silk over pads or module antenna. Pin A1 marker outside the package.
 line((-6.6,4.2),(-6.6,5.6),p.F_SilkS,.15);line((-6.6,5.6),(-5.2,5.6),p.F_SilkS,.15)
 f.Reference().SetPosition(vec(-3,6));f.Reference().SetTextSize(vec(.9,.9));f.Reference().SetTextThickness(mm(.13));f.Value().SetVisible(False)
 p.PCB_IO_MGR.PluginFind(p.PCB_IO_MGR.KICAD_SEXP).FootprintSave(str(ROOT/'hardware/Breakout.pretty'),f)

# net assignments, schematic layout, PCB layout/rotation; all parts top-side.
PARTS=[
 ('U1','Breakout:NORA-B106','NORA-B106-00B','NORA-B106',MODULE_NETS,(208.28,50.8),(118,108.2,90)),
 ('U2','Regulator_Linear:XC6206PxxxMR','XC6206P332MR-G','SOT-23-3',{'1':'GND','2':'+3V3','3':'VBUS'},(110.49,30.48),(121,121,180)),
 ('U3','Power_Protection:USBLC6-2SC6','USBLC6-2SC6','SOT-23-6',{'1':'USB_DM','2':'GND','3':'USB_DP','4':'USB_DP','5':'VBUS','6':'USB_DM'},(110.49,66.04),(111.275,124.5,90)),
 ('J1','Connector:USB_C_Receptacle_USB2.0_16P','TYPE-C-31-M-12','USB_C_Receptacle_HRO_TYPE-C-31-M-12',{'A1':'GND','B12':'GND','A12':'GND','B1':'GND','A4':'VBUS','B9':'VBUS','A9':'VBUS','B4':'VBUS','A5':'CC1','B5':'CC2','A6':'USB_DP','B6':'USB_DP','A7':'USB_DM','B7':'USB_DM','S1':'GND'},(35.56,53.34),(113.6,132.5,0)),
 ('J2','Connector_Generic:Conn_01x05','SWD / PICO','PinHeader_1x05_P2.54mm_Vertical',{'1':'+3V3','2':'GND','3':'SWCLK','4':'SWDIO','5':'RESET_N'},(274.32,43.18),(103,116,0)),
 ('J3','Connector_Generic:Conn_01x08','GPIO 3V3','PinHeader_1x08_P2.54mm_Vertical',{'1':'+3V3','2':'GND','3':'P1.12_TX','4':'P1.13_RX','5':'P0.04_AIN0','6':'P0.05_AIN1','7':'P1.02_SDA','8':'P1.03_SCL'},(274.32,134.62),(133,113,0)),
 ('R1','Device:R','5k1/1%','R_0805_2012Metric',{'1':'CC1','2':'GND'},(76.2,81.28),(108.4,124.5,90)),
 ('R2','Device:R','5k1/1%','R_0805_2012Metric',{'1':'CC2','2':'GND'},(101.6,81.28),(118.5,124.5,90)),
 ('R3','Device:R','1k','R_0805_2012Metric',{'1':'LED','2':'LED_A'},(104.14,116.84),(126.5,121.5,90)),
 ('D1','Device:LED','GREEN','LED_0805_2012Metric',{'1':'GND','2':'LED_A'},(124.46,116.84),(126.5,117.5,90)),
 ('C1','Device:C','1u/16V','C_0805_2012Metric',{'1':'VBUS','2':'GND'},(83.82,30.48),(123,125,0)),
 ('C2','Device:C','4u7/10V','C_0805_2012Metric',{'1':'+3V3','2':'GND'},(129.54,30.48),(121,117.5,0)),
 ('C3','Device:C','100n/16V','C_0805_2012Metric',{'1':'+3V3','2':'GND'},(149.86,45.72),(113,117,90)),
 ('C4','Device:C','100n/16V','C_0805_2012Metric',{'1':'VBUS','2':'GND'},(139.7,66.04),(116.5,117.5,90)),
 ('SW1','Switch:SW_Push','RESET','SW_PUSH_6mm',{'1':'RESET_N','2':'GND'},(111.76,152.4),(121.5,129,0)),
]
FP_SOURCE={'SOT-23-3':'Package_TO_SOT_SMD','SOT-23-6':'Package_TO_SOT_SMD','USB_C_Receptacle_HRO_TYPE-C-31-M-12':'Connector_USB','PinHeader_1x05_P2.54mm_Vertical':'Connector_PinHeader_2.54mm','PinHeader_1x08_P2.54mm_Vertical':'Connector_PinHeader_2.54mm','R_0805_2012Metric':'Resistor_SMD','C_0805_2012Metric':'Capacitor_SMD','LED_0805_2012Metric':'LED_SMD','SW_PUSH_6mm':'Button_Switch_THT'}
SYMBOLS={}

def prepare_libs():
 module_footprint()
 for fp,lib in FP_SOURCE.items():
  dest=ROOT/f'hardware/Breakout.pretty/{fp}.kicad_mod'
  shutil.copyfile(f'/usr/share/kicad/footprints/{lib}.pretty/{fp}.kicad_mod',dest)
  if fp=='USB_C_Receptacle_HRO_TYPE-C-31-M-12':
   data=sx.load(dest.open());data=[node for node in data if not (key(node).startswith('fp_') and child(node,'layer') is not None and str(child(node,'layer')[1])=='F.SilkS')]
   write(dest,sx.dumps(data))
 SYMBOLS['Breakout:NORA-B106']=make_module_symbol()
 for _,libid,*_ in PARTS:
  if libid not in SYMBOLS:
   lib,name=libid.split(':');SYMBOLS[libid]=source_symbol(lib,name)
 library=[sx.Symbol('kicad_symbol_lib'),[sx.Symbol('version'),20241209],[sx.Symbol('generator'),'nora-breakout']]
 for libid,sym in SYMBOLS.items():
  clone=copy.deepcopy(sym);clone[1]=libid.split(':')[1];library.append(clone)
 write(ROOT/'hardware/Breakout.kicad_sym',sx.dumps(library))
 write(ROOT/'sym-lib-table','(sym_lib_table (version 7) (lib (name "Breakout") (type "KiCad") (uri "${KIPRJMOD}/hardware/Breakout.kicad_sym") (options "") (descr "Local breakout symbols")))')
 write(ROOT/'fp-lib-table','(fp_lib_table (version 7) (lib (name "Breakout") (type "KiCad") (uri "${KIPRJMOD}/hardware/Breakout.pretty") (options "") (descr "Project-local verified footprints")))')

def schematic():
 sheet=uid('schematic');parts=[];embedded=[]
 for libid,sym in SYMBOLS.items():
  clone=copy.deepcopy(sym);clone[1]=libid;embedded.append(sx.dumps(clone))
 root=f'(kicad_sch (version 20250114) (generator "nora-breakout") (uuid {sheet}) (paper "A4") (title_block (title "NORA-B106 breakout") (date "2026-10-18") (rev "A") (company "Prototype - verify before production")) (lib_symbols {" ".join(embedded)})'
 def wire(x1,y1,x2,y2):
  ident=uid(f'wire:{x1}:{y1}:{x2}:{y2}')
  parts.append(f'(wire (pts (xy {x1:.4f} {y1:.4f}) (xy {x2:.4f} {y2:.4f})) (stroke (width 0) (type default)) (uuid {ident}))')
 def label(net,x,y,justify='left'):
  parts.append(f'(label {q(net)} (at {x:.4f} {y:.4f} 0) (effects (font (size 0.9 0.9)) (justify {justify} bottom)) (uuid {uid(f"label:{net}:{x}:{y}")}))')
 for ref,libid,value,fp,nets,sch,pcb in PARTS:
  for unit in ((1,2) if ref=='U1' else (1,)):
   x,y=sch if unit==1 else (208.28,127.0);sym=SYMBOLS[libid];sid=uid(ref)
   pin_nodes=[]
   for sub in children(sym,'symbol'):
    subunit=int(sub[1].rsplit('_',2)[1])
    if subunit in (0,unit):pin_nodes.extend(children(sub,'pin'))
   if ref.startswith(('C','R')):tx,ry,vy,justify=x+3.81,y-1.27,y+1.27,'(justify left)'
   else:
    tx=x;offset=(34.29 if unit==1 else 38.1) if ref=='U1' else (25.4 if ref=='J1' else (12.7 if ref=='J3' else (17.78 if ref=='U3' else 10.16)))
    ry,vy,justify=y-offset,y-offset+2.54,''
   props=f'(property "Reference" {q(ref)} (at {tx} {ry} 0) (effects (font (size 1.27 1.27)) {justify})) (property "Value" {q(value)} (at {tx} {vy} 0) (effects (font (size 1.0 1.0)) {justify})) (property "Footprint" {q("Breakout:"+fp)} (at {x} {y} 0) (effects (font (size 1.27 1.27)) (hide yes)))'
   symbol=f'(symbol (lib_id {q(libid)}) (at {x} {y} 0) (unit {unit}) (in_bom yes) (on_board yes) (dnp no) (uuid {sid if unit==1 else uid(ref+":2")}) {props}'
   for pin in pin_nodes:symbol+=f'(pin {q(child(pin,"number")[1])} (uuid {uid(ref+":"+child(pin,"number")[1])}))'
   symbol+=f'(instances (project "nora-b106-board" (path "/{sheet}" (reference {q(ref)}) (unit {unit})))))';parts.append(symbol)
   ground_endpoints=[]
   for pin in pin_nodes:
    num=child(pin,'number')[1];at=child(pin,'at');px=round(x+float(at[1]),4);py=round(y-float(at[2]),4);angle=float(at[3]);net=nets.get(num)
    if net is None:
     parts.append(f'(no_connect (at {px} {py}) (uuid {uid(ref+":nc:"+num)}))');continue
    if ref=='U1' and PIN_NAMES[num]=='GND':ground_endpoints.append((px,py));continue
    dx,dy={0:(-5.08,0),180:(5.08,0),90:(0,3.81),270:(0,-3.81)}[int(angle)]
    ex,ey=round(px+dx,4),round(py+dy,4);wire(px,py,ex,ey);label(net,ex,ey,'right' if dx<0 else 'left')
   if ground_endpoints:
    by=ground_endpoints[0][1]+3.81
    for px,py in ground_endpoints:wire(px,py,px,by)
    xs=sorted(px for px,_ in ground_endpoints)
    for a,b in zip(xs,xs[1:]):wire(a,by,b,by)
    for px in xs[1:-1]:parts.append(f'(junction (at {px} {by}) (diameter 0) (color 0 0 0 0) (uuid {uid("gndjunction:"+str(px))}))')
    label('GND',xs[0],by,'right')
 # Power inputs from USB connector and ground are deliberately flagged.
 flag=source_symbol('power','PWR_FLAG');flag[1]='power:PWR_FLAG';root=root.replace('(lib_symbols ','(lib_symbols '+sx.dumps(flag)+' ',1)
 for i,net in enumerate(('VBUS','GND')):
  x,y=35.56+i*25.4,175.26
  ident=uid('flag'+net)
  parts.append(f'(symbol (lib_id "power:PWR_FLAG") (at {x} {y} 0) (unit 1) (in_bom no) (on_board yes) (uuid {ident}) (property "Reference" "#FLG0{i+1}" (at {x} {y+2.54} 0) (effects (font (size 1.27 1.27)) (hide yes))) (property "Value" "PWR_FLAG" (at {x} {y-3.81} 0) (effects (font (size 0.9 0.9)))) (pin "1" (uuid {uid("flagpin"+net)})) (instances (project "nora-b106-board" (path "/{sheet}" (reference "#FLG0{i+1}") (unit 1)))))')
  label(net,x,y)
 def text(t,x,y,size=1):parts.append(f'(text {q(t)} (at {x} {y} 0) (effects (font (size {size} {size})) (justify left top)) (uuid {uid("note"+t)}))')
 text('POWER: USB 5 V -> XC6206 -> 3.3 V\nVDD and VDDH tied: normal-voltage mode.\nUSB VBUS pin receives USB 5 V.',20.32,88.9)
 text('USB-C device only; no USB-PD.\nFirst flash via SWD. USB needs firmware.\nCC1 and CC2 each have their own 5.1k Rd.',20.32,104.14)
 text('TEST LED: P0.20, active high.\nRESET switch uses module internal pull-up.',76.2,132.08)
 text('J2: 3V3 sense, GND, CLK, DIO, RESET.\nPico GP2 -> CLK; GP3 -> DIO; GP1 -> RESET.\nDo not connect Pico 3V3 when USB-powered.',20.32,188.0,.9)
 text('J3: 3V3 logic only; no 5V-tolerant GPIO.\nUse the internal LF RC clock; no 32k crystal.\nAll unbroken-out GPIO and reserved pads NC.',76.2,164.0,.9)
 write(ROOT/'nora-b106-board.kicad_sch',root+'\n'+'\n'.join(parts)+'\n(embedded_fonts no))')

def project():
 data=json.loads(Path('/usr/share/kicad/template/kicad.kicad_pro').read_text())
 settings=data.setdefault('board',{}).setdefault('design_settings',{})
 settings.setdefault('rules',{}).update({'min_clearance':.15,'min_track_width':.15,'min_via_diameter':.6,'min_through_hole_diameter':.3,'min_via_annular_width':.15,'min_copper_edge_clearance':.25,'min_silk_clearance':.1,'min_text_height':.8,'min_text_thickness':.12,'min_hole_clearance':.2,'min_hole_to_hole':.25})
 data['net_settings']={'classes':[{'name':'Default','clearance':.15,'track_width':.18,'via_diameter':.6,'via_drill':.3,'diff_pair_width':.7,'diff_pair_gap':.15,'diff_pair_via_gap':.25,'microvia_diameter':.3,'microvia_drill':.1,'wire_width':6,'bus_width':12,'line_style':0,'pcb_color':'rgba(0, 0, 0, 0.000)','schematic_color':'rgba(0, 0, 0, 0.000)'}],'meta':{'version':4},'net_colors':None,'netclass_assignments':None,'netclass_patterns':[]}
 write(ROOT/'nora-b106-board.kicad_pro',json.dumps(data,indent=2))

def board():
 b=p.BOARD();b.SetFileName(str(ROOT/'nora-b106-board.kicad_pcb'))
 ds=b.GetDesignSettings();nc=ds.m_NetSettings.GetDefaultNetclass();nc.SetClearance(mm(.15));nc.SetTrackWidth(mm(.18));nc.SetViaDiameter(mm(.6));nc.SetViaDrill(mm(.3));ds.SetBoardThickness(mm(.8));ds.m_MinClearance=mm(.15);ds.m_TrackMinWidth=mm(.15);ds.m_CopperEdgeClearance=mm(.25);ds.m_ViasMinSize=mm(.6);ds.m_MinThroughDrill=mm(.3);ds.m_ViasMinAnnularWidth=mm(.15);ds.m_SolderMaskMinWidth=mm(.1)
 nets={}
 for name in sorted({n for part in PARTS for n in part[4].values()}):
  n=p.NETINFO_ITEM(b,name);b.Add(n);nets[name]=n
 footprints={}
 for ref,libid,value,fp,assign,sch,pcb in PARTS:
  f=p.FootprintLoad(str(ROOT/'hardware/Breakout.pretty'),fp)
  if not f:raise RuntimeError('Footprint missing '+fp)
  f.SetFPID(p.LIB_ID('Breakout',fp));f.SetReference(ref);f.SetValue(value);f.SetPosition(vec(pcb[0],pcb[1]));f.SetOrientationDegrees(pcb[2]);f.SetPath(p.KIID_PATH('/'+uid('schematic')+'/'+uid(ref)))
  f.Reference().SetVisible(True);f.Reference().SetTextSize(vec(.8,.8));f.Reference().SetTextThickness(mm(.12));f.Value().SetVisible(False)
  f.Reference().SetTextAngle(p.EDA_ANGLE(0,p.DEGREES_T));f.Reference().SetKeepUpright(True)
  for pad in f.Pads():
   num=pad.GetNumber()
   if num in assign:pad.SetNet(nets[assign[num]])
   if ref=='U1' and assign.get(num)=='GND':pad.SetLocalZoneConnection(p.ZONE_CONNECTION_FULL)
  b.Add(f);footprints[ref]=f
 def line(a,c,layer=p.Edge_Cuts,width=.05):
  item=p.PCB_SHAPE();item.SetShape(p.SHAPE_T_SEGMENT);item.SetStart(vec(*a));item.SetEnd(vec(*c));item.SetWidth(mm(width));item.SetLayer(layer);b.Add(item)
 for a,c in [((100,100),(136,100)),((136,100),(136,136)),((136,136),(100,136)),((100,136),(100,100))]:line(a,c)
 def text(t,x,y,size=.85,layer=p.F_SilkS):
  item=p.PCB_TEXT(b);item.SetText(t);item.SetPosition(vec(x,y));item.SetTextSize(vec(size,size));item.SetTextThickness(mm(.13));item.SetLayer(layer);item.SetMirrored(layer==p.B_SilkS);b.Add(item)
 text('NORA-B106  rev A',118,111,1,p.B_SilkS)

 text('USB / 5V',113.6,131.3,.8)
 text('ANTENNA - KEEP CLEAR',118,102.2,.8,p.B_SilkS)
 for i,label in enumerate(('3V3','GND','CLK','DIO','RST')):text(label,106.5,116+i*2.54,.8)
 for i,label in enumerate(('3V3','GND','1.12 TX','1.13 RX','0.04 A0','0.05 A1','1.02 SDA','1.03 SCL')):
  text(('3V3','GND','TX','RX','A0','A1','SDA','SCL')[i],130.2,113+i*2.54,.8)
 text('RESET',124.8,127.4,.8)
 text('LED',126.5,124.0,.8)
 text('J2: 1=3V3 2=GND\n3=CLK 4=DIO 5=RST\nJ3: 1=3V3 2=GND\n3=P1.12 4=P1.13\n5=P0.04 6=P0.05\n7=P1.02 8=P1.03\nUSB POWER / 3V3 I/O',118,119,.85,p.B_SilkS)
 # RF keepout per SIM Fig 11: x(local)>=4.7 within +/-4.1 mm.
 # Extra outer antenna ground pads remain outside this central rectangle.
 z=p.ZONE(b);z.SetIsRuleArea(True);layers=p.LSET();layers.AddLayer(p.F_Cu);layers.AddLayer(p.B_Cu);z.SetLayerSet(layers)
 z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True);z.SetDoNotAllowCopperPour(True);z.SetDoNotAllowPads(True);z.SetDoNotAllowFootprints(False)
 outline=z.Outline();outline.NewOutline()
 for x,y in [(113.9,99.9),(122.1,99.9),(122.1,100.4),(120.9,100.4),(120.9,101.2),(122.1,101.2),(122.1,103.5),(113.9,103.5),(113.9,101.2),(115.1,101.2),(115.1,100.4),(113.9,100.4)]:outline.Append(mm(x),mm(y))
 z.SetZoneName('ANTENNA: no copper on either layer');b.Add(z)
 # Ground planes are filled after routing. Keepouts clip both planes.
 for layer in (p.F_Cu,p.B_Cu):
  z=p.ZONE(b);z.SetLayer(layer);z.SetNet(nets['GND']);z.SetLocalClearance(mm(.15));z.SetThermalReliefGap(mm(.2));z.SetThermalReliefSpokeWidth(mm(.2));z.SetPadConnection(p.ZONE_CONNECTION_FULL if layer==p.B_Cu else p.ZONE_CONNECTION_THERMAL);z.SetMinThickness(mm(.15));outline=z.Outline();outline.NewOutline()
  for x,y in [(100.25,100.25),(135.75,100.25),(135.75,135.75),(100.25,135.75)]:outline.Append(mm(x),mm(y))
  b.Add(z)
 # Position reference markings explicitly to avoid bodies, pads, and header labels.
 refpos={'U1':(124.8,111),'U2':(118.7,119.8),'U3':(111.3,122.0),'J1':(113.6,133.5),'J2':(103,113.5),'J3':(133,110.5),'R1':(108.4,122),'R2':(118.5,122.6),'R3':(124.2,121.5),'D1':(126.5,114.7),'C1':(123,123.5),'C2':(121,115.5),'C3':(110.7,117),'C4':(116.5,115.5),'SW1':(124.8,135.4)}
 for ref,f in footprints.items():f.Reference().SetPosition(vec(*refpos[ref]))
 # Clip the connector's stock silk at the board edge; its metal lip overhangs.
 for graphic in list(footprints['J1'].GraphicalItems()):
  if graphic.GetLayer()==p.F_SilkS:footprints['J1'].Remove(graphic)
 # Route native USB first, with a short, via-free pair. The long parallel section
 # is 0.70 mm width / 0.15 mm gap on 0.8 mm FR4; narrow escapes only at pads.
 def trace(net,points,width):
  for a,c in zip(points,points[1:]):
   t=p.PCB_TRACK(b);t.SetStart(vec(*a));t.SetEnd(vec(*c));t.SetWidth(mm(width));t.SetLayer(p.F_Cu);t.SetNet(nets[net]);t.SetLocked(True);b.Add(t)
 trace('USB_DP',[(113.6,111.5),(112.8,111.5),(111.7,112.6),(111.7,113.4)],.18)
 trace('USB_DM',[(113.6,110.4),(112.8,110.4),(110.85,112.35),(110.85,113.4)],.18)
 for net,x in [('USB_DP',111.7),('USB_DM',110.85)]:
  trace(net,[(x,113.4),(x,120.9)],.7)
  trace(net,[(x,120.9),(x,121.7)],.18)
 trace('USB_DP',[(111.7,121.7),(112.225,122.225),(112.225,123.3625),(112.225,125.6375),(113.35,126.7625),(113.35,128.455)],.18)
 trace('USB_DM',[(110.85,121.7),(110.325,122.225),(110.325,123.3625),(110.325,125.6375),(110.325,126.6),(111.025,127.3),(112.85,127.3),(112.85,128.455)],.18)
 trace('USB_DP',[(113.35,127.3),(114.35,127.3),(114.35,128.455)],.18)
 trace('USB_DM',[(112.85,128.455),(112.85,129.5),(113.85,129.5),(113.85,128.455)],.18)
 # Fan out buried LGA signals through the open rows before general routing.
 # These are ordinary 0.6/0.3 mm drilled vias outside the solder lands.
 for net,points,xy in [
  ('P1.12_TX',[(114.7,107.1),(114.7,106.55),(116.5,106.55),(116.9,106.15)],(116.9,106.15)),
  ('P1.13_RX',[(113.6,107.1),(112.2,107.1)],(112.2,107.1)),
  ('SWDIO',[(121.3,106.0),(121.3,105.45),(119.55,105.45),(119.0,106.0)],(119.0,106.0)),
  ('RESET_N',[(120.2,104.9),(119.35,104.9)],(119.35,104.9)),
 ]:
  trace(net,points,.18)
  via=p.PCB_VIA(b);via.SetPosition(vec(*xy));via.SetFrontWidth(mm(.6));via.SetDrill(mm(.3));via.SetViaType(p.VIATYPE_THROUGH);via.SetLayerPair(p.F_Cu,p.B_Cu);via.SetNet(nets[net]);via.SetLocked(True);b.Add(via)
 # Keep the pair's B.Cu reference plane free of unrelated tracks or vias.
 z=p.ZONE(b);z.SetIsRuleArea(True);z.SetLayer(p.B_Cu);z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True);z.SetDoNotAllowCopperPour(False);z.SetDoNotAllowPads(False);z.SetDoNotAllowFootprints(False)
 outline=z.Outline();outline.NewOutline()
 for x,y in [(110.2,113.2),(112.35,113.2),(112.35,121.1),(110.2,121.1)]:outline.Append(mm(x),mm(y))
 z.SetZoneName('USB reference plane: no B.Cu tracks or vias');b.Add(z)
 p.SaveBoard(str(ROOT/'nora-b106-board.kicad_pcb'),b)
 # Omit the top pour from router input, so SMT GND pads need real paths to B.Cu.
 for zone in list(b.Zones()):
  if not zone.GetIsRuleArea() and zone.GetLayer()==p.F_Cu:b.Remove(zone)
 if not p.ExportSpecctraDSN(b,str(ROOT/'build/unrouted.dsn')):raise RuntimeError('DSN export failed')
 manifest={'module_pin_names':PIN_NAMES,'parts':[{'reference':r,'value':v,'footprint':fp,'nets':n,'pcb_position':pos} for r,_,v,fp,n,_,pos in PARTS],'board_mm':[36,36],'thickness_mm':.8}
 write(ROOT/'hardware/design.json',json.dumps(manifest,indent=2))
 with (ROOT/'hardware/BOM.csv').open('w',newline='') as out:
  w=csv.writer(out);w.writerow(['Reference','Quantity','Value','Footprint','Notes'])
  for r,_,v,fp,n,_,pos in PARTS:w.writerow([r,1,v,fp,'Optional: omit for minimum population' if r in ('D1','R3','SW1') else ''])

if __name__=='__main__':
 if (ROOT/'nora-b106-board.kicad_pcb').exists() and '--overwrite' not in sys.argv and '--schematic-only' not in sys.argv:
  raise SystemExit('Refusing to replace the finished routed PCB. Initial-layout regeneration requires --overwrite.')
 for pattern in ('~nora-b106-board.kicad_pcb.lck','~nora-b106-board.kicad_sch.lck'):
  if (ROOT/pattern).exists():raise SystemExit('Close the design editor before regenerating: '+pattern)
 (ROOT/'build').mkdir(exist_ok=True)
 prepare_libs();schematic()
 if '--schematic-only' not in sys.argv:project();board()
 print('Generated schematic, two-layer PCB, local libraries, design manifest and BOM.')
