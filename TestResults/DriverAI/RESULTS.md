# Seated drivers and 19 opponents — 2026-10-08

## Implementation
- Original seated driver mesh with suit, contrast panels, gloves, boots, full-face helmet and dark curved visor. F1-inspired styling, with original colour combinations and no copied sponsor graphics.
- Six imported mesh/material batches under `/Game/RoadToF1/Art/DriversV01`. Runtime material colour parameters distinguish all 20 racers. Assets explicitly included in cooking.
- 20 open-ended white positioning boxes on the start straight; player occupies slot 20. The native director spawns exactly 19 opponents into the other slots.
- Player cap 57 km/h, AI cap 55 km/h. Shared swept kart movement, braking and ground support. Opponents anticipate bends, keep traffic gaps, change lanes and reverse to recover from blocking traffic.
- AI route index follows contiguous samples to avoid switching to nearby adjoining sections. Static-world ground queries avoid treating another kart as ground.
- Field waits for player acceleration. HUD shows position; F5 resets player, all opponents, checkpoint progress and finish standings. Finish order is retained while opponents continue driving a cooldown lap.

## Verification
- Initial autonomous test exposed route switching and traffic bunching; fixed and reran the full race rather than accepting spawned stationary NPCs.
- `AutomationFixed/index.json`: all five suites passed, zero errors/warnings. All 19 opponents physically drove three ordered laps within 600 simulated seconds, without exceeding 55 km/h. Player 57 km/h cap and existing handling, rejoin, timing, gates and reset regressions passed.
- GridFinal.png and DriverCloseup.png rendered in Unreal and visually inspected. First Grid.png had pending shaders; warm-cache render confirmed suit colours.
- Final build succeeded in 59.25 seconds; reimport succeeded with zero errors/warnings. Final suit panels visually verified in DriverFinal.png. Standings wrap around the finish line without losing a nearly completed lap.
- `AutomationFinal/index.json`: all five suites passed again, zero errors/warnings, process exit 0. Added verification that all six driver meshes actually load and all 20 suit colours are distinct. All 19 autonomous three-lap races, 57/55 caps, field reset and original regressions passed.

## Preservation and limits
- User saved and closed Unreal before edits. Backups: `D:/Boring/RaceValidation/DriverAI-Before`. Original RacePrototype and pre-existing VehicleBasic actor edits preserved.
- Driver is a static seated mesh prototype; no animated skeleton, cloth simulation or official team liveries. AI race test parks the human player's kart safely off-track; a human-driven competitive race remains to be tried.
- Local changes only in this phase; no commit or push performed.
