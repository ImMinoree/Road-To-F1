"""Actual lit/unlit comparison. Visibility toggle is transient and never saved."""
import unreal as u,json,time,math
from pathlib import Path
R=Path(u.Paths.project_dir()).resolve(); E=R/'Evidence/LampAim'
L=u.get_editor_subsystem(u.LevelEditorSubsystem); A=u.get_editor_subsystem(u.EditorActorSubsystem)
assert L.load_level('/Game/RoadToF1/Maps/DesertKarting_Visual')
entries=json.loads((E/'aim.json').read_text())['DesertKarting_Visual']
entry=entries[0]; p=entry['position_cm']; t=entry['target_cm']; dx=t[0]-p[0];dy=t[1]-p[1]; d=max(math.hypot(dx,dy),1)
pos=u.Vector(t[0]-dy/d*1100,t[1]+dx/d*1100,220)
target=u.Vector((p[0]+t[0])/2,(p[1]+t[1])/2,500); v=target-pos
cam=A.spawn_actor_from_class(u.CameraActor,pos,u.Rotator(pitch=math.degrees(math.atan2(v.z,math.hypot(v.x,v.y))),yaw=math.degrees(math.atan2(v.y,v.x))))
cam.camera_component.set_field_of_view(80)
lights=[a.light_component for a in A.get_all_level_actors() if isinstance(a,u.SpotLight) and a.get_actor_label().startswith('GH_FloodPool_')]
for cmd in ['r.SetRes 1920x1080w','r.ScreenPercentage 100','t.MaxFPS 60']:u.SystemLibrary.execute_console_command(None,cmd)
s=dict(start=time.monotonic(),task=None,stage=0,busy=False);tasks=[]
def tick(dt):
    if s['busy']:return
    s['busy']=True
    try:
        if s['task'] is None and time.monotonic()-s['start']>16:
            task=u.AutomationLibrary.take_high_res_screenshot(1920,1080,str(E/('TrackLamps_On.png' if s['stage']==0 else 'TrackLamps_Off.png')),camera=cam,delay=2); tasks.append(task);s['task']=task
        elif s['task'] and s['task'].is_task_done():
            if s['stage']==0:
                for c in lights:c.set_visibility(False)
                s.update(stage=1,start=time.monotonic(),task=None)
            else:
                u.unregister_slate_post_tick_callback(handle);u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')
    finally:s['busy']=False
handle=u.register_slate_post_tick_callback(tick)
