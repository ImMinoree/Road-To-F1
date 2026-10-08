# Corner surfaces and offroad recovery — 2026-10-08

- Cause: original curve offsets folded ten asphalt triangles and several kerb/edge triangles backwards at tight turns. Centre-only ground support also let the kart's collision box catch the 6.5cm grass/asphalt step.
- Changes: uniformly sampled curve smoothing removes folded strips; existing checkpoints/spawn follow the corrected route. Footprint ground probes support the kart across small surface transitions, with a 12cm climb limit and swept collision retained.
- Geometry validation: `node Art/KartLab/validate-track.mjs` passes for all 16,840 road/kerb/edge triangles.
- Native build succeeded in 12.52 seconds. Asset patch completed with zero errors/warnings.
- All four Unreal automation suites succeeded with zero errors. SouthGardaPIE captured one unrelated HTTP connectivity-probe timeout warning.
- Added 48 actual driven grass-to-road recovery cases across both sides of the circuit, forward and reverse: all passed. Existing throttle/braking/speed/steering, 600 centreline collision samples, ordered checkpoints, finish and restart tests still pass.
- Rendered and visually inspected `Corner.png` near checkpoint 10: the repaired road is continuous, without the reported black folded patch or kerb strip cutting across asphalt.
- Backups: `D:/Boring/RaceValidation/CornerRejoinFix-Before`. Unrelated actors/assets preserved. Playable map was saved before creating the separate CornerReview render map.
- Limits: automated driving recovery and programmatic lap gates are not a full human-driven race. User should try the previously troublesome bends in Play.
- Saved locally; no commit or push performed.
