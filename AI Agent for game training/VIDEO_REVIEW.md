# Gameplay clip review: launch and NPC movement

This review starts from two supplied files, `bad start.mp4` and `trial 1.mp4`. Their file timestamps precede the current recorder implementation. No associated human telemetry is available. File names are labels, not evidence that a particular failure occurred. The trial clip has now been reviewed through all 13 contact sheets and selected full frames; observed findings are recorded below. The initial code review remains a list of **code-derived hypotheses**, separately identified from video evidence.

## Code-derived launch hypotheses to check

| Hypothesis | Source evidence | Visual evidence needed |
| --- | --- | --- |
| Player reversing unintentionally releases the whole field | `KartRaceDirector::Tick` releases when absolute player speed exceeds 0.5 km/h, including reverse | First moving frame, whether player moves backward while NPCs launch |
| Legitimate waiting becomes unsafe reverse recovery | Any speed below 30 cm/s for three seconds can trigger 1.2 seconds of reverse, unless fire is ahead. A stopped ordinary kart does not suppress recovery | Kart initially waits safely behind traffic, then backs into the following row without a wall blockage |
| Early grid convergence compounds crowding | Authored slots are about 400 cm apart laterally; row spacing is about 500 cm. Initial internal lane state is ±130 cm although physical grid lanes are about ±200 cm. Drivers steer inward immediately | Simultaneous inward movement at launch, contacts before first corner, lane-target mismatch |
| Lane-change safety ignores transient actual lateral offset | Lane-crossing rejection uses internal `State.Lane`, not the actual measured lateral projection of the kart. This can differ during initial convergence or after a collision | Side contact during a supposedly safe lane change; recovery yaw/lateral offset differs from planned lane |
| Sequential simulation can make tightly packed traffic inconsistent | Director updates opponents in array order; safety reads current actor speeds/positions. Kart actors tick after the director, but speed values reflect the preceding frame, including contacts | A repeatable particular grid position rear-ends a slowing kart; need controlled replay, not just appearance |
| NPCs keep racing after their finish state | FinishPlace is recorded, but Tick does not immediately brake finished opponents | Relevant only at race end, not evidence of a start failure |

Kart collision boxes have half extents 98×63 cm. Authored grid gaps alone are not overlapping these boxes. Initial spacing being numerically safe does not guarantee safe subsequent movement. A hard relative impact ≥700 cm/s (~25.2 km/h) triggers six seconds of fire; lesser contacts may stun without flames. Fire visible in a clip does not identify the original collision cause.

## Review procedure

1. Preserve source clips. Extract limited sample frames into ignored `local-frames/` and save source hashes, frame timestamps and extraction settings. Use full motion or denser sampling around contacts; a sparse frame montage cannot establish contact order.
2. Review each clip independently. Mark gameplay start, first player movement, first NPC movement, first approach to traffic, contact, recovery and reset. Read HUD speed/position only when legible; do not infer exact steering from camera rotation.
3. Record evidence in `video_event_review_template.csv`. Distinguish `observed`, `uncertain` and `not_visible`. Identify the actual visible actor if possible; an unreadable kart number stays unknown.
4. Classify each interval: `clean_reference`, `failed_launch`, `blocked_wait`, `collision`, `recovery`, `reset`, or `uncertain`. Incident clips are useful regression scenarios, not positive driving policies.
5. Only clearly observed, clean forward-racing intervals may be manually summarized into the existing `observations_template.csv` for fitting. Review CSVs are not fitter inputs. Never copy all failure-event rows into the tendency fitter. No exact input sequence is recovered from video.
6. Test any proposed launch fix with controlled forward and reverse player starts, stationary player, two-lane queue, blocked lead kart without fire, fire hazard, varied grid position and low/high frame rates. Check contact counts, reverse recovery, time to clear grid and retained checkpoint correctness.
7. Tune or deploy only after code tests and gameplay review. The review itself does not approve a policy or change existing profiles.

The two clips cannot yet supply a credible clip holdout for skill learning unless independent clean intervals are actually found in both. Failure-only clips should remain an evaluation set. Do not relabel frame fragments of one recording as independent clips.

## Event annotation schema

| Column | Meaning |
| --- | --- |
| `clip_id` | Stable label; source hash stored separately |
| `start_seconds`, `end_seconds` | Approximate verified interval in the source video |
| `event_type` | One of the interval classes above |
| `actor_number` | Legible kart number or `unknown` |
| `evidence_status` | observed / uncertain / not_visible |
| `confidence` | 0.01–1; reflects visibility rather than confidence in a theory |
| `visible_speed_kmh` | HUD speed if readable; blank otherwise |
| `description` | What was visible, separating observation from interpretation |
| `hypothesis` | Optional code-derived explanation, explicitly unconfirmed |
| `eligible_for_reference` | yes only for verified clean forward behaviour; otherwise no |
| `frame_refs` | Extracted frame filenames/timestamps supporting this interval |

When new recorder sessions are available, telemetry should establish actual signed speed, controls, lane position, nearby traffic and incident counts. Old video alone cannot manufacture those exact measurements.

## Observed trial 1 findings — 2026-10-09

Source duration is 310.7 seconds at 60 fps, 2560×1440. Reviewed extraction samples occur at odd seconds, two seconds apart, with 155 frames. Paths are ignored local assets under `local-frames/20261009-review/trial_1/`; times below refer to the video, not the lap timer. Sparse sampling establishes incident states, but cannot identify the exact first contact or held keys.

| Approximate video time | Direct observation | Reference eligibility |
| --- | --- | --- |
| 1–5 s | Field stationary in the grid; player HUD position 20, speed 0 | No: stationary setup |
| 7–11 s | Player accelerates: HUD 17 km/h at 7 s, 38 at 9 s, 57 at 11 s. At 11 s player is position 14; several NPCs show 0–12 km/h and a burning kart is visible at left | No: launch incident scenario |
| 15 s | Player is first at 57 km/h, on the opening straight. NPC #1, #2, #3 and #19 rows are orange at 0 km/h | No: explicit incident regression evidence |
| 17–89 s | Player drives largely alone, crosses ordered checkpoints and completes lap one. At 91 s HUD shows lap two with last lap 1:17.954 | Candidate clean driving intervals after individual review; no exact control inference |
| 137–143 s | At 137 s player approaches purple-suited traffic at HUD 57. By 139 s player and purple kart immediately ahead both have visible flames; player HUD FIRE/recovering, 0 km/h through 143 s | No: collision/recovery. Which vehicle initiated contact is not established |
| 145 s | Player begins moving again, HUD 8 km/h; NPC ahead is no longer visibly burning | No: recovery transition |
| 209–215 s | Several NPCs are close together across a bend. Player speed reads 0 at 209 s, 10 at 211 s, 23 at 213 s and 45 at 215 s. No player flames are apparent in these frames | No until dense motion review distinguishes contact from braking/queuing |
| 277 s | HUD FINISHED, all laps complete, position 1, total 4:24.515. Player still travelling at 57 km/h after crossing finish | Evaluation: completed result does not end vehicle movement |
| 287–291 s | Post-finish player stops and burns, with cyan-suited kart immediately behind/touching. HUD FIRE/recovering temporarily replaces FINISHED while all-laps-complete and final timing remain displayed | No: post-finish collision regression |
| 293–309 s | FIRE clears and FINISHED label returns. Player continues to 24, 46 and 57 km/h at 295/297/299 s, then is stopped by 303 s while NPCs continue passing | No: post-finish/cooldown policy scenario |

Key evidence frames: `frame_0006.jpg` (11 s launch), `frame_0008.jpg` (15 s standings), `frame_0069.jpg` (137 s approach), `frame_0070.jpg` (139 s fire), `frame_0139.jpg` (277 s finish), `frame_0144.jpg` (287 s post-finish fire), `frame_0147.jpg` (293 s recovery).

The launch demonstrates a substantial NPC field slowdown from visible incidents, allowing the player to lead before the first bend. It does **not** show that the player reversed to release the field, that a queued NPC's reverse recovery caused the first crash, or exactly how inward convergence contributed. Those code hypotheses need dense opening-sequence inspection or controlled telemetry tests. Later frames show different NPC speeds and lateral placements; these samples do not establish identical periodic weaving or quantify successful avoidance decisions.

Priorities supported by this clip: prevent/reproduce early NPC collisions; inspect following-distance and side-clearance during the 137–139 s approach; decide and test a post-finish vehicle/collision policy. Increasing speed or blindly copying the player's movement would not address these failures. No video-derived policy was fitted or installed.

## Observed bad start findings — main-agent review

The following findings were provided by the main agent reviewing `bad_start` frames. The training subagent reviewed trial 1 independently; it did not independently inspect the bad-start images.

| Approximate video time | Reported visual evidence |
| --- | --- |
| 11–35 s | Launch pack bunches; player speed varies through 23, 28, 19, 16, 37, 19, 4, 3, 5, 2, 1, 0 and 7 km/h. Karts visibly yaw across the straight around 15, 25 and 33 s |
| 45–51 s | First clearly visible NPC fire in the reviewed samples |
| 47–93 s | Player progresses from HUD position 20 at 47 s to position 1 by 93 s |
| ~111 s | Additional visible NPC fire |
| ~125 s | First lap completed; last lap reads 1:45.734 |
| ~203 s | Second lap completed; last lap reads 1:19.180 |
| ~249 s | Further visible NPC fire |
| ~291 s | Player finishes first, total 4:32.561 |
| ~295 s | NPC reaches the player's rear after finish |
| 297–355 s | Viewport appears green with a complexity colour bar and checkered background. This resembles an Unreal debug visualization; it does not by itself prove a rendering fault |

Both clips are useful failure/regression evidence: severe start-field congestion, repeated incidents, easy early player leadership after NPC slowdowns, and continuing interactions after finish. Their results do not establish identical NPC movement, exact driver inputs, or the causal first contact. Failed-launch and collision intervals remain excluded from positive-reference fitting. No code changes, profile tuning, approval-file deployment or publication followed this video review.
