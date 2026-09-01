"""
Cerelog ESP-EEG 16CH enclosure - parametric build script.

Run headless:
  /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd case_16ch.py

All dimensions in mm. Board coordinates come from 16ch_step.step (see
16ch_measurements.md); the PCB is centred on the XY origin in that file and
this script keeps the same frame. Case Z=0 is the outside of the base floor.

Every number that a design decision depends on is a named constant below.
Change a constant, re-run, get new STLs.

Differences from the V2 case, all confirmed by the board designer:
  * the 2x40 electrode header moved from the +X edge to the -Y edge, so the
    lid opening for it cuts through the -Y lid rim over 52 mm.
  * two DHA-08TQR 8-position DIP switches are mounted on the BOTTOM of the
    board, 2.385 mm proud. They set the standoff height and each gets a
    through-opening in the case floor.
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
# --- PCB, measured from 16ch_step.step
PCB_L, PCB_W, PCB_T = 116.50, 46.87, 1.51
PCB_R = 3.00                      # board corner radius

# --- fit and shell
CLR      = 0.30                   # gap between PCB edge and inner wall
WALL     = 1.60                   # side wall thickness (4 perims @ 0.4 nozzle)
FLOOR_T  = 1.20                   # base floor thickness (3 perims @ 0.4)
LID_T    = 1.60                   # lid plate thickness
BASE_H   = 10.05                  # base outer bottom -> rim top
                                  # set by the USB-C shell (top 9.13 in case
                                  # frame) + 0.92 under the lid plate. The rim
                                  # clears it via RIM_NOTCH instead of the
                                  # whole case growing.
LIP_H    = 1.20                   # lid lip depth into cavity
LIP_CLR  = 0.20                   # lip-to-wall clearance per side
LIP_W    = 1.20                   # lip wall thickness (hollow rim)

# --- standoffs: printed pegs, no screws
BOSS_H   = 3.00                   # floor top -> PCB underside (shoulder)
                                  # V2 used 2.50. Raised because the board now
                                  # carries bottom-side parts: DHA-08TQR DIP
                                  # switches reach -2.385 and the 2.54 mm
                                  # header pins -1.405. 3.00 leaves 0.62 under
                                  # the switches and 1.60 under the pins.
BOSS_OD  = 4.50                   # shoulder the board rests on
PEG_D    = 2.00                   # pin through the 2.20 mm board hole
PEG_CHAM = 0.35                   # lead-in chamfer on the pin tip
MOUNT_HOLES = [                   # measured, deliberately NOT symmetric
    (-54.859, -19.766),
    ( 55.050, -19.766),
    (-54.859,  19.501),
    ( 55.050,  19.501),
]

# --- derived
Z_PCB_BOT = FLOOR_T + BOSS_H      # 4.20 : PCB underside in case frame
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
    ("usb_c",        "-X",  -5.60,   5.50, -0.90, 6.00),
    ("battery_cable","-X", -16.80, -10.30, -1.30, 6.00),
    # open to the top of the wall: MK-12C02-G020 protrudes 0.36 mm PAST the
    # board edge, so the board cannot drop in past a closed slot.
    ("slide_switch", "-Y", -47.00, -36.90,  0.30, 6.20),
    ("microsd",      "-Y", -30.20, -11.70,  0.20,  4.10),
]

# --- floor openings: (name, x0, x1, y0, y1)
# NEW for 16CH. Two DHA-08TQR 8-position DIP switches are mounted on the
# underside of the board and must be reachable from outside the case.
#   DHA-08TQR    X -7.995..3.295   Y -11.616..-3.516   Z -2.385..-0.085
#   DHA-08TQR001 X 26.205..37.495  Y -11.616..-3.516   Z -2.385..-0.085
# 0.80 mm clearance on every side. Straight through-holes, no counterbore:
# a counterbore would be a first-layer overhang and prints badly.
FLOOR_CUTS = [
    ("dip_switch_1",  -8.80,   4.10, -12.42, -2.72),
    ("dip_switch_2",  25.40,  38.30, -12.42, -2.72),
]

# --- floor relief pockets: (name, x0, x1, y0, y1, floor_left)
# None. The only thing reaching below the DIP switches is the unnamed centre
# SOLID in the STEP, confirmed by the board designer to be a bad 3D model.
FLOOR_RELIEF = []

# --- local wall thinning: (name, wall, a0, a1, z0, z1, keep)
# Removes material from the OUTER face inward, leaving `keep` mm of wall.
# USB-C sits 0.15 mm inside the board edge and the battery connector 0.13 mm;
# full-thickness wall puts their mouths 2.05 mm down a tunnel.
WALL_THIN = [
    ("switch_thin",  "-Y", -48.00, -36.00, -0.20, 6.20, 0.60),
    ("microsd_thin", "-Y", -32.00, -10.00, -0.50, 5.00, 0.80),
    ("minus_x_ports","-X", -18.00,   7.00, -1.40, 6.20, 0.70),
]

# --- snap fit: bead on the lid rim, groove in the base wall.
# Short segments rather than one continuous bead: an 80 mm bead is far too
# stiff to deflect, a 14 mm one snaps with thumb pressure.
SNAP_PROT   = 0.45                # bead sticks this far off the rim face
SNAP_Z      = BASE_H - LIP_H + 0.60   # apex, measured up from rim bottom
SNAP_HALF   = 0.325               # bead half-height, so 0.65 tall overall
# (wall, centre along the wall, length).
# The -Y rim is almost fully consumed: the 2x40 header opening removes it over
# X 0.30..52.30, the switch notch thins the wall to 0.60 over X -48..-36 and
# the microSD zone to 0.80 over X -32..-10 -- a 0.55 groove in either would
# leave 0.05/0.25 mm standing. So -Y gets only two short segments and the
# retention load is carried by +Y and the two ends. V2 used +/-Y only; this
# case is 14 mm longer, so the ends are used too.
SNAP_SEGS = [
    ("-Y", -52.00,  6.00),
    ("-Y",  -5.00,  8.00),
    ("+Y", -40.00, 14.00),
    ("+Y", -12.00, 14.00),
    ("+Y",  16.00, 14.00),
    ("+Y",  44.00, 12.00),
    ("-X",  15.00, 10.00),        # -X rim is notched over Y -17.5..9.5
    ("+X", -12.00, 12.00),
    ("+X",  12.00, 12.00),
]
SNAP_GROOVE_D = 0.55              # groove depth into the 1.60 mm wall
SNAP_GROOVE_PAD = 0.10            # groove is this much taller than the bead

# --- LED light holes: straight through the lid, directly over each LED.
# Three identical 2.10 x 2.11 parts with consecutive LCSC numbers
# (C2874116/7/8), tops at case Z 6.80, i.e. 3.25 mm below the lid.
LED_HOLE_D = 1.20
LED_HOLES = [
    (-26.505,   1.100),           # C2874118
    (-48.450, -18.055),           # C2874117
    (-33.100,  -5.495),           # C2874116
]

# --- lid sleeves: tubes on the lid underside that drop over the pegs
# poking up through the PCB, locating the lid and capping the board.
SLEEVE_ON    = True
SLEEVE_OD    = 5.00               # 4.50 on V2. Must NOT come out tangent to the
                                  # rim inner face at |X| 57.15: at OD 4.20 the
                                  # +X sleeves touched it exactly, and the
                                  # tessellation left 14 open edges (the lid STL
                                  # was not watertight). 5.00 overlaps the rim
                                  # by 0.40 (+X) / 0.21 (-X) -- a real boolean
                                  # union, which meshes closed.
SLEEVE_BORE  = 2.30               # PEG_D 2.00 + 0.30 clearance
SLEEVE_GAP   = 0.10               # sleeve stops this far above the PCB

# --- lid rim notches: (name, x0, x1, y0, y1)
# The rim is the lowest part of the lid. Notching it over the tall -X
# connectors lets the whole case sit lower instead of clearing them with
# the rim. The lid plate above still clears them.
RIM_NOTCH = [
    ("minus_x_connectors", -60.00, -56.90, -17.50,  9.50),
]

# --- lid openings: (name, x0, x1, y0, y1)
LID_CUTS = [
    # PinHeader_2x20, the electrode header. X 1.06..51.86, Y -22.28..-17.20,
    # top Z 14.34 in case frame -- 2.7 mm above the outside of the lid.
    # Its body stops 0.06 mm short of the lid rim's inner face, so the opening
    # has to take the rim with it. The lid keeps a 1.74 mm ledge over the wall.
    ("header_2x40",   0.30,  52.30, -23.60, -16.40),
    # PinHeader_1x02 (X 20.28..22.82) and the two 1x01 pins near +X
    ("header_1x02",  19.60,  23.50,  -3.70,   2.70),
    ("header_1x01a", 52.10,  56.00,  -4.20,  -0.40),
    ("header_1x01b", 51.70,  55.60, -10.90,  -7.10),
    # the two SKRPABE tactile buttons
    ("button_lo",   -56.60, -50.60, -10.30,  -5.50),
    ("button_hi",   -56.60, -50.60,   9.20,  14.00),
]

# --- lid text
TEXT_FONT  = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
TEXT_LINES = ["Cerelog", "ESP-EEG 16CH"]
TEXT_SIZE  = 7.0
TEXT_DEPTH = 0.80                 # engraving depth: half of LID_T
TEXT_CX    = 1.50                  # centre of the free lid area
TEXT_CY    = 13.00                # pushed +Y so no LED hole lands in a letter
TEXT_GAP   = 3.00                 # line spacing

# --- small engraved labels: (text, size, x_centre, y_centre)
# ON / OFF flank the slide-switch actuator, which sits at X -41.96 and
# travels in X. ON is at lower X (the USB-C / battery end of the case).
LABEL_DEPTH = 0.50
LABELS = [
    ("ON",      3.00, -49.00, -21.20),
    ("OFF",     3.00, -34.50, -21.20),
    ("microSD", 3.00, -20.95, -21.20),
]

# --- lid top texture: fine diagonal grooves
TEX_ON      = False               # see README: use a textured build plate
TEX_DEPTH   = 0.25
TEX_WIDTH   = 0.55
TEX_PITCH   = 2.40
TEX_ANGLE   = 45.0
TEX_KEEPOUT = [
    (-10.00, 50.00,   1.00, 23.00),
    (-56.00, -12.00, -23.00, -18.50),
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

def snap_bead(wall, c, length):
    """Triangular bead on the lid rim's outer face, on any of the four walls."""
    import Part, FreeCAD as App
    if wall in ("-Y", "+Y"):
        sign = -1.0 if wall == "-Y" else 1.0
        a_r = sign * (IN_W/2.0 - LIP_CLR)          # rim outer face
        a_t = a_r + sign * SNAP_PROT               # apex, pushed into the wall
        pts = [App.Vector(0, a_r, SNAP_Z - SNAP_HALF),
               App.Vector(0, a_t, SNAP_Z),
               App.Vector(0, a_r, SNAP_Z + SNAP_HALF)]
        d = App.Vector(length, 0, 0)
        off = App.Vector(c - length/2.0, 0, 0)
    else:
        sign = -1.0 if wall == "-X" else 1.0
        a_r = sign * (IN_L/2.0 - LIP_CLR)
        a_t = a_r + sign * SNAP_PROT
        pts = [App.Vector(a_r, 0, SNAP_Z - SNAP_HALF),
               App.Vector(a_t, 0, SNAP_Z),
               App.Vector(a_r, 0, SNAP_Z + SNAP_HALF)]
        d = App.Vector(0, length, 0)
        off = App.Vector(0, c - length/2.0, 0)
    face = Part.Face(Part.makePolygon(pts + [pts[0]]))
    sol = face.extrude(d)
    sol.translate(off)
    return sol

def snap_groove(wall, c, length):
    """Matching groove cut into the base cavity wall."""
    z0 = SNAP_Z - SNAP_HALF - SNAP_GROOVE_PAD
    z1 = SNAP_Z + SNAP_HALF + SNAP_GROOVE_PAD
    if wall in ("-Y", "+Y"):
        sign = -1.0 if wall == "-Y" else 1.0
        a_w = sign * IN_W/2.0                      # cavity inner face
        y0, y1 = sorted([a_w, a_w + sign * SNAP_GROOVE_D])
        return cut_box(c - length/2.0 - 0.40, c + length/2.0 + 0.40, y0, y1, z0, z1)
    sign = -1.0 if wall == "-X" else 1.0
    a_w = sign * IN_L/2.0
    x0, x1 = sorted([a_w, a_w + sign * SNAP_GROOVE_D])
    return cut_box(x0, x1, c - length/2.0 - 0.40, c + length/2.0 + 0.40, z0, z1)

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

    doc = App.newDocument("case_16ch")
    log("=== Cerelog ESP-EEG 16CH case ===")
    log("outer     %.2f x %.2f x %.2f (base+lid = %.2f)"
        % (OUT_L, OUT_W, BASE_H, BASE_H + LID_T))
    log("cavity    %.2f x %.2f, corner R %.2f" % (IN_L, IN_W, IN_R))
    log("PCB sits at Z %.2f .. %.2f" % (Z_PCB_BOT, Z_PCB_BOT + PCB_T))
    log("DIP switch underside at Z %.2f (floor outer face is Z 0.00)"
        % (Z_PCB_BOT - 2.385))

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

    # ---- floor openings for the bottom-side DIP switches
    for name, x0, x1, y0, y1 in FLOOR_CUTS:
        c = cut_box(x0, x1, y0, y1, -1.0, FLOOR_T + 0.01)
        before = base.Volume
        base = base.cut(c)
        log("  floor cut %-13s %.2f x %.2f mm, removed %.1f mm3"
            % (name, x1-x0, y1-y0, before - base.Volume))
    base = base.removeSplitter()

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
    for wall, c_, ln in SNAP_SEGS:
        base = base.cut(snap_groove(wall, c_, ln))
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
    for wall, c_, ln in SNAP_SEGS:
        lid = lid.fuse(snap_bead(wall, c_, ln))
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
    y_cur = TEXT_CY + total_h / 2.0 - TEXT_SIZE
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

    for nm, sh in (("case_16ch_base", base), ("case_16ch_lid", lid)):
        m = Mesh.Mesh()
        m.addFacets(sh.tessellate(0.05))
        p = os.path.join(STL_DIR, nm + ".stl")
        m.write(p)
        log("wrote %s  (%d facets)" % (p, m.CountFacets))

    doc.saveAs(os.path.join(FCSTD_DIR, "case_16ch.FCStd"))
    log("wrote case_16ch.FCStd")

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
                  FLOOR_CUTS=FLOOR_CUTS,
                  DIP_SWITCHES=[["DHA-08TQR",    -7.995,  3.295, -11.616, -3.516],
                                ["DHA-08TQR001", 26.205, 37.495, -11.616, -3.516]],
                  DIP_BOTTOM_Z=Z_PCB_BOT - 2.385,
                  BAD_MODELS=["530480210 (height wrong)", "SOLID", "SOLID001", "SOLID002"])
    with open(os.path.join(DESIGN_DIR, "case_16ch_params.json"), "w") as f:
        json.dump(params, f, indent=2)
    log("wrote case_16ch_params.json")
    log("OK")
except Exception:
    log(traceback.format_exc())
