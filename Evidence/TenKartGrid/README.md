# Ten-kart race update

Normal Play in DesertKarting_Visual now spawns nine AI opponents in slots 1–9 and the player in slot 10. All use the current articulated PlayerVehicleV4 kart and full-body driver. Only the local player creates the owner-only cockpit driver.

Each slot has a unique kart livery and a unique driver/helmet color. Driver colors are offset from kart colors so each driver's outfit differs from their kart. Existing contrasting graphics, rubber and mechanical materials are retained.

| Slot | Kart | Driver |
|---|---|---|
|1|Red|Lime|
|2|Orange|Green|
|3|Gold|Cyan|
|4|Lime|Blue|
|5|Green|Purple|
|6|Cyan|Pink|
|7|Blue|Pearl white|
|8|Purple|Red|
|9|Pink|Orange|
|10 (player)|Pearl white|Gold|

All karts share a 38 mph (16.98752 m/s) forward top speed. Full-throttle power was increased; the established partial-throttle response is retained. AI still slows for corners and traffic. Legacy movement's forward cap is also 38 mph.

## Actual validation

- Editor build succeeded (build_verified.log).
- Actual Unreal PIE: 10 karts, nine AI, player slot 10, ten unique kart colors, ten unique driver colors, matching mechanical models, no AI first-person mesh or duplicate legacy presentation.
- All nine AI moved during the normal race launch. All ten reached 38.0 mph in a separate temporary straight-line test. Test actors and map changes were not saved.
- Map SHA256 hashes unchanged (validation.json).
- Nine automation tests ran: eight passed, one existing ForceScenarios test failed its two brake-slide assertions. The saved pre-task solver and final solver produced identical brake-entry results: 2.861821088/3.081029473 degrees maximum sideslip, zero drift steps. This failure predates this change; no test thresholds were weakened. See compare_baseline.cpp/.cmd and baseline_comparison.txt.
- Current evidence does not establish completion of a full ten-kart race or network multiplayer testing.

Actual final screenshots: 01_ten_kart_grid00001.png, 02_matching_ai_model00001.png, 03_ten_karts_racing00001.png, 04_shared_38mph_test00001.png. These are Unreal captures, not generated images.

## Files and reversibility

Shared defaults: Source/Road_To_F1_New/KartRaceSettings.h. Visual assignment: KartMechanicalVisuals. Spawn/grid: TrackRacingAI and ProofPawn. Materials are separate assets under Content/RoadToF1/RaceLiveries; originals remain unchanged.

Pre-task source copies are under Checkpoints/TenKartGrid/Source. Compare/restore only this task's changes because the workspace already contained other edits. No map edits, push or merge were performed.
