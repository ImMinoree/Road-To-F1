# Gameplay competition review — 29 October 2026

Implemented in `/Game/RoadToF1/Maps/DesertKarting_Visual`; four existing simulated AI opponents retained. No commit, push or merge.

## Verified causes and focused changes
The existing AI already had track-relative lane planning, perception, passing/defending states, four personalities and shared KartTireDynamics. Conservative planning capped lateral acceleration at 265 cm/s² and exit acceleration at 150 cm/s². A failed offset feasibility check could request a full stop for a conflict up to 18 m away. Opponents were losing pace rather than disappearing.

AI-only planning defaults are now 420 and 300 cm/s², bounded by existing grip and braking envelopes. Abort braking scales with available distance instead of immediately requesting zero speed. Existing personality and lane-clearance decisions remain. These are plausible tuning values, not measured real kart parameters. Physics, player input, camera, art, circuit and the common approximately 61 km/h speed limit were not changed.

Changed sources: TrackRacingAI.h/.cpp, KartAITrackPlan.h/.cpp, KartRacecraft.cpp, ProofPawn.cpp (development diagnostic input latch only), RaceStartGantry.cpp (HUD only), new KartRaceStatus.cpp and the existing physical-plan test. Added compact position, lap, speed, current/last/best timing feedback through the existing HUD and lap progress system.

## Measured comparison
Two 240-second five-kart races per configuration, normal and reversed AI grids. Both configurations use the same opponent-aware automated reference-player policy (420/300 budgets), identical physical karts and unchanged top speed. This is not a replay of human inputs. Actual physics runs at 240 Hz; test world frames fixed at 40 Hz.

| Measurement | Before | After |
|---|---:|---:|
| AI completed laps | 16 | 16 |
| Median AI lap | 112.94 s | 94.14 s |
| Median flying lap | 110.75 s | 92.63 s |
| Tight-corner mean speed | 13.40 km/h | 16.28 km/h |
| Mean AI speed | 34.13 km/h | 40.31 km/h |
| All confirmed position exchanges | 14 | 13 |
| AI-versus-AI exchanges | 6 | 5 |
| AI retakes after player passes | 0 | 3 |
| Player time without opponent within 20 m along track | 349.75 s | 24.38 s |
| Contacts / off-track events / stuck seconds | 0 / 0 / 0 | 0 / 0 / 0 |

Proximity measurement covers 470 racing seconds excluding opening staging. Nearby time increased from 25.6% to 94.8%. Position reversals require 2.5 m separation and one-second confirmation. Every sample asserted five karts present. Each AI completed two laps in each run; all runs exited successfully. Defensive-hold counters increased 17 to 22, but these state counters alone do not prove successful defense. The committed-pass counter remained zero despite measured position exchanges: this pass-state classification remains a limitation, and total overtakes did not increase.

After-test AI tick CPU mean 0.138–0.142 ms, observed maximum 0.716 ms, including the automated fifth driver. Headless CPU measurements do not establish rendered frame rate or 20-kart scalability. Control/perception remain 20/10 Hz, independent of tire substeps.

## Video and barrier review
Reviewed extracted frames from the actual 105.8-second recording, including 92–96 seconds. The kart approaches the inner tire island and crosses the curb/runoff edge, then returns toward the asphalt. Steering visibly responds. The recording lacks input and speed telemetry, so it cannot establish braking use, a steering defect or precise impact severity. No handling changes were justified. Collision recovery for that exact human maneuver remains unverified; ordinary multi-kart races recorded no contacts or off-track events.

## Validation and limits
Development Editor build and PhysicalPlanAndPresets automation passed. Target-map rendered PIE verified five racers, one authoritative start event, normal human-player progress tracking and readable HUD. Valid decoded screenshots: Feedback/staged00000.png and Feedback/feedback00000.png. The separate rendered UI probe produced valid results but its editor process crashed during shutdown after QUIT_EDITOR; race comparison processes exited zero. No claim of a fully clean renderer lifecycle.

Hash verification confirms target map, tire-physics sources and configuration unchanged from checkpoint. Existing uncommitted map/cockpit work preserved. Reversible source checkpoint is in Checkpoint/; restore copied sources/test and remove the newly added KartRaceStatus.cpp to reverse this pass. Diagnostic driver input latching now survives zero-axis callbacks only in explicitly enabled non-shipping tests. The reference-player plan is also test-only.

Human difficulty calibration, exact recorded-input replay, blocked-pass/forced-contact recovery and a fresh 20-kart stress test were not verified here. Existing five difficulty presets remain Rookie, Amateur, Intermediate, Pro and Elite; default Intermediate. Standard races use no adaptive rubber-banding or physical boosts.

## Play
Open Road_To_F1_New.uproject, load /Game/RoadToF1/Maps/DesertKarting_Visual and press Play. Four opponents use the existing five-light start. Drive with existing controls; new race information is at upper right. Do not launch with diagnostic RacingAIPlayerTest flags for manual play.

Raw evidence: comparison.json, Baseline/baseline.json, After/after.json and their telemetry.csv files. Video frames are in Video/. Repeatable test and summary tools are Tools/gameplay_competition_test.py and Tools/summarize_gameplay_competition.py.
