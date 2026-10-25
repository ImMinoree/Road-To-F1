from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent/'Textures';P.mkdir(exist_ok=True);n=1024;y,x=np.mgrid[:n,:n];rng=np.random.default_rng(47)
warp=np.sin(x*np.pi/4);weft=np.sin(y*np.pi/4);over=((x//8+y//8)%2);h=np.where(over,warp,weft)*.32+np.sin((x+y)*np.pi/16)*.08+rng.normal(0,.035,(n,n));dx=np.roll(h,-1,1)-np.roll(h,1,1);dy=np.roll(h,-1,0)-np.roll(h,1,0);normal=np.stack((-dx,-dy,np.ones_like(h)*1.4),-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
Image.fromarray(np.uint8((normal*.5+.5)*255)).save(P/'T_CT4_Weave_N.png');gray=np.clip(.82+h*.13+rng.normal(0,.012,h.shape),0,1);Image.fromarray(np.uint8(np.repeat(gray[:,:,None],3,2)*255)).save(P/'T_CT4_Weave_C.png');Image.fromarray(np.uint8(np.clip(.76+h*.13,0,1)*255)).save(P/'T_CT4_Weave_R.png')
im=Image.new('RGB',(1024,640),(106,132,100));d=ImageDraw.Draw(im)
for yy in range(640):d.line((0,yy,1024,yy),fill=(106+yy//50,132+yy//70,100+yy//80))
font=lambda z:ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',z)
d.rounded_rectangle((28,26,210,305),14,fill=(19,30,21));d.text((75,35),'1',font=font(200),fill=(126,156,119));d.text((35,310),'DRIVE',font=font(43),fill=(20,35,24));d.text((800,150),'km/h',font=font(49),fill=(17,33,21));d.line((24,382,1000,382),fill=(30,48,32),width=5);d.text((30,418),'TIME',font=font(49),fill=(19,35,23));d.line((24,528,1000,528),fill=(30,48,32),width=5);d.text((30,552),'LOAD',font=font(34),fill=(19,35,23))
for i in range(23):d.rectangle((210+i*31,559,232+i*31,608),fill=(25,70,42) if i<16 else (37,49,36))
im.save(P/'T_CT4_LCD.png')
