# Kart control and track fixes — 2026-10-08

Fixed:
- Raised grid/finish objects replaced by flush surface markings. Grid boxes are two staggered lanes of position markers behind start; finish checks align with the actual race gate. Markings have NoCollision.
- Separated rectangular kerb pieces replaced by curve-following, closed ribbons with matching endpoints. Added continuous white edge paint and removed the sparse placeholder barrier blocks. Kerb surfaces are decorative and non-blocking; track and terrain retain collision.
- Removed floating debug checkpoint boxes in the kart map; checkpoint hints are now thin surface lines. Original RacePrototype debug gates remain unchanged.
- Forward cap reduced from 90 to 55 km/h, reverse cap to 14.4 km/h, acceleration from 6.5 to 3 m/s².
- A/D steering ramps in and recentres smoothly. Yaw rate also smooths and is capped at 55 degrees/second. Restart clears steering/yaw state.

Verification: C++ build succeeded (build.log). Surface reimport completed (surfaces.log). All four automation suites passed with zero errors/warnings (Automation/index.json). Regression includes actual long straight driving past the grid and finish paint, 55 km/h cap, gradual steering response across successive frames, 600 road support samples, lap rules, finish and reset, plus original RacePrototype tests. Rendered driving-view screenshots saved alongside this report.

Backups of pre-fix maps and affected meshes: D:/Boring/RaceValidation/KartControlFixes-Before. Existing actor transforms and unrelated assets were preserved. Changes saved locally; no commit/push performed.

Handling is still an arcade prototype. Next step: user play feedback on cornering and speed before further tuning.
