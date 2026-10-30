Full track-edge tire placement and smoother countdown

Target: /Game/RoadToF1/Maps/DesertKarting_Visual.
10,713 existing-model tires (5,418 black; 5,295 red), 3,571 three-high stacks, 15 retained runs across both full measured track-edge loops. Two reused HISM components; original mesh assets, materials and LODs unchanged. The prior 1,725-tire placement was replaced, avoiding doubled walls. Typical offset is 250 cm beyond the measured asphalt boundary, adapted up to 440 cm where geometry requires it, versus the previous 530–620 cm corner offsets. Walls now occupy the outer runoff strip where needed; asphalt and painted curbs remain clear. Intentional access openings and geometry/structure clearance gaps remain. Both sides were planned around the full circuit rather than only selected bends.

Source meshes and measured boundary samples define the layout. Minimum modeled tire-edge margin beyond asphalt/painted curbs is 35 cm. New columns use five terrain-support traces; uneven or fixed-object overlaps are rejected. Nearby walls are checked for opposing-edge overlap. No track mesh, lighting, input, AI, movement, checkpoints, race-start timing or vehicle assets changed.

Countdown: same authoritative red-light events, descending 5–1 and START. Quintic fade with gentle start/end acceleration, fading through the final 58% of each cue. Removed the scale pulse and hard outline; runtime font rendered at 1.5x resolution and reduced to display size for smoother edges. Warm ivory numerals, restrained sage green START, lighter shadow; START fades over 1.35 seconds. This is presentation only; it never releases the movement gate.

Verification completed: Unreal Editor Development build succeeded. RoadToF1.RaceStart.CountdownPresentation automation test succeeded. Save/reload retained all 10,713 transforms. 2,264 kart-sized route/edge/grid sweeps matched the pre-change baseline exactly, with eight pre-existing outer-edge obstructions and zero new obstructions. Simple tire collision tested in all 15 runs. PIE rendered both readable and late-fading numeral states plus the real first-person driver view. Existing lights-out event released normally. PNG files decoded and were visually inspected. Full-lap driving and a GPU performance comparison were not performed during this pass.

Screenshots: all_track_edges.png; closer_driver_edges00000.png; countdown_readable00000.png; countdown_fading00000.png.
Checkpoint contains the exact prior map and both prior countdown source files. No commit or push was performed for this change.
