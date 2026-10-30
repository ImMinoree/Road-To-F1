Implemented competitive racecraft in the existing `UTrackRacingAI`; normal Play now defaults to four opponents. Open `/Game/RoadToF1/Maps/DesertKarting_Visual` and Play. No additional game mode, pawn, track asset, physics model, teleport or catch-up boost was added.

The old implementation assigned every driver the same zero lane preference and speed target, disallowed passing whenever a bend was detected within 28 metres, periodically reset pass targets, and continued matching a leader's speed even after selecting another lane. Lane validation used center-relative values while target generation added the guide offset again.

The new planner uses actual paired edges with a 175 cm target inset, guide-relative curved trajectories, two predicted pass corridors, 1.5-second longitudinal gap prediction, bounded 18-second pass commitment, safe abort/merge states, and lane retention during overlap. Defense begins before overlap, moves inside by at most 85 cm, and has a cooldown. Lateral targets change at 101–119 cm/s with the default personalities; vehicle motion still comes entirely from the shared tire simulation. Recovery checks rear traffic and geometry, prohibits reversing alongside, and limits blocked-leader backoff to once per 60-second window. It can wait for space rather than forcing a pass.

Four `Drivers` profiles expose aggressiveness, braking confidence, passing preference and consistency on the existing racing AI component. Defaults respectively use aggressiveness 0.4/0.75/0.6/0.85, braking confidence 0.82/0.94/0.88/1.0, passing preference -1/+1/0/-0.5, and consistency 0.88/0.91/0.94/0.97. Identical kart physics and the shared 38 mph ceiling are preserved. `bEnableRacecraft=false` retains the old planner as a reversible fallback. Configure profiles before starting Play.

Measured normal competition, aggregated across two 180-second races (normal and reversed AI grid orders):

| Measurement | Original baseline | Final racecraft |
|---|---:|---:|
| Completed kart-laps | 10 | 10 |
| Confirmed overtakes / pairwise position exchanges | 0 | 22 |
| AI-versus-AI exchanges within that total | 0 | 9 |
| Planner-confirmed defensive holds | 0 | 15 |
| Per-kart non-ground contact episodes | 0 | 0 |
| Sustained off-track events | 0 | 0 |
| Raw body-edge excursion time | 0 s | 0 s |
| Stuck time after the first five racing seconds | 0 s | 0 s |

Final grid-order results were 14 and 8 exchanges, including 6 and 3 between AI opponents; each race completed five kart-laps. Defensive holds were 4 and 11. All five racers used matching mass, engine force, steering limit, tire stiffness and speed cap. Each race had exactly five staged participants and one lights-out event.

These were actual headless Unreal PIE races on the saved circuit, with the existing opt-in diagnostic autopilot driving the player for repeatability. The fixed timestep was 1/40 second, with the unchanged tire dynamics internally substepped. Only the pre-race grid ordering was changed between trials, through transient grid-slot numbering; no racer was repositioned during competition. The old binary spawned nine opponents by default, so excess opponents were removed before countdown to establish the five-kart baseline. The final binary naturally spawns exactly five total karts.

An exchange requires a pair to reverse signed, unwrapped route progress with 250 cm clearance and one second of confirmation, after the first five racing seconds. This measures real position changes, not different lane offsets. A contact episode is a rise in the existing physics collision counter, separated from the previous episode by more than 0.5 seconds; ground contacts are excluded by the physics implementation. Track checks project the kart's 90-by-60 cm collision half-extents onto the sensed road normal. An off-track episode requires more than 0.3 seconds outside the road polygon, but raw excursion time and maximum excess are also recorded; both final trials recorded zero raw time. Defensive holds are planner events after three seconds of inside defense with a pursuer still behind. Target-specific planned-pass completion counters are more conservative than overall order exchanges: four planned passes completed, 24 were safely aborted, and two were still active at the race endpoints.

A separate 65-second stalled-grid test held the existing pole kart stationary from lights-out until 18.05 seconds, without changing its position. It is excluded from competitive pass counts. There were zero contacts and edge excursions; one follower waited 7.9 seconds and subsequently resumed. All five racers advanced more than 439 metres by the end. Bounded recovery guards also pass focused unit tests. This is safe waiting/recovery evidence, not a claim that every permanently blocked route can be bypassed.

Build and focused automation passed. `baseline.json`, `after.json`, `blocked.json`, `Automation/index.json`, `build_verified.log` and `protected_validation.json` contain the results. The six protected map/player/physics hashes are unchanged. Existing cockpit, HUD, countdown and scenery assets were not edited. `Checkpoint/` preserves the previous AI sources and prior native-test JSON evidence. Earlier safety-tuning attempts are retained separately; their brief body-edge excursions are not the final results.

Limits: two starting orders and short races, not endurance or large-grid validation; player behavior during measured races was automated, not human input. No rendered race capture, multiplayer test or GPU benchmark was performed. The planner deliberately favors aborting or waiting over aggressive contact. No commit, merge or push was performed.
