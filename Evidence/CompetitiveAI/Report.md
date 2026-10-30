# Competitive AI implementation and validation — 2026-10-28

The default four-opponent racing configuration is implemented and tested. This is a conservative upgrade with recorded stress-test failures, not a claim of commercial-game-level AI or complete acceptance of every requested scenario.

## Architecture and preserved work

`UTrackRacingAI` still drives real `AProofPawn` karts through steering, throttle and proportional service-brake commands. The 240 Hz `KartTireDynamics` simulation, its parameters, collision handling, human inputs and authoritative five-light start are unchanged. No position swapping, in-race teleporting, spline movement, boost or hidden rubber-banding was added.

The controller caches the existing 748-sample asphalt boundary/reference route, curvature, grade, corridor, corner zones and backward braking/forward acceleration speed envelopes. A speed-sensitive pure-pursuit controller follows bounded lane offsets. Planning uses actual sensed grip and existing wheelbase/steering lock to reject physically impossible inside routes. Perception predicts bounded neighboring motion, projects kart dimensions and retains targets. Explicit prepare/pass/defend/alongside/abort/recovery states use clearance checks, cooldowns and smooth lane transitions. Normal control runs at 20 Hz, perception at 10 Hz, strategy roughly 5–7 Hz; tire dynamics remain at 240 Hz.

Five selectable presets are ROOKIE, AMATEUR, INTERMEDIATE, PRO and ELITE. They vary braking margin, corner confidence, reactions, smoothness and mistake frequency. Individual profiles expose pace, braking confidence, aggression, passing preference/willingness, defense, consistency, reaction, hesitation likelihood and recovery skill. All retain identical physical parameters and the shared 38 mph speed limit. Mistakes are deterministic recoverable pace hesitations, not random steering or fake slides. Adaptive difficulty is not enabled.

Changed files: `TrackRacingAI.h/.cpp`, `KartRacecraft.cpp`, additive AI-only control APIs in `ProofPawn.h/.cpp`; new `KartAITrackPlan.h/.cpp`, `KartAIPerception.cpp`, `KartAIDifficulty.cpp`, `KartAIDebug.cpp`, and `Tests/KartCompetitiveAITests.cpp`. All are under `Source/Road_To_F1_New/`.

Reused route: `/Game/RoadToF1/RacingAI/DA_DesertTrackEdges`. Reused map: `/Game/RoadToF1/Maps/DesertKarting_Visual`. Checkpoint copies are in `Evidence/CompetitiveAI/Checkpoint`. `protected_verification.json` confirms protected maps, physics, configuration and art stayed unchanged; every existing pawn/game-mode function body matches its checkpoint. No commit or push was made.

## Measured Unreal results

The baseline already had rudimentary passing/defense; it was not a pure single-file controller. Its weaknesses included heuristic corner speeds, no cached braking envelope, opaque tactical states and limited target persistence. The new controller is more bounded and inspectable. The data does **not** establish an increased overtaking rate or calibrated difficulty against a human.

These are real Unreal PIE simulations with swept collisions and actual tire forces. Most tests use NullRHI and fixed 40 Hz game frames with 240 Hz physics substeps; Rendered uses the graphics renderer. The player is driven only by the explicit diagnostic command-line flag. Actual AI-versus-AI duels omit that flag, leaving the human kart staged behind the two racing AIs. A deliberately slower driver request is used in the duel, without changing physical parameters.

| Test/run | Seconds | AI circuit laps | AI order exchanges | Contact episodes | Off-track episodes | Stuck seconds | Controller mean ms/update |
|---|---:|---:|---:|---:|---:|---:|---:|
| Baseline 1 | 180 | 4 | 6 | 0 | 0 | 0.00 | 0.000 |
| FinalPack 1 | 300 | 8 | 3 | 0 | 0 | 0.00 | 0.094 |
| FinalPack 2 | 300 | 8 | 3 | 0 | 0 | 0.00 | 0.094 |
| FinalPassing 1 | 60 | 0 | 1 | 0 | 0 | 0.00 | 0.057 |
| FinalPassing 2 | 60 | 0 | 0 | 0 | 0 | 0.00 | 0.056 |
| FinalDefense 1 | 75 | 0 | 1 | 0 | 0 | 0.00 | 0.059 |
| Restart 1 | 95 | 0 | 2 | 0 | 0 | 0.00 | 0.091 |
| KnownLowGrip 1 | 40 | 0 | 2 | 0 | 0 | 0.00 | 0.080 |
| Scale4 1 | 60 | 0 | 2 | 0 | 0 | 0.00 | 0.071 |
| Scale20 1 | 90 | 0 | 46 | 0 | 1 | 0.00 | 0.385 |
| Rendered 1 | 35 | 0 | 2 | 0 | 0 | 0.00 | 0.116 |

Circuit laps are full route-length progress from each staged position, not invented finish-line events. Exchanges require a longitudinal order reversal with at least 250 cm clearance and one second confirmation, after the initial five seconds. Contacts are per-kart starts of non-ground swept contacts separated by 0.5 seconds. Off-track episodes require the projected 90×60 cm collider to exceed the measured asphalt boundary for over 0.3 seconds. Stuck time means speed below 30 cm/s with a requested speed above 150 cm/s, or any continuous stop beyond five seconds; short commanded yields are separately logged.

The two final five-kart races each lasted 300 seconds with different AI grid orders: all four opponents completed two full circuits each, with six AI-versus-AI order exchanges total and zero contacts, off-track episodes or stuck time. AI lap samples span approximately 109–120 seconds. The faster-AI duel completed a clean pass from one grid arrangement and stayed behind during the other 60-second test. The defensive test recorded one early defensive hold followed by a successful pass. Side-by-side corner motion and aborted maneuvers were observed in actual running traffic. Dedicated deliberate gap-closure and deliberate off-track-rejoin fixtures remain unverified.

Normal restart and low grip known before lights-out are separate tests. The low-grip test tags the road Grass only in transient PIE, observes a 0.457 grip ratio, then restores asphalt; it is a short check, not a complete grass lap or a test of authored dirt terrain. The planning/preset automation test passed (`automation.log`). Native grid evidence records zero AI pre-start movement and one lights-out event per race epoch, including twenty staged participants. Selected physical parameters were asserted identical across karts.

## Recorded limitations and failed stress cases

The twenty-participant 90-second test has zero contacts and stuck time but one approximately 0.5-second asphalt excursion at the tight hairpin, reaching about 95 cm body-edge excess. Twenty-kart competition remains experimental; no full-grid endurance claim is made. Its controller mean was about 0.38 ms/update, peak about 0.81 ms. These are component elapsed timings, not full CPU/GPU frame-time profiling or a promised frame rate.

The abrupt-friction-loss stress test (`Systems/after.json`) changes the entire asphalt road to grass friction at racing speed, without advance warning. One opponent left the road, hit a barrier and remained there before restart. Preserve that result as a failure. Known-low-grip and normal-restart passes do not erase it. The raw post-restart stress-harness contact at time zero inherits a cumulative collision counter; use the separate clean Restart test for restart validation.

The reference remains conservative rather than a globally optimized minimum-time entry/apex/exit line. Human pace calibration, extended twenty-kart racing, sudden-grip-loss recovery, authored dirt transitions and comprehensive rendered frame-time profiling remain unfinished.

## Play and debugging

Open the existing project, load `/Game/RoadToF1/Maps/DesertKarting_Visual`, and press Play. Four opponents are the default; keep that count for the verified configuration. Existing driving inputs are unchanged. All launch through the existing lights-out event.

Console: `kart.ai.Difficulty 0` through `4` selects Rookie through Elite; `2` is Intermediate. `kart.ai.Debug 1` enables state/control text, `kart.ai.Paths 1` enables reference/local-path/prediction drawing; set either to `0` to disable. `kart.ai.Opponents N` applies next Play, up to nineteen opponents, but higher-count racing is experimental. Test harnesses are the `Tools/competitive_ai_*.py` files; `Tools/summarize_competitive_ai.py` regenerates metrics from the saved results.

## Actual screenshots

The PNGs are actual first-person PIE captures. `screenshots_verified.json` checks dimensions, PNG CRCs and decompression; gameplay images were also decoded and viewed. Normal screenshot capture suppresses engine debug messages, so the UI-inclusive debug capture is kept separately.

[debug00000.png](D:/Boring/GitHub/Road-To-F1-New/Road_To_F1_New/Evidence/CompetitiveAI/Rendered/debug00000.png) — 1267×550.

[grid00000.png](D:/Boring/GitHub/Road-To-F1-New/Road_To_F1_New/Evidence/CompetitiveAI/Rendered/grid00000.png) — 1267×550.

[racing00000.png](D:/Boring/GitHub/Road-To-F1-New/Road_To_F1_New/Evidence/CompetitiveAI/Rendered/racing00000.png) — 1267×550.

[debug00000.png](D:/Boring/GitHub/Road-To-F1-New/Road_To_F1_New/Evidence/CompetitiveAI/DebugView/debug00000.png) — 1280×720.

[grid00000.png](D:/Boring/GitHub/Road-To-F1-New/Road_To_F1_New/Evidence/CompetitiveAI/DebugView/grid00000.png) — 1267×550.

The UI-inclusive DebugView screenshot was decoded and viewed with the AI overlay visible. That test editor returned exit -1073741819 during shutdown after QUIT_EDITOR; it did not exit cleanly. The ordinary rendered gameplay, normal restart, known-low-grip and final competition processes exited 0. If global screen messages are disabled, run `EnableAllScreenMessages` before enabling AI text.
