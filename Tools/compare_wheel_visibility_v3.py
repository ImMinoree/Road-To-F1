"""Label/rescale genuine Unreal screenshots for comparison; no generated cockpit imagery."""
from pathlib import Path
import json,hashlib,shutil
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent.parent;E=ROOT/'Evidence/Wheel_Visibility_v3';OLD=E/'Before';OLD.mkdir(exist_ok=True)
for name in ['straight_center','straight_left','straight_right']:
 if not (OLD/(name+'.png')).exists():shutil.copy2(ROOT/'Evidence/Cockpit_Reference_v2/After'/(name+'.png'),OLD/(name+'.png'))
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',23)
canvas=Image.new('RGB',(1920,1164),(20,22,27));d=ImageDraw.Draw(canvas)
for col,(name,label) in enumerate([('straight_center','CENTER'),('straight_left','FULL LEFT'),('straight_right','FULL RIGHT')]):
 for row,(folder,title) in enumerate([(OLD,'BEFORE'),(E/'After','AFTER')]):
  im=Image.open(folder/(name+'.png')).convert('RGB');im.thumbnail((640,360));x=col*640;y=row*582;canvas.paste(im,(x,y+42));d.text((x+15,y+10),title+' — '+label,font=font,fill='white')
  crop=Image.open(folder/(name+'.png')).convert('RGB').crop((590,520,1010,900));crop.thumbnail((196,176));canvas.paste(crop,(x+220,y+406));d.text((x+15,y+438),'Wheel detail',font=font,fill='white')
canvas.save(E/'Before_After_Steering.png')
prior=json.loads((E/'preserved_before.json').read_text());checked=[{'path':x['Path'],'unchanged':hashlib.sha256(Path(x['Path']).read_bytes()).hexdigest().upper()==x['Hash']} for x in prior];(E/'preservation_check.json').write_text(json.dumps({'checks':checked,'note':'This task edits only the local visual component/test and separate POV art. Concurrent project changes are not reverted.'},indent=2))
