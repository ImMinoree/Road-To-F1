# Handling refinement — 2026-10-26

Active project: `Road_To_F1_New.uproject`, Unreal 5.8.3, branch `main`, starting HEAD `5fb1349`. Existing uncommitted Model/Game work was preserved. No commit or push was made. The Instagram reference was inaccessible; three gameplay recordings were not supplied. Findings below come from source inspection and engine tests, not those videos.

The requested physical handling restores the existing 240 Hz `KartTireModel` / `UKartTireDynamics` as the default for `AProofPawn` and all four AI. `-LegacyKartMovement` retains the previously requested no-drift fallback. No new vehicle class, input stack, countdown, route, HUD, map, plugin or collision scene was introduced.

| Confirmed cause | Targeted correction |
|---|---|
| Default fallback directly rotated from steering, lacked lateral inertia and zeroed speed on every blocking hit | Route normal Play through the existing tire-force solver; preserve engine/brake, steering-range and grip settings |
| A 28 cm collision sphere did not cover the kart's body | One root box with half-extents 90 × 60 × 16 cm; cosmetics still have no collision |
| Contact removed only the moving kart's normal velocity; another kart received no momentum | Equal/opposite planar impulses using both masses, yaw inertias and contact levers; Coulomb contact friction 0.35, restitution 0.05 above 0.5 m/s closing speed |
| Remaining sweep used the displacement computed before impact | Recompute remaining movement from post-impact velocity, with at most three contact sweeps per substep |
| Penetration cleared all motion | Bounded query-based separation, at most 2 cm per substep, retaining tangential momentum |
| Height jumped to the highest wheel sample and pitch/roll were forced to zero | Average four supporting samples, critically damped vertical support (24 rad/s), gravity without support, damped surface attitude |
| Chase driver/wheel used the previous simulation frame's rack state | Update exterior steering after tire simulation and during the existing start hold |
| Chase rotation followed yaw abruptly | Small 16 s⁻¹ rotation smoothing, substepped spring arm after pawn motion; existing obstacle probe retained |

Tire relaxation, speed-sensitive rack limits, combined grip, front/rear slip, load transfer and rear-brake behavior remain the production model. Normal steering does not invoke a drift mode. Yaw and lateral travel emerge from integrated tire/contact forces. Physics never reads cosmetic camera motion. Existing tiny cockpit vibration also reads bounded vertical acceleration and a decaying contact signal. `GetDrivingSpeed()` reads current simulated velocity, including impulses received from another kart.

Unreal scene queries provide broadphase/narrowphase and sweep results; Chaos rigid-body simulation is not enabled on the kart. There is one physical collision owner. No duplicate GJK/EPA, rigid-body solver or global manifold system was added. CSV telemetry with `-KartTelemetry` now includes recent contact impulse, maximum penetration and vertical acceleration alongside slip/yaw/speed/forces.

## Validation

Development Editor builds passed. An intermediate build failed when concurrent Model chat work added `KartMechanicalVisuals.cpp` with `auto* Rod=Parts[7+I]`; explicit `.Get()` corrected that pointer deduction error without replacing the component. The combined build and all seven final automation suites then passed, including tire-force acceleration/braking, tight and high-speed corners, excessive demand, brake-entry/countersteer recovery, surface transitions, steering release/rate limits, start/reset, cockpit ownership/toggle and existing AI/debris tests. One existing SurfaceFX fixture mobility warning remains. Contact tests cover rear and side impacts, repeated contacts, conservation/dissipation, barrier holding, a 12.58 m/s barrier impact and an 8 cm kerb. Actual component sweeps/contact at 30/60/120 Hz finished at the same measured position. See `Evidence/HandlingRefinement/AutomationFinal`, `ContactFinal`, `world_contact_metrics.json` and logs for numbers.

Four AI completed two laps and all 64 sectors with both a moving diagnostic player (271.16 simulated seconds, no recoveries) and a stationary player (315.72 seconds, two AIs used three recoveries each). Both runs had zero measured pre-start movement and edge excursions, and one start event. Passing/recovery worked in these runs; this is not a claim of exhaustive traffic coverage.

Rendered PIE verified the original grid, held throttle before lights-out, launch, a 10.02° rear slide and recovery at driving speed, dirt/grass grip and debris, both camera views, and race restart. Maximum flat-pad height error was 0.06 cm. Seven screenshots were saved and inspected, including the actual circuit/grid cockpit and the explicitly staged, unsaved off-circuit pad. The test repositioning occurs only at setup/reset, never inside a maneuver. `Tools/validate_handling_refinement_pie.py` runs this procedure with `-KartDynamicsTest -KartTelemetry`; `Tools/verify_handling_refinement.py` checks reports, image decoding and protected hashes.

## Limits and manual verification

This is still a 2.5D kart: mass/inertia and yaw are physical, vertical support is damped, and pitch/roll follow the sampled surface rather than a full 3D suspension/rollover simulation. Swept translation and bounded overlap recovery approximate rotating chassis contacts. Contact impulses are solved sequentially in pawn order, not in a globally synchronized multi-body manifold solver; cross-kart results are not guaranteed bit-identical at every rendering rate. Moving Chaos objects are not coupled to this custom impulse model. Network multiplayer and packaged builds were not tested. The captured CL5 combined chassis has no separately steerable/spinning front-wheel meshes. The concurrent Model chat added a new mechanical renderer near the end of validation, but its `/Game/RoadToF1/PlayerVehicleV4` assets were not on disk at the final check; that renderer was not visually validated and currently falls back to existing visuals. Tire feedback assets missing in the earlier pass remain missing. Subjective handling still needs player feedback.

Open `/Game/RoadToF1/Maps/DesertKarting_Visual`, Play and click the viewport. Wait for five reds to go out. W accelerates, S brakes/reverses, Space brakes, A/D steer, V switches view, R resets. Begin with gentle inputs; try a short rear-brake application during a moderate turn, then release the brake and ease/countersteer. Holding full steering and rear brake at speed can still spin the kart. Run `Automation RunTests RoadToF1` for repeatable checks.

Reversible checkpoint: `Checkpoints/BeforeHandlingRefinement_20261026/source_config.zip` plus map hashes and original HEAD. Restore individual files selectively because this shared workspace also contains Model chat changes. Map geometry/scenery and the original physics repository were not edited.
