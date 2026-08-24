# v2 PCB — measured geometry

Source: `v2_step.step` (KiCad STEP export, 236 solids). All values in mm,
extracted via FreeCAD headless. Board origin is at the PCB center.

## Board

| Property | Value |
|---|---|
| Outline | 98.80 x 42.75 (rounded rect) |
| Extents | X -49.40..49.40, Y -21.38..21.38 |
| Thickness | 1.51 |
| Corner radius | 3.00 (4 arcs + 4 lines, clean outline) |
| Top face area | 4163.8 mm2 |

## Mounting holes — D = 2.20 (M2 clearance)

| # | X | Y |
|---|---|---|
| 1 | -46.27 | -18.79 |
| 2 |  46.37 | -18.61 |
| 3 | -46.33 |  18.75 |
| 4 |  46.40 |  18.38 |

NOTE: not symmetric. Spread is 0.13 in X and 0.41 in Y. Standoffs must use
these exact coordinates, not a mirrored pattern.

## Vertical envelope

| | Z |
|---|---|
| Highest point (pin headers) | +10.14 |
| PCB top | +1.51 |
| PCB bottom | 0.00 |
| Lowest point (unidentified SOLID) | -4.21 |
| Total stack | 14.35 |

## Below-board protrusions (drive standoff height)

| Part | Z min | Footprint |
|---|---|---|
| SOLID (UNIDENTIFIED) | -4.21 | X -2.12..2.12, Y -4.53..0.98 |
| PinHeader 2x12 | -1.41 | X 31.60..36.68 |
| PinHeader 1x01 / 1x02 | -1.41 | various |
| 530480210 battery conn | -0.61 | X -48.88..-43.38 |

## Components requiring wall openings

| Part | Function | Edge | Overhang | Z range |
|---|---|---|---|---|
| TYPE-C-16PIN-2MD-073 | USB-C | -X | 0.15 inside | 0.77..4.93 |
| 530480210 | battery (PicoBlade) | -X | 0.52 inside | -0.61..5.20 |
| MK-12C02-G020 | slide switch | -Y | 0.99 PAST edge | 1.09..3.00 |
| TF-SMD_TF-01A | microSD | -Y | 0.08 PAST edge | 0.85..3.43 |
| DHA-08TQR | connector | +X | 0.95 inside | 1.60..3.90 |
| ESP32-S3-MINI-1-N8 | module (RF keepout) | +Y | 0.40 inside | 2.39..4.15 |

## Components requiring top access

| Part | Function | Position | Z top |
|---|---|---|---|
| SKRPABE010 | tactile button | X -47.08..-42.38, Y -8.23..-4.69 | 4.09 |
| SKRPABE011 | tactile button | X -47.05..-42.35, Y 11.27..14.81 | 4.09 |
| PinHeader 2x12 | electrode header | X 31.60..36.68, Y -14.76..15.72 | 10.14 |
| PinHeader 1x01 x2 | X 26.63..29.67 | +/-Y edge area | 10.14 |
| PinHeader 1x02 | X 12.39..17.47, Y -15.89..-13.35 | | 10.14 |

## Change vs v1

- MCU: ESP32-WROOM-32-N4 -> ESP32-S3-MINI-1-N8
- ADC: ADS1299-6PAG (unchanged)
- NEW: TP4056 charger + LM2664 charge pump + TPS72325 LDO -> battery powered
- NEW: TF-SMD_TF-01A microSD socket
- NEW: 2x SKRPABE010 tactile buttons
- NEW: 530480210 Molex PicoBlade battery connector
- Switch changed: SK22D02L5 -> MK-12C02-G020
- Board shrank: v1 case was 113.23 x 53.98 x 15.00

## No copper exported

Entity census found zero copper layer assignments, no track/via/zone naming,
236 solids. Board outline + component bodies only. No netlist, no gerbers.
