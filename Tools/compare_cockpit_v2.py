"""Compose labeled evidence from unaltered Unreal captures and the supplied real reference."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
import json
ROOT=Path(__file__).resolve().parents[1];EV=ROOT/'Evidence/Cockpit_Reference_v2';ART=ROOT/'Art/PlayerVisuals/Cockpit_Reference_v2'
fontpath='C:/Windows/Fonts/arial.ttf'
font=ImageFont.truetype(fontpath,26);small=ImageFont.truetype(fontpath,19);title=ImageFont.truetype(fontpath,34)
def make_sheet(shot,name):
 canvas=Image.new('RGB',(2400,1120),(19,24,32));d=ImageDraw.Draw(canvas);d.text((26,16),'ROAD TO F1 | Cockpit geometry and road visibility',font=title,fill='white')
 paths=[EV/'Before'/f'{shot}.png',EV/'After'/f'{shot}.png',EV/'reference_real.png'];labels=['BEFORE | preserved Unreal cockpit','AFTER | reference-inspired 3D cockpit','REFERENCE | supplied real kart photo']
 for i,(path,label) in enumerate(zip(paths,labels)):
  im=Image.open(path).convert('RGB');x=i*800;d.text((x+20,72),label,font=font,fill=(225,233,242));panel=ImageOps.contain(im,(784,441),Image.Resampling.LANCZOS);canvas.paste(panel,(x+8,112+(441-panel.height)//2))
  if i<2:
   y=112+int(441*.60)
   for xx in range(x+8,x+792,24):d.line((xx,y,min(xx+13,x+791),y),fill=(61,213,235),width=2)
  d.text((x+20,574),'DETAIL | cropped from the image above',font=small,fill=(185,197,210))
  w,h=im.size
  crop=im.crop((int(w*.26),int(h*.54),int(w*.74),h)) if i<2 else im.crop((int(w*.22),int(h*.22),int(w*.79),h))
  crop=ImageOps.contain(crop,(784,410),Image.Resampling.LANCZOS);canvas.paste(crop,(x+8+(784-crop.width)//2,615+(410-crop.height)//2))
 d.text((24,1060),'Cyan guide: 60% screen height. Reference informs geometry, not a fixed camera composition.',font=small,fill=(190,203,219))
 d.text((24,1086),'Unreal road samples are stationary diagnostic POVs. No AI-generated imagery or retouching.',font=small,fill=(190,203,219));canvas.save(EV/name)
make_sheet('straight_center','Before_After_Reference.png');make_sheet('corner_left','Corner_Before_After_Reference.png')
shots=['straight_center','straight_left','straight_right','corner_left','corner_right'];grid=Image.new('RGB',(2400,1080),(19,24,32));d=ImageDraw.Draw(grid)
for i,name in enumerate(shots):
 x=(i%3)*800;y=(i//3)*540;im=Image.open(EV/'After'/f'{name}.png').convert('RGB').resize((784,441),Image.Resampling.LANCZOS);grid.paste(im,(x+8,y+62));d.text((x+20,y+15),name.replace('_',' ').upper(),font=font,fill='white')
d.text((1620,575),'ACTUAL UNREAL POV',font=title,fill='white');d.text((1620,635),'Center and +/-25 degree steering',font=small,fill='white');d.text((1620,670),'Straight and corner road samples',font=small,fill='white');d.text((1620,705),'105 degree horizontal FOV',font=small,fill='white');grid.save(EV/'Unreal_Views.png')
g=json.loads((ART/'geometry_validation.json').read_text());surfaces=json.loads((ART/'surface_contacts.json').read_text())
summary={'screenshots':'Actual Unreal 1600x900 renders, stationary diagnostic camera/visual rig at measured road samples; gameplay actors not teleported. No driving dynamics claim.','straight_pose_cm':[-503.9471,21.3882,31],'corner_pose_cm':[9034.8835,-1290.1299,31],'screen_framing':g['projected_driver_wheel_bounds'],'worst_sampled_glove_compression_mm':-g['worst_signed_clearance_m']*1000,'surface_check_maxima':{k:max(x[k] for x in surfaces['rows']) for k in ['arm_leg_surface_pairs','arm_chassis_surface_pairs','leg_chassis_surface_pairs','left_right_leg_surface_pairs']},'display':'Cosmetic DEMO readout, not live telemetry','images':[str(EV/n) for n in ['Before_After_Reference.png','Corner_Before_After_Reference.png','Unreal_Views.png']]}
(EV/'validation_summary.json').write_text(json.dumps(summary,indent=2));print('COMPARISON_COMPLETE')
