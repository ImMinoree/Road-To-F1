import json
from pathlib import Path
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[1];data=json.loads((root/'Art/RacingAI/track_edges.json').read_text());report=json.loads((root/'Evidence/RacingAI/race_result.json').read_text())
image=Image.new('RGB',(1600,850),'white');draw=ImageDraw.Draw(image)
for pane,(x0,y0,x1,y1) in enumerate([(-6000,-22000,13000,2000),(-3000,-13500,1500,-9000)]):
    scale=min(750/(x1-x0),780/(y1-y0))
    def project(p):return (int(20+pane*800+(p[0]-x0)*scale),int(810-(p[1]-y0)*scale))
    for i in range(len(data['center'])):
        j=(i+1)%len(data['center']);draw.polygon([project(data[k][v]) for k,v in [('left',i),('left',j),('right',j),('right',i)]],fill='#dddddd')
    for key,color in [('center','black'),('guide','royalblue')]:draw.line([project(p) for p in data[key]]+[project(data[key][0])],fill=color,width=2)
    for racer in report['racers']:
        x,y=project((racer['x'],racer['y']));draw.ellipse((x-4,y-4,x+4,y+4),fill='red');draw.text((x+5,y),str(racer['slot']),fill='red')
image.save(root/'Evidence/RacingAI/route_diagnostic.png')
