# Race flow and competitive pace — implementation report

Branch: `fix/packed-race-stability`. HEAD: `761e6d0bddfe3e6dc3a90e6b2d9e58dbeb9ddc82`. Prior packed-stability changes remain preserved and uncommitted. No push or merge. No user Unreal process was running at inspection. No assets or project copies changed.

## CONFIRMED ROOT CAUSES

1. **Lateral tracking oscillation on straights.** The short high-speed pursuit target, combined with the pawn's existing steering/yaw smoothing, caused large measured lane oscillations despite a steady desired lane. Diagnostic train traces showed desired lane 300 cm with actual lanes oscillating approximately 129–488 cm. Karts then triggered edge guidance and following brakes. Increasing straight-line lookahead fixed the controlled train without lowering safety margins or raising the cap.
2. **Checkpoint guidance disrupted ordinary racing lanes.** It reset desired lane to actual lane each update, targeted a point only 150 cm past the gate even when already aligned, and applied 400 cm/s when lateral offset exceeded 250 cm. These conditions interrupted passing and amplified tracking corrections inside a 480 cm half-width gate. Guidance now preserves safe desired lanes, only uses the edge cap near the usable boundary, and retains normal pursuit on aligned straights.
3. **Rejected intermediate lane targets caused unnecessary stops.** Rejecting a desired lane only reset its endpoint; the interpolated lane remained unsafe and produced a zero speed target until it caught up. Both planner values now reset to measured occupancy after rejection. This does not teleport or snap the physical kart.
4. **Narrow, binary speed control generated repeated brake/coast cycles.** Baseline field mean was315.95 brake events per NPC. Proportional throttle near target and brake hysteresis reduce switching; measured final mean 170.32. Safety reductions remain immediate.
5. **Clear-air top speed was already healthy.** Baseline clear air reached 54.94 km/h. The three seeded corner exits reached95% of cap in 2.85s. No evidence supported increasing the 55 km/h cap or globally raising corner limits.

The normal-pass fixture did **not** reproduce erroneous application of the 400 cm/s obstruction cap. Baseline full-race obstruction limiting averaged only 2.90s per NPC, versus 94.96s traffic and 53.22s combined gate/steering guidance. The emergency cap was not the primary measured cause. Corner constraints are recomputed each frame; no stale corner timer was found. Video observations remain qualitative, not the source of the percentages below.

## IMPLEMENTED

- Straight-only speed-dependent pursuit lookahead: `(350 + speed * 0.6) / route spacing`, bounded 3–7 samples above 600 cm/s. Original bend lookahead and corner limits retained.
- Preserve planned lanes through gates when physically safe; edge correction uses gate half-width minus kart half-width and existing safety margin. No gates widened and no validation bypassed.
- Follow / Consider / Committed / Passing / Clear state with tracked rival, bounded 8s commitment, safe abort and 1s clearance hold before ordinary lane scoring resumes. Existing driver aggression influences consideration delay; individual preferred lines, corner skill and decision timing remain.
- Measured occupancy, predicted conflict, safety margins and nearby lane reservations retained. Unsafe planner targets are abandoned immediately; physical movement remains swept and smoothly steered.
- Normal committed pass uses 130 cm/s lane-target interpolation; slow/stopped emergency maneuver retains 240 cm/s interpolation and 400 cm/s local target. Ordinary side-by-side passing does not inherit that cap.
- Throttle ramps proportionally within 100 cm/s of target; maximum response is bounded 0.96–1.0 by aggression. Launch throttle logic remains unchanged. Brake hysteresis enters at 50 cm/s overspeed and exits at 10; original pawn braking force remains unchanged.
- Traffic targets decrease immediately for safety and increase at 800 cm/s². This clears even a near-stop limit within 2s when the conflict disappears; no retained obstruction latch. Existing gap/relative-speed/braking-distance calculation was retained because fixing the tracking/control chain resolved the controlled train.
- `State.TargetSpeed` now records the final normal-driving target, including steering guidance, rather than an earlier intermediate value.
- Opt-in `bPaceDiagnostics` snapshots plus test-only aggregate metrics. No tick log spam or automatic recording/upload. Existing F9 schema and learning architecture unchanged.

## Measurement design / diagnostic access

Set director `bPaceDiagnostics=true` in a development fixture/debugger. For NPC 8 read `GetOpponents()[7]`: `Pace.Corner/Traffic/Obstruction/Guidance/Recovery`, `Pace.Reason`, `Pace.Ahead/RelativeSpeed`, `Lane/DesiredLane/ActualLane`, `PassPhase/PassTarget`, `TargetSpeed`; actual speed, throttle and brake are its kart's `GetSpeedKmh()`, `GetThrottleInput()` and `IsBrakeHeld()`. Recovery/finish branches use the explicit recovery reason/limit; normal target is not a signed reverse command. Units are cm/s and cm internally. The test reports convert speed distributions to mph.

Moving averages exclude speed<=1 mph and finished racers. Dominant-limit durations are mutually exclusive, not time spent with every possible overlapping constraint. Low-speed queue means queued and<10 mph. Field averages are equal-weight means of the 19 NPC metrics. Contact totals sum per-kart registrations, not unique collision pairs. Tracked pass completions mean the specific rival is300 cm behind while nearby; they are maneuver diagnostics, not guaranteed official position gains. Baseline pass counters were unavailable and are marked accordingly.

Baseline driving code was unchanged apart from diagnostic writes. It reproduces the previous443.82s mean/596.9s last finish. Baseline and Final JSON are separate. Intermediate failed experiments remain local. A subsequent train-fixture correction resets the newly introduced filter after warming/teleporting racers to the intended44 km/h initial state; the baseline had no filter, so the initial-state intention is unchanged. No performance threshold was weakened.

## AUTOMATED TESTED

Full final suite: **15 passed,0 failed,0 test warnings**, including all 14 previous suites and the new pace suite. Evidence: `Final/index.json`. Baseline:14 passed,1 expected new pace-test failure (`Baseline/index.json`).

| Measurement | Baseline | Final |
|---|---:|---:|
| Field mean moving speed | 19.67 mph|22.72 mph|
| Moving time above 30 mph |17.21%|31.97%|
| Moving time below 20 mph |51.56%|40.62%|
| Traffic-limited time / NPC |94.96s|79.56s|
| Guidance-limited time / NPC |53.22s|28.44s|
| Obstruction-limited time / NPC |2.90s|0.92s|
| Brake events / NPC |315.95|170.32|
| Brake duration / NPC |48.46s|26.62s|
| Mean finish time |443.82s|376.54s|
| Last finisher |596.90s|487.50s|
| Summed per-kart contacts |49|42|

All 19 finish the unchanged ordered three-lap /12-checkpoint race within 600 simulated seconds. Existing distinct styles,57/55 km/h caps, incidents, launch, stopped/two-kart avoidance, reverse safety, displaced occupancy, finish/reset, HUD, audio and training tests pass. Launch remains zero-contact.

Clear-air acceleration to90/95% cap improves5.20/5.50s to4.75/5.00s. All three seeded exits reach90/95% in2.35/2.60s versus2.55/2.85s. First two exit speeds at 1/2/3s improve34.97/44.55/54.13 to35.86/46.33/54.32 km/h. Exit 300 is51.51 km/h at3s as its route geometry differs; no blanket corner-speed increase was used.

The exit fixtures seed 25.38 km/h at authored samples 120/210/300 near bend exits: the raw label `apex_kmh` denotes this controlled seed, **not a measured natural apex**. Distances to90/95% are displacement from that seed. Natural apex-to-exit traces under human traffic remain a follow-up; full-race tests traverse all actual bends.

Six-kart train: roughly 40 km/h leader, then acceleration; final followers have minima40.26–42.39 km/h and finish54.72–54.98 km/h with zero contacts. Baseline tail minimum17.01 km/h and final29.06 km/h. Normal pass: one tracked attempt/completion, zero contacts, zero left/right flips, no emergency cap. Removed obstacle: traffic limit188.3→1527.8 cm/s within 2s. Reset clears new pass/filter state.

Per-NPC distributions, limits, contacts, finishes, pass counts, gaps and exit times/distances: **METRICS.md**, reproducible using `summarize.py Baseline Final`.

## Builds / files

- UE5.8.3 Editor Win64 Development: succeeded (`build-final-editor.log`,6.04s final incremental build). Existing HUD-test deprecated InputKey warnings appeared during an earlier full module compile; no new compiler errors.
- Standalone Windows Development: succeeded (`build-final-game.log`, 507.19s; cold precompiled-header load dominated).
- `git diff --check`: passed.
- This phase changes KartRaceDirector.h/.cpp, Tests/KartIntegrationTests.cpp, new Tests/PaceMetrics.h and Tests/RacePaceTests.cpp, test evidence/report/script, BUILD_LOG.md and .gitignore. KartPawn's existing stability edits are preserved; this phase does not change its physics.

## MANUAL TESTING REQUIRED / REMAINING LIMITATIONS

No rendered or human driving verification in this phase, and no packaged/cooked/Steam validation. Full-race contact count remains42 and one racer finishes 487.5s, well behind most of the field. These tests establish improvement in deterministic fixtures, not that a human can no longer open a large lead. One seed/track/default-profile configuration is measured; learned profiles and other frame rates need broader evaluation. Passing can still abort when physical occupancy becomes unsafe. Prior post-finish collision filtering remains unchanged; racing collisions were not disabled.

1. Drive a complete 20-kart race with F9 recording. Confirm reverse-before-start still holds the field and normal launch stays clean.
2. Follow at similar speed, slow moderately on a straight, then accelerate. Watch tail karts for unnecessary brake waves.
3. Let a faster NPC pass on each side. Check that it maintains its lane while alongside and returns gradually once clear.
4. Compare corner exits and CP7: prompt acceleration, stable line, no missed gates or abrupt edge corrections.
5. Stop temporarily with an open passing lane, then move away. Verify cautious avoidance followed by prompt normal speed.
6. Test dense contacts, occupied-rear recovery, finish and F5. Confirm HUD, commentary, badges and F9 behavior remain intact.

Recommended next task: compare human F9 sessions against these measured distributions, especially overtakes through bends, CP7 and the slowest finisher. Do not increase the AI cap based only on the player's reported clear-air advantage.
