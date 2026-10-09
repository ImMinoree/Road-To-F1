# Training framework validation — 2026-10-09

## Delivered
- A dedicated development subagent built `AI Agent for game training/` with independent telemetry, video, learning, styles and evaluation Python modules.
- Native Unreal F9 recorder captures actual player inputs, speed, route/lateral position, curvature, nearby-traffic context, incidents and lap progress at up to 10 Hz. F5 starts a fresh recording session/file; stop/EndPlay flushes data. CSV stays local in ignored Saved/Training/Telemetry.
- Native experimental aggregate learner proposes 19 distinct seeded, bounded styles after at least 300 clean samples including 20 corner and 20 straight samples. It exports aggregate metrics and preferences, never a control timeline or route replay. Proposals are inactive until evaluated and explicitly approved.
- Approved profiles load atomically at gameplay startup, retaining geometry/traffic-based control, collision safety and 57/55 km/h limits. Invalid schema, track, IDs, count, bounds, duplicates or identical styles are rejected. Synthetic demonstrations and automation-validation provenance are rejected as deployment sources.
- Native recorder, learner and loader are runtime code, not editor-only. Optional reviewed Content/Training/approved_profiles.json is staged as UFS for packaging; Saved/Training/approved_profiles.json supports local approval overrides. No candidate is bundled by default.
- No background automatic recording, upload, signup or cloud service. F9 is an explicit local playtest action; future automatic collection requires a signup consent flow. Codex subagent and Python fitter are development tools, not shipped hosted agents.

## Tests and evidence
- UE5.8.3 editor target: successful build.
- UE5.8.3 standalone Win64 Development game target: successful build, including all native training modules with editor code disabled. This is not a full cooked/Steam release validation.
- `Automation/index.json`: nine Unreal suites passed, zero errors/warnings. Six racecraft/rules regressions retained, including all 19 NPCs completing three ordered laps; capture lifecycle/CSV/F5 boundary, native proposal bounds/diversity/reproducibility, and profile validation passed.
- Offline Python: 11 unit tests passed. Session holdout isolation, invalid inputs, signed reverse handling, bounded distinct profiles, no trajectory export and video-input error handling verified. Initial sandbox fixture-permission failure was resolved by running with appropriate filesystem access.
- Three actual native automation CSVs (47 samples total) passed offline schema validation and produced 19 bounded profiles with two training sessions and one holdout. Output explicitly labeled telemetry_automation_validation, remains ignored and uninstalled. These short starts/idle resets are integration checks, not real human training data.
- HUD screenshot inspected at `HUD.png`; native recorder is off by default. Raw build/test/render logs remain local.

## Limits and next steps
- First implementation learns statistical tendencies within a tested controller; it is not reinforcement learning or proof of optimal racing skills. General responses come from current curvature/traffic/hazard evaluation. Different parameters do not guarantee visibly different trajectories.
- No real player sessions or race videos were supplied. NPC difficulty improvements and unseen-track generalization are unverified. Record multiple clean/traffic sessions, fit with whole-session holdout, then compare candidate and baseline full races before deployment.
- Video pipeline supports optional FFmpeg frame extraction and manual observations. Automatic visual reconstruction of steering/world geometry is not implemented; no video was analyzed.
- Packaging is architected and the standalone game target builds. Cooked release, Steam integration, signup consent UI and packaging-distribution tests remain future work.
