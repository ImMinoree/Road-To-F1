# Kart speed gauge

`Source/Road_To_F1_New/KartSpeedGauge.h` draws a responsive bottom-right 270-degree speed arc, white fill, red upper-range accent, ticks and a three-digit readout with muted leading zeroes. `RaceStartGantry.cpp` calls it from the existing HUD after the navigation-map suppression check. It uses the existing font and Canvas drawing, with no texture imports or new project dependencies.

The source is `AProofPawn::GetVelocity()`, which reads the authoritative tire-dynamics velocity when enabled. Planar cm/s magnitude is converted to km/h using 0.036. Reverse motion uses the same positive speed magnitude and an actual velocity/forward-vector dot product for the REVERSE label. The arc represents speed, not engine RPM, and does not invent gears for the direct-drive kart. No movement, tire coefficient, input, race-start or map asset changes are needed.

Default: km/h, 80 km/h visual scale. Optional Unreal console settings: `kart.SpeedGauge.MPH 1` for mph (`0` for km/h), `kart.SpeedGauge.MaxKmh 80` for the display range, and `kart.SpeedGauge.Enabled 0` to hide it. These settings only affect presentation. `kart.SpeedGauge.Debug 1` logs actual rendered values for validation; normally off.

Open the existing project and Play DesertKarting_Visual with the normal driving mode. `Tools/validate_speed_gauge.py` supplies explicit development input under `-KartDynamicsTest` to capture real acceleration, braking and reverse, plus the full-map view. It saves no level changes. `validation.json`, `pie_final.log` and the six numbered PNGs are runtime evidence. Earlier captures changed units or closed the map before the screenshot frame; the final run delays those transitions. A stopped screenshot alone does not validate a moving speed gauge.

The final native build is `build_final.log`. This machine's PCH load stalled; the same HUD source was compiled with the generated compiler response file plus `/Y-`, then linked by the normal Unreal build. Existing open editors can temporarily lock the DLL. Earlier failed build logs are retained; only the final successful build is authoritative.

Rollback: remove the `KartSpeedGauge.h` include and `KartSpeedGauge::Draw` call from RaceStartGantry.cpp, then rebuild. Its full pre-change source is in `Backup/RaceStartGantry.cpp`; avoid restoring that whole file over unrelated later edits. No commit or push.
