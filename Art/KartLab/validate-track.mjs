import assert from 'node:assert/strict';
import {createCircuit} from './scene.mjs';

let triangles=0;
for(const mesh of createCircuit().children.filter(o=>/Track asphalt|kerb|edge line/.test(o.name))){
  const p=mesh.geometry.attributes.position,index=mesh.geometry.index;
  for(let i=0;i<index.count;i+=3){
    const a=index.getX(i),b=index.getX(i+1),c=index.getX(i+2);
    const up=(p.getZ(b)-p.getZ(a))*(p.getX(c)-p.getX(a))-(p.getX(b)-p.getX(a))*(p.getZ(c)-p.getZ(a));
    assert(up>0,`${mesh.name}: folded or degenerate triangle ${i/3}`);
    triangles++;
  }
}
console.log(`PASS: ${triangles} road, kerb and edge-line triangles face upward without folds.`);
