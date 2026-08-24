"""Shared path + parameter resolution for the tools in this folder.

Nothing here hard-codes a dimension. Every Z value comes from
design/case_v2_params.json, which case_v2.py rewrites on every build.
That is deliberate: an earlier version of these scripts had Z_PCB_BOT
hard-coded, and it silently went stale every time the standoff changed.
"""
import os, json

TOOLS      = os.path.dirname(os.path.abspath(__file__))
DESIGN_DIR = os.path.dirname(TOOLS)
ROOT       = os.path.dirname(DESIGN_DIR)
FCSTD_DIR  = os.path.join(ROOT, "Case files FreeCAD")
STL_DIR    = os.path.join(ROOT, "stl")

STEP      = os.path.join(FCSTD_DIR, "v2_step.step")
CASE_FCSTD= os.path.join(FCSTD_DIR, "case_v2.FCStd")
ASM_FCSTD = os.path.join(FCSTD_DIR, "assembly_v2.FCStd")
BASE_STL  = os.path.join(STL_DIR, "case_v2_base.stl")
LID_STL   = os.path.join(STL_DIR, "case_v2_lid.stl")

# Models in the KiCad STEP that are known wrong. Confirmed by the board
# designer. Skipped by every check so they stop generating false hits.
BAD_MODELS_PREFIX = ("SOLID",)
BAD_MODELS_EXACT  = {"530480210"}   # height wrong; still checked for XY

def params():
    with open(os.path.join(DESIGN_DIR, "case_v2_params.json")) as f:
        return json.load(f)

def board_solids(doc, skip_bad=True):
    """Yield (label, Shape) for every real board solid in an imported STEP."""
    for o in doc.Objects:
        if not hasattr(o, "Shape"):
            continue
        try:
            if not o.Shape.Solids:
                continue
        except Exception:
            continue
        if o.Label == "v2_step 1":          # top-level compound
            continue
        if skip_bad and o.Label.startswith(BAD_MODELS_PREFIX):
            continue
        yield o.Label, o.Shape
