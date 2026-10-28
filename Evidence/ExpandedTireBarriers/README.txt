Expanded tire barriers — DesertKarting_Visual

Saved target: /Game/RoadToF1/Maps/DesertKarting_Visual
Reused meshes: /Game/RoadToF1/Trackside/TireBarriers/Meshes/SM_TB_Tire_Black and SM_TB_Tire_Red.
Reused foliage: /Game/RoadToF1/Trackside/TireBarriers/Instancing/FT_TireBarrier_Black and FT_TireBarrier_Red.
No imports, asset/material changes, C++ edits, physics/AI changes, lighting changes or commits.

575 three-high columns; 1,725 tires across the same two HISM components. Added 1,581 tires (786 black, 795 red). All original 144 transforms retained.
Retained continuous wall runs: corner 1: 213 columns; corner 2: 26; corner 3: 44; corner 4: original 24 unchanged; corner 5: 24; corner 6: 51; corner 7: 193. Six corner areas expanded, seven retained sections overall.
Columns follow measured asphalt edges and original source road/curb/runoff BVHs. Nominal new pitch 54.7 cm, tire diameter 55 cm, height 55.2 cm. Five support traces per new column, maximum support variation 2.5 cm. Fixed-object overlaps were trimmed; access straights and original grid were excluded. Original modules/materials/collision/LODs unchanged.

Acceptance: save/reload and instance transforms verified. 2,264 oriented box sweeps using 180 x 120 x 32 cm kart bounds across center/edge lanes and 20 grid slots. Eight pre-existing outer-edge obstructions at route indices 525–534 remained identical; zero new obstructions. Seven wall collision probes passed using existing simple convex collision. Additional 748 actual AI-guide sweeps found zero tire hits. All protected hashes checked after capture: 76 unchanged files, including source/config/tire assets/source art and other maps.

Actual PIE: authoritative five-red-light start released normally; 3.016-second low-speed corner probe travelled 6.885 m with roll 0.0046 degrees. No full lap or high-speed impact validation was performed.
Performance: same stationary POV, uncapped offscreen editor PIE, expanded vs original 144 instances. Median Slate frame intervals 10.630 vs 10.642 ms; p95 12.026 vs 11.958 ms. No measurable slowdown in this short probe. This is not a packaged GPU benchmark; RHI draw/triangle counters were unavailable (returned zero). Two HISM components and four existing mesh LODs retained; no per-tire actors added.

Screenshots: aerial_all_barriers.png (temporary unsaved increased cull distance so all walls are visible from above), driver_hairpin_entry00000.png, driver_sweeper00000.png, curved_barrier_detail.png. Actual Unreal captures, PNG decoded and visually inspected. Driver views use the real ProofPawn first-person camera with no camera-setting changes.

Reversible checkpoint: Checkpoint/DesertKarting_Visual.before_expansion.umap. Restore only with Unreal closed and after preserving any later edits. The apply script deliberately refuses to run if it does not find exactly the original 144 tires, preventing accidental duplicate placement. Later capture/performance scripts never save the map. Some screenshot sessions encountered an editor shutdown crash after evidence and validation were written; the final performance and hairpin checks exited normally.
