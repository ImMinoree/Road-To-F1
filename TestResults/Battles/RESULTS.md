# Human-versus-AI racecraft — local playtest candidate

Branch: `fix/packed-race-stability`. HEAD: `761e6d0bddfe3e6dc3a90e6b2d9e58dbeb9ddc82`.
No commit, push, merge, project copy, map edit, or asset replacement. Earlier uncommitted stability/pace work is preserved. User resolved the conflicting cap instructions: **player 57 / NPC 55 km/h**.

## 1. Confirmed root causes and evidence

- The starting controller had no defensive state, defensive cooldown, or memory of losing a position to the player. It could avoid traffic but could not deliberately hold a defensive line or identify a repass opportunity.
- Lane planning could select a passing lane before the consideration timer elapsed. Intent registration required another lane change, so an already-started maneuver could remain untracked. Promotion now recognizes an existing safe maneuver after consideration.
- There was no explicit side-overlap corridor hold. Ordinary lane selection could resume while another moving racer remained alongside. A safe intended corridor is now held until longitudinal overlap clears.
- Pass cancellation causes were not counted. Final full-race counters show 26 occupancy rejections, 16 timeouts, and 7 intermediate-corridor contact-risk cancellations. These are conservative controller decisions, not proof that every rejected pass would have collided. No direct corner/guidance/speed-loss cancellation exists; those counters correctly remain zero. Their speed limits are recorded separately.
- Finishers coasted to a stop with existing kart collision filtering and remained visible indefinitely. This allowed parked visual accumulation. Delayed presentation retirement removes that accumulation without changing official results.
- Fresh instrumented baseline reproduces the previous results: 15/15 suites, 22.72 mph moving average, 376.54s mean finish, 487.50s last finish, 42 summed per-kart contacts.
- Existing human CSV evaluation is in `HumanEvaluation.json`. The 4-contact session averages 25.92 mph during the first 100 seconds and 32.69 mph during seconds 100–300 before finishing. Another session records 18 contacts. Existing CSVs do not contain official position: the approximately 94-second P20-to-P1 observation remains attributed to the user's video, not independently reconstructed from telemetry. These recordings were evaluated, not used to train or install profiles.

## 2. Implemented

- Bounded one-side defense against a closing player or AI: choose a side on a straight, require a safe corridor and enough longitudinal gap to finish the lateral move, hold for 2–3 seconds, then apply a six-second defense cooldown. Existing aggression influences lane magnitude and hold duration. No new speed boost or physics change.
- Do not initiate blocking against a significantly alongside rival. Moving side overlap holds an already-safe intended lane, with entry/exit hysteresis. Physical occupancy and predictive checks still override the hold.
- Six-second player-rival memory after a local position loss on the same lap. Repass requires proximity, genuine speed advantage, suitable straight geometry, a moving non-burning rival, and a safely faster adjacent corridor. It is optional, not forced.
- Safe passing intent remains committed through overlap. Already-selected passing lanes can acquire explicit intent once consideration has elapsed. Existing eight-second timeout remains bounded; it was not blindly lengthened to improve completion counts.
- Per-NPC battle counters and explicit cancellation categories. Optional development-only, buffered 5 Hz battle CSV accompanies F9 recording when launched with `-RaceBattleDebug`. No normal Tick log spam and no change to the original F9 schema.
- Finished NPCs retain actors and official results, coast under the existing finish logic, then hide only after at least four seconds and below 1 km/h. They are not teleported or destroyed at the line. F5 restores visibility and all battle state. Existing post-finish collision filtering remains; active racing collision is unchanged.

## 3. Files changed in this phase

- `RoadToF1/Source/RoadToF1/KartRaceDirector.cpp` and `.h`: racecraft state use, decision logic, diagnostics, buffered sidecar lifecycle, finisher retirement.
- New `RoadToF1/Source/RoadToF1/KartBattleState.h`: isolated battle state and outcome definitions.
- `RoadToF1/Source/RoadToF1/KartPawn.cpp`: reset restores actor visibility. No acceleration, steering, speed cap, or collision-physics retuning.
- New `RoadToF1/Source/RoadToF1/Tests/BattleTests.cpp`: controlled real-actor battle regressions and F9 compatibility checks.
- `RoadToF1/Source/RoadToF1/Tests/KartIntegrationTests.cpp`: full-field battle counters and delayed finisher visibility assertion.
- `.gitignore`: retain baseline/final JSON; keep intermediate exports local without deleting them.
- `BUILD_LOG.md`, `TestResults/Battles/RESULTS.md`, `METRICS.md`, `HumanEvaluation.json`, `CaptureSmoke.json`, `summarize.py`, `analyze_session.py`, and baseline/final JSON evidence.

Other modified/untracked files shown by Git include the user's earlier packed-race and pace work; they were not reverted or claimed as newly created here.

## 4. Tests added and retained

New battle suite tests closing-attacker defense; fixed-side hold; actual moving defense without contact; no blocking when alongside; separate physical corridors; safe pass commitment during overlap; normal player proximity avoiding emergency obstruction cap; successful real-controller player repass; no distant repass; corner-entry corridor selection; delayed finish retirement; reset; and optional sidecar flushing without changing the training header.

The existing suites retain launch, train, normal moving-rival pass, stopped/two-kart blockage, reverse/recovery, ordered checkpoints, all-19 three-lap completion, finish results, F5, HUD, presentation, audio and training checks. The new full-race assertion verifies that all finished NPCs have retired their visible parked presentation by the end of the run.

## 5. Automated results

Fresh `Final/index.json`: **16/16 suites passed**, zero test errors/warnings. Fresh baseline: 15/15. Tests run real actors and swept movement in headless PIE on South Garda, not a synthetic replacement movement model.

Editor Win64 Development build passed (20.00 seconds). Standalone Win64 Development build passed (243.64 seconds, including cold compiler/PCH loading). The final battle CSV was also parsed successfully: 19 NPC rows with all 47 fields present. `git diff --check` passed; Git notes an existing header line-ending normalization warning, not a whitespace error. No packaged/cooked/Steam build was claimed.

## 6–8. Battle, contact and full-race metrics

| Field metric | Baseline | Final |
|---|---:|---:|
| Moving average speed | 22.72 mph | 22.87 mph |
| Moving time above 30 mph | 31.97% | 32.85% |
| Mean NPC finish | 376.54s | 367.56s |
| Last NPC finish | 487.50s | 378.90s |
| Summed per-kart contacts | 42 | 28 |
| Tracked passing attempts | 63 | 52 |
| Tracked completions | 3 | 3 |
| Completion ratio | 4.8% | 5.8% |
| Defensive activations | not implemented | 45 |

Contacts are per-kart counters, not unique collision pairs. All 19 NPCs finish three ordered laps. Full-race player is parked; player repass counters are therefore zero and do not measure human competition. The controlled player fixture records one loss, one repass attempt, one completed repass, and zero contacts. The alongside fixture runs three seconds with zero contacts and minimum NPC speed 41.02 km/h. Normal moving-AI pass remains successful with zero contacts, no lane flips, and no emergency cap. Launch remains zero-contact.

Per-NPC finish/speed/traffic/braking/contacts/pass/defense/side-overlap/loss/repass metrics and cancellation counts are in `METRICS.md`. Final 52 attempts reconcile to 3 completions + 26 occupied + 16 timeout + 7 contact-risk cancellations. Counts also reflect the repaired intent registration; they are not purely a behavioral before/after measure.

## 9. Post-finish result

The single-finisher test confirms visibility at the finish instant and hidden presentation only after cooldown/stopping. The full-race test confirms all 19 finished NPCs are hidden rather than left as a permanent parked stack. Reset restores all 19. This does not prove that moving ghosted finishers never briefly overlap during coasting; existing collision filtering is retained, and that visual transition needs manual review.

## 10. Remaining limitations

- **Not yet proven that a human cannot reach P1 in roughly one lap.** There is no new human full-race evaluation yet, and automated player fixtures are not presented as a fair human replay.
- Absolute tracked full-field pass completions remain three. Safe controlled passes/repasses work, but passing frequency in dense competition is still limited. Occupancy and timeout diagnostics identify the next investigation rather than justify removing safety.
- Corner-entry corridor selection is tested; prolonged human-controlled side-by-side corner battles and all narrow-track situations still need manual testing.
- One deterministic map/profile setup is not proof across all incident patterns or human steering. Full-field contacts are reduced, not eliminated.
- The first iteration regressed contacts to 53. It was not retained as the final candidate; the gap/time defense check and safe intended-corridor hold improved it. Intermediate evidence remains local.
- Sidecar time begins with F9 capture, not race/video time. Five-Hz positions and counter changes provide context; they do not establish causal classifications such as 'clean overtake' or 'position gained because of incident.'
- Full original F9 recorder/learner behavior is preserved. The new sidecar is evaluation-only and is never fed to the learner.

## 11. Exact manual PIE checklist

1. Open the original project using UE 5.8.3 with `-RaceBattleDebug` appended to the editor launch command. Do not create a conversion copy. Open `/Game/RoadToF1/SouthGarda_KartRace`, then Play.
2. Press F9 before accelerating. Verify the original dynamic HUD, audio/commentary, MPH display, badges, and 20-racer field. Launch from P20 and watch for grid contact or lateral crossing.
3. Close on an NPC on a straight with a modest speed advantage. Expect at most one deliberate defensive move, sufficient room, and a bounded hold. Record any late block or repeated side changes.
4. Establish overlap on each side before the braking zone. Check that the NPC does not turn through you, immediately surrender throttle, or fall to the emergency obstruction speed. Repeat into a representative bend and exit; inspect contacts and checkpoint validity.
5. Pass an NPC, then allow it a genuine safe speed advantage for several seconds. Check for a safe repass. Repeat after opening a large gap; no forced repass should occur.
6. Drive a complete three-lap race. Record approximate P20/P15/P10/P5/P1 timestamps and contacts, especially through lap 1. Repeat a second race to assess variance. Do not use these recordings for training without separate approval.
7. Observe finishers: results freeze immediately; karts coast; stationary NPC presentation disappears after a delay. Check for awkward moving overlap during that delay and for any permanent parked stack.
8. Press F5 while racing, during a battle, and after finishing. Check the full field reappears in grid slots, results/timers reset, launch holds, and no stale defensive/repass state remains.
9. Stop F9. Keep matching video and the original CSV plus adjacent `.csv.battle-v1.csv`. Run `analyze_session.py <sidecar path>` for actual position milestones and nearby context. Report capture/video offset and any problematic timestamp.

Sidecar numeric enums: pass Follow=0, Consider=1, Committed=2, Passing=3, Clear=4; defense Normal=0, Holding=1, Released=2. `ahead_cm` positive means player ahead; `side_cm` is signed track-right offset; `closing_cms` positive means player is faster along the NPC's route direction. Distances/limits are centimeters and cm/s; explicit speed field is km/h. Rival is kart number, zero when none. Counters are cumulative per reset. Output is buffered and flushed on stop/reset/endplay or buffer threshold; it is absent in Shipping builds.

Publication remains held for human playtesting and explicit authorization.
