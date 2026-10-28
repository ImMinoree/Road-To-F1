# Gloved grip validation

Actual PIE run: 1167 samples. All A–L functional checks passed. The wrist and distal joints of all five fingers on both hands were tracked against the wheel; maximum relative drift was 0.01619 cm. This measures joint alignment rather than certifying every surface intersection.

See hands_center.png, hands_left.png, hands_right.png, cockpit.png and steering_sequence.html for actual Unreal evidence. The glove revision is saved in the editable Blender assembly and both driver skins. The original driver suit still has inherited seam/tailoring limitations. These are modeled game gloves, not photorealistic scanned hands.

Hand structure revision (2026-10-28): outside-to-inside finger wrap, fuller tapered palm, repositioned opposed thumb and wrist. The original steering wheel is preserved. The final runtime log is pie_structure_20261028.log. Imported grip normals retain smooth glove lighting. Original suit seams remain. structure_static_hash_verification.json checks all 18 versioned static kart meshes against this revision's backup. protected_hash_verification.json compares maps and tire sources against the older integration baseline: maps and tire CPP files match; two tire headers differ from that older baseline and were not edited or reverted by this hand revision.
