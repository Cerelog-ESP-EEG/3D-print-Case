# 16CH PCB — measured geometry

Source: `Case files FreeCAD/16ch_step.step` (KiCad STEP export, 224 solids).
All values in mm, extracted via FreeCAD headless by `tools/measure_board.py`;
raw output in `16ch_raw_measurements.txt`. Board origin is at the PCB center.

## Board

| Property | Value |
|---|---|
| Outline | 116.50 x 46.87 (rounded rect) |
| Extents | X -58.25..58.25, Y -23.43..23.43 |
| Thickness | 1.51 |
| Corner radius | 3.00 (4 arcs + 4 lines, clean outline) |
| Top face area | 5391.6 mm2 |

## Mounting holes — D = 2.20 (M2 clearance)

| # | X | Y |
|---|---|---|
| 1 | -54.859 | -19.766 |
| 2 |  55.050 | -19.766 |
| 3 | -54.859 |  19.501 |
| 4 |  55.050 |  19.501 |

NOTE: not symmetric. X spread is 0.19, Y spread 0.265. Standoffs use these
exact coordinates, not a mirrored pattern.

## Vertical envelope

| | Z |
|---|---|
| Highest point (pin headers) | +10.135 |
| PCB top | +1.510 |
| PCB bottom | 0.000 |
| Lowest real point (DHA-08TQR DIP switches) | -2.385 |
| Lowest modelled point (unidentified SOLID, bogus) | -4.206 |
| Total real stack | 12.52 |

## Below-board protrusions (these drive standoff height)

| Part | Z min | Footprint |
|---|---|---|
| **DHA-08TQR** (DIP switch) | **-2.385** | X -8.00..3.30, Y -11.62..-3.52 |
| **DHA-08TQR001** (DIP switch) | **-2.385** | X 26.21..37.50, Y -11.62..-3.52 |
| PinHeader 2x20 | -1.405 | X 1.06..51.86 |
| PinHeader 1x02 / 1x01 x2 | -1.405 | various |
| unnamed solids `16chpcbcad 1.211..216` | -1.185 | X 20.8..49.7, Y -14.95..-12.72 |
| 530480210 battery conn | -0.611 | X -58.13..-52.62 |
| C_0402 (one bottom-side cap) | -0.585 | X 41.43..42.43 |
| SOLID (UNIDENTIFIED, bogus) | -4.206 | X -2.12..2.12, Y -4.53..0.98 |

The two DHA-08TQR are 8-position DIP switches mounted on the **underside** of
the board. They set `BOSS_H` and each gets a through-opening in the case floor.

## Components requiring wall openings

| Part | Function | Edge | Overhang | Z range |
|---|---|---|---|---|
| TYPE-C-16PIN-2MD-073 | USB-C | -X | 0.15 inside | 0.77..4.93 |
| 530480210 | battery (PicoBlade) | -X | 0.13 inside | -0.61..5.20 |
| MK-12C02-G020 | slide switch | -Y | 0.36 PAST edge | 1.10..3.00 |
| TF-SMD_TF-01A | microSD | -Y | 0.56 inside | 0.85..3.43 |

## Components requiring top access

| Part | Function | Position | Z top |
|---|---|---|---|
| PinHeader 2x20 | electrode header | X 1.06..51.86, Y -22.28..-17.20 | 10.135 |
| PinHeader 1x02 | | X 20.28..22.82, Y -3.04..2.04 | 10.135 |
| PinHeader 1x01 x2 | | X 52.38..55.29, Y -10.24..-1.03 | 10.135 |
| SKRPABE010 | tactile button | X -55.93..-51.23, Y -9.65..-6.12 | 4.095 |
| SKRPABE011 | tactile button | X -55.90..-51.20, Y 9.85..13.38 | 4.095 |

## Components requiring bottom access

| Part | Function | Position | Z range |
|---|---|---|---|
| DHA-08TQR | 8-pos DIP switch | X -8.00..3.30, Y -11.62..-3.52 | -2.385..-0.085 |
| DHA-08TQR001 | 8-pos DIP switch | X 26.21..37.50, Y -11.62..-3.52 | -2.385..-0.085 |

## LEDs (lid light-pipe holes)

Same three LCSC parts as V2, 2.10 x 2.11, tops at Z 2.595.

| Part | Centre |
|---|---|
| C2874118 | (-26.505, 1.100) |
| C2874117 | (-48.450, -18.055) |
| C2874116 | (-33.100, -5.495) |

## Change vs V2

- Board grew: 98.80 x 42.75 -> **116.50 x 46.87** (+17.70 x +4.12)
- ADC: **two** ADS1299-6PAG (was one) -> 16 channels
- Electrode header moved from the **+X edge** to the **-Y edge**, and grew
  from 2x12 to **2x20**. This is the single biggest case change: the lid
  opening for it has to cut through the -Y lid rim over 52 mm.
- **Two DHA-08TQR moved to the underside of the board.** On V2 the single
  DHA-08TQR was top-side at the +X edge with a wall opening. They are now
  8-position DIP switches under the board and need floor openings.
- MCU, charger, LDO, charge pump, microSD, buttons, slide switch, battery
  connector, LEDs: all unchanged from V2.
- Case grew: 102.60 x 46.55 x 11.35 -> 120.30 x 50.67 x 11.65

## No copper exported

224 solids: board outline + component bodies only. No netlist, no reference
designators, no gerbers. Same as the V2 export — which is why ON/OFF polarity
still cannot be derived from this file.
