"""Reconcile a generated PCB's net names and NC pads with KiCad's own netlist."""
from pathlib import Path
import subprocess
import sexpdata as s
import pcbnew as p

root=Path(__file__).resolve().parents[1]
netfile=root/'build/schematic.net'
subprocess.run(['kicad-cli','sch','export','netlist','-o',str(netfile),str(root/'nora-b106-board.kicad_sch')],check=True)
def key(n):return str(n[0]) if isinstance(n,list) and n else ''
def child(n,name):return next(x for x in n if key(x)==name)
netlist=s.load(netfile.open());assignment={}
for net in child(netlist,'nets')[1:]:
    if key(net)!='net':continue
    name=child(net,'name')[1]
    for node in net:
        if key(node)=='node':assignment[(child(node,'ref')[1],child(node,'pin')[1])]=name
board=p.LoadBoard(str(root/'nora-b106-board.kicad_pcb'))
for net in board.GetNetsByNetcode().values():
    name=net.GetNetname()
    if name and not name.startswith(('/', 'unconnected-')):net.SetNetname('/'+name)
nets={n.GetNetname():n for n in board.GetNetsByNetcode().values()}
seen=set()
for footprint in board.GetFootprints():
    for pad in footprint.Pads():
        if not pad.GetNumber():continue
        pin=(footprint.GetReference(),pad.GetNumber())
        if pin not in assignment:raise RuntimeError(f'Physical pad absent from schematic: {pin}')
        name=assignment[pin]
        if name not in nets:
            nets[name]=p.NETINFO_ITEM(board,name);board.Add(nets[name])
        pad.SetNet(nets[name]);seen.add(pin)
missing=set(assignment)-seen
if missing:raise RuntimeError(f'Schematic pins absent from board: {missing}')
board.BuildConnectivity();p.ZONE_FILLER(board).Fill(board.Zones());p.SaveBoard(str(root/'nora-b106-board.kicad_pcb'),board)
print(f'Reconciled {len(seen)} unique component pads with KiCad-exported netlist.')
