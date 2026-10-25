# Custom printed servo hubs

No stock horn or center screw is used by this design. A replaceable hex insert engages the servo shaft and keys into the carrier or drum. The fixed cheek C18 retains the MG995 carrier axially; the A09 fairlead keeper retains the MG90S drum. Install these keepers before operating the connected drives. Their modeled axial running clearance is 0.4 mm. S01/S02 retain the servo cases in their cradles.

## Dimensions and evidence

| Servo | User-reported bare shaft | Model's engagement |
|---|---|---|
| MG995 | 5.5–6 mm diameter; 4 mm exposed height | About 3.5 mm, with 0.5 mm case-face gap; nominal H01 25T / 6 mm trial profile |
| MG90S | 4.5–5 mm diameter; 4.5–5 mm exposed height | About 4.1–4.6 mm, with 0.4 mm case-face gap; nominal H02 21T / 4.8 mm trial profile |

The parenthetical measurements are treated as ranges, not as a verified major/minor spline-diameter pair. Tooth counts, root diameters, flank form, fit class and allowable printed-hub torque are not established. The polygonal trial spline is not a manufacturer-certified spline.

The [TowerPro MG90S page](https://towerpro.com.tw/product/mg90s-3/) gives overall case dimensions but no complete shaft/spline drawing. The [MG995 branded datasheet hosted by Robotistan](https://maker.robotistan.com/wp-content/uploads/2023/10/MG995_Tower-Pro-Datasheet.pdf) also does not define the complete mating spline. The [MG996R page](https://towerpro.com.tw/product/mg996r/) concerns the replacement model and cannot certify the shaft on your MG995. These documents therefore cannot supply the missing fit profile reliably. Screw thread sizes are unnecessary for this screw-free design.

## Fit choices

| IDs | Trial tooth count | Bore diameters, in ID order | Marking |
|---|---:|---|---|
| F11 / F12 / F13 | 25 | 5.60 / 5.85 / 6.10 mm | 1 / 2 / 3 dots |
| F14 / F15 / F16 | 24 | 5.60 / 5.85 / 6.10 mm | 1 / 2 / 3 dots + bar |
| F21 / F22 / F23 | 21 | 4.60 / 4.85 / 5.10 mm | 1 / 2 / 3 dots |
| F24 / F25 / F26 | 20 | 4.60 / 4.85 / 5.10 mm | 1 / 2 / 3 dots + bar |

These counts are alternatives for diagnosis, not verified options for your exact servos. Count the visible shaft teeth if practical; do not force a mismatched tooth count into place. The fit samples have the same hex exterior and engagement length as H01/H02, so a successful sample can replace its nominal insert. Small dots/bar are on the closed end.

With power off, offer a sample straight to the shaft using light finger pressure. It should seat to the intended depth without splitting, deforming shaft teeth, bottoming on the case or rocking. Remove it if it binds. Select the smallest sample that seats without force and has no perceptible rotational play, then test in the carrier/drum with the keeper installed. Do not use pliers, hammering or the servo motor to cut a mismatched profile. Fine FDM spline reproduction may still be inadequate; if all samples fail, revise the profile from the actual shaft rather than enlarging until it slips.

Calibrate the servo unloaded before registering the hub, then install it at the closed/curl datum. Printed insert strength, creep, wear and peak torque capacity have not been tested. Start with the lightest elastic tension that returns the tongue. The custom hub and keeper eliminate assembly screw requirements; they do not eliminate the need for this physical fit test.
