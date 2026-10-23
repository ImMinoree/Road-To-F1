# Reference kart

`Kart_Reference.blend` is the editable scene in estimated metric scale. `Exports/SM_Kart_Reference.fbx` is the Unreal-ready interchange model, and `Kart_Reference.glb` is useful in other viewers and DCC tools. Open `Kart_Explore.html` in a browser for the offline interactive model. `Kart_Reference.png` is the rendered preview. Run `D:\Boring\blender.exe -b -t 8 --python build_kart.py` to regenerate the set, and `python package_viewer.py` to rebuild the viewer.

The kart is about 1.8 m long and 1.25 m wide, with front along +X and Z up. The model has separate named mesh components for the four axle-centered wheels, chassis, body, seat, controls, engine, exhaust, chain drive, tank, brakes, and small fittings. It has satin graphite body panels, visible welds and scratches, slick tires with detailed sidewalls and alloy rims, a finned 125 cc air-cooled engine, exposed sprockets and chain, curved exhaust, fuel cap, pedals, steering wheel, hydraulic lines, and fasteners. There is no driver because none is shown in the reference.

For Unreal, open the project and run `Tools/import_kart.py` from **Tools → Execute Python Script**. It imports the FBX as separate Static Mesh assets into `/Game/RoadToF1/DesertKarting/Kart`, with embedded material colors. It does not create or change a level. Wheel components retain separate pivots for later Blueprint attachment and animation; add collision and physics settings when creating the gameplay kart.

The reference has a cinematic, weathered finish, so fine material grain and wear are procedural in Blender. FBX carries component geometry, material base colors, metallic values, roughness, and smooth shading; Blender-only procedural grain is preserved in the `.blend` source.
