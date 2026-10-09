# AI Agent for game training

This directory contains the offline part of RoadToF1's NPC training workflow. The first implementation fits **bounded driving tendencies from recorded telemetry**, then creates 19 different driver profiles. It does not replay the human's route or steering inputs. The existing Unreal planner still chooses actions from current track geometry, nearby karts, and hazards.

No real player dataset or gameplay video was supplied during implementation. Demo data is explicitly synthetic. This is statistical tendency fitting, not reinforcement learning, a neural driver, or proof that the NPCs are stronger. Parameter diversity is tested; convincing movement must also pass races and human inspection.

## Modules and responsibilities

| Module | Implementation | Output |
| --- | --- | --- |
| Telemetry collection | Unreal recorder, outside this directory | Per-session CSV |
| Input validation | `training_agent/telemetry.py` and `common.py` | Validated finite samples with session/track boundaries |
| Context analysis | `training_agent/learning.py`: `summary`, `contexts` | Pace, smoothness, incident and conditional braking statistics |
| Behaviour learning | `training_agent/learning.py`: `tendencies`, `fit_telemetry` | Conservative aggregate priors |
| Style variation | `training_agent/styles.py` | Independently stratified aggression, corner precision, lane preference and decision commitment |
| Evaluation | `training_agent/evaluation.py`, tests | Descriptive holdout gaps, profile distances and bounds |
| Video intake | `training_agent/video.py` | Separate manually annotated tendency priors |

The training subagent can review these outputs, inspect supplied videos or extracted frames, suggest annotations and profile revisions, and compare race outcomes. The code provides a repeatable workflow rather than an autonomous agent watching the desktop in the background.

The Python toolkit and Codex subagent are development tools. They are not a Python subprocess or hosted Codex agent inside a Steam build. The packaged counterpart is native Unreal telemetry/profile code, compiled for gameplay builds. Recording is off by default; F9 is an explicit local testing opt-in. Future signup-based collection needs a separate consent flow before automatic capture. No signup, network upload, cloud account requirement or background collection is implemented here. Packaging/licensing and distribution testing remain separate work.

## Record the player in our game

Use the original South Garda project. The Unreal integration records at 10 Hz with **F9** to start/stop. Files go to `RoadToF1/Saved/Training/Telemetry/<guid>.csv`. Restarting with F5 begins a new session/file if recording is enabled. Controls and positions remain local input data.

Collect at least two separate sessions on one track; four or more are better. Include clean fast laps, cautious laps, braking into different corner shapes and traffic encounters. Split sessions should ideally come from separate runs; related copies of the same run must share the same session ID and must not be disguised as independent sessions. Holdout splitting can only enforce the IDs provided. A single session is rejected rather than silently training and testing on the same run.

CSV required header:

```text
time_seconds,session_id,track_id,route_index,lane_cm,speed_kmh,throttle,steering,brake,collision_count,burning
```

Optional columns:

| Field | Meaning |
| --- | --- |
| `curvature` | Absolute route curvature in 1/cm; ≥0.0002 marks a bend with radius ≤50 m |
| `nearest_ahead_cm` | Distance to a kart ahead; empty if none |
| `relative_speed_kmh` | Player minus kart ahead speed; positive means closing; empty if none |
| `next_checkpoint`, `completed_laps` | Nonnegative race progress values, validated but not replayed |
| `x_cm`, `y_cm`, `yaw_deg` | Optional recording context; not consumed or exported by this fitter |

Controls must be finite: throttle/brake 0–1, steering −1–1. Speed is nonnegative. Time must strictly increase and collision counts cannot decrease inside a session. Track IDs cannot change inside a session; mixed tracks are rejected during fitting. The prototype ID is `SouthGarda_KartRace`.

Combine completed recordings into one CSV with one header, preserving distinct session IDs. Keep raw recordings in ignored `local-data/` or Unreal's ignored Saved directory. Do not commit recordings accidentally.

## Fit a candidate

Python 3.10+; standard library only. From this directory:

```powershell
python train.py telemetry local-data/player_sessions.csv --output candidate-runs/candidate_001.json --seed 42
python -m unittest -v test_training.py
```

Output filenames must be fresh; the CLI refuses to overwrite files. A seeded split reserves 25% of whole sessions (at least one) for holdout. Holdout samples never influence generated profiles. Each session has equal weight; per-session means are weighted by actual elapsed time, rather than uneven sample frequency.

Training reports straight/corner pace, brake fraction, near-traffic and closing-traffic behaviour when optional fields cover at least one second per context per session. These are correlations. They do not establish whether a human's braking, apex, overtake or speed was optimal. Pace and control smoothness influence bounded general priors; closing-traffic braking makes a small cautious adjustment only with coverage in at least two training sessions. Corner speed is reported rather than copied as a target. The runtime planner remains responsible for geometry-aware corner speed and collision avoidance.

The exported policy contains **no timeline, input route indices, coordinates, recorded steering sequence, or session identifiers**. Lane preference is a moderate aggregate bias; independent variation spreads the field across the approved lateral bounds. Different seeds create different reproducible fields. The player and NPC speed limits remain 57/55 km/h in Unreal.

## Review and deploy explicitly

`profiles.schema.json` documents schema version 1. `racer_index` is 1–19. Runtime parameters are bounded to aggression 0.25–0.97, corner skill 0.95–1.0, preferred lane −130–130 cm, decision commitment 1.2–3.5 seconds. Current movement safety, checkpoint rules and speed caps override preferences.

The fitter never installs a policy. To opt in after reviewing it, copy the approved candidate JSON to `RoadToF1/Saved/Training/approved_profiles.json`, then start a fresh gameplay session. The Unreal loader validates the version, track, count, IDs, finite bounds and nonzero diversity. It accepts provenance telemetry or observations; it rejects synthetic_demo as well as invalid profiles and retains built-in drivers. Remove or rename the approved file to return to defaults. Profiles are loaded at race startup, not mutated during racing.

Compare default and candidate drivers in the same scenarios, with several seeds and grid positions:

1. All 19 NPCs must complete the intended laps and ordered checkpoints. No speed-cap violation.
2. Compare collisions, time stuck, recoveries and near-crash avoidance to the default field.
3. Inspect lane-change frequency, overtaking attempts and position changes; reject periodic left/right motion.
4. Inspect a mixed field entering a corner and approaching a blocked road; different preferences must not override collision avoidance.
5. Test route/starting-speed/traffic changes outside training conditions. A session holdout on South Garda cannot establish performance on an unseen circuit.

Holdout aggregate gaps reveal data mismatch, not race completion or a trained model's prediction accuracy. Distinct parameters do not guarantee visibly distinct trajectories. Approval therefore depends on live race results, not just the exported diversity score.

## Synthetic smoke test

```powershell
python train.py demo --directory candidate-runs/demo_001
```

This creates clearly named `SYNTHETIC_telemetry.csv` and `SYNTHETIC_profiles.json` with `training.source = synthetic_demo`. It validates the pipeline only; do not present it as learning from a player or install it as a proven improvement.

## Video analysis: separate, optional workflow

Telemetry is the primary path. Video support is a manual observation workflow, ready for future supplied clips. If FFmpeg is already on PATH:

```powershell
python train.py frames local-data/race.mp4 --directory local-frames/clip_001 --interval 2
```

This samples at most 600 frames, scales to 1280 px width and saves source hash/provenance. It refuses an existing frame directory. It does not install FFmpeg or download media. With no FFmpeg, review the clip in a video player. Sparse frames alone cannot show precise steering or collision timing; use the full video for motion when possible.

Make a CSV using `observations_template.csv`. One row summarizes an observed situation; repeat rows for multiple situations per clip. Use different `clip_id` values for genuinely independent clips, not frames from the same video. At least two independent clips are required. Annotation definitions:

| Field | Scale |
| --- | --- |
| `confidence` | 0.01–1: clarity/reliability of the observation |
| `pace_fraction` | 0–1: approximate pace from visible speed UI; descriptive only |
| `aggression` | 0–1: observed willingness to attempt an overtake |
| `corner_precision` | 0–1: subjective smoothness/consistency; not ground truth skill |
| `lane_bias` | −1–1: broad left/right preference relative to travel direction |
| `decision_seconds` | 1.2–3.5: approximate commitment before reconsidering a lane choice |

```powershell
python train.py observations local-data/observations.csv --output candidate-runs/video_candidate_001.json --seed 42
```

Confidence weights annotations within each clip; clips receive equal weight, with whole-clip holdout. Video candidates are explicitly marked `observations`, independent from telemetry candidates. A monocular video does not automatically provide steering input, calibrated track coordinates, reliable hidden opponents or a causal driving strategy. The subagent must describe uncertainty and provenance rather than invent measurements. Do not merge video observations into exact telemetry as if they had the same accuracy.

## Validation performed

Eleven unit tests passed on 2026-10-09: malformed/nonfinite input rejection, session restart/order validation, whole-session holdout independence, track separation, minimum session count, deterministic bounded diversity, forbidden replay-data exclusion, optional context aggregation, observation holdout/bounds, missing-FFmpeg handling, reverse telemetry excluded from skill and reverse-only sessions lacking skill coverage. Synthetic CLI output is separately labelled. No real-player learning quality or video inference performance has been tested yet.

## Native packaged candidate generation

The native candidate generator requires at least 300 clean samples, including 20 corner and 20 straight samples. It writes an experimental candidate only, without activating it. Native fitting has no session holdout, so offline evaluation and live-race review remain essential. Automated Unreal capture tests validate recorder mechanics; they are not human driving data or evidence of learned human skill. Python modules stay development tooling; the native module is the packaged counterpart.

An approved JSON can also be staged at `RoadToF1/Content/Training/approved_profiles.json` as a UFS resource for a packaged game. A valid Saved/Training approved JSON provides the local override. The same validation and human review apply; do not bundle an unreviewed experiment. Native gameplay-target compilation and a distributed Steam package are separate checks; a successful editor test alone does not prove packaging or Steam installation.
