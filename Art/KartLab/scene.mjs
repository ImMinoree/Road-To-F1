import * as T from './vendor/three.module.js';
export const palette = {};
function material(name,color,metalness=0,roughness=.65){const m=new T.MeshStandardMaterial({name,color,metalness,roughness});palette[name]=m;return m;}
const red=material('Fairing',0xc91928,.15,.26), steel=material('Chassis',0xcc2334,.7,.32), alloy=material('Aluminium',0xb8bdc2,.88,.3), black=material('Rubber',0x15171a,0,.88), carbon=material('Carbon',0x252a2b,.15,.42), dark=material('Engine',0x3e444b,.75,.37), gold=material('Chain',0xa68a40,.85,.4), white=material('White',0xf0ede3,0,.5);
export function mesh(g,m,p,parent,name){const o=new T.Mesh(g,m);o.position.set(...p);o.name=name||m.name;o.castShadow=true;o.receiveShadow=true;parent.add(o);return o;}
function box(parent,name,p,s,m){return mesh(new T.BoxGeometry(...s),m,p,parent,name);}
function tube(parent,name,points,r,m){return mesh(new T.TubeGeometry(new T.CatmullRomCurve3(points.map(p=>new T.Vector3(...p))),Math.max(12,points.length*8),r,8,false),m,[0,0,0],parent,name);}
function rod(parent,name,a,b,r,m){const va=new T.Vector3(...a),vb=new T.Vector3(...b),d=vb.clone().sub(va);const o=mesh(new T.CylinderGeometry(r,r,d.length(),16),m,va.clone().add(vb).multiplyScalar(.5).toArray(),parent,name);o.quaternion.setFromUnitVectors(new T.Vector3(0,1,0),d.normalize());return o;}
function fairing(parent,name,outline,depth,p,m){const s=new T.Shape();outline.forEach(([x,z],i)=>i?s.lineTo(x,z):s.moveTo(x,z));s.closePath();const g=new T.ExtrudeGeometry(s,{depth,bevelEnabled:true,bevelThickness:.035,bevelSize:.035,bevelSegments:3,steps:1});g.rotateX(-Math.PI/2);return mesh(g,m,p,parent,name);}
export function createKart(){const kart=new T.Group();kart.name='RoadToF1_125_Concept';const parts={};const part=n=>{const g=new T.Group();g.name=n;kart.add(g);parts[n]=g;return g;};
const frame=part('Tubular steel chassis');
for(const x of [-.31,.31])tube(frame,'32mm chassis rail',[[x,.14,.77],[x,.14,.5],[x,.14,-.45],[x*.75,.14,-.79]],.016,steel);
for(const z of [-.63,-.13,.48,.7])rod(frame,'Crossmember',[-.33,.14,z],[.33,.14,z],.016,steel);
tube(frame,'Rear bumper',[[-.65,.16,.77],[-.65,.22,.91],[.65,.22,.91],[.65,.16,.77]],.02,black);
box(frame,'Aluminium floor tray',[0,.15,-.22],[.66,.012,.94],alloy);
const wheels=part('Slick tires and hubs');
for(const z of [-.65,.66])for(const side of [-1,1]){const x=side*(z<0?.56:.57),radius=z<0?.128:.14,width=z<0?.115:.19;
const tire=mesh(new T.CylinderGeometry(radius,radius,width,48,1,false),black,[x,radius,z],wheels,'Slick racing tire');tire.rotation.z=Math.PI/2;
const hub=mesh(new T.CylinderGeometry(radius*.58,radius*.58,width+.006,32),alloy,[x,radius,z],wheels,'Cast alloy rim');hub.rotation.z=Math.PI/2;
for(const outer of [-1,1]){const ring=mesh(new T.TorusGeometry(radius*.71,.007,8,40),black,[x+outer*width*.48,radius,z],wheels,'Tire shoulder');ring.rotation.y=Math.PI/2;for(let i=0;i<3;i++){const a=i*2*Math.PI/3;rod(wheels,'Hub bolt',[x+outer*(width/2+.005),radius+.033*Math.cos(a),z+.033*Math.sin(a)],[x+outer*(width/2+.013),radius+.033*Math.cos(a),z+.033*Math.sin(a)],.007,dark);}}
}
const body=part('Nosecone and side pods');
fairing(body,'Impact nosecone',[[-.54,-.15],[-.55,.08],[-.4,.18],[.4,.18],[.55,.08],[.54,-.15],[.29,-.24],[-.29,-.24]],.12,[0,.18,-.96],red);
for(const side of [-1,1]){fairing(body,'Side pod',[[-.115,-.4],[.09,-.43],[.145,-.28],[.145,.3],[.07,.37],[-.115,.31]],.13,[side*.47,.17,.05],red);rod(frame,'Side pod mounting bar',[side*.3,.16,-.22],[side*.5,.16,.22],.014,steel);}
fairing(body,'Front number panel',[[-.18,-.22],[.18,-.22],[.125,.25],[-.125,.25]],.025,[0,.26,-.4],white).rotation.x=-.48;
box(body,'Nose stripe',[0,.34,-.94],[.23,.007,.24],white);
const cockpit=part('Seat steering and pedals');
const seatShape=new T.Shape();seatShape.moveTo(-.22,0);seatShape.lineTo(-.24,.19);seatShape.lineTo(-.19,.47);seatShape.lineTo(.19,.47);seatShape.lineTo(.24,.19);seatShape.lineTo(.22,0);seatShape.closePath();
const seat=mesh(new T.ExtrudeGeometry(seatShape,{depth:.026,bevelEnabled:true,bevelSize:.025,bevelThickness:.02,bevelSegments:3}),carbon,[0,.18,.38],cockpit,'Carbon seat back');seat.rotation.x=-.16;
fairing(cockpit,'Bucket seat base',[[-.22,-.23],[.22,-.23],[.2,.19],[-.2,.19]],.03,[0,.2,.2],carbon);
for(const x of [-.22,.22])tube(cockpit,'Bucket seat side',[[x,.23,-.01],[x*1.05,.28,.17],[x,.48,.38]],.033,carbon);
rod(cockpit,'Steering column',[0,.18,-.57],[0,.58,-.24],.014,alloy);
const sw=new T.Group();sw.position.set(0,.58,-.24);sw.rotation.x=-.7;cockpit.add(sw);
mesh(new T.TorusGeometry(.145,.016,12,48),black,[0,0,0],sw,'Steering wheel rim');for(let i=0;i<3;i++){const a=i*Math.PI*2/3;rod(sw,'Steering spoke',[0,0,0],[Math.sin(a)*.13,Math.cos(a)*.13,0],.009,alloy);}box(sw,'Telemetry display',[0,.07,-.012],[.078,.038,.022],dark);
for(const x of [-.2,.2]){tube(cockpit,'Pedal',[[x,.16,-.73],[x,.32,-.77],[x+.06,.32,-.77]],.009,alloy);}
for(const side of [-1,1])rod(frame,'Steering tie rod',[0,.15,-.57],[side*.47,.13,-.64],.008,alloy);
const drive=part('125cc engine and rear axle');
rod(drive,'Live rear axle',[-.71,.14,.66],[.71,.14,.66],.025,alloy);
box(drive,'Two stroke crankcase',[.35,.26,.49],[.21,.19,.24],dark);box(drive,'Cylinder',[.35,.41,.49],[.15,.16,.15],alloy);
for(let i=0;i<8;i++)box(drive,'Cylinder cooling fin',[.35,.35+i*.018,.49],[.195,.008,.19],dark);
rod(drive,'Spark plug',[.35,.5,.49],[.35,.55,.49],.012,white);
box(drive,'Airbox',[.34,.29,.26],[.17,.14,.18],black);
tube(drive,'Expansion chamber exhaust',[[.39,.38,.52],[.56,.36,.58],[.51,.28,.85],[.25,.28,.85],[-.04,.29,.73]],.065,dark);
rod(drive,'Exhaust silencer',[-.15,.3,.72],[-.4,.3,.81],.035,alloy);
for(const x of [.22,-.18]){const disc=mesh(new T.CylinderGeometry(x>0?.077:.09,x>0?.077:.09,.009,32),x>0?gold:alloy,[x,.14,.66],drive,x>0?'Rear sprocket':'Brake disc');disc.rotation.z=Math.PI/2;}
box(drive,'Brake caliper',[-.18,.22,.67],[.055,.06,.08],dark);
tube(drive,'Drive chain',[[.23,.14,.57],[.23,.2,.4],[.23,.29,.4],[.23,.22,.72],[.23,.14,.74],[.23,.14,.57]],.008,gold);
box(drive,'Fuel tank',[0,.26,-.23],[.18,.18,.24],white);rod(drive,'Fuel cap',[0,.35,-.23],[0,.38,-.23],.025,black);
box(drive,'Water radiator',[-.31,.43,.3],[.045,.32,.22],alloy);for(let i=0;i<15;i++)box(drive,'Radiator fin',[-.337,.28+i*.02,.3],[.006,.008,.205],dark);
tube(drive,'Coolant hose',[[-.32,.56,.3],[-.12,.52,.46],[.29,.47,.48]],.012,black);
kart.userData.parts=parts;return kart;}
const asphalt=material('Asphalt',0x666968,0,.92), grass=material('Grass',0x61744a,0,.97), curbBlue=material('Kerb_blue',0x326dab,0,.7), building=material('Concrete',0xb6b7ac,0,.86), roof=material('Roof',0x727c83,.5,.5), leaves=material('Foliage',0x344e2a,0,.95), bark=material('Bark',0x64543b,0,.9), gravel=material('Gravel',0xb4aa91,0,.95), glass=material('Glass',0x32566b,.3,.2);
// Art blockout, not a survey or a homologated reconstruction. Coordinates in metres.
export const route=[[-135,-52],[85,-52],[130,-43],[145,-18],[125,-5],[70,-12],[22,-15],[-15,-5],[-20,14],[8,23],[72,18],[120,26],[138,43],[112,57],[63,52],[37,34],[8,38],[-13,58],[-45,61],[-67,42],[-91,24],[-122,32],[-143,21],[-147,0],[-123,-10],[-84,-1],[-48,-16],[-73,-33],[-128,-27],[-151,-37]];
export function trackCurve(){
// Filter uniformly spaced samples before offsetting the 9m road. The original
// tight control-point bends had radii smaller than the road half-width, folding
// inner asphalt/kerb triangles backwards into the racing surface.
const raw=new T.CatmullRomCurve3(route.map(([x,z])=>new T.Vector3(x,0,z)),true,'catmullrom',.3);
raw.arcLengthDivisions=6000;
const points=Array.from({length:600},(_,i)=>raw.getPointAt(i/600));
const smooth=points.map((_,i)=>{const p=new T.Vector3();for(let j=-6;j<=6;j++)p.add(points[(i+j+600)%600]);return p.divideScalar(13);});
const c=new T.CatmullRomCurve3(smooth,true,'centripetal');c.arcLengthDivisions=6000;return c;
}
function ribbon(curve,width,offset,y,segments=1100,start=0,end=1){const p=[],uv=[],indices=[];for(let i=0;i<=segments;i++){const t=start+(end-start)*i/segments,v=curve.getPointAt(t),d=curve.getTangentAt(t),n=new T.Vector3(-d.z,0,d.x);for(const side of [-1,1]){const q=v.clone().addScaledVector(n,offset+side*width/2);p.push(q.x,y,q.z);uv.push((side+1)/2,t*curve.getLength()/6);}if(i<segments){const a=i*2;indices.push(a,a+1,a+2,a+1,a+3,a+2);}}const g=new T.BufferGeometry();g.setAttribute('position',new T.Float32BufferAttribute(p,3));g.setAttribute('uv',new T.Float32BufferAttribute(uv,2));g.setIndex(indices);g.computeVertexNormals();return g;}
const kerbWhite=material('Kerb_white',0xf0ede3,0,.7),kerbSurfaceBlue=material('Kerb_blue_surface',0x326dab,0,.7),paint=material('RoadPaint',0xf0ede3,0,.85);
export function createCircuit(){const group=new T.Group();group.name='SouthGarda_ArtBlockout';const c=trackCurve();mesh(new T.BoxGeometry(430,.8,260),grass,[0,-.44,0],group,'Grass infield');mesh(ribbon(c,9,0,.025),asphalt,[0,0,0],group,'Track asphalt');
const samples=640;for(let i=0;i<samples;i++)for(const side of [-1,1])mesh(ribbon(c,.6,side*4.8,.033,4,i/samples,(i+1)/samples),i%2?kerbWhite:kerbSurfaceBlue,[0,0,0],group,'Continuous painted kerb');
for(const side of [-1,1])mesh(ribbon(c,.08,side*4.42,.028),paint,[0,0,0],group,'Continuous track edge line');
// Paddock and start straight buildings.
box(group,'Paddock asphalt',[0,.015,-100],[295,.03,65],asphalt);
box(group,'Pit building',[12,3,-70],[182,6,13],building);box(group,'Pit building roof',[12,6.15,-70],[186,.3,15],roof);
for(let x=-73;x<97;x+=8){box(group,'Garage shutter',[x,2,-63.45],[5.8,3.7,.1],roof);box(group,'Upper glazing',[x,5,-63.4],[5.8,1,.12],glass);}
box(group,'Grandstand back',[0,3,-85],[110,6,1],building);for(let i=0;i<7;i++){box(group,'Grandstand terrace',[0,.5+i*.6,-79-i*.9],[110,1+i*1.2,.9],building);for(let x=-52;x<53;x+=3)box(group,'Spectator seats',[x,1.1+i*.6,-79-i*.9],[2,.3,.6],i%2?curbBlue:white);}
box(group,'Grandstand canopy',[0,6.7,-82],[114,.25,11],roof);for(const x of [-54,-27,0,27,54])rod(group,'Canopy column',[x,0,-86],[x,6.7,-86],.16,alloy);
for(let i=0;i<20;i++){const x=-125+i*13;box(group,'Team tent',[x,2,-115],[9,4,6],i%3?white:curbBlue);box(group,'Service truck',[x,1.4,-126],[8,2.8,2.6],white);}
for(let row=0;row<6;row++)for(const lane of [-1,1]){const x=-76-row*6,z=-52+lane*2;box(group,'Grid position rear line',[x,.029,z],[.06,.001,1.3],paint);for(const side of [-1,1])box(group,'Grid position side line',[x+.85,.029,z+side*.65],[1.7,.001,.06],paint);}
const finish=c.getPointAt(.06),finishDir=c.getTangentAt(.06),finishNormal=new T.Vector3(-finishDir.z,0,finishDir.x);
for(let row=0;row<2;row++)for(let column=0;column<12;column++){const p=finish.clone().addScaledVector(finishDir,(row-.5)*.6).addScaledVector(finishNormal,(column-5.5)*.75);const o=box(group,'Finish checker',[p.x,.03,p.z],[.6,.001,.75],(row+column)%2?paint:black);o.rotation.y=Math.atan2(-finishDir.z,finishDir.x);}
for(const z of [-58,-46])rod(group,'Start gantry post',[-55,0,z],[-55,6,z],.18,roof);box(group,'Start gantry',[-55,6,-52],[.45,.8,13],white);
for(let i=0;i<5;i++)mesh(new T.SphereGeometry(.19,10,8),red,[-54.75,5.85,-53+i*.5],group,'Start light');
// Deterministic Mediterranean cypress and broadleaf silhouettes.
let seed=187;const random=()=>{seed=(seed*16807)%2147483647;return(seed-1)/2147483646;};
for(let i=0;i<170;i++){const edge=i%4;const x=edge<2?-203+random()*406:(edge===2?-198:198),z=edge<2?(edge===0?-145:115):-140+random()*255;const h=7+random()*7;rod(group,'Tree trunk',[x,0,z],[x,h*.65,z],.3,bark);if(i%3===0)mesh(new T.ConeGeometry(1.25,h,10),leaves,[x,h*.65,z],group,'Cypress');else mesh(new T.IcosahedronGeometry(h*.31,1),leaves,[x,h*.68,z],group,'Broadleaf tree');}
for(let i=0;i<20;i++){const x=-320+i*35;const hill=mesh(new T.SphereGeometry(1,20,10),grass,[x,-22,185],group,'Distant hill');hill.scale.set(50,30+15*Math.sin(i),45);}
// The first circuit uses a continuous kerb boundary. Omit the previous sparse
// barrier blocks until a proper safety-barrier layout is authored.
group.userData.routeLength=c.getLength();group.userData.start=[-75,.5,-52];return group;}
