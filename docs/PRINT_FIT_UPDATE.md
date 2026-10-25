# Flat pins and tongue hinge clearance

This updates V6 in place. The user confirmed that the old three-dot round pin hole fitted and that the tongue printed, but its moving stop tab welded to the outer hinge and needed snipping.

## Pins and matching holes

The 28 assembly pins and T02 coupon pin now have two broad, parallel flats. Their head, shank and split nose share a **3 mm print thickness**. Most shanks are 4 mm wide; the three smaller sector pins R24–R26 are 3.6 mm wide. They lie lengthwise in the print layers instead of standing on their heads. This improves the intended load direction relative to the layers, but measured strength and fatigue have not been established.

The successful old 4.5 mm hole around a 4 mm pin corresponds to **0.25 mm clearance per side**. New production holes retain that setting: 4.5 mm wide × 3.5 mm between flats, or 4.1 × 3.5 mm for the smaller sector pins. T01 still has one/two/three dots for 0.15/0.20/0.25 mm per side; three dots now match the production flat profile. Check T01/T02 before committing to all replacement parts because a flat hole can print differently from the earlier round one.

At the three jaw pivots R21–R23, the fixed frame has a keyed hole to hold the flat pin. The rotating jaw/carrier/gear bores remain round, 4.5 mm, so flattening the pin does not lock the jaws. No screw is added.

## Tongue

The tongue retains its **previous side-standing orientation, with hinge axes vertical**, and still prints as one captive assembly. Its maximum print height remains 36 mm. It is now partly curled across the bed: each joint sits at 22.5° during printing, away from its 0° and 45° stops. Keep the supplied relative positions in the slicer.

The earlier straight print pose placed the moving tab against its stop face; other nearby clearances were only 0.1–0.2 mm. The revised recess removes the narrow inner lip, provides 0.8 mm axial space behind the tab, and clears surrounding flesh from the fork. The tab has **0.8 mm minimum clearance in the supplied print pose**. The smallest whole-joint surface gap is about 0.347 mm at the captive bearing, distinct from the larger tab clearance. The bearing's nominal radial clearance remains 0.4 mm. The functional 0–45° stop angles are unchanged.

Print `Hinge_Sample_Print_in_Place.stl` first if you want to check the revised release with minimal material. Keep supports and brim out of the joints. Do not snip the moving tab: it is the motion stop. The updated geometry has been digitally checked but has not yet been physically printed.

For a small first print, use [Bed 00 — fit samples](../print_beds/Bed_00_Fit_Samples.stl). It preserves your quick-test export with the revised flat pins and hinge. These pieces also appear on the full Bed 01; print one set unless you want spares.

## What needs reprinting

- All connector pins R01–R28 and the T01/T02 flat-pin fit set.
- Parts with changed printed mounting holes: **B01, C01, C02, C04, C09, C10, C11, C12, C15, C16, C17, C18, G00, G02, A00 and A09**. The new keyed pins require these matching holes for intended retention/alignment; they are not a guaranteed retrofit into old round sockets.
- The full `Tongue_Print_in_Place.stl`, or the two-section hinge sample for a preliminary check. Individual captive tongue sections are not intended to be swapped into an already printed chain.

Teeth, leaves, servo spline inserts, case clips, display shims and the tendon drum have not changed. Firmware and servo travel remain unchanged.

## Print beds

The eight BED layers and matching STLs are regenerated. Your saved jaw, frame, stem, clip, tray and cheek orientations are retained. The cheek is on Bed 01 and the open electronics tray is on Bed 02, as in your saved spatial arrangement. Pins and tongue are repacked for their new footprint; off-bed duplicate test copies are consolidated into the numbered bed set. All parts are grounded at Z=0. Existing nesting is kept where there is at least 3 mm between unrelated solids.

The tallest print is now the stem at 133.2 mm. The lower jaw is 55.4 mm high and upper head 74.6 mm high in your retained orientations. Supports still need inspection in the slicer.

Validation: 91 closed printable components; 29 flat pin/coupon print faces; third-hole clearance measured from CAD at 0.2497 mm; six tab-clearance checks; 546 hinge motion samples; 192 full mechanism poses; five cord poses. See `validation/fit_update.json` and the other reports. These are geometry checks, not physical fit or strength certification.
