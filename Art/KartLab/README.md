# Road To F1 — kart and first venue art

Run `./serve.ps1` and open http://127.0.0.1:8086/index.html. The HTML loads its JavaScript and texture locally; use HTTP rather than double-clicking the file because browsers restrict module imports on file URLs.

The viewer includes OrbitControls, a component selector, exploded view, livery colour, turntable and a South Garda-inspired circuit scene. This is an authored visual kart concept and a venue art blockout. It is not a certified kart, a surveyed circuit replica or a new vehicle physics implementation. Existing RacePrototype remains the tested race-loop map.

`node export.mjs` regenerates centimetre/Z-up OBJ assets and `exports/manifest.json` for Unreal. Unreal's OBJ pipeline converts right-handed OBJ Y to Unreal Y; the import script uses that verified coordinate convention for actor placements. `Tools/build_south_garda_art.py` imports these into a new asset folder and saves a separate map. Re-running that script refuses to overwrite an existing map.

Unreal art map: `/Game/RoadToF1/SouthGarda_ArtPreview`. It starts on an aerial review camera and retains the static display kart. Material actors are grouped under SouthGarda/Environment and SouthGarda/KartDisplay.

Playable Unreal map: `/Game/RoadToF1/SouthGarda_KartRace`, now the project startup/default map. Native KartPawn supplies arcade driving, follow camera and collision; 12 ordered checkpoints connect to the race HUD, timers, finish and F5 reset. W accelerates, S brakes/reverses, A/D steer and Space brakes. See TestResults/SouthGardaGameplay/RESULTS.md for verified behavior and current limits. The original RacePrototype is preserved.

Control/track fix pass: 55 km/h beginner cap, gentler acceleration, smoothly filtered steering/yaw, non-colliding grid/finish paint and continuous kerb/edge strips. Latest validation: TestResults/KartControlFixes/RESULTS.md.

Driver/AI pass: original seated driver with fitted suit, contrasting panels, gloves, boots, full-face helmet and curved visor. Six mesh/material batches in `exports/Driver_*.obj`; liveries use runtime colour parameters. This is a static seated mesh concept, without a skeletal animation rig. The viewer includes the driver as a selectable component.

The playable race field uses 20 open-ended positioning boxes, the player in slot 20, and 19 native AI karts. Player top speed is 57 km/h; opponent top speed is 55 km/h. AI slow for bends, follow contiguous route samples, negotiate traffic and use swept movement for recovery. Opponents wait until the player accelerates; F5 resets the whole field. Position is shown on the HUD.

`Tools/import_driver_ai.py` imports the driver and grid paint, then stores route/grid data on the native KartRaceDirector in SouthGarda_KartRace. Driver assets are explicitly included in cooking through DefaultGame.ini. Generated liveries use F1-inspired suit styling and original colour combinations rather than copied sponsor graphics.

Third-party files: Three.js 0.180.0 (MIT, vendor/LICENSE-Three.txt); Poly Haven Asphalt Track diffuse texture by Dimitrios Savva (CC0), https://polyhaven.com/a/asphalt_track and https://docs.polyhaven.com/en/faq. No paid assets or subscriptions were acquired. Original geometry is authored in scene.mjs.

Reference: South Garda's official historical circuit drawing: https://racing.southgardakarting.it/sites/racing.southgardakarting.it/files/South%20Garda%20Karting%20CIK%20FIA.26-09-2015_1.pdf. The current route is an approximation for art development; do not present it as matching this drawing.
