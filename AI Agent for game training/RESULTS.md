# Offline toolkit validation — 2026-10-09

Implemented telemetry validation, whole-session holdout, time-weighted aggregate fitting, optional corner/traffic context summaries, 19 deterministic independently varied bounded profiles, manual video annotations and optional FFmpeg frame extraction.

Validation: all eleven `unittest` tests passed. Synthetic CLI smoke test generated 19 profiles from four explicitly synthetic sessions (three training, one holdout). Demo data remains in ignored `candidate-runs/demo_001/`; it was not installed into Unreal or described as real player learning. The optional FFmpeg execution path has not been exercised with an actual clip; missing-FFmpeg handling is tested.

No supplied real telemetry or video was available. No claim of improved human racing performance, automatic video driving inference, or reinforcement learning is made. Session holdout measures descriptive aggregate agreement; profile diversity measures parameters rather than observed driving paths. Unreal completion/collision and live visual checks are separate deployment gates.

All edits by the training subagent are confined to this directory. No editor control, source edits outside this directory, commit, push, merge, or automatic profile deployment was performed by this subagent.

Integration update: signed speed/throttle accepted; reversing and burning excluded from skill summaries with full recovery metrics retained. Package split into independent telemetry, video, learning, styles and evaluation modules; train.py remains a compatibility CLI.

## Native recorder integration validation

Three actual CSV artifacts produced by Unreal's automated capture test passed modular `load_telemetry` validation:

| Artifact | Samples | Span | Speed range km/h |
| --- | --- | --- | --- |
| `425994A549492A02B6CAD6975F21F9B1.csv` | 21 | 2.0 s | 0–15.12 |
| `85795E244CA70660E465B6BFF51895F2.csv` | 13 | 1.2 s | 0–0 |
| `9BE642C3488F4C2EB3EC0D86DB47E602.csv` | 13 | 1.2 s | 0–0 |

All use `SouthGarda_KartRace`, with one distinct session per file. They were read from the original project's `Saved/Training/Telemetry/` directory without modifying them. Combining the 47 rows in ignored `candidate-runs/native-capture-validation.csv` then calling `fit_telemetry` succeeded: two training sessions, one holdout and 19 distinct bounded profiles. Output is `candidate-runs/native-capture-NONDEPLOYABLE.json` with provenance **`telemetry_automation_validation`**, intentionally rejected by the runtime's deployment source whitelist and the deployment schema. It was not installed.

These are short automated start/restart checks, including two stationary sessions. They establish schema/recorder/offline integration only; they are not representative driving, human learning data, unseen-track performance or an NPC skill improvement. Stationary nonnegative samples are valid telemetry but not evidence of good driving. No video supplied or analysed. No automatic collection/signup flow added.
