# CircuitDevelopment runtime sample

Standalone Unreal Editor game session, D3D12 SM6, NVIDIA RTX 3080 10 GB, i7-10700KF and 32 GB RAM. 1920x1080 output, Balanced scalability 2, 75% internal resolution / TSR, software Lumen, conventional shadows, VSync and frame cap off.

The final 10.0060 seconds of the existing bounded driving test recorded 1283 frames: **7.799 ms average / 128.22 FPS**. Raw data: Runtime.json; engine log: ../CircuitRuntime.log. The unchanged temporary pawn accelerated, steered, braked and exited normally. Final location was (3561.53, -31.76, 34.45) cm, versus spawn (800, 0, 31); it followed the new road's mild elevation.

This is a start-straight sample in an editor game build, not a packaged full-lap test or a 20-kart benchmark. It does not establish worst-case frame time around the circuit. The raw scope string is inherited from the original generic smoke-test code; no concurrent validation editor was running during this sample. No individual GPU-pass bottleneck ranking was measured.

Repeated props use instancing and runtime 140–240 m culling. Tire collision uses simple boxes; fences/signs/drains do not add collision. Validation screenshots use Epic at full internal resolution. Their overhead view extends component culling temporarily to show all placement, without saving that override into the runtime map.
