from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import shutil
ROOT=Path(__file__).resolve().parent.parent;E=ROOT/'Evidence/Cockpit_Target_v4';B=E/'Before';B.mkdir(exist_ok=True)
for p in (ROOT/'Evidence/Wheel_Visibility_v3/After').glob('*.png'):
 if not (B/p.name).exists():shutil.copy2(p,B/p.name)
f=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',25)
canvas=Image.new('RGB',(2160,980),(20,22,27));d=ImageDraw.Draw(canvas)
for col,(path,label) in enumerate([(B/'straight_center.png','PREVIOUS'),(E/'After/straight_center.png','ACTUAL UNREAL — V4'),(E/'reference.png','YOUR TARGET')]):
 im=Image.open(path).convert('RGB');im.thumbnail((720,405));canvas.paste(im,(720*col,45));d.text((720*col+15,10),label,font=f,fill='white');original=Image.open(path).convert('RGB');W,H=original.size;crop=original.crop((int(W*.22),int(H*.43),int(W*.78),H));crop.thumbnail((700,485));canvas.paste(crop,(720*col+(720-crop.width)//2,485))
canvas.save(E/'Previous_Actual_Target.png')
canvas=Image.new('RGB',(1920,400),(20,22,27));d=ImageDraw.Draw(canvas)
for col,name in enumerate(['straight_left','straight_center','straight_right']):
 im=Image.open(E/'After'/(name+'.png')).convert('RGB');im.thumbnail((640,360));canvas.paste(im,(640*col,40));d.text((640*col+15,5),name.replace('straight_','').upper(),font=f,fill='white')
canvas.save(E/'Steering_Check.png')
