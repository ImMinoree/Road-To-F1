# Full-pace AI and tire-wall gap repair

Implemented in /Game/RoadToF1/Maps/DesertKarting_Visual. No commit or push by this task.

## AI maximum-speed pursuit
Cached a separate curvature/backward-braking speed ceiling alongside the conservative forward acceleration profile. On a settled clear straight, AI uses that ceiling and requests the full 70 km/h target where braking distance permits, removing unnecessary exit-ramp and personality lifting. Traffic, surface grip, steering-path curvature, corner braking and recovery caps still apply. Eligibility requires no committed maneuver/overlap, a clear lead gap, good grip, small tracking error and gentle path/road curvature. Existing corner behavior and personalities remain.

Changed classes: FKartAITrackPlan (KartAITrackPlan.h/.cpp) and UTrackRacingAI (TrackRacingAI.cpp). The default AI cap remains 70 km/h and Pro difficulty. No engine force, drag, tire forces, player cap/input, race-start or circuit geometry changes.

With the current 1000 N motor, 165 kg mass, drag 0.32/s and 15 N rolling resistance, the simple flat straight-line equilibrium estimate is (1000-15)/(165*0.32)*3.6 = 67.16 km/h. Tire forces and corners can reduce it further. Therefore 70 is a requested ceiling, not a promise that this powertrain can attain it. No hidden engine boost was added.

## Tire walls
Reused /Game/RoadToF1/Trackside/TireBarriers/Meshes and the existing FT_TireBarrier_Black/Red instancing assets. No tire mesh/material/LOD reimport or asset changes. Continuous wall contours derive from the actual asphalt/curb mesh footprints and existing runoff outline; thin decorative runoff-strip holes are excluded. The wall follows approximately the existing placement line, with rounded caps at narrow infield tips instead of skipping long runs. All short valid sections are retained. Ground height uses a small swept probe to catch thin surfaces; eight points on the hollow tire contact rim validate support. Small bounded terrain detours retain asphalt and neighboring-tire clearance.

Original instances 10,713; final **11,004**, an increase of **291**. Same two HISM groups, three-high red/black stacks. Eight continuous sections replace fifteen previous sections. Kept the two existing service crossing locations, producing openings on each side (66 omitted columns). One fixed fixture and one unsuitable ground placement remain omitted. These are individual columns, not long unguarded stretches. Largest centre spacing inside a continuous section is 94.7 cm (clear tire-to-tire gap approximately 39.7 cm), smaller than the kart's 120 cm collider width. No claim of perfectly touching tires everywhere.

Saved/reloaded the target map and verified all 2264 lane/grid sweeps match the baseline: 8 existing hits, zero new hits. All eight sampled wall sections block the expected collision query. Existing actors, other foliage, lighting and camera placement are preserved. Tire asset, physics, player-pawn and config hashes are unchanged. Original map/source checkpoint is in Checkpoint/; account for subsequent edits before restoring it.

## Combined race validation
Actual headless PIE, ten karts, 150 simulated seconds, real 240 Hz tire simulation; existing opt-in automated reference player. One authoritative lights-out event. All nine AI completed lap one. Fastest AI 92.15 s; reference player 103.90 s. 0 collisions, 0 polygon-corridor boundary events, 17 confirmed position exchanges. Total brief low-speed flags 0.250 s, not prolonged immobilization. Both final placement and race editor processes exited zero. This is a focused normal-grid test, not proof across all grid orders or 20-kart stress.

Against the previous recorded ten-kart configuration (same 70 km/h governor), full-throttle sample share changed from 46.21% to 46.76%; samples above 65 km/h from 0.316% to 0.402%. Peak remained 65.42 km/h. Near-70 target share changed from 11.32% to 11.15%, and above-60 share from 8.94% to 8.61%. The overall gain is modest; changed walls/traffic confound attribution, and not every speed statistic increased. The policy pursues available speed without claiming an unmeasured top-speed increase.

AI tick mean 0.239 ms, observed maximum 16.166 ms during the test; no rendered frame-rate or draw-call benchmark was captured. Same instancing groups and assets, with 2.7% more tire instances. Intermediate failed contour placements were rejected or rolled back before accepting the final layout; they are not final evidence. Earlier offscreen shutdown failures do not apply to the final successful runs.

Valid matched screenshots are in BeforeAfter.html; final aerial is all_repaired_edges.png. All six comparison PNGs passed signature, chunk CRC and pixel-stream decompression checks. Final screenshot files: before_gap_west00000.png, after_gap_west00005.png, before_gap_hairpin00000.png, after_gap_hairpin00005.png, before_gap_sweeper00000.png, after_gap_sweeper00005.png.

## Play
Open Road_To_F1_New.uproject, load /Game/RoadToF1/Maps/DesertKarting_Visual and press Play. Existing controls and race start remain. No diagnostic command-line flags are needed for normal play.

Repeatable tools: tire_gap_geometry.py (Blender source export), tire_gap_contours.py (free Shapely dependency in isolated temporary folder), tire_gap_apply.py (Unreal placement/validation), full_pace_race_test.py (combined race). Raw evidence: validation.json, verification.json, pace_comparison.json and Race/after.json/telemetry.csv.
