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
