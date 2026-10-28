"""Independent native-file connectivity, footprint and via-in-pad checks."""
from pathlib import Path
import pcbnew as p,json,sys,math
root=Path(__file__).resolve().parents[1]
b=p.LoadBoard(str(Path(sys.argv[1]) if len(sys.argv)>1 else root/'nora-minimal.kicad_pcb'))
d=json.loads((root/'design.json').read_text());fs={f.GetReference():f for f in b.GetFootprints()}
assert set(fs)==set(d['parts']), (set(fs),set(d['parts']))
for ref,assignments in d['parts'].items():
 for q in fs[ref].Pads():
  n=q.GetNumber()
  if n in assignments:assert q.GetNetname()=='/'+assignments[n],(ref,n,q.GetNetname())
u=fs['U1'];actual={q.GetNumber():q for q in u.Pads()};assert len(actual)==82
expected=p.FootprintLoad(str(root/'hardware/Breakout.pretty'),'NORA-B106')
for q in expected.Pads():
 a=actual[q.GetNumber()]
 assert tuple(a.GetFPRelativePosition())==tuple(q.GetFPRelativePosition()),q.GetNumber()
 assert tuple(a.GetSize())==tuple(q.GetSize()),q.GetNumber()
 assert a.GetLocalSolderMaskMargin()==q.GetLocalSolderMaskMargin(),q.GetNumber()
 assert a.GetLocalSolderPasteMargin()==q.GetLocalSolderPasteMargin(),q.GetNumber()
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA):
  for q in u.Pads():
   c=p.SHAPE_POLY_SET();q.TransformShapeToPolygon(c,p.F_Cu,p.FromMM(.151),p.FromMM(.002))
   assert not c.Contains(t.GetPosition()),('Open via drill intersects module land',q.GetNumber())
assert abs(p.ToMM(b.GetDesignSettings().GetBoardThickness())-1.6)<.001
assert b.GetCopperLayerCount()==2
print('Audit passed: 82 module land positions/sizes/mask/paste, all assigned pad nets, 1.6 mm / 2 layers, no open via drill in module lands.')

# Compact board dimensions, recommended ground extent and tall-part RF spacing.
edges=[v for q in b.GetDrawings() if isinstance(q,p.PCB_SHAPE) and q.GetLayer()==p.Edge_Cuts for v in [q.GetStart(),q.GetEnd()]]
x0,y0=min(v.x for v in edges),min(v.y for v in edges);x1,y1=max(v.x for v in edges),max(v.y for v in edges)
assert (round(p.ToMM(x1-x0),4),round(p.ToMM(y1-y0),4))==(31.5,27.5)
body=[v for q in u.GraphicalItems() if q.GetLayer()==p.F_Fab for v in [q.GetStart(),q.GetEnd()]]
left=min(v.x for v in body);right=max(v.x for v in body);bottom=max(v.y for v in body)
assert min(left-x0-p.FromMM(.4),x1-right-p.FromMM(.4),y1-bottom-p.FromMM(.4))>=p.FromMM(10)
rf=next(z for z in b.Zones() if z.GetIsRuleArea() and z.GetZoneName().startswith('Antenna:'))
outline=rf.Outline().COutline(0);points=[outline.CPoint(i) for i in range(outline.PointCount())]
rx0,ry0=min(v.x for v in points),min(v.y for v in points);rx1,ry1=max(v.x for v in points),max(v.y for v in points)
for ref in ['J1','J2','J3']:
 points=[v for q in fs[ref].GraphicalItems() if q.GetLayer()==p.F_CrtYd for v in [q.GetStart(),q.GetEnd()]]
 cx0,cy0=min(v.x for v in points),min(v.y for v in points);cx1,cy1=max(v.x for v in points),max(v.y for v in points)
 distance=math.hypot(max(rx0-cx1,cx0-rx1,0),max(ry0-cy1,cy0-ry1,0))
 assert distance>=p.FromMM(10),(ref,p.ToMM(distance))
 print(ref,'courtyard-to-antenna clearance:',round(p.ToMM(distance),2),'mm')
assert len(list(fs['J3'].Pads()))==6
print('Compact dimensions, six-pin GPIO header and recommended RF clearances passed.')
