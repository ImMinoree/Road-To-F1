# Actual Unreal validation

See `validation.json`, `motion.csv`, `pie_final.log` and `build_final_link.log` for the final run. Earlier failed attempts remain for diagnosis; their error files are historical and do not describe the final run.

The A–L checks exercised centre/left/right steering, rapid steering, acceleration, reverse, simultaneous steer/roll, braking, sustained turning, drift recovery, collision/restart and countdown gating. This is a functional validation, not certification of anatomical surface fit. Ground-speed wheel roll does not simulate tire angular slip. The separate fixed-rod automation swept 481 steering values.

The seven numbered PNGs are actual Unreal viewport captures. `steering_sequence.html` plays the captured cockpit frames. Driver garment seams, finger/rim surface contact, seat contact and inherited body proportions need manual art refinement. There is no performance/LOD certification. Physics and map hashes still match the recorded baseline.
