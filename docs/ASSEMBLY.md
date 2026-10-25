# V6 assembly — printed retention throughout

Use V6 parts together. Directions use head-local +Y forward, +Z up, X left/right; the head datum is 265 mm above the bottom rim. The assembled Rhino file shows the installed positions; the print-bed file is for manufacturing.

## Fit and base

1. Complete the coupon checks in [PRINT_BEDS.md](PRINT_BEDS.md) and [CUSTOM_HUBS.md](CUSTOM_HUBS.md). Clean the printed running surfaces and slots without removing snap shoulders or hinge stops. To release a push pin, compress its split tip from the far side and push it back; avoid levering on delicate shells.
2. Cut the sleeve and optional floor/soil inserts using [SLEEVE.md](SLEEVE.md). Seat the bottom floor on C09's inside lip. Insert the electronics into C10's edge rails, then attach C10 to C09 with R01–R03. Board outlines are nominal envelopes; adjust nonconductive cardboard edge shims if the actual breakout differs. Keep rails/shims clear of components and solder joints.
3. Fit the sleeve into C09. Insert C15 from outside the front opening, C16/C17 from inside, and R10/R11 from the rear clamps toward the bezel. Fit the display and D01/D02 edge inserts. Sleeve wall stiffness and clamp grip must be checked on the actual sheet material.
4. Attach C11 to B01 using R04–R06 from underneath. Attach the C12 stem foot to C11 with R07–R09. Feed wires through the hollow stem, then seat the top rim onto the sleeve. Use folded cardboard shims to obtain a firm removable friction fit. Fit C13/C14 leaves into the stem's split-tang sockets. Support the assembly by the rigid base during handling.
5. Attach C04 to the stem with R15–R17, inserted downward from the head. Install MG995 in C04 and press S01 across the case into its channels. Align the shaft with the opposite upper bearing before installing the carrier; the servo reference axis is Y=-50, Z=8. Verify the actual case is firmly retained without crushing it.

## Both moving jaws

1. Install the MG90S into the lower-jaw cradle, shaft pointing right, and press S02 into its retaining channels. Its local axis is Y=-13, Z=-19.8. Leave a flexible wiring loop at the jaw pivot.
2. Fit G02 to the inside of the lower jaw's left arm with R24–R26. The three smaller pins have 3.6 mm shanks. The toothed quadrant points upward at rest. Insert lower pivots R22 on the right and R23 on the left through the jaw, sector and stationary frame as shown in the assembled file. The pivot pins capture the jaw without clamping its running surfaces.
3. Press the chosen MG995 custom insert into G00's hex socket and onto the unloaded, calibrated servo shaft. G00 includes the upper carrier, pinion and spacer as one print. Fit the upper right pivot R21. At the closed datum, the upper pinion tooth points toward the lower sector's upward gap. With the drive disconnected, move the upper carrier through its 50° range: the lower jaw should turn oppositely by 12.5°.
4. Attach C18 to C04 using R27/R28. Its internal thrust pad is the MG995 axial keeper; check that the upper carrier turns freely while staying captured. The cover is fixed while both jaws move. There is no separate upper-jaw hard stop or counterbalance; establish the servo endpoints unloaded.
5. Fit the teeth as described in [TEETH.md](TEETH.md), then attach C01 to G00 with R18–R20 after the tongue has been tested. The lips remain slightly parted around the fangs at rest.

## Captive tongue and drum

1. Print `Tongue_Print_in_Place.stl` as one assembly. Gently free all six hinges and check each from straight to 45° upward curl. No loose hinge axle is inserted. The papillae and larger 2.2 mm cord guides face up; smaller 1.6 mm pull-string guides face down.
2. Pin A00 onto the lower jaw with R12/R13. Slide A01's split rectangular root into the saddle until the back stop seats; the small interference ribs provide the removable grip. Do not bend the flesh to force an over-tight root.
3. Install the chosen small spline insert in A08 and seat it on the unloaded/calibrated MG90S. Attach A09 with R14 after placing the drum. A09 provides the guide and axial keeper. Confirm the drum turns freely without slipping off its shaft. The drum, root and servo all move with the lower jaw.
4. Thread 0.4–0.6 mm nonstretch braided line, starting with at least 500 mm. Anchor it in A08's tie hole, leave a partial wrap at the curled position, pass through A09 and every underside tongue tunnel, then tie a stopper beyond A07. Winding the drum must shorten the underside path and straighten the tongue. Keep the string in a single layer on the drum.
5. Use six separate soft round elastic links, nominally 0.8 mm, one across each hinge. Each runs through the upper tunnel of the preceding section and the next section, with stopper knots at the two outer ends. Intermediate tunnels carry two opposing strands. Start with about 80 mm per link and leave adjustment tails. Bulky flat bands will not fit the guides.
6. Hold a joint at its curled stop and shorten its elastic just enough for reliable return. Match the six tensions. Pull the underside string gently by hand with the jaws open; the tongue should unroll forward. Release slowly and confirm all hinges return completely before closing the head. Gravity assists deployment and opposes return.

The nominal 23.0 mm pull requires 131.7° drum rotation at a 10 mm effective string radius. Aim initially for less than about 4 N hand pull (0.04 N·m at the drum); this is a tuning target, not a simulated force or established servo margin. Free stiff hinges and reduce excess elastic tension before powered testing. The animation simplifies the six elastic links and assumes equal joint angles; a physical chain may move unevenly.

## Commission and finish

Follow [ELECTRONICS.md](ELECTRONICS.md). Begin with the skull removed, correctly installed keepers, slow travel and no automatic hourly cycles. Verify complete tongue return before closing. Paint the red skin and pale plaques, pink lips/tongue and green stem after fitting. The surface relief is actual geometry; rendered mottled colour is not automatically printed by a single-material printer. Keep paint off teeth roots, spline bores, hinge gaps, gear teeth, stops and string guides. Repeat checks after finishing.

## Push-pin map

The shank has two flat sides: 4 × 3 mm for most pins and 3.6 × 3 mm for R24–R26. Static holes match this profile with 0.25 mm clearance per side. At R21–R23, the fixed frame is keyed while the moving jaw/carrier holes remain round at 4.5 mm to preserve rotation. Grip is the retained stack length, excluding the head and split nose. `NZ` means insert downward. Detailed origins and connected part IDs are in `validation/press_fit_joints.json`.

| Pin | Connection | Grip, mm | Insertion axis |
|---|---|---:|---|
| R01 | Bottom tray to rim 1 | 7.8 | Z |
| R02 | Bottom tray to rim 2 | 7.8 | Z |
| R03 | Bottom tray to rim 3 | 7.8 | Z |
| R04 | Top support to rim 1 | 5.2 | Z |
| R05 | Top support to rim 2 | 5.2 | Z |
| R06 | Top support to rim 3 | 5.2 | Z |
| R07 | Stem foot 1 | 9.4 | Z |
| R08 | Stem foot 2 | 9.4 | Z |
| R09 | Stem foot 3 | 9.4 | Z |
| R10 | Display sleeve sandwich 1 | 23.9 | Y |
| R11 | Display sleeve sandwich 2 | 23.9 | Y |
| R12 | Tongue saddle 1 | 7.7 | Z |
| R13 | Tongue saddle 2 | 25.7 | Z |
| R14 | Tendon guide | 7.4 | Z |
| R15 | Head frame to stem 1 | 19.0 | NZ |
| R16 | Head frame to stem 2 | 19.0 | NZ |
| R17 | Head frame to stem 3 | 11.0 | NZ |
| R18 | Skull to carrier 1 | 16.0 | Z |
| R19 | Skull to carrier 2 | 16.0 | Z |
| R20 | Skull to carrier 3 | 9.4 | Z |
| R21 | Upper right free-running pivot | 15.0 | X |
| R22 | Lower right free-running pivot | 15.0 | X |
| R23 | Lower left free-running pivot | 21.4 | X |
| R24 | Sector to jaw 1 | 12.4 | X |
| R25 | Sector to jaw 2 | 12.4 | X |
| R26 | Sector to jaw 3 | 12.4 | X |
| R27 | Removable cheek 1 | 27.0 | X |
| R28 | Removable cheek 2 | 27.0 | X |
