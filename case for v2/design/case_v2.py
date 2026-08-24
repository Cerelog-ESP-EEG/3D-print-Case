"""
Cerelog ESP-EEG V2 enclosure - parametric build script.

Run headless:
  /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd case_v2.py

All dimensions in mm. Board coordinates come from v2_step.step (see
v2_measurements.md); the PCB is centred on the XY origin in that file and
this script keeps the same frame. Case Z=0 is the outside of the base floor.

Every number that a design decision depends on is a named constant below.
Change a constant, re-run, get new STLs.
"""
import os, sys, traceback

# This script lives in design/. Outputs are routed to sibling folders:
#   design/            this script, logs, params, measurements, previews
#   Case files FreeCAD/  .FCStd documents
#   stl/               printable STLs + PRINT.md
DESIGN_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT       = os.path.dirname(DESIGN_DIR)
FCSTD_DIR  = os.path.join(ROOT, "Case files FreeCAD")
STL_DIR    = os.path.join(ROOT, "stl")
for _d in (FCSTD_DIR, STL_DIR):
    if not os.path.isdir(_d):
        os.makedirs(_d)
OUTDIR = DESIGN_DIR
LOG = open(os.path.join(DESIGN_DIR, "build_log.txt"), "w")
def log(*a):
    s = " ".join(str(x) for x in a)
    LOG.write(s + "\n"); LOG.flush()

# ---------------------------------------------------------------- parameters
# --- PCB, measured from v2_step.step
PCB_L, PCB_W, PCB_T = 98.80, 42.75, 1.51
PCB_R = 3.00                      # board corner radius

# --- fit and shell
CLR      = 0.30                   # gap between PCB edge and inner wall
WALL     = 1.60                   # side wall thickness (4 perims @ 0.4 nozzle)
FLOOR_T  = 1.20                   # base floor thickness (3 perims @ 0.4)
LID_T    = 1.60                   # lid plate thickness
BASE_H   = 9.75                   # base outer bottom -> rim top
                                  # set by ESP32 under the rim (top 7.85)
                                  # +0.70 + lip. The taller -X connectors clear
                                  # via RIM_NOTCH instead of raising the case.
LIP_H    = 1.20                   # lid lip depth into cavity
LIP_CLR  = 0.20                   # lip-to-wall clearance per side
LIP_W    = 1.20                   # lip wall thickness (hollow rim)

# --- standoffs: printed pegs, no screws
BOSS_H   = 2.50                   # floor top -> PCB underside (shoulder)
                                  # gated by 2.54mm header pins (-1.41),
                                  # leaving 1.09 mm for the solder fillet
BOSS_OD  = 4.50                   # shoulder the board rests on
PEG_D    = 2.00                   # pin through the 2.20 mm board hole
PEG_CHAM = 0.35                   # lead-in chamfer on the pin tip
MOUNT_HOLES = [                   # measured, deliberately NOT symmetric
    (-46.27, -18.79),
    ( 46.37, -18.61),
    (-46.33,  18.75),
    ( 46.40,  18.38),
]

# --- derived
Z_PCB_BOT = FLOOR_T + BOSS_H      # 8.00 : PCB underside in case frame
def bz(z):                        # board-frame Z -> case-frame Z
    return z + Z_PCB_BOT

IN_L, IN_W = PCB_L + 2*CLR, PCB_W + 2*CLR
IN_R       = PCB_R + CLR
OUT_L, OUT_W = IN_L + 2*WALL, IN_W + 2*WALL
OUT_R      = IN_R + WALL

# --- wall openings: (name, wall, a0, a1, z0, z1)
# wall '-X'/'+X' -> a is Y range;  '-Y'/'+Y' -> a is X range
# z values are board-frame, converted via bz() at cut time
WALL_CUTS = [
    ("usb_c",        "-X",  -5.80,   8.60, -0.90, 6.40),
    ("battery_cable","-X", -16.60,  -8.40, -1.30, 6.40),
    ("slide_switch", "-Y", -37.60, -28.60,  0.60, 3.50),
    ("microsd",      "-Y", -20.80,  -3.40,  0.35, 3.95),
]

# --- floor relief pockets: (name, x0, x1, y0, y1, floor_left)
# None. The only thing that reached below the header pins was an unnamed
# centre SOLID in the STEP, confirmed by the board designer to be a bad 3D
# model (like 530480210). The floor is flat and solid.
FLOOR_RELIEF = []

# --- local wall thinning: (name, wall, a0, a1, z0, z1, keep)
# Removes material from the OUTER face inward, leaving `keep` mm of wall.
# The slide switch passes the board edge by only 1.00 mm and the microSD
# socket mouth by 0.07 mm, so full-thickness wall buries both.
WALL_THIN = [
    ("switch_thin", "-Y", -40.00, -26.00, -0.20, 4.50, 0.60),
    ("microsd_thin","-Y", -24.00,  -0.50, -0.50, 5.00, 0.80),
    ("minus_x_ports","-X", -19.00, 11.00, -1.40, 6.40, 0.70),
]

# --- snap fit: bead on the lid rim, groove in the base wall.
# Short segments rather than one continuous bead: a 80 mm bead is far too
# stiff to deflect, three 14 mm ones snap with thumb pressure.
SNAP_PROT   = 0.45                # bead sticks this far off the rim face
SNAP_Z      = BASE_H - LIP_H + 0.60   # apex, measured up from rim bottom
SNAP_HALF   = 0.325               # bead half-height, so 0.65 tall overall
SNAP_LEN    = 14.00               # length of each segment
SNAP_X      = [-30.0, 0.0, 30.0]  # segment centres, both long walls
SNAP_GROOVE_D = 0.55              # groove depth into the 1.60 mm wall
SNAP_GROOVE_PAD = 0.10            # groove is this much taller than the bead

# --- LED light holes: straight through the lid, directly over each LED.
# Three identical 2.10 x 2.11 parts with consecutive LCSC numbers
# (C2874116/7/8), tops at case Z 6.30, i.e. 3.45 mm below the lid.
LED_HOLE_D = 1.20
LED_HOLES = [
    (-24.25,  -4.07),
    (-39.60, -16.63),
    (-17.65,   2.53),
]

# --- lid sleeves: tubes on the lid underside that drop over the pegs
# poking up through the PCB, locating the lid and capping the board.
SLEEVE_ON    = True
SLEEVE_OD    = 4.50
SLEEVE_BORE  = 2.30               # PEG_D 2.00 + 0.30 clearance
SLEEVE_GAP   = 0.10               # sleeve stops this far above the PCB

# --- lid rim notches: (name, x0, x1, y0, y1)
# The rim is the lowest part of the lid. Notching it over the tall -X
# connectors lets the whole case sit lower instead of clearing them with
# the rim. The lid plate above still clears them.
RIM_NOTCH = [
    ("minus_x_connectors", -51.00, -47.20, -17.50,  9.50),
]

# --- lid openings: (name, x0, x1, y0, y1)
LID_CUTS = [
    # one large opening over the right-hand header cluster:
    # PinHeader_2x12 + both 1x01 AVDD/AVSS pins
    # extends right toward the edge in two steps: full width until the two
    # +X lid sleeves start at X 44.12, then narrowed to pass between them
    # and reach the rim inner face at X 48.30.
    ("header_block",     25.80, 43.60, -19.90, 19.20),
    ("header_block_ext", 43.40, 48.20, -15.50, 15.30),
    # the two SKRPABE010 tactile buttons
    ("button_lo",   -47.60, -41.90,  -8.80, -4.20),
    ("button_hi",   -47.60, -41.90,  10.70, 15.30),
    # PinHeader_1x02, reaches Z 18.14 - needs its own opening
    ("header_1x02",  11.80,  18.10, -16.50, -12.80),
]

# --- lid text
TEXT_FONT  = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
TEXT_LINES = ["Cerelog", "ESP-EEG V2"]
TEXT_SIZE  = 7.0
TEXT_DEPTH  = 0.80                # engraving depth: half of LID_T
TEXT_CX    = -8.00                # centre of the free lid area
TEXT_GAP   = 3.00                 # line spacing

# --- small engraved labels: (text, size, x_centre, y_centre)
# ON / OFF flank the slide-switch actuator, which sits at X -32.46 and
# travels in X. ON is at lower X (the USB-C / battery end of the case).
LABEL_DEPTH = 0.50
LABELS = [
    ("ON",      3.00, -38.00, -18.80),
    ("OFF",     3.00, -27.00, -18.80),
    ("microSD", 3.00, -12.10, -18.80),
]

# --- lid top texture: fine diagonal grooves
TEX_ON      = False               # see README: use a textured build plate
TEX_DEPTH   = 0.25                # shallower than any engraving
TEX_WIDTH   = 0.55
TEX_PITCH   = 2.40
TEX_ANGLE   = 45.0
# smooth plaques where lettering goes - texture through 3 mm letters is unreadable
TEX_KEEPOUT = [
    (-38.00, 22.00, -11.00, 11.00),   # Cerelog / ESP-EEG V2 title block
    (-42.00,  -2.00, -21.00, -16.60),  # ON / OFF / microSD label row
]

# ------------------------------------------------------------------- helpers
def rbox(l, w, h, r, z0=0.0, cx=0.0, cy=0.0):
    """Rounded-rectangle prism, centred on (cx,cy)."""
    import Part, FreeCAD as App
    b = Part.makeBox(l, w, h, App.Vector(cx - l/2.0, cy - w/2.0, z0))
    if r > 0:
        vert = [e for e in b.Edges
                if abs(e.Vertexes[0].Point.x - e.Vertexes[1].Point.x) < 1e-9
                and abs(e.Vertexes[0].Point.y - e.Vertexes[1].Point.y) < 1e-9]
        b = b.makeFillet(r, vert)
    return b

def cut_box(x0, x1, y0, y1, z0, z1):
    import Part, FreeCAD as App
    return Part.makeBox(x1-x0, y1-y0, z1-z0, App.Vector(x0, y0, z0))

def snap_bead(sign, xc):
    """Triangular bead on the lid rim's outer face. sign = -1 (-Y) or +1 (+Y)."""
    import Part, FreeCAD as App
    y_r = sign * (IN_W/2.0 - LIP_CLR)          # rim outer face
    y_t = y_r + sign * SNAP_PROT               # apex, pushed into the wall
    pts = [App.Vector(0, y_r, SNAP_Z - SNAP_HALF),
           App.Vector(0, y_t, SNAP_Z),
           App.Vector(0, y_r, SNAP_Z + SNAP_HALF)]
    wire = Part.makePolygon(pts + [pts[0]])
    face = Part.Face(wire)
    sol = face.extrude(App.Vector(SNAP_LEN, 0, 0))
    sol.translate(App.Vector(xc - SNAP_LEN/2.0, 0, 0))
    return sol

def snap_groove(sign, xc):
    """Matching groove cut into the base cavity wall."""
    y_w = sign * IN_W/2.0                      # cavity inner face
    y0, y1 = sorted([y_w, y_w + sign * SNAP_GROOVE_D])
    return cut_box(xc - SNAP_LEN/2.0 - 0.40, xc + SNAP_LEN/2.0 + 0.40,
                   y0, y1,
                   SNAP_Z - SNAP_HALF - SNAP_GROOVE_PAD,
                   SNAP_Z + SNAP_HALF + SNAP_GROOVE_PAD)

def wall_thin_solid(wall, a0, a1, z0, z1, keep):
    """Box removing the outer part of a wall, leaving `keep` mm standing."""
    over = 5.0
    if wall in ("-Y", "+Y"):
        face = IN_W/2 + keep
        if wall == "-Y":
            return cut_box(a0, a1, -OUT_W/2 - over, -face, bz(z0), bz(z1))
        return cut_box(a0, a1, face, OUT_W/2 + over, bz(z0), bz(z1))
    face = IN_L/2 + keep
    if wall == "-X":
        return cut_box(-OUT_L/2 - over, -face, a0, a1, bz(z0), bz(z1))
    return cut_box(face, OUT_L/2 + over, a0, a1, bz(z0), bz(z1))

def wall_cut_solid(wall, a0, a1, z0, z1):
    """Box that punches fully through the named wall."""
    over = 5.0
    if wall == "-X":
        return cut_box(-OUT_L/2 - over, -IN_L/2 + 1.0, a0, a1, bz(z0), bz(z1))
    if wall == "+X":
        return cut_box(IN_L/2 - 1.0, OUT_L/2 + over, a0, a1, bz(z0), bz(z1))
    if wall == "-Y":
        return cut_box(a0, a1, -OUT_W/2 - over, -IN_W/2 + 1.0, bz(z0), bz(z1))
    if wall == "+Y":
        return cut_box(a0, a1, IN_W/2 - 1.0, OUT_W/2 + over, bz(z0), bz(z1))
    raise ValueError(wall)

# ---------------------------------------------------------------------- main
try:
    import FreeCAD as App, Part, Draft, Mesh

    doc = App.newDocument("case_v2")
    log("=== Cerelog ESP-EEG V2 case ===")
    log("outer     %.2f x %.2f x %.2f (base+lid = %.2f)"
        % (OUT_L, OUT_W, BASE_H, BASE_H + LID_T))
    log("cavity    %.2f x %.2f, corner R %.2f" % (IN_L, IN_W, IN_R))
    log("PCB sits at Z %.2f .. %.2f" % (Z_PCB_BOT, Z_PCB_BOT + PCB_T))

    # ---- BASE
    base = rbox(OUT_L, OUT_W, BASE_H, OUT_R, 0.0)
    cavity = rbox(IN_L, IN_W, BASE_H - FLOOR_T + 1.0, IN_R, FLOOR_T)
    base = base.cut(cavity)
    log("base shell volume %.1f" % base.Volume)

    # ---- standoff bosses
    peg_h = PCB_T + 1.20              # through the board, 1.20 mm proud
    for x, y in MOUNT_HOLES:
        post = Part.makeCylinder(BOSS_OD/2.0, BOSS_H, App.Vector(x, y, FLOOR_T))
        peg = Part.makeCylinder(PEG_D/2.0, peg_h - PEG_CHAM,
                                App.Vector(x, y, FLOOR_T + BOSS_H))
        tip = Part.makeCone(PEG_D/2.0, PEG_D/2.0 - PEG_CHAM, PEG_CHAM,
                            App.Vector(x, y, FLOOR_T + BOSS_H + peg_h - PEG_CHAM))
        base = base.fuse(post).fuse(peg).fuse(tip)
    base = base.removeSplitter()
    log("after %d peg standoffs (boss %.2f + peg %.2f), volume %.1f"
        % (len(MOUNT_HOLES), BOSS_H, peg_h, base.Volume))

    for name, x0, x1, y0, y1, keep in FLOOR_RELIEF:
        c = cut_box(x0, x1, y0, y1, keep, FLOOR_T + 0.01)
        before = base.Volume
        base = base.cut(c)
        log("  relief %-12s floor left %.2f mm, removed %.1f mm3"
            % (name, keep, before - base.Volume))
    base = base.removeSplitter()

    # ---- wall openings
    for name, wall, a0, a1, z0, z1 in WALL_CUTS:
        c = wall_cut_solid(wall, a0, a1, z0, z1)
        before = base.Volume
        base = base.cut(c)
        log("  cut %-14s on %s wall, removed %.1f mm3" % (name, wall, before - base.Volume))
    n = 0
    for sign in (-1, 1):
        for xc in SNAP_X:
            before = base.Volume
            base = base.cut(snap_groove(sign, xc))
            n += 1
    base = base.removeSplitter()
    log("  cut %d snap grooves, %.2f mm deep into the %.2f mm wall"
        % (n, SNAP_GROOVE_D, WALL))

    for name, wall, a0, a1, z0, z1, keep in WALL_THIN:
        c = wall_thin_solid(wall, a0, a1, z0, z1, keep)
        before = base.Volume
        base = base.cut(c)
        log("  thin %-13s on %s wall to %.2f mm, removed %.1f mm3"
            % (name, wall, keep, before - base.Volume))
    base = base.removeSplitter()

    # ---- LID
    lid = rbox(OUT_L, OUT_W, LID_T, OUT_R, BASE_H)
    # hollow rim, NOT a slab: a solid lip collides with every tall part
    lip_o = rbox(IN_L - 2*LIP_CLR, IN_W - 2*LIP_CLR, LIP_H, IN_R - LIP_CLR,
                 BASE_H - LIP_H)
    lip_i = rbox(IN_L - 2*LIP_CLR - 2*LIP_W, IN_W - 2*LIP_CLR - 2*LIP_W,
                 LIP_H + 2.0, max(IN_R - LIP_CLR - LIP_W, 0.1),
                 BASE_H - LIP_H - 1.0)
    lip = lip_o.cut(lip_i)
    lid = lid.fuse(lip).removeSplitter()
    log("lid blank volume %.1f" % lid.Volume)

    if SLEEVE_ON:
        peg_top   = Z_PCB_BOT + PCB_T + 1.20
        sleeve_bot = Z_PCB_BOT + PCB_T + SLEEVE_GAP
        sleeve_h   = BASE_H - sleeve_bot
        bore_h     = (peg_top - sleeve_bot) + 0.60
        for x, y in MOUNT_HOLES:
            tube = Part.makeCylinder(SLEEVE_OD/2.0, sleeve_h,
                                     App.Vector(x, y, sleeve_bot))
            bore = Part.makeCylinder(SLEEVE_BORE/2.0, bore_h,
                                     App.Vector(x, y, sleeve_bot - 0.01))
            lid = lid.fuse(tube).cut(bore)
        lid = lid.removeSplitter()
        log("  %d lid sleeves: %.2f tall, bore %.2f x %.2f deep, stop %.2f above PCB"
            % (len(MOUNT_HOLES), sleeve_h, SLEEVE_BORE, bore_h, SLEEVE_GAP))

    for x, y in LED_HOLES:
        hole = Part.makeCylinder(LED_HOLE_D/2.0, LID_T + 2.0,
                                 App.Vector(x, y, BASE_H - 1.0))
        lid = lid.cut(hole)
    lid = lid.removeSplitter()
    log("  %d LED holes, %.2f mm dia, through the %.2f mm lid"
        % (len(LED_HOLES), LED_HOLE_D, LID_T))

    for name, x0, x1, y0, y1 in RIM_NOTCH:
        c = cut_box(x0, x1, y0, y1, BASE_H - LIP_H - 0.50, BASE_H + 0.01)
        before = lid.Volume
        lid = lid.cut(c)
        log("  notch %-13s in lid rim, removed %.1f mm3" % (name, before - lid.Volume))
    lid = lid.removeSplitter()

    for name, x0, x1, y0, y1 in LID_CUTS:
        c = cut_box(x0, x1, y0, y1, BASE_H - LIP_H - 1.0, BASE_H + LID_T + 1.0)
        before = lid.Volume
        lid = lid.cut(c)
        log("  cut %-14s in lid, removed %.1f mm3" % (name, before - lid.Volume))
    lid = lid.removeSplitter()

    n = 0
    for sign in (-1, 1):
        for xc in SNAP_X:
            lid = lid.fuse(snap_bead(sign, xc))
            n += 1
    lid = lid.removeSplitter()
    log("  added %d snap beads, %.2f mm proud (%.2f mm engagement past the wall)"
        % (n, SNAP_PROT, SNAP_PROT - LIP_CLR))

    # ---- lid top texture (cut before text so engravings stay deeper)
    if TEX_ON:
        import math
        zt_ = BASE_H + LID_T
        diag = math.hypot(OUT_L, OUT_W) + 4.0
        n_t = int(diag / TEX_PITCH) + 2
        bars = []
        for k in range(-n_t, n_t + 1):
            bar = Part.makeBox(diag, TEX_WIDTH, TEX_DEPTH + 1.0,
                               App.Vector(-diag/2.0, k*TEX_PITCH - TEX_WIDTH/2.0,
                                          zt_ - TEX_DEPTH))
            bar.rotate(App.Vector(0, 0, zt_), App.Vector(0, 0, 1), TEX_ANGLE)
            bars.append(bar)
        tex = Part.makeCompound(bars)
        for kx0, kx1, ky0, ky1 in TEX_KEEPOUT:
            tex = tex.cut(cut_box(kx0, kx1, ky0, ky1,
                                  zt_ - TEX_DEPTH - 0.5, zt_ + 1.0))
        before = lid.Volume
        lid = lid.cut(tex)
        lid = lid.removeSplitter()
        log("  texture: %d grooves @ %.2f pitch, %.2f deep, removed %.1f mm3"
            % (len(bars), TEX_PITCH, TEX_DEPTH, before - lid.Volume))

    # ---- lid text (engraved)
    zt = BASE_H + LID_T
    total_h = len(TEXT_LINES) * TEXT_SIZE + (len(TEXT_LINES) - 1) * TEXT_GAP
    y_cur = total_h / 2.0 - TEXT_SIZE
    for line in TEXT_LINES:
        ss = Draft.make_shapestring(String=line, FontFile=TEXT_FONT,
                                    Size=TEXT_SIZE, Tracking=0.0)
        doc.recompute()
        sh = ss.Shape
        bb = sh.BoundBox
        # engraved: cut down into the top face, not raised off it
        sol = sh.extrude(App.Vector(0, 0, TEXT_DEPTH + 1.0))
        sol.translate(App.Vector(TEXT_CX - bb.Center.x, y_cur - bb.YMin,
                                 zt - TEXT_DEPTH))
        lid = lid.cut(sol)
        log("  text '%s' width %.2f at y %.2f" % (line, bb.XLength, y_cur))
        doc.removeObject(ss.Name)
        y_cur -= (TEXT_SIZE + TEXT_GAP)
    lid = lid.removeSplitter()

    for label, size, lx, ly in LABELS:
        ss = Draft.make_shapestring(String=label, FontFile=TEXT_FONT,
                                    Size=size, Tracking=0.0)
        doc.recompute()
        bb = ss.Shape.BoundBox
        sol = ss.Shape.extrude(App.Vector(0, 0, LABEL_DEPTH + 1.0))
        sol.translate(App.Vector(lx - bb.Center.x, ly - bb.Center.y,
                                 zt - LABEL_DEPTH))
        lid = lid.cut(sol)
        log("  label '%s' %.2f wide at (%.2f, %.2f), %.2f deep"
            % (label, bb.XLength, lx, ly, LABEL_DEPTH))
        doc.removeObject(ss.Name)
    lid = lid.removeSplitter()

    # ---- validate + export
    for nm, sh in (("base", base), ("lid", lid)):
        log("%s: solids=%d valid=%s volume=%.1f"
            % (nm, len(sh.Solids), sh.isValid(), sh.Volume))
        b = sh.BoundBox
        log("      bbox %.2f x %.2f x %.2f  (Z %.2f..%.2f)"
            % (b.XLength, b.YLength, b.ZLength, b.ZMin, b.ZMax))

    Part.show(base, "base"); Part.show(lid, "lid")
    doc.recompute()

    for nm, sh in (("case_v2_base", base), ("case_v2_lid", lid)):
        m = Mesh.Mesh()
        m.addFacets(sh.tessellate(0.05))
        p = os.path.join(STL_DIR, nm + ".stl")
        m.write(p)
        log("wrote %s  (%d facets)" % (p, m.CountFacets))

    doc.saveAs(os.path.join(FCSTD_DIR, "case_v2.FCStd"))
    log("wrote case_v2.FCStd")

    # Emit the derived dimensions so the tools/ scripts never drift out of
    # sync with this file. Every tool reads this, nothing hard-codes Z.
    import json
    params = dict(PCB_L=PCB_L, PCB_W=PCB_W, PCB_T=PCB_T, PCB_R=PCB_R,
                  CLR=CLR, WALL=WALL, FLOOR_T=FLOOR_T, LID_T=LID_T,
                  BASE_H=BASE_H, LIP_H=LIP_H, LIP_W=LIP_W, LIP_CLR=LIP_CLR,
                  BOSS_H=BOSS_H, PEG_D=PEG_D,
                  Z_PCB_BOT=Z_PCB_BOT, Z_PCB_TOP=Z_PCB_BOT + PCB_T,
                  RIM_UNDERSIDE=BASE_H - LIP_H, TOTAL_H=BASE_H + LID_T,
                  IN_L=IN_L, IN_W=IN_W, OUT_L=OUT_L, OUT_W=OUT_W,
                  MOUNT_HOLES=MOUNT_HOLES, LED_HOLES=LED_HOLES,
                  BAD_MODELS=["530480210 (height wrong)", "SOLID", "SOLID001", "SOLID002"])
    with open(os.path.join(DESIGN_DIR, "case_v2_params.json"), "w") as f:
        json.dump(params, f, indent=2)
    log("wrote case_v2_params.json")
    log("OK")
except Exception:
    log(traceback.format_exc())
