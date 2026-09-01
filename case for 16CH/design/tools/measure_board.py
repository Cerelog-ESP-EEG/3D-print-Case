"""Measure the 16CH board from its KiCad STEP export.

    /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd measure_board.py

Writes design/16ch_raw_measurements.txt. Read-only: touches no case geometry.
This is the input to 16ch_measurements.md and to every constant in case_16ch.py.
"""
import sys, os, traceback
HERE = os.path.dirname(os.path.abspath(__file__))
DESIGN = os.path.dirname(HERE)
ROOT = os.path.dirname(DESIGN)
STEP = os.path.join(ROOT, "Case files FreeCAD", "16ch_step.step")
OUT = open(os.path.join(DESIGN, "16ch_raw_measurements.txt"), "w")
def w(*a):
    s = " ".join(str(x) for x in a)
    OUT.write(s + "\n"); OUT.flush(); print(s)

try:
    import FreeCAD as App, Import, Part
    App.newDocument("bd")
    Import.insert(STEP, "bd")
    d = App.getDocument("bd")

    solids = []
    for o in d.Objects:
        if not hasattr(o, "Shape"):
            continue
        try:
            if not o.Shape.Solids:
                continue
        except Exception:
            continue
        solids.append((o.Label, o.Shape))
    w("total objects with solids: %d" % len(solids))

    # overall bbox
    gb = None
    for lbl, sh in solids:
        b = sh.BoundBox
        gb = b if gb is None else (gb.add(b) or gb)
    w("GLOBAL bbox  X %.3f..%.3f  Y %.3f..%.3f  Z %.3f..%.3f"
      % (gb.XMin, gb.XMax, gb.YMin, gb.YMax, gb.ZMin, gb.ZMax))
    w("GLOBAL size  %.3f x %.3f x %.3f" % (gb.XLength, gb.YLength, gb.ZLength))
    w("")

    # find the PCB: biggest flat solid
    w("=== candidates for the PCB substrate (thin, large footprint) ===")
    cands = []
    for lbl, sh in solids:
        b = sh.BoundBox
        if b.ZLength < 3.0 and b.XLength > 30 and b.YLength > 20:
            cands.append((b.XLength * b.YLength, lbl, sh))
    cands.sort(reverse=True, key=lambda t: t[0])
    for area, lbl, sh in cands[:6]:
        b = sh.BoundBox
        w("  %-34s %8.1f mm2  %.2f x %.2f x %.2f  Z %.3f..%.3f"
          % (lbl[:34], area, b.XLength, b.YLength, b.ZLength, b.ZMin, b.ZMax))
    w("")

    pcb_lbl, pcb = cands[0][1], cands[0][2]
    pb = pcb.BoundBox
    w("PCB  = %s" % pcb_lbl)
    w("PCB  outline %.3f x %.3f  thickness %.3f" % (pb.XLength, pb.YLength, pb.ZLength))
    w("PCB  X %.3f..%.3f  Y %.3f..%.3f  Z %.3f..%.3f"
      % (pb.XMin, pb.XMax, pb.YMin, pb.YMax, pb.ZMin, pb.ZMax))
    w("PCB  centre (%.3f, %.3f)" % (pb.Center.x, pb.Center.y))
    w("")

    # PCB top face -> outline geometry + holes
    w("=== PCB top face analysis ===")
    top_faces = [f for f in pcb.Faces
                 if abs(f.Surface.Axis.z) > 0.99 and abs(f.BoundBox.ZMin - pb.ZMax) < 1e-6] \
                if all(hasattr(f.Surface, "Axis") for f in pcb.Faces) else []
    if not top_faces:
        top_faces = []
        for f in pcb.Faces:
            try:
                if abs(f.BoundBox.ZLength) < 1e-6 and abs(f.BoundBox.ZMin - pb.ZMax) < 1e-6:
                    top_faces.append(f)
            except Exception:
                pass
    top_faces.sort(key=lambda f: -f.Area)
    if top_faces:
        tf = top_faces[0]
        w("top face area %.1f mm2, wires %d" % (tf.Area, len(tf.Wires)))
        outer = tf.OuterWire
        arcs = [e for e in outer.Edges if e.Curve.TypeId == "Part::GeomCircle"]
        lines = [e for e in outer.Edges if e.Curve.TypeId == "Part::GeomLine"]
        w("outline: %d edges (%d arcs, %d lines)" % (len(outer.Edges), len(arcs), len(lines)))
        radii = sorted(set(round(e.Curve.Radius, 3) for e in arcs))
        w("outline arc radii: %s" % radii)
        w("")
        w("=== holes in the PCB (inner wires of the top face) ===")
        holes = []
        for wi in tf.Wires:
            if wi.isSame(outer):
                continue
            b = wi.BoundBox
            dia = max(b.XLength, b.YLength)
            holes.append((dia, b.Center.x, b.Center.y, len(wi.Edges)))
        holes.sort(reverse=True)
        w("inner wires: %d" % len(holes))
        for dia, cx, cy, ne in holes[:40]:
            w("   D %6.3f  at (%8.3f, %8.3f)   edges %d" % (dia, cx, cy, ne))
        w("")
        w("=== mounting-hole sized (D 1.8 .. 4.5) ===")
        for dia, cx, cy, ne in sorted(holes, key=lambda h: (h[2], h[1])):
            if 1.8 <= dia <= 4.5:
                w("   D %6.3f  at (%8.3f, %8.3f)" % (dia, cx, cy))
    w("")

    # every component solid, sorted by height
    w("=== ALL SOLIDS (excluding the PCB), by top Z ===")
    rows = []
    for lbl, sh in solids:
        if lbl == pcb_lbl:
            continue
        b = sh.BoundBox
        if b.XLength * b.YLength * b.ZLength <= 0:
            continue
        rows.append((b.ZMax, b.ZMin, lbl, b))
    rows.sort(reverse=True)
    w("%-36s %8s %8s   %-18s %-18s" % ("label", "Zmin", "Zmax", "X range", "Y range"))
    for zmax, zmin, lbl, b in rows:
        w("%-36s %8.3f %8.3f   %7.2f..%7.2f  %7.2f..%7.2f"
          % (lbl[:36], zmin, zmax, b.XMin, b.XMax, b.YMin, b.YMax))
    w("")
    w("=== BELOW-BOARD protrusions (Zmin < PCB bottom %.3f) ===" % pb.ZMin)
    for zmax, zmin, lbl, b in sorted(rows, key=lambda r: r[1]):
        if zmin < pb.ZMin - 1e-6:
            w("  %-36s Zmin %8.3f  (%.3f below board)  X %7.2f..%7.2f Y %7.2f..%7.2f"
              % (lbl[:36], zmin, pb.ZMin - zmin, b.XMin, b.XMax, b.YMin, b.YMax))
    w("")
    w("=== EDGE-PROXIMATE parts (within 2.0 mm of, or past, a board edge) ===")
    for zmax, zmin, lbl, b in rows:
        msgs = []
        if b.XMin < pb.XMin + 2.0: msgs.append("-X  overhang %+.2f" % (pb.XMin - b.XMin))
        if b.XMax > pb.XMax - 2.0: msgs.append("+X  overhang %+.2f" % (b.XMax - pb.XMax))
        if b.YMin < pb.YMin + 2.0: msgs.append("-Y  overhang %+.2f" % (pb.YMin - b.YMin))
        if b.YMax > pb.YMax - 2.0: msgs.append("+Y  overhang %+.2f" % (b.YMax - pb.YMax))
        if msgs:
            w("  %-34s Z %6.2f..%6.2f  X %7.2f..%7.2f Y %7.2f..%7.2f  | %s"
              % (lbl[:34], zmin, zmax, b.XMin, b.XMax, b.YMin, b.YMax, "; ".join(msgs)))
except Exception:
    w(traceback.format_exc())
OUT.close()
