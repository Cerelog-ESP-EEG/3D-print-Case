"""Open the assembly in the FreeCAD GUI with everything visible.

    /Applications/FreeCAD.app/Contents/MacOS/FreeCAD show_assembly.py

A document built headlessly has no saved GUI state, so FreeCAD hides most
objects on first open. This sets them all visible, makes the lid
translucent so you can see the fit, saves, and leaves the window open.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _paths
import FreeCAD as App, FreeCADGui as Gui

d = App.openDocument(_paths.ASM_FCSTD)
n = 0
for o in d.Objects:
    vo = getattr(o, "ViewObject", None)
    if vo is None:
        continue
    try:
        vo.Visibility = True
        if o.Label == "CASE_LID":
            vo.Transparency = 60
        n += 1
    except Exception:
        pass
d.save()
try:
    Gui.activeDocument().activeView().viewAxonometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
print("visible:", n)
