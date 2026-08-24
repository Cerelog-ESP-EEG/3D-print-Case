"""Tessellate the board into two meshes for render_preview.py.

    /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd export_board_mesh.py

Writes design/tools/_pv_pcb.stl and _pv_comp.stl, already translated into
case coordinates. Coarse on purpose - these are for pictures, not fit.
"""
import sys, os, traceback
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _paths

try:
    import FreeCAD as App, Import, Mesh
    P = _paths.params(); Z = P["Z_PCB_BOT"]
    App.newDocument("bd"); Import.insert(_paths.STEP, "bd")
    bd = App.getDocument("bd")
    pcb, comp = Mesh.Mesh(), Mesh.Mesh()
    for lbl, sh in _paths.board_solids(bd):
        s = sh.copy(); s.translate(App.Vector(0, 0, Z))
        m = Mesh.Mesh(); m.addFacets(s.tessellate(0.7))
        (pcb if "PCB" in lbl else comp).addMesh(m)
    pcb.write(os.path.join(_paths.TOOLS, "_pv_pcb.stl"))
    comp.write(os.path.join(_paths.TOOLS, "_pv_comp.stl"))
    print("pcb %d facets, components %d facets" % (pcb.CountFacets, comp.CountFacets))
except Exception:
    traceback.print_exc()
