from pathlib import Path
import base64,json,struct

p=Path(__file__).resolve().parent
b=(p/'Kart_Reference.glb').read_bytes()
assert b[:4]==b'glTF' and struct.unpack_from('<I',b,8)[0]==len(b)
n=struct.unpack_from('<I',b,12)[0];g=json.loads(b[20:20+n])
for a in g['accessors']:
    assert a['count']>0 and a['bufferView']<len(g['bufferViews'])
t=(p/'kart_viewer_template.html').read_text(encoding='utf-8')
t=t.replace('Desert Karting','Sprint Kart | Reference Study').replace('A detailed, explorable sunset circuit study','A close look at the exposed 125 cc racing kart')
t=t.replace('<button data-view="circuit">Circuit</button>','<button data-view="circuit">Driver view</button>')
t=t.replace('<button data-view="grandstand">Grandstand</button>','<button data-view="grandstand">Engine</button>')
t=t.replace('<button data-view="top">Plan view</button>','<button data-view="top">Top view</button>')
t=t.replace('<label><input id="background" type="checkbox" checked> Distant circuit</label>', '<label>Unreal import</label><a href="Exports/SM_Kart_Reference.fbx">Download FBX model ↓</a>')
t=t.replace('if(!document.getElementById(\'background\').checked&&d.name.startsWith(\'13 \'))continue;','')
t=t.replace('theta=-2.60,phi=.97,radius=470,target=[20,0,45]','theta=.60,phi=1.02,radius=4.0,target=[-.03,.42,0]')
t=t.replace('overview:[-2.60,.97,470,[20,0,45]],circuit:[2.72,.85,276,[4,0,-2]],grandstand:[-1.2,1.12,95,[124,6,-42]],top:[Math.PI,.035,460,[12,0,45]]','overview:[.60,1.02,4.0,[-.03,.42,0]],circuit:[.10,1.14,3.5,[.28,.48,0]],grandstand:[-.80,1.08,3.8,[-.42,.47,0]],top:[0,.035,4.4,[-.03,.42,0]]')
t=t.replace('n=10,far=15000','n=.05,far=100')
t=t.replace('Includes 48 karts, drivers, spectators, tensile canopies, towers, pit transporters, wire fencing, tire stacks, palms, and lighting.','Includes separate chassis, body panels, bucket seat, axle pivots, slicks, alloy rims, controls, steering, fuel tank, brakes, chain and sprockets, finned engine, and exhaust.')
t=t.replace('Full materials, cameras, and physical lighting are included in the Blender file.','The Blender source preserves procedural material grain and the editable component origins.')
t=t.replace('Self-contained 3D viewer · No installation or internet required','Unbranded reference model · Dimensions approximated from the photo')
t=t.replace('__GLB_BASE64__',base64.b64encode(b).decode())
assert '__GLB_BASE64__' not in t and 'Distant circuit' not in t
(p/'Kart_Explore.html').write_text(t,encoding='utf-8')
print('Packaged self-contained kart viewer:',len(t),'bytes,',len(g['meshes']),'mesh definitions')
