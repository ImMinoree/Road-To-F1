"""Capture actual grass at kart eye height and from above; no map changes saved."""
import unreal as u,json,time,math
from pathlib import Path
R=Path(u.Paths.project_dir()).resolve();E=R/'Evidence/InfieldGrass';E.mkdir(parents=True,exist_ok=True)
g=json.loads((R/'Art/InfieldGrass/scatter.json').read_text());route=json.loads((R/'Art/DesertRoute/audit.json').read_text())['route_cm']
L=u.get_editor_subsystem(u.LevelEditorSubsystem);A=u.get_editor_subsystem(u.EditorActorSubsystem)
views=[('DesertKarting_Visual','Close'),('DesertKarting_Visual','Aerial'),('DesertKarting','Close')]
s=dict(i=0,busy=False);tasks=[]
def prepare():
    name,view=views[s['i']];assert L.load_level('/Game/RoadToF1/Maps/'+name)
    if view=='Aerial':
        pos=u.Vector(3500,-3500,5500);rot=u.Rotator(pitch=-65,yaw=-135);fov=90
    else:
        # A lawn-edge point near the straight; camera stays at kart eye height.
        p=min(g['placements'],key=lambda p:(p['location'][0]-1800)**2+(p['location'][1]+1200)**2)['location']
        q=min(route,key=lambda q:(q[0]-p[0])**2+(q[1]-p[1])**2);dx=p[0]-q[0];dy=p[1]-q[1];d=max(math.hypot(dx,dy),1)
        pos=u.Vector(p[0]-dx/d*150,p[1]-dy/d*150,p[2]+80);rot=u.Rotator(pitch=-13,yaw=math.degrees(math.atan2(dy,dx))+28);fov=82
    cam=A.spawn_actor_from_class(u.CameraActor,pos,rot);cam.camera_component.set_field_of_view(fov)
    s.update(camera=cam,start=time.monotonic(),task=None,done=None)
    for cmd in ['r.SetRes 1920x1080w','r.ScreenPercentage 100','sg.ViewDistanceQuality 2','sg.ShadowQuality 2','t.MaxFPS 60']:u.SystemLibrary.execute_console_command(None,cmd)
def tick(dt):
    if s['busy']:return
    s['busy']=True
    try:
        if time.monotonic()-s['start']>22 and s['task'] is None:
            name,view=views[s['i']];task=u.AutomationLibrary.take_high_res_screenshot(1920,1080,str(E/(name+'_'+view+'.png')),camera=s['camera'],delay=2);tasks.append(task);s['task']=task
        if s['task'] and s['task'].is_task_done():
            if s['done'] is None:s['done']=time.monotonic()
            if time.monotonic()-s['done']>2:
                s['i']+=1
                if s['i']==len(views):u.unregister_slate_post_tick_callback(handle);u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')
                else:prepare()
    except Exception as e:
        (E/'capture_error.txt').write_text(str(e));u.unregister_slate_post_tick_callback(handle);u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')
    finally:s['busy']=False
prepare();handle=u.register_slate_post_tick_callback(tick)
