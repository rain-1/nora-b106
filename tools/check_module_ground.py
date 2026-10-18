"""Check the module ground-reference constraints that ordinary ERC misses."""
from pathlib import Path
import math

import pcbnew as pcb


def segment_hits_box(start, end, bounds):
    """Clip a segment against an axis-aligned rectangle, in board units."""
    lower, upper = 0.0, 1.0
    for a, b, low, high in zip(start, end, bounds[:2], bounds[2:]):
        if a == b:
            if not low <= a <= high:
                return False
        else:
            entering, leaving = sorted(((low - a) / (b - a), (high - a) / (b - a)))
            lower, upper = max(lower, entering), min(upper, leaving)
            if lower > upper:
                return False
    return True


def point_segment_distance(point, start, end):
    dx, dy = end[0] - start[0], end[1] - start[1]
    length_squared = dx * dx + dy * dy
    t = (((point[0] - start[0]) * dx + (point[1] - start[1]) * dy)
         / length_squared) if length_squared else 0
    t = max(0, min(1, t))
    return math.hypot(point[0] - start[0] - t * dx, point[1] - start[1] - t * dy)


def segment_box_distance(start, end, bounds):
    if segment_hits_box(start, end, bounds):
        return 0
    xmin, ymin, xmax, ymax = bounds
    distances = [math.hypot(max(xmin - x, 0, x - xmax), max(ymin - y, 0, y - ymax))
                 for x, y in (start, end)]
    distances += [point_segment_distance((x, y), start, end)
                  for x in (xmin, xmax) for y in (ymin, ymax)]
    return min(distances)


def check(board):
    module = next(f for f in board.GetFootprints() if f.GetReference() == 'U1')
    corners = [point for item in module.GraphicalItems()
               if item.GetLayer() == pcb.F_Fab
               for point in (item.GetStart(), item.GetEnd())]
    xmin, ymin = min(p.x for p in corners), min(p.y for p in corners)
    xmax, ymax = max(p.x for p in corners), max(p.y for p in corners)
    errors = []
    ground_vias = []
    for item in board.GetTracks():
        if isinstance(item, pcb.PCB_VIA):
            if item.GetNetname() == '/GND':
                ground_vias.append(item)
                continue
            position = item.GetPosition()
            dx = max(xmin - position.x, 0, position.x - xmax)
            dy = max(ymin - position.y, 0, position.y - ymax)
            radius = item.GetWidth(pcb.B_Cu) / 2 + pcb.FromMM(.15)
            if math.hypot(dx, dy) < radius - 1:
                errors.append(f'{item.GetNetname()} via clearance enters module ground reference')
        elif item.GetLayer() == pcb.B_Cu and item.GetNetname() != '/GND':
            margin = item.GetWidth() / 2 + pcb.FromMM(.15) - 1
            bounds = (xmin, ymin, xmax, ymax)
            if segment_box_distance(tuple(item.GetStart()), tuple(item.GetEnd()), bounds) < margin:
                errors.append(f'{item.GetNetname()} back track clearance enters module ground reference')
    for zone in board.Zones():
        if zone.GetIsRuleArea() or zone.GetNetname() != '/GND':
            continue
        polygons = zone.GetFilledPolysList(zone.GetLayer())
        if zone.GetLayer() == pcb.B_Cu and polygons.OutlineCount() != 1:
            errors.append('Back ground plane is split into separate copper regions')
        if zone.GetLayer() == pcb.F_Cu:
            counts = [sum(polygons.Contains(v.GetPosition(), i) for v in ground_vias)
                      for i in range(polygons.OutlineCount())]
            if any(count < 2 for count in counts):
                errors.append(f'Top ground islands need at least two stitching vias each: {counts}')
            print(f'Top ground islands: {len(counts)}; vias per island: {counts}')
    if errors:
        raise SystemExit('\n'.join(errors))
    print(f'Module ground reference passed; {len(ground_vias)} ground stitching vias')


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    check(pcb.LoadBoard(str(root / 'nora-b106-board.kicad_pcb')))
