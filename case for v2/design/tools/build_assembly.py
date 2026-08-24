"""Rebuild Case files FreeCAD/assembly_v2.FCStd = case + board, positioned.

    /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd build_assembly.py

The board solids are copied straight from v2_step.step and translated in Z
only, by exactly Z_PCB_BOT. No scaling, no rotation, no geometry edits.
Known-bad models are omitted.
"""
import sys, os, traceback
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _paths

try:
    import FreeCAD as App, Import
    P = _paths.params(); Z = P["Z_PCB_BOT"]
    cd = App.openDocument(_paths.CASE_FCSTD)
    base = [o for o in cd.Objects if o.Label == "base"][0].Shape.copy()
    lid  = [o for o in cd.Objects if o.Label == "lid"][0].Shape.copy()
    App.newDocument("bd"); Import.insert(_paths.STEP, "bd")
    bd = App.getDocument("bd")

    a = App.newDocument("assembly_v2")
    o = a.addObject("Part::Feature", "CASE_BASE"); o.Shape = base
    o = a.addObject("Part::Feature", "CASE_LID");  o.Shape = lid
    n = 0
    for lbl, sh in _paths.board_solids(bd):
        s = sh.copy(); s.translate(App.Vector(0, 0, Z))
        ob = a.addObject("Part::Feature",
                         "PCB_" + lbl.replace(" ", "_").replace(".", "_")[:36])
        ob.Shape = s; ob.Label = "PCB: " + lbl
        n += 1
    a.recompute()
    a.saveAs(_paths.ASM_FCSTD)
    print("assembly_v2.FCStd: 2 case parts + %d board solids, lifted %.2f mm" % (n, Z))
except Exception:
    traceback.print_exc()
