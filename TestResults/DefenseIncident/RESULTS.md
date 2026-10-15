# Defense and incident containment: human playtest candidate

2026-10-15. Branch `fix/packed-race-stability`; HEAD `761e6d0bddfe3e6dc3a90e6b2d9e58dbeb9ddc82`. No commit, push, merge, project copy, asset replacement, speed-cap change or training from human recordings. Existing uncommitted work remains in place. Player/NPC caps remain **57/55 km/h**.

## 1. Confirmed root causes

- Defense required more than 80 cm/s closing speed (2.88 km/h), exceeding the 2 km/h cap difference. A cap-speed player could approach without satisfying that condition.
- Straight-line defense could choose an arbitrary outer lane instead of protecting the attacker's corridor. Eligibility could evaluate a clear proposed bypass while the actual corridor remained blocked.
- Burning traffic ahead imposed an incident slowdown even outside the actual conflict corridor.
- Rejecting an unsafe intermediate lane discarded a safe final escape route. Rear destination reservations could obstruct the leading kart's outward escape.
- Queue suppression also disabled recovery for a kart genuinely trapped against a stationary obstruction with clear space behind.
- Pass timeout did not distinguish a safely advancing side-by-side kart from an unsuccessful attempt.

These are code/fixture findings. Attribution to particular human overtakes remains uncertain; see [sampled video and F9 evidence](HUMAN_EVIDENCE.md).

## 2. Defense findings

The cap-speed controlled fixture now activates one bounded move, holds the selected line, and produces zero contacts. Minimum defender speed: **54.68 km/h**; measured lateral movement **188.33 cm**; first movement above 25 cm occurs after **1.35 s**. The attacker is scripted to drive straight: this demonstrates a working response, not resistance to an adaptive human.

Eligibility uses a 25 cm/s minimum closing rate, an eight-second closing horizon, physical gap/move-time feasibility, suitable geometry and a sufficiently clear actual corridor. No new block starts when already alongside. One side is held for 3-6 seconds, with a six-second cooldown. Slow incident/rejoin traffic takes priority over defense.

## 3. Incident-cascade findings

Early candidates exposed secondary collisions, stale lane plans and stationary dead ends. Those candidates were rejected. Earlier stopped/slow-object detection and explicit bypass checks remove contact in both final fixtures. A kart trapped against a stationary object may back out only after a sustained stop and clear rear checks. This special maneuver lasts at most two seconds; rear closing prediction covers its duration. Ordinary recovery retains its prior limits. No collider disabling or teleporting was added.

The difficult one-sided fixture still takes **27.35 seconds** for its last follower to clear. This is a remaining responsiveness concern for visual playtesting, despite safe, finite clearance.

## 4. Implemented

- Earlier, feasible one-move defense; attacker-corridor protection on straights and inside-line preference on approach to a bend.
- Physical-corridor incident classification, expiring bypass preferences, separate final/intermediate lane validation, and measured-position rejoin handling.
- Scoped shared-rear-corridor escape and common-motion handling for stable parallel karts; actual occupancy and predictive conflict checks remain active.
- At most three additional seconds for an expiring pass only while safely alongside and making forward progress.
- Optional five-Hz development `battle-v2.csv` sidecar with defense, incident and recovery diagnostics. The original 19-column F9 schema and training tools are unchanged.
- Evaluation-only position-gain labels, with unknown cases retained and contact/incident labels explicitly heuristic. A physical crossing cannot be reused for multiple gains.

## 5. Files changed this phase

- `RoadToF1/Source/RoadToF1/KartRaceDirector.cpp`
- `RoadToF1/Source/RoadToF1/KartBattleState.h`
- `RoadToF1/Source/RoadToF1/Tests/BattleTests.cpp`
- `RoadToF1/Source/RoadToF1/Tests/IncidentTests.cpp` (new)
- `RoadToF1/Source/RoadToF1/Tests/KartIntegrationTests.cpp`
- `.gitignore`, `BUILD_LOG.md`, and reports/scripts/evidence in `TestResults/DefenseIncident/`.

Other modified files in Git status predate this phase. In particular, the director header and prior pawn/asset work were preserved.

## 6. Tests added or extended

Actual-cap defense, one-side commitment, retained speed, distant/non-closing attacker rejection, no alongside blocking, safe advancing pass extension, displaced-kart rejoin, and 74-column sidecar/original-F9 compatibility. New ten-NPC fixtures include a stopped leader with nine followers, then two stationary blockers with eight followers and only one usable side. They require every follower to clear within 30 seconds, zero contact, and recovery to 90% of cap within ten seconds after clearance. Existing launch, train, reverse, moving/stopped blockage, ordered race, finish/reset, HUD, audio and training tests remain enabled.

Four Python tests check heuristic classification, unknown gains, stale defense outcomes and duplicate-crossing suppression.

## 7. Automated validation

- Fresh baseline: **16/16** suites passed.
- Final complete RoadToF1 suite: **17/17 passed**, zero automation warnings/errors. Actual actors and collision sweeps run in headless PIE; this is not interactive visual testing.
- RoadToF1Editor Win64 Development: **passed**, 15.83 s final incremental build.
- RoadToF1 Win64 Development: **passed**, 263.47 s.
- Evaluation analyzer: **4/4 passed**; generated sidecar separately checked for consistent 74-column rows.
- `git diff --check`: passed (Git line-ending notices only).

Baseline and final exports are separate. Intermediate failures remain local; no existing assertion was relaxed to accept them. The new incident scenario runs 36 seconds to observe speed recovery while retaining its 30-second clearance assertion. No packaged/cooked/Steam build was tested.

## 8. Defense outcome metrics

Full-field activations: **45 -> 142**. New outcome counters were unavailable in the baseline, so their baseline is not reported as zero.

| Final outcome | Count |
|---|---:|
| Held | 14 |
| Too late | 22 |
| Alongside release | 24 |
| Occupied | 25 |
| Threat cleared | 1 |
| Lost speed / obstruction release | 56 |
| Contact-risk release | 0 |
| Track too wide | 0 |

`Held` means the rival remained behind through the controller's hold window, not proof of a delayed human pass. Alongside release can be correct legal behavior. Track-too-wide is a reserved category without a dedicated detector; zero does not establish that road width is irrelevant.

## 9. Passing metrics

| Metric | Baseline | Final |
|---|---:|---:|
| Attempts | 52 | 72 |
| Completions | 3 | 11 |
| Completion ratio | 5.8% | 15.3% |
| Occupied aborts | 26 | 29 |
| Timeout aborts | 16 | 31 |
| Contact-risk aborts | 7 | 0 |
| Rival unavailable | 0 | 1 |

Timeouts and occupied aborts remain common; passing is improved in this fixture, not solved generally. Corner/guidance/speed-loss cancellation counts remain zero because these limits do not directly cancel the current pass state. Controlled moving-rival pass and player-like repass each complete once with zero contact. The full-field player is parked, so its repass count is zero and is not a human benchmark.

## 10. Incident metrics

| Fixture | Cleared | Contacts | Last clearance |
|---|---:|---:|---:|
| Both bypass sides available | 9/9 | 0 | 19.20 s |
| One side blocked | 8/8 | 0 | 27.35 s |

Both side choices are used in the open case. Every follower regains 90% cap within ten seconds after clearance; the last one-sided follower does so **2.80 s** after clearing. Side-choice counters record intentions across the maneuver, not exclusive final routes.

Full race: **548 per-NPC low-speed obstruction episodes**, **12 secondary contact-counter increments**, longest interval with at least three low-speed queued racers **4.10 s**. Mean completed obstruction episode **0.77 s**; mean completed recovery to 90% cap **5.78 s** (252 recoveries). These are not 548 unique crashes; detection can separate brief episodes. Recovery means exclude unfinished/interrupted recoveries. Equivalent detailed baseline counters were unavailable.

## 11. Contact and finish metrics

| Metric | Baseline | Final |
|---|---:|---:|
| NPCs finishing ordered three laps | 19/19 | 19/19 |
| Mean moving speed | 22.87 mph | 22.62 mph |
| Moving time above 30 mph | 32.85% | 31.62% |
| Mean finish | 367.56 s | 368.16 s |
| Last finish | 378.90 s | 382.10 s |
| Summed kart contacts | 28 | 23 |
| Launch contacts | 0 | 0 |

Contacts sum per-kart counters and may count both participants; they are not unique incident pairs. Pace is close to baseline but slightly lower, not faster. Existing delayed finisher hiding, frozen results and reset tests pass. No new post-finish behavior was needed. Detailed per-NPC results are in [METRICS.md](METRICS.md).

## 12. Remaining limitations

No new human-driven or rendered visual test was performed. The supplied clips were sampled, not watched continuously; exact position-gain causality cannot be reconstructed from their original F9 CSVs. One deterministic track/profile setup does not cover every human battle or random incident. Defense often releases for speed/occupancy, pass timeouts remain high, and one blocked follower takes 27.35 s to escape. The first-lap P20-to-P1 success criterion remains unverified until human playtesting. No hidden boost, global collision change, checkpoint widening or global handling increase was introduced.

## 13. Exact manual PIE checklist

1. Open the original `D:/Boring/GitHub/Road-To-F1/RoadToF1/RoadToF1.uproject` in UE 5.8.3 and load `/Game/RoadToF1/SouthGarda_KartRace`.
2. In the console enter `RoadToF1.BattleDebug 1`. Start a video capture; press F9 at the start of the run. Keep the original CSV and matching `.battle-v2.csv` from `RoadToF1/Saved/Training/Telemetry/`. Sidecar time is relative to F9, not necessarily race start.
3. Run a clean first lap from P20. Record first times reaching P15, P10, P5 and P1. Do not infer them solely from the original training CSV. Check whether defense actually delays your pass.
4. Approach a rival on a straight with a modest closing advantage. Check one early deliberate move, retained speed, no weaving or late chop. Repeat from the other side and when already alongside.
5. Hold a safe side-by-side corridor into a bend. Check room at the apex and exit, stable lane commitment and no unjustified emergency braking. Leave a safe repass opportunity and observe whether the NPC uses it.
6. In a separate run, observe a naturally occurring dense incident or reproduce a light contact in traffic. Record how following karts choose routes, whether queues propagate, whether reverse starts only with clear rear space, and how long the last delayed kart takes to clear. Do not judge only the lead kart.
7. Complete all three laps. Check official results freeze and finishers coast before disappearing; observe any brief post-finish overlap. Leave the session running long enough to see the delayed NPCs finish.
8. Stop F9. Use F5 both after a finish and in a separate mid-race incident. Check the grid, launch, positions, timing, visible racers and normal forward behavior reset, with no stale defense/recovery state.
9. Check Tab standings, automatic HUD fades, MPH display, badges, engine audio and commentary during these runs. These passed automated regressions but need visual/audio confirmation.
10. Run `python TestResults/DefenseIncident/analyze_session.py "<capture.csv.battle-v2.csv>"` to obtain heuristic gain categories and position milestones. Compare at least two runs with video, especially early easy passes, long queues and contact variance. Disable extra diagnostics with `RoadToF1.BattleDebug 0` when finished.

Await human playtest approval. **Do not commit, push or merge this candidate.**
