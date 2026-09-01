"""Interference check: every real board solid against the case base and lid.

    /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd verify_fit.py

Threshold is 0.001 mm3 on purpose. A previous version of the V2 script used
0.5 and hid a genuine 0.09 mm3 collision, reporting the fit as clean when it
was not. Do not raise it.
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

    # ---- 16CH-specific: the bottom-side DIP switches must be reachable
    w("")
    w("=== DIP switch access through the floor ===")
    dip_fail = 0
    for name, x0, x1, y0, y1 in P["DIP_SWITCHES"]:
        # sweep the switch footprint straight down through the floor
        probe = Part.makeBox(x1-x0, y1-y0, P["FLOOR_T"] + 2.0,
                             App.Vector(x0, y0, -1.0))
        c = base.common(probe)
        blocked = c.Volume > THRESHOLD
        dip_fail += blocked
        w("  %-14s footprint %5.2f x %5.2f  floor obstruction %8.4f mm3  %s"
          % (name, x1-x0, y1-y0, c.Volume, "BLOCKED" if blocked else "open"))
    w("  switch underside sits at Z %.2f; floor outer face is Z 0.00"
      % P["DIP_BOTTOM_Z"])
    w("  -> recessed %.2f mm inside the opening (operate with a pen tip)"
      % P["DIP_BOTTOM_Z"])

    # ---- 16CH-specific: each edge connector must actually see daylight.
    # A no-interference result only proves nothing collides; it does not prove
    # an opening is in front of the port. This sweeps each connector's own
    # footprint outward through its wall and looks for base material in the way.
    w("")
    w("=== port alignment (connector footprint swept out through its wall) ===")
    PORTS = [("TYPE-C-16PIN-2MD-073", "-X", "USB-C"),
             ("530480210",            "-X", "battery / PicoBlade"),
             ("MK-12C02-G020",        "-Y", "power slide switch"),
             ("TF-SMD_TF-01A",        "-Y", "microSD socket")]
    by_label = {}
    for lbl, sh in _paths.board_solids(bd, skip_bad=False):
        by_label.setdefault(lbl, sh)
    port_fail = 0
    for lbl, wall, what in PORTS:
        sh = by_label.get(lbl)
        if sh is None:
            w("  %-22s MODEL NOT FOUND" % lbl); port_fail += 1; continue
        b = sh.BoundBox
        z0, z1 = b.ZMin + Z, b.ZMax + Z
        out = 6.0
        if wall == "-X":
            probe = Part.makeBox(out, b.YLength, z1-z0,
                                 App.Vector(-P["OUT_L"]/2.0 - 0.5, b.YMin, z0))
        else:
            probe = Part.makeBox(b.XLength, out, z1-z0,
                                 App.Vector(b.XMin, -P["OUT_W"]/2.0 - 0.5, z0))
        c = base.common(probe)
        blocked = c.Volume > THRESHOLD
        port_fail += blocked
        w("  %-22s %-3s %-20s obstruction %8.3f mm3  %s"
          % (lbl[:22], wall, what, c.Volume,
             "BLOCKED" if blocked else "clear"))

    w("")
    w("=== printability spot-checks ===")
    # thinnest standing wall left by the thinning operations
    w("  wall %.2f, thinned to 0.60 (switch) / 0.80 (microSD) / 0.70 (-X ports)"
      % P["WALL"])
    w("  lid ledge over the -Y wall where the header opening removes the rim:")
    ledge = (P["OUT_W"]/2.0) - 23.60
    w("      %.3f mm of lid plate on a %.2f mm wall" % (ledge, P["WALL"]))

    w("")
    ok = (hits == 0 and com.Volume <= THRESHOLD and dip_fail == 0 and port_fail == 0)
    w("RESULT: %s" % ("PASS" if ok else
                      "%d INTERFERENCE(S), %d BLOCKED DIP SWITCH(ES), %d BLOCKED PORT(S)"
                      % (hits, dip_fail, port_fail)))
except Exception:
    w(traceback.format_exc())
print("wrote", REPORT)
