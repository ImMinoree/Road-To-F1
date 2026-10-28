# Current ten-kart defaults

Normal Play uses nine AI in slots 1–9 and the player in slot 10. All use the current articulated player kart, distinct kart/driver colors, and a shared 38 mph top speed. See [current validation](Evidence/TenKartGrid/README.md). Full ten-kart lap completion has not been validated.

The four-opponent implementation and results below are historical; the older five-pawn validation scripts target that configuration.

# Four track-edge opponents

Normal Play in DesertKarting_Visual creates four additional ProofPawn racers in existing grid slots 2–5. The player keeps slot 1. There are no placed duplicate pawns, second game mode or additional countdown. RestartRaceStart stages the same participants again. The existing gate blocks all five karts until the authoritative lights-out event.

TrackRacingAI is an input-planning component on ProofGameMode. It supplies throttle and steering to the existing movement implementation. Its 748 paired boundaries are read from the original asphalt polygon vertices with the existing map alignment. It measures lateral clearance, follows the verified route, anticipates bends, adjusts speed for traffic and only requests passing lanes inside the asphalt corridor. Progress follows contiguous route sections to avoid selecting the wrong leg of a hairpin.

The opponents reuse SM_PlayerKartChassis, SM_FP_SteeringWheel and A_FP_KartSteering. SK_AI_KartDriver is the existing full V5 driver on the original first-person grip-bind skeleton. Its steering pose and wheel rotation share the same input. No source Blender file is overwritten. Wheels retain the prototype's fixed spin/linkage presentation.

This is deterministic driving logic, not a trained neural network. Neuroevolution remains a future experiment. The optional RacingAIPlayerTest flag supplies a diagnostic driver for the human pawn only during automated tests.

## Validation

Build Road_To_F1_NewEditor Win64 Development. RoadToF1.RacingAI.EdgesAndPresentation checks paired boundary data, inset lane requests, rejection of swapped edges and reuse of the driver skeleton.

For the accelerated race launch UnrealEditor-Cmd with the project and DesertKarting_Visual plus `-game -nullrhi -benchmark -fps=60 -RacingAITest -RacingAIPlayerTest`. Success requires two laps from every opponent, 64 visited track sectors, no movement before lights-out, one start event and no asphalt-edge excursion beyond the footprint tolerance.

Run Tools/validate_racing_ai_pie.py in a rendered editor with both diagnostic flags for actual grid/launch/racing screenshots and the five-pawn PIE check. It uses a temporary camera and never saves either map. Evidence is in Evidence/RacingAI. A successful build does not establish lap completion.

The user approved equal steering tuning for all five karts after the initial runs exposed the original 14.1 m minimum turning radius. SteeringYawRateAtTopSpeed is now an editable 240 degrees/second coefficient at the existing 1600 cm/s reference, giving a minimum radius of approximately 3.82 m. The original acceleration, drag, maximum speeds, swept movement and road-following trace are retained. The planner derives its steering normalization from that same property, so opponents receive no separate steering advantage.

The final moving-player test completed two full laps for every opponent, all 64 sectors visited, zero asphalt-edge excursions, zero movement before lights-out, one start event and no recoveries. The diagnostic player also completed more than two laps. This uses actual Unreal gameplay with a fixed 60 Hz simulation, not a separate mathematical replay. Failed earlier diagnostic logs are retained for provenance.

The stationary-player test also passed at 30 Hz: all four opponents completed two laps, all 64 sectors, with zero measured edge excursions or pre-start movement. Two opponents each used three clearance-checked backoffs to get past the stopped player. The final rendered PIE run confirmed five pawns, four visible moving opponents, one authoritative start and unchanged map files. The three actual PIE PNG captures are 1600 by 900 and were decoded successfully. Both Unreal automation tests passed. Tools/verify_racing_ai.py checks these saved results and writes Evidence/RacingAI/validation_summary.json; it does not substitute for running Unreal.

Passing is limited to sufficiently straight approaches. Stopped queues may back off only after a sustained stop and clearance checks for karts and static geometry behind them. These rules prevent a passing attempt into the tight hairpin and give a stuck leader room to recover. Collision still uses the existing small swept sphere; production chassis/contact physics and wheel spin/linkage animation remain outside this prototype.

