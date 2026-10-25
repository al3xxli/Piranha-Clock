# V6 checks and their limits

The reports in `validation/` record digital geometry checks; they do not certify physical fit or strength.

- Saved and reopened both Rhino files: 91 unique printable component solids; 340 valid closed meshes in the assembly document including repeated poses/reference hardware; 91 in the print-bed document.
- Eight 240 × 240 mm bed layers, every part included once, 10 mm edge margin, at least 3 mm between unrelated solids, including nested open frames. Tallest part 133.200 mm. All bed STLs reopened with the expected closed positive components.
- Captive tongue export: seven closed components, all grounded, no solid overlap. The moving tab has 0.8 mm clearance in the 22.5° print pose, with a minimum whole-joint gap of about 0.347 mm. All 29 connector/coupon pins have a continuous flat print face and 3 mm print height. Hinge sample: two production sections, grounded and nonintersecting.
- 192 sampled jaw/tongue poses check rigid head parts, custom hubs, pins, tongue, stem and simplified servo case envelopes. Tolerance: 0.05 mm³. Only two explicitly bounded 0.05 mm tongue-root crush ribs are excluded as intentional compression.
- 546 adjacent-hinge checks over 0–45° plus ±1 mm axial retention-displacement checks. These establish geometric freedom/capture, not break-free force, wear or printed reliability.
- Fourteen 3 mm-thick tooth exports and 574 exposed-crown insertion/withdrawal samples. Flexible root barb compression is not simulated.
- Static complete-assembly check excludes only explicit leaf and tongue-root interference ribs. The documented residual contacts are intentional press-fit regions.
- Five simplified free-string/elastic poses; knots, doubled strands, wound string, friction and elastic force are excluded.
- Source rebuild uses local geometry code; no prior-revision cache is required. The V6 sketch includes calibration commands, built-in RTC timing and optional clock/display/piezo support; see validation/firmware.json for compile results and docs/ELECTRONICS.md for wiring.

The CAD solid total changed from 1013.2 to 755.3 cm³, approximately 25.5% less including test pieces. This comparison is not grams or actual slicer usage. The removed sleeve material is now user-cut sheet stock.

Not performed: slicing or G-code review, physical print, fit/retention/torque/fatigue tests, flexure or spring simulation, real servo calibration, electronics bench operation, cardboard buckling or stability tests. Shaft spline counts and tooth profiles remain unconfirmed despite user-supplied diameters/heights. Print the fit samples first.
