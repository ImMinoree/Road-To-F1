# Racecraft, incidents and engine compatibility — 2026-10-09

## Implemented locally
- Original `RoadToF1/RoadToF1.uproject` targets Unreal 5.8; actual lab engine is 5.8.3 (CL 58210709). The previous custom engine-association GUID was replaced with the installed 5.8 association.
- Compared the engine-created `RoadToF1 5.8` copy with the original before implementation: Source, Config and Content matched by SHA-256. The project association differed; both used the same engine installation. Backup: `D:/Boring/RaceValidation/Racecraft-Before`.
- Nineteen individually configured opponents have different corner pace, aggression, lane preference and decision cadence. Traffic-based lane choices commit for several seconds and transition gradually; lane changes are restricted to straights. Player/AI limits remain 57/55 km/h.
- Swept kart collisions reduce speed and briefly disable throttle. Hard closing impacts (at least 700 cm/s, about 25 km/h) trigger six seconds of animated flame/smoke and orange lighting. Light bumps do not ignite; cooldown prevents repeated contact events from one impact. F5 clears incidents and resets everyone.
- Approaching NPCs slow for burning karts, evaluate open lanes and hold back behind a blocked incident. A kart behind cannot prevent the front kart escaping a pileup.
- Left leaderboard displays position, kart number, unique fictional driver name and current speed for all 20 racers. Player highlighted; incident rows tinted red. Right panel retains laps/checkpoints/timers, position, controls and reset.

## Validation
- Native editor build succeeded on UE 5.8.3. Initial build stalled in accelerator/cache handling; local no-cache builds completed successfully. Final build logs retained locally.
- `AutomationRecovery/index.json`: all six suites passed, zero errors/warnings (AIRacePIE, IncidentsPIE, SouthGardaPIE, GateGeometry, PrototypePIE, Rules).
- All 19 AI physically drove three ordered laps within 600 simulated movement seconds. Unique names/numbers/profiles, 55 km/h cap, retained standings and full-field reset passed.
- Actual swept rear-end collision registered on both karts and ignited both on hard impact. Light-contact, cooldown and reset checks passed.
- Controlled two-kart burning blockage: following NPC stayed below 18.5 km/h and did not add another collision.
- Rendered incident test passed with zero errors/warnings. `IncidentFinal.png` shows the leaderboard, race HUD and engine fire. HUD anchoring and long incident text were corrected after visual inspection.
- Existing ordered gates, race finish/timing/reset, smooth steering, speed caps and grass/road rejoin checks passed.

## Limits and next steps
- Fire is an arcade prototype effect built from animated meshes, smoke and lighting, not a realistic damage/fire simulation. Not every collision causes fire. NPC contact is still possible; avoidance reduces risk rather than guarantees collision-free racing.
- Full-field test parks the human player's kart off-track. Competitive difficulty, human overtaking and recovery feel need the user's driving test.
- User saved/closed the copied editor. Fresh comparison found identical Content, unchanged copy Source against the pre-change backup, and unchanged copy Config against HEAD. Retired the duplicate to `D:/Boring/RaceValidation/RetiredProjects/RoadToF1-5.8-20261009` for recovery; the repository now has one active project folder.
- Racecraft work is on `ai-racecraft-incidents`, based on `main` commit `dea3d96`. On 2026-10-09 the user explicitly authorized pushing and merging this completed phase. The separate training-agent phase follows afterward.
- Open the original `D:/Boring/GitHub/Road-To-F1/RoadToF1/RoadToF1.uproject` for this implementation, not the copy.
