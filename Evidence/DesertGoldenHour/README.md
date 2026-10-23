# Golden-hour atmosphere pass

Saved in both DesertKarting and DesertKarting_Visual. Revert complete atmosphere and materials using /Game/RoadToF1/Checkpoints/DesertKarting_BeforeGoldenHour or DesertKarting_Visual_BeforeGoldenHour. Original scenery/material/source assets remain unchanged; duplicate lighting actors remain disabled for recovery.

- Lighting: one active movable sun instead of three overlapping 65,000-lux suns. Elevation 17 degrees, yaw 120, 28,000 lux, 5500 K, source angle 1.2 degrees. One active movable sky fill, intensity 1.25 with real-time capture. Original shadow renderer/config retained.
- Atmosphere: one active sky/fog stack; Mie scattering .003 and anisotropy .75. Fog density .002, height falloff .25, start 250 m, maximum opacity .22; volumetric fog disabled for clear racing visibility and cost control.
- Clouds: local instance of Unreal's built-in simple volumetric cloud material, authored global scale, coverage .30, density .65, no storm component; layer 2.5-3.7 km, view samples .6 and shadow samples .4. No cloud shadow maps.
- Post process: one active unbound volume; fixed ISO100, 1/125s, f/5.6 (about EV12), exposure compensation 0; saturation +2%, contrast +2.5%, highlight gain RGB (1.015,1,.985), bloom .12, vignette .10; lens flare, grain and chromatic aberration zero.
- Materials: visual map asphalt tint multiplied by .94; runoff 15% toward neutral then multiplied by .90. Existing PBR grain, normals, roughness, rubber marks and curbs retained. New material copies/actor overrides only.
- Fixtures: existing lens geometry uses a warm emissive material (RGB 1800,1510,1100). Four 35,000-lumen, 4800 K spot pools aligned to existing poles, 35 m attenuation, 30/55 degree cones, no shadows. Pole geometry unchanged.

Limitations: existing stylized meshes and vegetation still limit photographic realism. Sun source angle does not guarantee area-light penumbrae with the existing shadow renderer. No claim of measured runtime FPS; four shadowless local lights and reduced cloud sampling bound the added cost.

Evidence contains actual Unreal aerial, start/finish and corner PNGs. InitialReview retains rejected first-pass images. Reproduction: Tools/desert_golden_apply.py, desert_golden_capture.py, desert_golden_preserve.py. Source/Config and original UAssets hash checked; static scenery transforms/meshes/collision/visibility and starts matched checkpoints. No gameplay code changes or commits.
