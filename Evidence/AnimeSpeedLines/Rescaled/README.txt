The animation's reference speeds are now scaled to the actual kart's speed range.
Actual km/h: <=19 clear; 19..34 subtle; 34..49 noticeable; 49..61 strong; >=61 full.
This maps the former 80 km/h reference look to the current approximately 61 km/h top speed.
Only KartSpeedLines defaults and response tests change. The material, physics, racecraft,
driving inputs, speed limit and circuit remain unchanged. F3 keeps its existing toggle.
Tests: SpeedResponse includes full strength at 61 km/h and equal smoothing at 30/120 Hz.
PIE captures use actual 15, 35 and 50 km/h readings, without any strength/speed override.
The 50 km/h target strength is approximately 0.6 instead of approximately 0.2; the smoothed driving reading can lag slightly during acceleration.
The 61 km/h full-strength endpoint is covered by the response test, not claimed as a
driving screenshot. Checkpoint contains the original defaults and tests.
