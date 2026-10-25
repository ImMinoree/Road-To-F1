"""Use the verified route as guidance inside the measured asphalt-edge corridor."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];path=ROOT/'Art/RacingAI/track_edges.json';data=json.loads(path.read_text())
data['guide']=data['center'];data['guide_method']='Verified original route between measured asphalt polygon edges'
data.pop('guide_min_radius_cm',None);path.write_text(json.dumps(data,indent=2));print('GUIDE_SAMPLES',len(data['guide']))
