"""Interference check: every real board solid against the case base and lid.

    /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd verify_fit.py

Threshold is 0.001 mm3 on purpose. A previous version used 0.5 and hid a
genuine 0.09 mm3 collision, reporting the fit as clean when it was not.
"""
import sys, os, traceback
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _paths

REPORT = os.path.join(_paths.DESIGN_DIR, "verify_fit.txt")
OUT = open(REPORT, "w")
def w(*a):
    OUT.write(" ".join(str(x) for x in a) + "\n"); OUT.flush()

THRESHOLD = 0.001

try:
    import FreeCAD as App, Import, Part
    P = _paths.params()
    Z = P["Z_PCB_BOT"]

    cd = App.openDocument(_paths.CASE_FCSTD)
    base = [o for o in cd.Objects if o.Label == "base"][0].Shape
    lid  = [o for o in cd.Objects if o.Label == "lid"][0].Shape

    App.newDocument("bd"); Import.insert(_paths.STEP, "bd")
    bd = App.getDocument("bd")

    w("case  %.2f x %.2f x %.2f    PCB underside at Z %.2f"
      % (P["OUT_L"], P["OUT_W"], P["TOTAL_H"], Z))
    w("skipping known-bad models: %s" % ", ".join(P["BAD_MODELS"]))
    w("")

    hits = 0; n = 0
    w("=== BOARD vs CASE (intersection > %.3f mm3) ===" % THRESHOLD)
    for lbl, sh in _paths.board_solids(bd):
        n += 1
        s = sh.copy(); s.translate(App.Vector(0, 0, Z))
        for cn, cs in (("BASE", base), ("LID", lid)):
            if not s.BoundBox.intersect(cs.BoundBox):
                continue
            try:
                com = s.common(cs)
            except Exception:
                continue
            if com.Volume > THRESHOLD:
                hits += 1
                b = com.BoundBox
                w("  %-28s x %-4s %8.3f mm3  X %7.2f..%7.2f Y %7.2f..%7.2f Z %6.2f..%6.2f"
                  % (lbl[:28], cn, com.Volume, b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax))
    if not hits:
        w("  none  (%d solids checked)" % n)

    w("")
    w("=== BASE vs LID ===")
    com = base.common(lid)
    w("  %.4f mm3  %s" % (com.Volume, "CLASH" if com.Volume > THRESHOLD else "clean"))

    w("")
    w("=== peg / sleeve mate ===")
    peg_top = P["Z_PCB_TOP"] + 1.20
    sleeve_bot = P["Z_PCB_TOP"] + 0.10
    w("  peg top %.2f, sleeve mouth %.2f -> engagement %.2f mm"
      % (peg_top, sleeve_bot, peg_top - sleeve_bot))
    for x, y in P["MOUNT_HOLES"]:
        probe = Part.makeCylinder(1.00, peg_top - sleeve_bot, App.Vector(x, y, sleeve_bot))
        c = lid.common(probe)
        w("  peg (%7.2f,%7.2f)  obstruction %.4f mm3  %s"
          % (x, y, c.Volume, "BLOCKED" if c.Volume > THRESHOLD else "clear"))

    w("")
    w("=== LED holes clear through the lid ===")
    for x, y in P["LED_HOLES"]:
        probe = Part.makeCylinder(0.50, 4.0, App.Vector(x, y, P["BASE_H"] - 0.5))
        c = lid.common(probe)
        w("  LED (%7.2f,%7.2f)  obstruction %.4f mm3  %s"
          % (x, y, c.Volume, "BLOCKED" if c.Volume > THRESHOLD else "open"))
    w("")
    w("RESULT: %s" % ("PASS" if hits == 0 else "%d INTERFERENCE(S)" % hits))
except Exception:
    w(traceback.format_exc())
print("wrote", REPORT)
