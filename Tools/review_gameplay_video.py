import sys,os,subprocess,json
from pathlib import Path
sys.path.insert(0,os.path.join(os.environ['TEMP'],'road_f1_video_decode'))
import imageio_ffmpeg
ff=imageio_ffmpeg.get_ffmpeg_exe();video=r'C:/Users/GBURG-4/Videos/NVIDIA/Unreal Engine 5/Unreal Engine 5 2026.10.29 - 20.11.49.01.mp4'
E=Path('Evidence/GameplayCompetition/Video');E.mkdir(parents=True,exist_ok=True)
r=subprocess.run([ff,'-hide_banner','-i',video],capture_output=True,text=True);(E/'metadata.txt').write_text(r.stderr)
for t in [8,16,24,40,60,80,92,93,94,95,96,102]:
 subprocess.run([ff,'-hide_banner','-loglevel','error','-y','-ss',str(t),'-i',video,'-frames:v','1','-vf','scale=960:-2',str(E/f'{t:03d}.png')],check=True)
print(r.stderr[:1200])
