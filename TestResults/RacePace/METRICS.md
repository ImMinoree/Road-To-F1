# Automated pace comparison

Units: speeds in mph; times in simulated seconds. Moving means speed >1 mph; reason durations use the dominant instantaneous limit, so overlapping limits are not double-counted. Headless fixtures are not human telemetry.

## Baseline

Suites: 14 passed, 1 failed.

| NPC | Peak | Moving avg | <20 % | <25 % | >30 % | Traffic s | Corner s | Obstruction s | Guidance s | Recovery s | Brake events | Brake s | Longest queue s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 34.16 | 20.02 | 51.1 | 66.4 | 18.9 | 7.5 | 187.3 | 0.3 | 65.2 | 0.0 | 238.0 | 42.9 | 2.1 |
| 2 | 34.16 | 21.07 | 44.9 | 63.0 | 19.6 | 1.8 | 178.5 | 0.0 | 58.8 | 0.0 | 240.0 | 42.9 | 0.0 |
| 3 | 34.17 | 20.27 | 49.2 | 65.7 | 19.6 | 14.8 | 180.4 | 0.9 | 69.2 | 0.0 | 257.0 | 43.8 | 1.5 |
| 4 | 34.16 | 19.98 | 50.4 | 67.4 | 18.4 | 64.9 | 170.9 | 2.0 | 56.3 | 0.6 | 272.0 | 42.9 | 5.2 |
| 5 | 34.16 | 20.37 | 48.9 | 66.7 | 18.9 | 70.0 | 156.5 | 0.6 | 49.4 | 18.8 | 281.0 | 60.9 | 6.4 |
| 6 | 34.17 | 19.68 | 52.0 | 68.6 | 17.8 | 127.4 | 148.1 | 5.0 | 41.0 | 1.1 | 342.0 | 43.8 | 8.8 |
| 7 | 34.16 | 19.32 | 53.0 | 71.4 | 14.7 | 133.2 | 210.5 | 1.4 | 62.4 | 12.4 | 414.0 | 73.5 | 9.3 |
| 8 | 34.16 | 19.34 | 52.6 | 70.0 | 16.0 | 144.8 | 149.9 | 1.9 | 35.4 | 6.9 | 369.0 | 49.6 | 8.9 |
| 9 | 34.17 | 20.3 | 49.8 | 66.2 | 20.9 | 76.2 | 154.6 | 4.1 | 49.7 | 6.7 | 286.0 | 49.3 | 8.3 |
| 10 | 34.16 | 20.21 | 48.7 | 65.9 | 20.4 | 81.8 | 166.3 | 1.8 | 43.8 | 0.5 | 305.0 | 40.1 | 7.1 |
| 11 | 34.16 | 20.04 | 49.7 | 67.2 | 19.1 | 62.8 | 156.5 | 1.5 | 61.6 | 6.1 | 315.0 | 50.8 | 8.7 |
| 12 | 34.16 | 19.17 | 53.3 | 71.1 | 14.4 | 137.2 | 149.9 | 5.5 | 45.9 | 0.6 | 334.0 | 43.9 | 5.4 |
| 13 | 34.16 | 20.08 | 50.2 | 67.1 | 18.8 | 75.5 | 146.8 | 5.1 | 55.0 | 12.9 | 282.0 | 54.1 | 10.9 |
| 14 | 34.17 | 19.23 | 52.7 | 70.8 | 14.4 | 133.0 | 139.1 | 5.0 | 50.3 | 0.0 | 373.0 | 43.6 | 6.5 |
| 15 | 34.16 | 18.92 | 54.5 | 72.3 | 13.5 | 117.5 | 162.4 | 3.8 | 50.2 | 6.5 | 319.0 | 50.7 | 8.0 |
| 16 | 34.16 | 19.02 | 54.8 | 70.6 | 17.5 | 124.9 | 150.3 | 1.2 | 49.0 | 0.5 | 336.0 | 44.4 | 5.5 |
| 17 | 34.17 | 18.99 | 54.0 | 71.0 | 15.8 | 142.8 | 140.6 | 6.3 | 53.7 | 6.3 | 330.0 | 49.9 | 6.5 |
| 18 | 34.16 | 19.05 | 54.0 | 72.6 | 14.6 | 162.5 | 126.8 | 3.4 | 48.9 | 6.7 | 353.0 | 48.4 | 6.9 |
| 19 | 34.16 | 18.66 | 55.9 | 72.6 | 13.6 | 125.6 | 163.9 | 5.3 | 65.3 | 0.4 | 357.0 | 45.3 | 5.7 |
| Field mean | 34.16 | 19.67 | 51.56 | 68.77 | 17.21 | 94.96 | 159.96 | 2.90 | 53.22 | 4.58 | 315.95 | 48.46 | 6.41 |

Field: mean finish 443.82s; last finisher 596.90s; summed per-kart contacts 49 (not unique collision pairs).

| NPC | Tracked pass attempts | Tracked completions |
|---|---|---|
| 1 | not instrumented | not instrumented |
| 2 | not instrumented | not instrumented |
| 3 | not instrumented | not instrumented |
| 4 | not instrumented | not instrumented |
| 5 | not instrumented | not instrumented |
| 6 | not instrumented | not instrumented |
| 7 | not instrumented | not instrumented |
| 8 | not instrumented | not instrumented |
| 9 | not instrumented | not instrumented |
| 10 | not instrumented | not instrumented |
| 11 | not instrumented | not instrumented |
| 12 | not instrumented | not instrumented |
| 13 | not instrumented | not instrumented |
| 14 | not instrumented | not instrumented |
| 15 | not instrumented | not instrumented |
| 16 | not instrumented | not instrumented |
| 17 | not instrumented | not instrumented |
| 18 | not instrumented | not instrumented |
| 19 | not instrumented | not instrumented |

### Scenario measurements and finish/contact diagnostics

```
MISSED gate7 racer7 at387.9s lateral-513 bound480 lane-320
Racer1 finish417.0s queued4.5s stopped2.7s
AI: laps 3, CP 0, speed 0.0, contacts 0, route 0, lane 125, pos X=-5897.942 Y=-5080.806 Z=24.500
Racer2 finish398.4s queued0.1s stopped0.3s
AI: laps 3, CP 0, speed 0.0, contacts 0, route 0, lane 30, pos X=-5553.762 Y=-5395.082 Z=24.500
Racer3 finish415.9s queued22.2s stopped3.1s
AI: laps 3, CP 0, speed 0.0, contacts 0, route 0, lane -81, pos X=-5861.855 Y=-5414.752 Z=24.500
Racer4 finish424.7s queued68.1s stopped11.9s
AI: laps 3, CP 0, speed 0.0, contacts 2, route 0, lane 13, pos X=-4702.010 Y=-5273.266 Z=24.500
Racer5 finish432.3s queued91.0s stopped24.1s
AI: laps 3, CP 0, speed 0.0, contacts 5, route 0, lane 128, pos X=-5759.109 Y=-5017.896 Z=24.500
Racer6 finish437.2s queued133.1s stopped13.0s
AI: laps 3, CP 0, speed 0.0, contacts 4, route 0, lane -143, pos X=-5187.564 Y=-4897.041 Z=24.500
Racer7 finish596.9s queued164.1s stopped23.7s
AI: laps 3, CP 0, speed 0.0, contacts 4, route 0, lane -129, pos X=-6006.683 Y=-5249.478 Z=24.500
Racer8 finish446.0s queued170.3s stopped18.0s
AI: laps 3, CP 0, speed 0.0, contacts 3, route 0, lane 22, pos X=-4894.609 Y=-5550.340 Z=24.500
Racer9 finish428.5s queued92.6s stopped20.5s
AI: laps 3, CP 0, speed 0.0, contacts 4, route 0, lane 25, pos X=-4910.759 Y=-5215.918 Z=24.500
Racer10 finish420.0s queued86.8s stopped8.9s
AI: laps 3, CP 0, speed 0.0, contacts 2, route 0, lane -69, pos X=-5342.844 Y=-5199.715 Z=24.500
Racer11 finish430.8s queued61.2s stopped13.8s
AI: laps 3, CP 0, speed 0.0, contacts 2, route 0, lane -139, pos X=-5506.949 Y=-4881.776 Z=24.500
Racer12 finish444.4s queued155.5s stopped11.8s
AI: laps 3, CP 0, speed 0.0, contacts 3, route 0, lane -65, pos X=-5472.828 Y=-5353.032 Z=24.500
Racer13 finish436.1s queued101.4s stopped20.6s
AI: laps 3, CP 0, speed 0.0, contacts 6, route 0, lane 61, pos X=-5918.392 Y=-5329.640 Z=24.500
Racer14 finish441.7s queued142.7s stopped7.0s
AI: laps 3, CP 0, speed 0.0, contacts 0, route 0, lane -107, pos X=-5672.176 Y=-5298.051 Z=24.500
Racer15 finish459.9s queued123.7s stopped19.0s
AI: laps 3, CP 0, speed 0.0, contacts 3, route 0, lane 130, pos X=-5740.414 Y=-4957.423 Z=24.500
Racer16 finish452.0s queued137.2s stopped14.9s
AI: laps 3, CP 0, speed 0.0, contacts 2, route 0, lane -159, pos X=-3362.558 Y=-5574.107 Z=24.500
Racer17 finish453.8s queued160.4s stopped15.5s
AI: laps 3, CP 0, speed 0.0, contacts 3, route 0, lane 149, pos X=-5796.291 Y=-4997.183 Z=24.500
Racer18 finish446.4s queued203.5s stopped14.2s
AI: laps 3, CP 0, speed 0.0, contacts 4, route 0, lane -101, pos X=-4668.499 Y=-4707.507 Z=18.000
Racer19 finish450.6s queued136.3s stopped6.9s
AI: laps 3, CP 0, speed 0.0, contacts 2, route 0, lane -81, pos X=-5374.001 Y=-5149.799 Z=24.500
CLEAR speed_kmh=54.94 t90=5.20 d90_cm=3605 t95=5.50 d95_cm=4032
EXIT120 apex_kmh=25.38 one=34.97 two=44.55 three=54.13 t90=2.55 d90_cm=2635 t95=2.85 d95_cm=3062 contacts=0
EXIT210 apex_kmh=25.38 one=34.97 two=44.55 three=54.13 t90=2.55 d90_cm=2649 t95=2.85 d95_cm=3074 contacts=0
EXIT300 apex_kmh=25.38 one=34.97 two=44.55 three=54.13 t90=2.55 d90_cm=2659 t95=2.85 d95_cm=3087 contacts=0
TRAIN0 min_kmh=38.88 final_kmh=54.68 contacts=0 peak_mph=34.18 moving_avg_mph=29.61 under20_pct=0.0 under25_pct=28.5 over30_pct=50.0 traffic_s=0.9 corner_s=0.0 obstruction_s=0.0 guidance_s=0.0 recovery_s=0.0 brake_events=1 brake_s=0.1 longest_queue_s=0.0
TRAIN1 min_kmh=13.57 final_kmh=30.66 contacts=0 peak_mph=34.15 moving_avg_mph=23.90 under20_pct=30.5 under25_pct=35.5 over30_pct=29.5 traffic_s=3.1 corner_s=0.0 obstruction_s=0.0 guidance_s=1.8 recovery_s=0.0 brake_events=2 brake_s=0.8 longest_queue_s=0.0
TRAIN2 min_kmh=0.00 final_kmh=6.82 contacts=0 peak_mph=34.16 moving_avg_mph=27.59 under20_pct=12.0 under25_pct=17.1 over30_pct=47.4 traffic_s=5.0 corner_s=0.0 obstruction_s=0.0 guidance_s=0.6 recovery_s=0.0 brake_events=2 brake_s=1.1 longest_queue_s=0.0
TRAIN3 min_kmh=0.00 final_kmh=3.40 contacts=0 peak_mph=34.08 moving_avg_mph=28.26 under20_pct=8.1 under25_pct=11.6 over30_pct=46.8 traffic_s=7.9 corner_s=0.0 obstruction_s=0.0 guidance_s=0.4 recovery_s=0.0 brake_events=8 brake_s=1.2 longest_queue_s=1.7
TRAIN4 min_kmh=18.16 final_kmh=29.94 contacts=0 peak_mph=34.14 moving_avg_mph=26.50 under20_pct=24.0 under25_pct=27.5 over30_pct=38.5 traffic_s=7.1 corner_s=0.0 obstruction_s=0.0 guidance_s=0.0 recovery_s=0.0 brake_events=13 brake_s=0.9 longest_queue_s=0.0
TRAIN5 min_kmh=17.01 final_kmh=29.06 contacts=0 peak_mph=34.17 moving_avg_mph=26.57 under20_pct=24.5 under25_pct=27.5 over30_pct=41.5 traffic_s=7.9 corner_s=0.0 obstruction_s=0.0 guidance_s=0.0 recovery_s=0.0 brake_events=13 brake_s=0.9 longest_queue_s=0.0
PASS success=1 flips=0 contacts=0 emergency=0 final_kmh=54.60
20-kart 8s launch: contacts 0, first-second lane drift 0.1 cm
```

## Final

Suites: 15 passed, 0 failed.

| NPC | Peak | Moving avg | <20 % | <25 % | >30 % | Traffic s | Corner s | Obstruction s | Guidance s | Recovery s | Brake events | Brake s | Longest queue s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 34.18 | 23.66 | 35.9 | 50.6 | 34.1 | 17.2 | 177.2 | 0.0 | 31.6 | 0.0 | 146.0 | 21.9 | 0.2 |
| 2 | 34.18 | 23.36 | 37.8 | 52.7 | 33.7 | 41.1 | 154.0 | 0.2 | 29.4 | 0.0 | 161.0 | 24.0 | 1.0 |
| 3 | 34.18 | 23.48 | 36.9 | 51.9 | 33.5 | 53.4 | 158.4 | 0.8 | 26.0 | 0.2 | 171.0 | 22.1 | 6.6 |
| 4 | 34.18 | 23.44 | 38.3 | 52.0 | 34.3 | 34.1 | 161.1 | 2.2 | 30.2 | 0.4 | 147.0 | 23.8 | 1.5 |
| 5 | 34.18 | 21.94 | 44.1 | 58.3 | 30.1 | 111.1 | 131.1 | 0.4 | 26.1 | 0.0 | 186.0 | 26.8 | 4.4 |
| 6 | 34.18 | 23.75 | 36.4 | 50.0 | 35.8 | 64.6 | 136.4 | 0.0 | 28.3 | 6.3 | 152.0 | 26.9 | 6.0 |
| 7 | 34.18 | 22.73 | 40.2 | 55.2 | 31.6 | 60.9 | 150.7 | 0.9 | 28.8 | 6.8 | 167.0 | 30.6 | 4.6 |
| 8 | 34.18 | 23.28 | 38.6 | 52.8 | 34.5 | 54.2 | 163.2 | 0.4 | 27.5 | 0.0 | 171.0 | 22.6 | 5.9 |
| 9 | 34.18 | 22.59 | 40.8 | 54.7 | 31.9 | 74.5 | 143.2 | 3.6 | 26.6 | 0.2 | 174.0 | 26.8 | 5.2 |
| 10 | 34.18 | 22.55 | 40.6 | 54.8 | 31.0 | 61.2 | 156.4 | 0.2 | 30.8 | 7.1 | 164.0 | 29.6 | 7.3 |
| 11 | 34.18 | 23.38 | 38.4 | 52.0 | 34.3 | 120.7 | 178.2 | 0.1 | 22.0 | 6.6 | 210.0 | 36.6 | 8.1 |
| 12 | 34.18 | 22.76 | 40.9 | 54.4 | 32.1 | 67.8 | 147.8 | 0.1 | 29.2 | 0.2 | 185.0 | 25.7 | 5.8 |
| 13 | 34.18 | 22.6 | 41.2 | 55.6 | 32.1 | 103.7 | 114.4 | 0.0 | 29.1 | 6.5 | 157.0 | 28.6 | 8.2 |
| 14 | 34.18 | 22.22 | 43.5 | 56.6 | 30.8 | 94.9 | 134.6 | 1.6 | 25.2 | 7.0 | 164.0 | 31.4 | 7.4 |
| 15 | 34.18 | 22.36 | 40.8 | 56.9 | 29.8 | 81.6 | 135.7 | 0.0 | 31.2 | 0.6 | 173.0 | 22.5 | 4.3 |
| 16 | 34.18 | 21.76 | 45.4 | 60.4 | 28.4 | 154.6 | 102.0 | 1.9 | 22.0 | 0.4 | 185.0 | 27.0 | 7.3 |
| 17 | 34.18 | 21.92 | 44.2 | 59.1 | 30.1 | 112.4 | 131.9 | 0.4 | 29.9 | 0.7 | 184.0 | 26.5 | 5.9 |
| 18 | 34.18 | 22.21 | 42.9 | 57.5 | 30.2 | 87.1 | 136.1 | 3.0 | 34.3 | 1.0 | 164.0 | 27.2 | 5.4 |
| 19 | 34.18 | 21.7 | 44.9 | 59.1 | 29.1 | 116.6 | 120.7 | 1.6 | 32.1 | 0.3 | 175.0 | 25.2 | 5.6 |
| Field mean | 34.18 | 22.72 | 40.62 | 54.98 | 31.97 | 79.56 | 143.85 | 0.92 | 28.44 | 2.33 | 170.32 | 26.62 | 5.30 |

Field: mean finish 376.54s; last finisher 487.50s; summed per-kart contacts 42 (not unique collision pairs).

| NPC | Tracked pass attempts | Tracked completions |
|---|---|---|
| 1 | 0 | 0 |
| 2 | 0 | 0 |
| 3 | 4 | 0 |
| 4 | 0 | 0 |
| 5 | 4 | 0 |
| 6 | 8 | 0 |
| 7 | 1 | 0 |
| 8 | 0 | 0 |
| 9 | 3 | 0 |
| 10 | 1 | 0 |
| 11 | 3 | 0 |
| 12 | 1 | 0 |
| 13 | 4 | 2 |
| 14 | 5 | 0 |
| 15 | 3 | 0 |
| 16 | 7 | 0 |
| 17 | 5 | 0 |
| 18 | 4 | 0 |
| 19 | 10 | 1 |

### Scenario measurements and finish/contact diagnostics

```
Racer1 finish348.6s queued11.2s stopped0.1s
AI: laps 3, CP 0, speed 0.0, contacts 0, route 0, lane 129, pos X=-3373.722 Y=-5261.177 Z=24.500
Racer2 finish351.8s queued51.1s stopped0.1s
AI: laps 3, CP 0, speed 0.0, contacts 0, route 0, lane 82, pos X=-3486.554 Y=-5750.043 Z=24.500
Racer3 finish354.7s queued74.1s stopped3.4s
AI: laps 3, CP 0, speed 0.0, contacts 1, route 0, lane 56, pos X=-3425.089 Y=-5271.874 Z=24.500
Racer4 finish353.5s queued60.0s stopped2.3s
AI: laps 3, CP 0, speed 0.0, contacts 2, route 0, lane 159, pos X=-3402.702 Y=-5183.023 Z=24.500
Racer5 finish385.6s queued141.5s stopped10.6s
AI: laps 3, CP 0, speed 0.0, contacts 0, route 0, lane 261, pos X=-3408.351 Y=-5203.882 Z=24.500
Racer6 finish353.6s queued97.8s stopped7.0s
AI: laps 3, CP 0, speed 0.0, contacts 2, route 0, lane -83, pos X=-3421.207 Y=-5170.014 Z=24.500
Racer7 finish374.0s queued84.8s stopped10.3s
AI: laps 3, CP 0, speed 0.0, contacts 4, route 0, lane -21, pos X=-3368.160 Y=-5367.136 Z=24.500
Racer8 finish361.7s queued74.0s stopped3.8s
AI: laps 3, CP 0, speed 0.0, contacts 0, route 0, lane 74, pos X=-3470.474 Y=-5795.171 Z=24.500
Racer9 finish372.6s queued106.4s stopped4.6s
AI: laps 3, CP 0, speed 0.0, contacts 1, route 0, lane 35, pos X=-3489.023 Y=-5825.336 Z=24.500
Racer10 finish384.5s queued94.6s stopped19.4s
AI: laps 3, CP 0, speed 0.0, contacts 6, route 0, lane -181, pos X=-3391.937 Y=-5749.971 Z=24.500
Racer11 finish487.5s queued141.3s stopped15.0s
AI: laps 3, CP 0, speed 0.0, contacts 4, route 0, lane 66, pos X=-3397.239 Y=-5236.855 Z=24.500
Racer12 finish364.2s queued87.1s stopped3.1s
AI: laps 3, CP 0, speed 0.0, contacts 1, route 0, lane -100, pos X=-3407.117 Y=-5324.089 Z=24.500
Racer13 finish377.4s queued136.7s stopped9.8s
AI: laps 3, CP 0, speed 0.0, contacts 4, route 0, lane 67, pos X=-3442.178 Y=-5481.027 Z=24.500
Racer14 finish379.7s queued122.5s stopped9.0s
AI: laps 3, CP 0, speed 0.0, contacts 4, route 0, lane -99, pos X=-3441.673 Y=-5008.726 Z=24.500
Racer15 finish368.1s queued113.7s stopped2.1s
AI: laps 3, CP 0, speed 0.0, contacts 3, route 0, lane 80, pos X=-3410.040 Y=-5292.734 Z=24.500
Racer16 finish386.1s queued183.0s stopped3.9s
AI: laps 3, CP 0, speed 0.0, contacts 2, route 0, lane -13, pos X=-3394.769 Y=-5383.030 Z=24.500
Racer17 finish385.7s queued129.2s stopped5.0s
AI: laps 3, CP 0, speed 0.0, contacts 3, route 0, lane -44, pos X=-3451.915 Y=-5652.510 Z=24.500
Racer18 finish378.6s queued97.8s stopped7.0s
AI: laps 3, CP 0, speed 0.0, contacts 4, route 0, lane 77, pos X=-3438.190 Y=-4867.146 Z=24.500
Racer19 finish386.4s queued150.1s stopped4.1s
AI: laps 3, CP 0, speed 0.0, contacts 1, route 0, lane -130, pos X=-3413.306 Y=-5422.719 Z=24.500
CLEAR speed_kmh=54.85 t90=4.75 d90_cm=3288 t95=5.00 d95_cm=3643
EXIT120 apex_kmh=25.38 one=35.86 two=46.33 three=54.32 t90=2.35 d90_cm=2427 t95=2.60 d95_cm=2781 contacts=0
EXIT210 apex_kmh=25.38 one=35.86 two=46.33 three=54.32 t90=2.35 d90_cm=2446 t95=2.60 d95_cm=2799 contacts=0
EXIT300 apex_kmh=25.38 one=35.86 two=46.33 three=51.51 t90=2.35 d90_cm=2456 t95=2.60 d95_cm=2812 contacts=0
TRAIN0 min_kmh=38.88 final_kmh=54.68 contacts=0 ahead_cm=-1.0 closing_cms=0.0 peak_mph=34.18 moving_avg_mph=29.61 under20_pct=0.0 under25_pct=28.5 over30_pct=50.0 traffic_s=2.1 corner_s=0.0 obstruction_s=0.0 guidance_s=0.0 recovery_s=0.0 brake_events=1 brake_s=0.1 longest_queue_s=0.0
TRAIN1 min_kmh=40.26 final_kmh=54.72 contacts=0 ahead_cm=-1.0 closing_cms=0.0 peak_mph=34.18 moving_avg_mph=31.53 under20_pct=0.0 under25_pct=0.0 over30_pct=69.0 traffic_s=2.8 corner_s=0.0 obstruction_s=0.0 guidance_s=0.0 recovery_s=0.0 brake_events=1 brake_s=0.1 longest_queue_s=0.0
TRAIN2 min_kmh=40.57 final_kmh=54.85 contacts=0 ahead_cm=499.6 closing_cms=3.7 peak_mph=34.18 moving_avg_mph=31.51 under20_pct=0.0 under25_pct=0.0 over30_pct=66.0 traffic_s=3.7 corner_s=0.0 obstruction_s=0.0 guidance_s=0.0 recovery_s=0.0 brake_events=0 brake_s=0.0 longest_queue_s=0.0
TRAIN3 min_kmh=41.07 final_kmh=54.72 contacts=0 ahead_cm=-1.0 closing_cms=0.0 peak_mph=34.18 moving_avg_mph=31.60 under20_pct=0.0 under25_pct=0.0 over30_pct=64.5 traffic_s=3.3 corner_s=0.0 obstruction_s=0.0 guidance_s=0.0 recovery_s=0.0 brake_events=0 brake_s=0.0 longest_queue_s=0.0
TRAIN4 min_kmh=41.69 final_kmh=54.85 contacts=0 ahead_cm=488.9 closing_cms=4.1 peak_mph=34.18 moving_avg_mph=31.62 under20_pct=0.0 under25_pct=0.0 over30_pct=67.5 traffic_s=4.3 corner_s=0.0 obstruction_s=0.0 guidance_s=0.0 recovery_s=0.0 brake_events=0 brake_s=0.0 longest_queue_s=0.0
TRAIN5 min_kmh=42.39 final_kmh=54.98 contacts=0 ahead_cm=1584.1 closing_cms=-1.6 peak_mph=34.18 moving_avg_mph=31.66 under20_pct=0.0 under25_pct=0.0 over30_pct=69.5 traffic_s=4.6 corner_s=0.0 obstruction_s=0.0 guidance_s=0.0 recovery_s=0.0 brake_events=0 brake_s=0.0 longest_queue_s=0.0
PASS success=1 flips=0 contacts=0 emergency=0 final_kmh=54.77 attempts=1 completed=1
RELEASE blocked_cms=188.3 clear_cms=1527.8 after_s=2
20-kart 8s launch: contacts 0, first-second lane drift 0.1 cm
```
