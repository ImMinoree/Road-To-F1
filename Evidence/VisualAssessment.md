# Visual acceptance: FAIL / incomplete

Inspected actual 1920×1080 SM6/D3D12 Unreal renders: 01_DriverEye.png, 02_Ground.png, 03_Wide.png. Fixed cameras and manual exposure are defined in Tools/build_scene.py; all captures use the Validation profile. Ground and wide views were corrected after detecting positional Rotator argument misuse. The saved final map uses named rotation arguments.

Compared with the supplied onboard reference: asphalt has a measured 2 m PBR repeat, but lacks track-specific rubber deposits, edge wear, cracks and varied shoulder transitions. Curbs have credible 0.5 m width, 1 m paint sections and 6 cm depth, but uniform unworn paint looks synthetic. Low perspective is plausible, but there is no cockpit/driver foreground. Verge topography varies by less than half a metre, but plain soil calibration materials and exposed mesh boundaries are conspicuously artificial. No vegetation, fences, tire walls, signage, drainage, structures or surrounding landscape are present. Daylight renders correctly after fixing sun rotation, but this sparse scene cannot establish convincing environmental lighting or shadow quality. No claim of BODYCAM similarity is supported.

Corrections made after inspecting renders: added curb thickness to remove visible sky gaps under edges; fixed rotation arguments; settled temporal screenshot capture for 8 frames. No expansion followed the failed art acceptance.

Rendering bottleneck observed: Validation VSM non-Nanite marking job queue overflow in CaptureFinal.log. The current broad, non-Nanite surfaces offer little reason to retain VSM in Balanced; Balanced uses conventional shadows, while Validation retains VSM for comparison. Reassess shadow mode after importing production assets and partitioning terrain. No GPU pass timing was measured, so this warning is not a quantified bottleneck ranking.

Art needed to continue is listed in ../ASSETS.md. Local Fab packages were inventoried, but license/ownership was not inferred from file presence. Third-party textures were neither staged nor committed.
