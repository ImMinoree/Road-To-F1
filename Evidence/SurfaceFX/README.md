# Rear-tire debris validation

Unreal Engine 5.8.3 Editor target built successfully. Native automation `RoadToF1.SurfaceFX.ContactAndPooling` passed against the final build; report in `Automation/`. Build/import/test logs are local ignored files `Evidence/surface_fx_*`.

Actual Play In Editor validation passed; see `pie_validation.json`. Grass: two emitting tires, 80 particles emitted during the sampled forward interval. Reverse: two emitting tires, 75 emitted. The sampled stationary, asphalt and airborne intervals emitted zero. The stationary interval had zero remaining particles. Peak observed active particles: 30, against a hard cap of 96 per kart.

`GrassTrail.png`, `Stopped.png`, `Asphalt.png` and `ReverseTrail.png` are genuine 1600×900 Unreal PIE captures. Forward and stopped images were inspected. The grass/soil chips are visible behind the rear tires; dust is deliberately subtle and can be difficult to distinguish from the ground in deep kart shadows. These screenshots use the existing chassis as a transient diagnostic presentation, not a new gameplay kart or driver asset. Final render log has no material-compilation or Python errors.

The script moves the existing pawn transiently to exercise contact cases. It does not establish tire-slip realism, off-track handling, packaged-build operation, multiplayer rendering or a 20-kart performance baseline. No FPS claim is made. The temporary test actors, camera and movement are not saved. All on-disk map hashes were unchanged by validation. Driving code received only the cosmetic component attachment; no grip, force, collision, input, AI or race-state calculation was changed by this effect.

Earlier diagnostic failure is retained as `initial_runtime_error.txt`; the final successful result is `pie_validation.json`.
