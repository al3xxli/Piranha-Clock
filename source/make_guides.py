"""Write the V6 fabrication handoff from the checked part/bed manifests."""
from pathlib import Path
import json, math

ROOT=Path(__file__).resolve().parents[1]
def put(name,text):
    p=ROOT/name;p.parent.mkdir(exist_ok=True,parents=True)
    p.write_text(text.strip()+'\n',encoding='utf-8')

def main():
    material=json.loads((ROOT/'validation/material_comparison.json').read_text())
    beds=json.loads((ROOT/'validation/print_beds.json').read_text())
    reduction=-material['change_percent']
    put('README.md',f'''# Piranha Clock V6 — press-fit and filament conscious

An MG995 lifts the upper head 50° and gears the lower jaw down 12.5°. An MG90S in the lower jaw pulls a string to unroll a 154 mm segmented tongue; light elastic links curl it back into the mouth. The plump lips, irregular skin relief, tongue papillae and internal 4:1 quadrant gear are retained.

V6 uses printed push pins and keepers, custom replaceable servo spline inserts, one captive print-in-place tongue, fourteen flat snap-in teeth, and two pot rims around a user-cut cardboard or foamcore sleeve. No assembly screws, nuts, metal hinge pins, glue or cable ties are specified. String and elastic still need threading and tying.

**Print-fit update:** the connector pins now print flat with the tested three-dot clearance. The tongue keeps vertical hinge axes, wider tab clearance and a partly curled print pose. See [what changed and what to reprint](docs/PRINT_FIT_UPDATE.md).

![Mechanism animation](images/internal_gears_mechanism.gif)

## Start here

- [Rhino print beds](cad/Piranha_Clock_V6_Print_Beds.3dm): eight 240 × 240 mm BED layers, one group per bed.
- [Assembled Rhino model](cad/Piranha_Clock_V6_Press_Fit.3dm): extended, curled and exposed-mechanism poses. Both documents are Rhino 7 compatible closed **mesh solids**, in millimetres.
- [Eight bed STLs](print_beds/) and [print guide](docs/PRINT_BEDS.md). The tallest part is {beds['max_height_mm']:.1f} mm; check your printer's Z travel.
- [Assembly and string routing](docs/ASSEMBLY.md), [custom hub fitting](docs/CUSTOM_HUBS.md), [flat teeth](docs/TEETH.md), [sleeve cut templates](docs/SLEEVE.md).
- [Materials and electronics](docs/BOM.md), [UNO R4 Minima wiring/calibration](docs/ELECTRONICS.md), [validation limits](docs/VALIDATION.md).

**Print the fit pieces first.** Your measured shaft diameters/heights are incorporated, but spline tooth counts and flank shape remain unconfirmed. The supplied hub profiles are trial fits. Do not force a sample onto a metal shaft or assume a smooth bore establishes a torque-capable connection.

The complete part set uses approximately **{reduction:.1f}% less CAD solid volume** than V5, including the fit samples. This is not a slicer filament estimate; supports, infill, walls and purge change actual usage. The two rings are the printed pot enclosure; the open internal tray and stem support remain structural parts.

![Print bed overview](images/print_beds_overview.png)

The saved meshes, print-bed bounds and sampled rigid motion are digitally checked. The user printed the earlier tongue and confirmed the three-dot pin-hole fit. This updated geometry has not yet been physically printed or load-tested. Hinge release, spline grip, snap durability, sleeve stiffness and elastic return require a prototype build. Use one complete revision; V6 parts are not a drop-in conversion of every V5 joint. This project contains only the current V6 design.

## Rebuild

Install Python 3.12 and `source/requirements.txt`, then run from this directory:

```text
python source/build_segmented.py
python source/validate_motion.py
python source/validate_cords.py
python source/validate_print_features.py
python source/validate_fit_update.py
python source/layout_print_beds.py
python source/sector_report.py
python source/render_segmented.py
python source/render_segmented.py --gif
python source/make_guides.py
```

The default build generates the base and all V6 parts from source, without requiring earlier versions. Previews use Windows Segoe UI. Parameter changes require rebuilding, rechecking and regenerating the beds. Keep the PIP assemblies in their shared print coordinates.

Unofficial fan-made physical prototype inspired by Nintendo's Piranha Plant. This project is not affiliated with Nintendo. No license to Nintendo characters or branding is implied.
''')
    table='\n'.join(f'| {b["bed"]:02} | {b["name"]} | {b["part_count"]} | {b["max_height_mm"]:.1f} |' for b in beds['beds'])
    put('docs/PRINT_BEDS.md',f'''# Printing V6

Open `cad/Piranha_Clock_V6_Print_Beds.3dm`. Each BED layer is one 240 × 240 mm plate, with one selectable group and a matching named top view. The separate guides layer is locked and must not be exported. Select a BED group and Export Selected as STL, in millimetres. The pre-exported files in `print_beds/` already use each bed's local origin and are the quickest route to a slicer.

| Bed | Contents | Closed components | Tallest, mm |
|---|---|---:|---:|
{table}

There are 91 closed components including trial samples. Seven tongue sections form one captive print assembly; the hinge coupon has two. When importing a bed or composite STL, retain the components as one multi-part object and preserve their relative positions. **Disable automatic rearrangement/separation of the tongue and hinge sample.** Do not union their moving components. Every section has its own contact with the bed.

The files provide 10 mm bed-edge clearance and at least 3 mm between unrelated solids. Valid nesting inside open frames is checked using actual solid distances. Teeth intentionally nest inside pot rims. The tongue's interlocking hinge components intentionally have overlapping bounding boxes and a 0.4 mm radial running clearance, with no solid overlap. Brims and supports are not included and must fit within the available gaps.

## First print

The optional `print_beds/Bed_00_Fit_Samples.stl` is the updated small test subset: T01–T05 and R15–R17. It is separate from the eight full-production beds. These pieces also occur on Bed 01, so do not print both sets unless spares are wanted.

Print T01 with T02, T03 with one tooth, the complete `Hinge_Sample_Print_in_Place.stl`, and the relevant F-series shaft samples. These are available on Bed 01; teeth are on Beds 07/08 or as individual STLs. Do this before committing to shells or the complete tongue.

- T01: one/two/three dots correspond to 0.15/0.20/0.25 mm clearance per side around the new flat pin. The successful three-dot setting is now the production fit: 4.5 mm wide and 3.5 mm between flats for the 4 × 3 mm shank. The split nose should compress, pass through and recover.
- T03: one/two/three dots correspond to 0.15/0.20/0.25 mm clearance per side around the flat tooth root. The middle socket matches the model.
- T04/T05: exact production tongue sections 6/7, printed together. Gently free the captive hinge and check the entire 0–45° range. No loose axle is inserted. Preserve the partly curled print pose so the stop tabs stay away from their end faces. Do not scale these parts to tune clearance.
- F11–F26: [shaft fit choices and markings](CUSTOM_HUBS.md). A fine nozzle may be required for spline detail.

## Starting settings and orientation

PETG is a starting choice for clips, pins and tooth roots because these must flex. These are untested starting settings: 0.12–0.16 mm layers; 3–4 walls on cosmetic shells, 5–6 around load-bearing pivots/hubs and locally solid gears, clips and push pins. Use sparse infill only where the slicer shows enclosed bulk. A 0.2 mm nozzle and 0.08–0.12 mm layers are preferable for the small trial spline inserts; a typical 0.4 mm nozzle may not resolve their teeth. Fit and torque tests determine suitability.

The tongue keeps its previous side-standing orientation with all hinge axes vertical. Each joint is printed at 22.5° between its 0° and 45° stops, so the tongue curves across the bed while retaining the same 36 mm height. The moving stop tab has 0.8 mm clearance in this print pose; the smallest complete-joint surface gap is about 0.347 mm at the captive bearing. Keep support and brim out of all captive clearances and cord passages. Inspect unsupported spans in the slicer. Teeth print on a broad flat face, 3 mm thick, without supports. Keep their split roots free of brim and paint. Pins print on a continuous 3 mm broad face, with their length and split nose parallel to the bed. This aligns the pin length with the print layers; physical strength still needs testing. Print the jaw/skull in the provided orientations with selective supports under lips, socket collars and internal overhangs. The cheek, stem flanges, frame and carrier also need local support inspection. The layout is not a claim of support-free printing.

`docs/print_beds.csv` gives each part's orientation/support guidance. `docs/print_parts.csv` lists dimensions. The individual A01–A07 and T04/T05 STLs are intentionally replaced by their composite print-in-place files to preserve capture alignment.

Print colours are optional. Beds 07/08 mix ring and tooth colours; assign slicer parts separately or print the tooth group separately if using one colour at a time. Small fasteners are identified by the bed map and IDs, not embossed numbers. Keep them sorted by grip length.
''')
    put('docs/CUSTOM_HUBS.md','''# Custom printed servo hubs

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
''')
    joints=json.loads((ROOT/'validation/press_fit_joints.json').read_text())
    pins='\n'.join(f'| {j["id"]} | {j["connection"]} | {j["grip_mm"]:.1f} | {j["axis"]} |' for j in joints)
    put('docs/ASSEMBLY.md','''# V6 assembly — printed retention throughout

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
'''+pins)
    put('docs/TEETH.md','''# Fourteen flat removable teeth

U01–U08 fit C01's upper sockets; L01–L06 fit C02's lower sockets. The curved fang silhouette is retained in a flat 3 mm plate. Print the broad face down. Each root is 5 × 3 mm with 7 mm engagement, a flexing center slit and 6.1 mm-wide snap shoulders. The production entry is 5.4 × 3.4 mm, opening into a 6.4 mm retention pocket. No adhesive is specified.

Test one tooth in T03 before the jaws. Its one/two/three-dot sockets have 0.15/0.20/0.25 mm clearance per side; two dots match the production jaw. The root should compress during insertion and recover inside the pocket. This is a design intent, not a measured retention force. If it cracks, jams or pulls out too easily, adjust the root/socket settings and reprint the sample before the jaws. PETG is a starting material for the flexing roots; brittle materials need particular care.

Use the assembled model's exploded-teeth layer to identify the socket positions. IDs increase with the angle around each rim from +X toward -X; upper angles are 5,25,45,65,115,135,155,175 degrees, lower 15,35,55,125,145,165. The roots are rectangular and should not be twisted. Push near the base of the fang along the socket axis. Do not press the sharp tip. For replacement, pull at the base along the same axis while supporting the lip; the inward barb taper permits removal, but repeated removal durability is untested.

The teeth on Beds 07 and 08 nest inside the empty pot rings to reduce bed count. Keep tooth roots free of paint and leave their slits open. No printed part is impact-proof; the separate teeth are replaceable if damaged. These flat roots are not compatible with V5's round D-shaped sockets.
''')
    put('docs/BOM.md','''# V6 materials and components

| Item | Quantity / starting provision |
|---|---|
| MG995 positional servo | 1, user-owned; jaw drive |
| MG90S positional servo | 1, user-owned; tongue drum |
| Arduino UNO R4 Minima | 1 |
| Optional DS3231 RTC breakout | 1 for time retention across power loss; default uses the built-in RTC |
| Optional TM1637 four-digit display | 1; check PCB fit and enable USE_DISPLAY |
| Regulated servo supply | Separate 4.8 V supply, sized for both servos' measured peak current |
| USB power/cable and signal leads | As needed; common ground |
| Optional passive piezo element + 1 kOhm resistor | 1 each; enable USE_BUZZER |
| Nonstretch braided line | 0.4–0.6 mm, at least 500 mm before trimming |
| Soft round elastic | Nominal 0.8 mm; six ~80 mm pieces plus spare |
| Cardboard / curved foamcore | 98 mm-high pot sleeve, plus seam; see cut guide |
| Cardboard floor / optional top infill and shims | User-cut sheet stock |
| Filament | Mechanical parts with flex-capable roots/clips; inspect slicer for actual quantity |
| Optional base ballast | Insulated, secured inside base after checking tipping stability |

Printed components include 28 split push pins, two case clips, 14 flat teeth, two replaceable spline inserts, 12 alternate spline trial inserts and fit coupons. The tongue is one captive assembly of seven sections. Only one fitting insert is installed per servo; unused F-series trials are spares/test pieces. No user-installed screw, nut, washer, metal hinge pin, purchased horn, glue or cable tie is part of V6 assembly.

The pot's continuous wall is sheet material. A printed open tray holds electronics and an open spoke support carries the stem; these are retained to provide a load path. Thin cardboard may need doubled layers and shims. Test rigidity and resistance to tipping with the head fully open and the tongue out before running the mechanism.
''')
    put('docs/MECHANISM.md','''# Mechanism

MG995 directly rotates G00, which incorporates the upper carrier and a 16-tooth pinion. G02 retains the working quadrant of a 64-tooth gear, so its 32 mm pitch radius remains four times the pinion's 8 mm radius. Both gears use module 1, a 25° pressure angle, nominal 0.20 mm pair backlash and 40 mm center spacing. The pinion turns 50° and the lower jaw turns 12.5° in the opposite direction. Removing unused sector teeth does not change the ratio. The full sector hub remains for its pivot and three push-pin connections.

The gears sit inside the head behind fixed removable cheek C18. The two servo cases may remain visible inside the mouth. C18 also retains the upper rotor axially. The MG90S moves with the lower jaw and winds an underside string onto A08. A09 guides that string and retains the drum axially. Neither output uses a stock horn or center screw.

The tongue has seven sections on a 22 mm pitch and six captive hinges. Each hinge permits 0–45° upward curl. An underside tendon straightens the chain, while six light elastic links across its upper side restore the curl. The nominal tendon difference from curled to straight is 22.986 mm; a 10 mm effective drum radius requires 131.700°. Gravity helps extension but must be overcome during return. Joint friction and unequal elastic tension are not represented by the equal-angle model.

The controller opens the jaws, deploys the tongue, chirps, releases the tendon, then closes the jaws. It has no position or force feedback. Full return is a physical tuning requirement before automatic operation. The GIF is a kinematic illustration made from the actual meshes, not a gravity/elastic/contact simulation or proof of reliable operation.

![Gear section](../images/sector_gear_detail.png)
''')
    put('docs/VALIDATION.md',f'''# V6 checks and their limits

The reports in `validation/` record digital geometry checks; they do not certify physical fit or strength.

- Saved and reopened both Rhino files: 91 unique printable component solids; 340 valid closed meshes in the assembly document including repeated poses/reference hardware; 91 in the print-bed document.
- Eight 240 × 240 mm bed layers, every part included once, 10 mm edge margin, at least 3 mm between unrelated solids, including nested open frames. Tallest part {beds['max_height_mm']:.3f} mm. All bed STLs reopened with the expected closed positive components.
- Captive tongue export: seven closed components, all grounded, no solid overlap. The moving tab has 0.8 mm clearance in the 22.5° print pose, with a minimum whole-joint gap of about 0.347 mm. All 29 connector/coupon pins have a continuous flat print face and 3 mm print height. Hinge sample: two production sections, grounded and nonintersecting.
- 192 sampled jaw/tongue poses check rigid head parts, custom hubs, pins, tongue, stem and simplified servo case envelopes. Tolerance: 0.05 mm³. Only two explicitly bounded 0.05 mm tongue-root crush ribs are excluded as intentional compression.
- 546 adjacent-hinge checks over 0–45° plus ±1 mm axial retention-displacement checks. These establish geometric freedom/capture, not break-free force, wear or printed reliability.
- Fourteen 3 mm-thick tooth exports and 574 exposed-crown insertion/withdrawal samples. Flexible root barb compression is not simulated.
- Static complete-assembly check excludes only explicit leaf and tongue-root interference ribs. The documented residual contacts are intentional press-fit regions.
- Five simplified free-string/elastic poses; knots, doubled strands, wound string, friction and elastic force are excluded.
- Source rebuild uses local geometry code; no prior-revision cache is required. The V6 sketch includes calibration commands, built-in RTC timing and optional clock/display/piezo support; see validation/firmware.json for compile results and docs/ELECTRONICS.md for wiring.

The CAD solid total changed from {material['previous_printed_solid_volume_cm3']:.1f} to {material['new_printed_solid_volume_cm3']:.1f} cm³, approximately {reduction:.1f}% less including test pieces. This comparison is not grams or actual slicer usage. The removed sleeve material is now user-cut sheet stock.

Not performed: slicing or G-code review, physical print, fit/retention/torque/fatigue tests, flexure or spring simulation, real servo calibration, electronics bench operation, cardboard buckling or stability tests. Shaft spline counts and tooth profiles remain unconfirmed despite user-supplied diameters/heights. Print the fit samples first.
''')
    # ELECTRONICS.md is maintained alongside the firmware.
    make_templates()

def make_templates():
    for thick in [1,5]:
        radius=77-thick/2;circ=2*math.pi*radius;w=circ+15
        # Seam is at rear; front window is at the middle of the developed sheet.
        center=12+circ/2;hole=radius*math.asin(29/radius)
        shapes=f'<path d="M12 15 H{12+w:.3f} V113 H12 Z" fill="none" stroke="black" stroke-width="0.25"/>'
        shapes+=f'<path d="M{12+circ:.3f} 15 V113" stroke="#567" stroke-width="0.25" stroke-dasharray="2 2"/>'
        shapes+=f'<rect x="{center-27.75:.3f}" y="49" width="55.5" height="31.5" fill="none" stroke="black" stroke-width="0.25"/>'
        for x in [center-hole,center+hole]:shapes+=f'<circle cx="{x:.3f}" cy="64" r="2.25" fill="none" stroke="black" stroke-width="0.25"/>'
        # Interlocking paper seam: three small tongues and their receiving slots.
        for y in [32,64,96]:
            shapes+=f'<path d="M{12+circ+4:.3f} {y-4} h7 v8 h-7" fill="none" stroke="black" stroke-width="0.25"/>'
            shapes+=f'<path d="M19 {y-4.5} v9" stroke="black" stroke-width="0.25"/>'
        shapes+=f'<text x="12" y="9" font-family="Arial" font-size="4">{thick} mm sheet: 98 mm high, {circ:.3f} mm developed circumference + 15 mm seam overlap. Print at 100%.</text>'
        shapes+='<path d="M12 126 h100 m-100 -2 v4 m100 -4 v4" stroke="black" stroke-width="0.25"/><text x="45" y="134" font-family="Arial" font-size="4">100 mm check</text>'
        put(f'templates/Sleeve_{thick}mm_1to1.svg',f'<svg xmlns="http://www.w3.org/2000/svg" width="{w+24:.3f}mm" height="140mm" viewBox="0 0 {w+24:.3f} 140">{shapes}</svg>')
    circles='<circle cx="80" cy="90" r="68.8"/><circle cx="245" cy="90" r="78.5"/><circle cx="245" cy="108" r="32.4"/>'
    for a in [35,145,270]:
        r=math.radians(a);circles+=f'<circle cx="{245+66*math.cos(r):.3f}" cy="{90-66*math.sin(r):.3f}" r="4"/>'
    put('templates/Optional_Floor_and_Soil_1to1.svg',f'<svg xmlns="http://www.w3.org/2000/svg" width="335mm" height="190mm" viewBox="0 0 335 190"><g fill="none" stroke="black" stroke-width="0.25">{circles}</g><g font-family="Arial" font-size="4"><text x="12" y="12">Floor: diameter 137.6 mm; use about 2 mm sheet</text><text x="170" y="12">Optional top infill: diameter 157 mm; stem cutout offset 18 mm</text><text x="12" y="181">Cut and trim to fit. Print at 100%. Ring diameters provide scale checks.</text></g></svg>')
    put('docs/SLEEVE.md','''# User-cut pot sleeve

Only the top/bottom rings are printed as the pot wall. The 98 mm-tall sleeve seats from world Z=3 to Z=101 between the rings. Channels run from radius 72 to 77.4 mm: 5.4 mm radial space. The nominal sleeve outer diameter is 154 mm. C11's open support and C10's open tray remain printed load-bearing parts.

Use the full-size SVG matching your sheet thickness: [1 mm cardboard](../templates/Sleeve_1mm_1to1.svg) or [5 mm foamcore](../templates/Sleeve_5mm_1to1.svg). These are wide sheets, so tile in your print application or trace dimensions manually. Print at **100%**, with no fit-to-page scaling; verify the 100 mm check line. Black lines cut; dashed line marks the start of the 15 mm seam overlap. Front window and holes are centered opposite the rear seam. The three small U-shaped flaps at the overlap tuck through the receiving slits to avoid adhesive. Test this seam on a scrap; trim/flap length depends on material compression. Thick foamcore may need its seam area locally thinned to interlock.

For thickness t, the centerline developed circumference is `2*pi*(77-t/2)` mm: 480.664 mm for 1 mm sheet or 468.097 mm for 5 mm sheet, plus the 15 mm seam overlap. The display opening is 55.5 × 31.5 mm in the flat template, with its lower edge 32.5 mm above the sleeve bottom. Two 4.5 mm clearance holes sit 49 mm above the bottom, at approximately ±29.7 mm arc distance from the front center. The slightly wider flat window accommodates bending. Dry-fit the bezel and mark final holes against the real parts before cutting finished material.

Curve the sheet with its outer face continuous. Foamcore needs closely spaced scores or kerfs on the inside to bend; make a scrap bend first. Thin cardboard requires folded edge shims to fill the ring channels and resist ovalizing. Double-wall cardboard or a braced sleeve will generally be stiffer than thin single sheet. The head load passes through the open upper support, top rim and sleeve to the bottom rim; sleeve stiffness is part of the structure.

[Optional floor/top infill template](../templates/Optional_Floor_and_Soil_1to1.svg): the 137.6 mm floor rests on the bottom lip; approximately 2 mm sheet fits below the tray. The 157 mm top infill covers the spokes around the offset stem; trim around posts/wires as needed. These are cosmetic/non-electrical sheet inserts, not replacements for C10/C11. Route leads through the rear opening and stem.

Check the friction fit, seam and resistance to tipping with the tongue fully extended. Add secured insulated ballast or internal cardboard bracing if needed. Cardboard compression, humidity and repeated use have not been physically tested. Do not lift the completed clock by its plant head.
''')

if __name__=='__main__':main()
