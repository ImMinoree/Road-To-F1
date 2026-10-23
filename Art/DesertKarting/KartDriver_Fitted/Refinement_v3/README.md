# Seated recline v3

Open `Kart_With_MakeHuman_Fitted_v3.blend` at frame 1. This is a separate editable version of the latest v2 scene. The source scene is untouched.

The torso now leans approximately 15 degrees backward rather than forward. The pelvis is reoriented independently from the lumbar spine, with a small rearward adjustment along the seat. The head remains upright and forward-facing. Shoulder adjustment maintains approximately 23–24 degrees of elbow bend. Both wrist and ankle positions are retained from v2, preserving the existing wheel grip and pedal alignment.

All original mesh geometry, skin weights, material assignments, the rest skeleton, and every kart object transform—including the refined tank—are unchanged. The saved pose is a new action, `Kart | supported recline v3`. No model was replaced or rebuilt. `validation_final.json` records preservation checks, source hash, reach errors, and collision checks.

`reclined_front.png`, `reclined_side.png`, and `reclined_three_quarter.png` are genuine Cycles renders of the saved scene. `comparison_*.png` places the matching v2 render on the left and v3 on the right.

## Remaining limitations

This is an improved recline, not a complete collision-free seating solution. The lower back sits closer to the seat, but the entire back still does not contact its steeper rake. The sampled back landmarks nearest the seat are approximately 10 mm from its sheet; wider lower-back regions remain farther away. A full seat-angle recline conflicts with the unchanged control reach and relaxed bent-arm requirement. The pose was not forced by stretching bones or changing weights.

Existing garment/seat-rib/bodywork and shoe/chassis/axle/hoses contacts remain. Their exact triangle-pair counts before and after are in `validation_final.json`; these counts are surface-intersection diagnostics, not penetration-depth measurements. Small clothing/bodywork contact counts change with the pose, so no blanket claim of zero new clothing clipping is made. The tank and wheel remain clear of the driver.

The original kart, v2 tank placement, Unreal assets, gameplay and collision assets are untouched. No racing suit, helmet, FBX export, push, or merge was started.
