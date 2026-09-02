# What to print — Cerelog ESP-EEG 16CH case

## Print these two. Nothing else.

| File | What it is |
|---|---|
| `case_16ch_base.stl` | Bottom half. Walls, floor, 4 press-fit pegs, all port openings, 2 DIP switch holes, mode legend on the outside face. |
| `case_16ch_lid.stl`  | Top half. Engraving, LED holes, snap beads, 4 sleeves. |

Assembled size **120.30 x 50.67 x 11.65 mm**. No screws, no hardware.

## Orientation — read this before slicing

**Base:** floor flat on the bed, walls up. This is how it exports. No supports.

**Lid: FLIP IT 180 degrees.** The STL exports with the rim and sleeves pointing
*down* (STL spans Z 5.81..11.65). If you drop it straight onto the bed the
slicer balances it on four sleeves and prints the plate in mid-air.

Rotate 180 degrees about X so the **engraved top face lies on the bed** and the
rim and sleeves build upward. Then there are no overhangs anywhere and no
supports are needed.

Bonus: a **textured PEI sheet** puts a moulded-grain finish on the lid top,
which is the face you look at. That is the intended finish — the texture is
deliberately not in the geometry.

## Settings

- Nozzle 0.4, layer 0.2. Nothing here needs finer.
- **No supports on either part.**
- Walls are 1.60 mm (4 perimeters). Locally 0.60-0.80 mm at the switch,
  microSD and -X ports — do not let the slicer gap-fill those away.
- Bridges in the base: the microSD opening (18.5 mm) and the two DIP switch
  floor holes (12.90 mm each, but these are in the first layers over open air
  below — they are plain holes, nothing to bridge). Slow the microSD layer down.
- The switch opening is cut open to the top of the wall, so it needs no bridge.
- 3-4 perimeters, 20-30% infill. Material is not critical; PETG or ABS if the
  snap needs to survive repeated opening, PLA is fine otherwise.
- The base is 120.30 mm long — check it fits your plate in the orientation you
  want. It does not fit diagonally on a 120 mm bed with a brim.

## Assembly

1. Drop the PCB straight down onto the four pegs in the base. It seats on the
   3.00 mm shoulders; the pegs pass through the 2.20 mm mounting holes.
   The slide switch overhangs the board edge by 0.36 mm, so its slot is cut
   open all the way to the top of the wall to let the board drop in vertically.
2. Check the two DIP switches drop into their floor openings without touching.
   There is 0.80 mm of clearance on every side.
3. Press the lid on. The four sleeves swallow the protruding pegs, and nine
   snap beads — 4 on +Y, 2 on -Y, 2 on +X, 1 on -X — click into grooves in the
   base wall. The -Y wall carries only two because the electrode header opening
   removes the rim over 52 mm of it.
4. To open: pull from a short end. The snaps are 0.25 mm engagement, split into
   6-14 mm segments so they release without tools.

## The DIP switches

Both `DHA-08TQR` 8-position switches face **downward, out through the base**.
Their openings are 12.90 x 9.70 mm.

The outside of the base is engraved either side of the openings, 0.50 mm deep
into the 1.20 mm floor:

```
   connector edge (electrode header / power switch / microSD)
   ------------------------------------------------------------
                                                  |
     D M                                          v
     i o      [ SW1 ]          [ SW2 ]           S M
     f d                                         R o
     f e                                         B d
      ^                                          1 e
      |
```

Both legends are **rotated 90 deg**, so the arrows run along the axis the
DHA-08TQR actuators actually travel (8 actuators in a row along the long axis,
each sliding across it). `Diff Mode` is on the -X side, `SRB1 Mode` on the +X
side.

With the case rolled over, **`Diff Mode` points toward the connector edge** —
the edge carrying the electrode header, power switch and microSD — and
**`SRB1 Mode` points toward the opposite edge**. These were reversed on the
first print; flip them again by swapping the two signs in `BOT_GROUPS`.

Text is **3.40 mm**. It was 2.60 on the first print, where Arial Bold strokes
come out ~0.45 mm — about one 0.4 mm extrusion, which prints mushy. At 3.40
the strokes are ~0.59 mm. V2's panel labels are 3.00 for comparison.

The legend is **mirrored**, so it reads correctly when you roll the case over
about its long axis — the way you would naturally turn a 120 mm case to reach
the switches. `SRB1 Mode` is then on your right. Each group is 6.9 mm clear of
its opening.

The switch bodies sit **1.82 mm inside** the opening — they are not flush with
the outside of the case. Set them with a pen tip or a small screwdriver. This
is a geometric consequence of keeping 1.60 mm of clearance under the header
pins; see `../design/OPEN_ITEMS.md` item 1 for the exact trade and the
one-constant change if you want them proud instead.

## Before you print a second one

- **ON / OFF may be backwards.** The labels come from the switch actuator's
  position and travel axis. The STEP carries no electrical data. Meter it.
- **The power switch actuator does not reach the outside face** — it passes the
  board edge by only 0.36 mm, less than V2's 1.00 mm. It needs a printed slider
  cap, which does not exist yet.
- **Caliper the DIP switch height** on a real board. At 2.385 mm modelled, it is
  now the part that sets the standoff height.

## Known-bad data in 16ch_step.step

The same wrong models as the V2 export, deliberately ignored:

- `530480210` battery connector — height is wrong.
- `SOLID`, `SOLID001`, `SOLID002` — unnamed, claim to hang 4.21 mm below the
  board. Confirmed not real.

If either turns out to be genuine, the case height and floor need revisiting.
