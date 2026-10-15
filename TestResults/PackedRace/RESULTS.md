# Packed race stability — implementation and verification

Branch: `fix/packed-race-stability`.
Starting main commit: `761e6d0bddfe3e6dc3a90e6b2d9e58dbeb9ddc82` (includes the approved dynamic HUD).
No push or merge is authorized for this phase.

## Confirmed baseline findings

- Reverse movement released the field because the director used absolute speed. A controlled regression failed on the original controller.
- The saved grid's lateral positions differ by 70 cm from the original planned +/-130 cm lanes. Measured grid offsets are approximately +/-200 cm. The original lane assertion failed.
- A frozen queue with occupied front/rear space triggered reverse after three seconds. The original controller failed this regression.
- Lane-crossing rejection used planned `State.Lane`, even though traffic occupancy depended on physical position.
- Finish place assignment existed, but finished NPCs continued through the same driving/recovery planner. Official finish order/time freezing was already implemented and has been preserved.
- These establish code defects and controlled reproductions, not the exact initiating cause of any particular video crash.

## Implemented

- Preserve deliberate forward-throttle launch, requiring positive signed speed, grid-aligned heading, proximity to the starting grid, no brake and no active contact recovery. Lap timing still starts only at the valid forward gate.
- Seed lanes from physical grid positions. Maintain an initial corridor and use full launch throttle for eight seconds (extend until 12 m travelled, bounded at ten seconds), avoiding acceleration differences that closed the starting gap in the controlled full-throttle player test. Existing individual styles resume afterward.
- Use measured lateral occupancy, rotated kart footprint, configurable safety margin and a short relative-motion prediction. Reserve nearby moving lane commitments and allow escape away from an overlapping safety margin.
- Recognize queues independently of fire. Permit wider low-speed obstruction maneuvers, preserve normal corner following, and gradually return toward normal lanes after passing.
- Guide displaced/outer-lane racers back inside the next checkpoint corridor without merging everyone into the center. Tests exposed missed gates beyond the unchanged 480 cm gate half-width; guidance changes steering, never awards an invalid gate or widens checkpoint acceptance.
- Reverse only after a genuine non-queue stall, with a bounded duration, rear kart/static-geometry clearance and cooldown. Recheck clearance while reversing; contact recovery brakes first.
- Finishers coast down at 400 cm/s² and ignore kart-to-kart collision while retaining world collision. This applies to player and NPC finishers, including interactions with still-racing karts. No kart is destroyed. F5 restores normal collision, driving and all AI state.
- Player/NPC caps remain 57/55 km/h. The obstruction maneuver temporarily targets at most 400 cm/s (14.4 km/h) while turning around close slow traffic; this is a local maneuver limit, not a global speed reduction. Existing steering smoothing remains active.
- Traffic collection uses inline storage once per director tick. No new plugin, map copy, asset rewrite, HUD redesign or training-policy change.

## Files

- `RoadToF1/Source/RoadToF1/KartPawn.h/.cpp`: footprint/contact state access; safe post-finish coast and reset.
- `RoadToF1/Source/RoadToF1/KartRaceDirector.h/.cpp`: launch, measured lane planning, obstruction handling, recovery and finisher transitions.
- `RoadToF1/Source/RoadToF1/Tests/PackedRaceTests.cpp`: controlled launch, queue, recovery, displacement, blockage, finish and reset scenarios.
- `RoadToF1/Source/RoadToF1/Tests/KartIntegrationTests.cpp`: diagnostic finish/queue/stop durations and missed-gate reporting; original 19-finisher/600-second requirement unchanged.
- `.gitignore`, `BUILD_LOG.md`, this report and automation evidence.

## Verification status

Baseline: `Baseline/index.json` retains the three expected failing reproductions against the original controller. Existing 13-suite baseline evidence is in `TestResults/DynamicHUD/Automation/index.json`.

Intermediate runs exposed and helped correct conservative lane reservations, slow lateral commitment, a false displacement heuristic and full-race completion regressions. Intermediate failures remain local and are not claimed as successful validation.

AUTOMATED TESTED (final fresh report: `Final/index.json`): all 14 RoadToF1 suites passed, zero test errors and warnings. Includes the existing 13 suites plus `RoadToF1.Racecraft.PackedSafety`. The final run repeats the successful full-race outcome and includes the strengthened player official-place assertion.

- All 19 NPCs physically complete three ordered laps within the unchanged 600-second simulation: finish times 398.4–596.9 seconds. No extra time or checkpoint exemptions were introduced.
- Controlled 20-kart eight-second launch: zero contacts, first-second lane drift 0.1 cm.
- Single stopped, continuously slow-moving, and two stopped non-burning blockage fixtures: all passed with zero subject impacts and no queued reverse.
- Directional release, occupied rear rejection/abort, bounded recovery and resumed movement, light contact, stale displaced lane, player/NPC finish/coast/result freeze and reset: passed.
- Existing burning incident, collision, track surface/rejoin, ordered gate, HUD, presentation, recorder, native learner and profile-validation suites: passed.
- UE5.8.3 `RoadToF1Editor Win64 Development`: succeeded (`build-final-editor.log`, 11.44 s).
- UE5.8.3 `RoadToF1 Win64 Development`: succeeded (`build-final-game.log`, 57.03 s).
- `git diff --check`: passed. Build/raw logs remain local; baseline and final JSON evidence retained.

MANUALLY VERIFIED: no human/manual driving or rendered visual validation in this phase. Tests use actual Unreal PIE actors and swept movement with NullRHI. No cooked/package or Steam validation has been performed.

## Human PIE checklist

1. Open the original project and SouthGarda_KartRace. Confirm player slot 20, three laps, 12 checkpoints and unchanged MPH HUD.
2. Before launch, reverse and release controls: NPCs should stay put. Start forward normally: no synchronized inward collapse or immediate pileup.
3. Drive in the pack, vary throttle, and permit overtakes. Watch for repeated weaving, excessive queues or a whole field becoming passive.
4. Slow or stop on a straight with space on one side, then near a bend. NPCs should brake and pass where a safe route exists, without requiring fire.
5. Create a two-kart blockage. With an open lane, following traffic should eventually pass. With the road fully blocked, waiting is correct until space opens.
6. Make light contact and displace a kart laterally. It should not force its way back through an occupied old lane.
7. Observe a genuinely stuck kart. Recovery should be brief and separated by cooldown; put a kart behind it and confirm reverse is withheld/aborted.
8. Finish and stop near the line. Final place/time should stay fixed; finishers should coast down without new kart impacts. Visual overlap with collision-filtered finishers is possible by design.
9. Press F5 after both an incident and a finish. Confirm normal collision, grid positions, timing and NPC launch return. Check audio, captions, number badges and optional F9 recording.

## Tuning rationale

Launch throttle is temporarily equalized so rear karts do not catch slower-accelerating grid neighbours before merging is safe; distinct aggression/corner/lane/decision settings resume afterward. Passing candidates extend to +/-300 cm with an outer-lane penalty. Close obstruction lane-target interpolation uses 240 cm/s instead of normal 70-95 cm/s because the original target shift happened too late to clear the blocker; the pawn still uses its existing smoothed steering. Braking prediction uses 1200 cm/s² (below the actual 1500 cm/s² braking capability) and a 0.1-second reaction allowance. Checkpoint approach correction uses a local 400 cm/s cap when significantly lateral near its plane. These are local safety/maneuver adjustments; forward caps and general corner profiles are unchanged.

## Remaining limitations / next task

Controlled tests cannot establish competitive quality across all human inputs. The passing full-race run includes a late finisher at 596.9 simulated seconds, only 3.1 seconds below the existing cutoff; the completion margin needs monitoring. Queue diagnostics include following moving traffic, not only stationary waiting. The full race is not collision-free. Racer 7 still missed gate 7 once at 387.9 seconds (lateral -513 cm against a 480 cm half-width), then correctly recovered its ordered progress by driving back around; it is the late finisher. Gate guidance reduces this failure but does not eliminate it in packed traffic. A truly stuck fixture models immobilization and then releases it; it does not prove escape from every physical barrier arrangement. Ghosted finishers can visibly overlap active karts. Sparse human footage does not establish precise crash initiators; no footage hypothesis is represented as proven by these synthetic fixtures. Validate multiple human-driven packed races and record F9 telemetry, particularly around first-corner merges, blocked bends and post-contact recovery. Review contacts, waiting duration, overtakes and missed gates before tuning further. Do not train on these synthetic test sessions as human demonstrations.
