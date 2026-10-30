# AI 70 km/h â€” implemented and measured

All AI opponents now have a configurable 70 km/h forward-speed governor (AITopSpeedKmh). The player remains at 38 mph / 61.155 km/h. Current normal gameplay retains the existing nine opponents; test flags temporarily selected four or nine without changing the map/grid configuration.

Default AI pace is now Pro, with corner planning budget 450 cm/sÂ² and exit planning budget 350 cm/sÂ². These are planning values, not new grip or engine force. The trajectory speed profile reads the actual kart governor instead of the shared player speed ceiling. Added a pursuit-curvature speed bound for passing/corrective turns and a shorter low-speed look-ahead at tight hairpins. Existing tire-force physics, collision, input and five-light start remain authoritative; no teleporting or rubber-banding.

## Final actual tests
Development Editor build succeeded. Automated headless PIE races used the real map, 240 Hz tire dynamics and fixed 40 Hz world frames. The reference player is an opt-in automated driver, not a replay of human inputs. Its governor and baseline trajectory budget remain 61.155 km/h and 420/300; reaction/difficulty settings share the race's selected preset, so this is not an exact fixed-policy human comparison.

| Final measurement | Five karts (240 s) | Ten karts (150 s) |
|---|---:|---:|
| Leading AI opening lap | 91.90 s | 92.15 s |
| Reference player opening lap | 97.40 s | 104.15 s |
| Completed AI laps | 8 (two per opponent) | 9 (one per opponent) |
| Confirmed position exchanges | 5 | 16 |
| Collision episodes | 0 | 0 |
| Body-footprint boundary excursions | 1 | 1 |
| Low-speed time counted as stuck | 0.125 s | 0.125 s |
| Actual observed peak AI speed | 65.34 km/h | 65.42 km/h |
| AI control tick mean / maximum | 0.101 / 0.296 ms | 0.192 / 0.449 ms |

The 70 km/h value is a ceiling, not a guaranteed speed through this circuit's short straights and corners. Runtime assertions verified AI governors at 70 and the player at 61.155, with equal mass, engine force, steering limits and tire stiffness. Each race used exactly one lights-out event. Both final editor test processes exited zero. Headless timings do not establish rendered frame rate.

Before this pass, the matched normal-grid test's quickest AI opening lap was 94.15 s and median AI opening lap 96.40 s; final values are 91.90 s and 95.90 s. Earlier before runs covered normal and reversed grids, but final broader testing stopped on a boundary warning, so no clean final reversed-grid claim is made. Individual AI personalities and traffic can still produce slower laps; the AI is not guaranteed to beat a human.

## Remaining limitation and diagnostic honesty
A brief body-footprint excursion persists around route sample 504â€“505 at the tight hairpin. The final harness checks nine collider-footprint points against the union of paired-edge corridor quads; local tangent-plane excess is retained separately because it can overestimate at sharp bends. These inconsistent geometric diagnostics are not proof of clean driving or of all four tires leaving asphalt; the warning remains unresolved. Axle surface telemetry at the first local-plane warning showed asphalt front/rear; this does not prove all four tires stayed inside the boundary throughout the event. Exact times/positions/durations are preserved in verification.json and raw race JSON. There were no contacts or sustained immobilizations, but the strict safety threshold tripped, so fully clean competitive racecraft remains unverified. The final repeated run was deliberately not expanded to the reversed grid after this warning.

Earlier stronger pace, wider-lane-clearance and controller trials are archived in Initial450_*, Initial400_*, ClearanceTrial_*, GovernorOnlyTrial_*, PursuitTrial_*, PreHairpinTrial_* and HairpinPlaneDiagnostics_* folders. They are not substituted for final evidence. The unsuccessful 2.75 m passing-clearance change was reverted; existing passing-clearance values remain.

## Source and preservation
Changed: TrackRacingAI.h/.cpp (AI governor, Pro defaults, controllers and diagnostic reference plan), KartAITrackPlan.cpp (per-kart speed ceiling). KartNavigationMap.cpp only renames three internal color constants to resolve unity-build name collisions; its appearance/behavior is unchanged. KartRacecraft.cpp was restored to its pre-pass checkpoint. No tire-physics, player-pawn, configuration or map file hash changed. A reversible checkpoint is in Checkpoint/. Preserve subsequent edits before using those copies.

No commit, push or merge performed. Another automated MCP settings-check editor had exited before a temporary close attempt; this task did not close or restart that separate editor.

## Play
Open Road_To_F1_New.uproject, load /Game/RoadToF1/Maps/DesertKarting_Visual and press Play. The existing nine AI opponents use the 70 km/h ceiling and Pro default. Existing difficulty selection remains available via kart.ai.Difficulty 0..4; 3 is Pro. Do not use RacingAIPlayerTest flags for manual play.

Raw results: After/after.json, TenKart/after.json, telemetry.csv files, summary.json, verification.json and final build/race logs. Repeatable harnesses: Tools/ai70_race_test.py and Tools/ai70_ten_kart_test.py. Before replay should restore the source checkpoint; AISpeedBaseline restores old speed/pace settings but retains current controller fixes.
