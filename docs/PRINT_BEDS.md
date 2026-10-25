# Printing V6

Open `cad/Piranha_Clock_V6_Print_Beds.3dm`. Each BED layer is one 240 × 240 mm plate, with one selectable group and a matching named top view. The separate guides layer is locked and must not be exported. Select a BED group and Export Selected as STL, in millimetres. The pre-exported files in `print_beds/` already use each bed's local origin and are the quickest route to a slicer.

| Bed | Contents | Closed components | Tallest, mm |
|---|---|---:|---:|
| 01 | Fit samples, flat pins and cheek | 46 | 34.0 |
| 02 | Upright hinges, drive and open tray | 18 | 36.0 |
| 03 | Stem and structural mounts | 6 | 133.2 |
| 04 | Open top support and leaves | 3 | 25.0 |
| 05 | Lower jaw | 1 | 55.4 |
| 06 | Upper head | 1 | 74.6 |
| 07 | Bottom rim and upper teeth | 9 | 14.0 |
| 08 | Top rim and lower teeth | 7 | 20.0 |

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
