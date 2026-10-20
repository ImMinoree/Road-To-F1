"""Editor tick capture: 3 fixed views, 1080p, quality 3, full resolution TSR."""
import unreal as u, time, json
from pathlib import Path
ROOT=Path(u.Paths.project_dir()).resolve()
level=u.get_editor_subsystem(u.LevelEditorSubsystem)
level.load_level('/Game/RoadToF1/Maps/VisualProof')
shots=json.loads((ROOT/'Evidence'/'scene.json').read_text())['shots']
mesh_report={}
for name in ['Road','CurbLeft','CurbRight','VergeLeft','VergeRight']:
    mesh=u.load_asset('/Game/RoadToF1/Meshes/'+name)
    box=mesh.get_bounding_box()
    mesh_report[name]={'min_cm':str(box.min),'max_cm':str(box.max),'collision':str(mesh.get_editor_property('body_setup').get_editor_property('collision_trace_flag'))}
(ROOT/'Evidence'/'ImportedMeshes.json').write_text(json.dumps(mesh_report,indent=2))
for cmd in ['sg.ViewDistanceQuality 3','sg.AntiAliasingQuality 3','sg.ShadowQuality 3','sg.GlobalIlluminationQuality 3','sg.ReflectionQuality 3','sg.PostProcessQuality 3','sg.TextureQuality 3','sg.EffectsQuality 3','sg.FoliageQuality 3','r.ScreenPercentage 100','r.SetRes 1920x1080w']:
    u.SystemLibrary.execute_console_command(None,cmd)
u.SystemLibrary.execute_console_command(None,'r.HighResScreenshotDelay 8')
u.SystemLibrary.execute_console_command(None,'r.Shadow.Virtual.Enable 1')
editor=u.get_editor_subsystem(u.UnrealEditorSubsystem)
state={'index':0,'time':time.monotonic(),'captured':False}
editor.set_level_viewport_camera_info(u.Vector(*shots[0][1]),u.Rotator(pitch=shots[0][2][0],yaw=shots[0][2][1],roll=shots[0][2][2]))
def tick(dt):
    elapsed=time.monotonic()-state['time']
    if elapsed>25 and not state['captured']:
        name=shots[state['index']][0]
        u.AutomationLibrary.take_high_res_screenshot(1920,1080,str(ROOT/'Evidence'/(name+'.png')))
        state['captured']=True
    if elapsed>32:
        state['index']+=1
        if state['index']>=len(shots):
            u.unregister_slate_post_tick_callback(handle)
            u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')
            return
        editor.set_level_viewport_camera_info(u.Vector(*shots[state['index']][1]),u.Rotator(pitch=shots[state['index']][2][0],yaw=shots[state['index']][2][1],roll=shots[state['index']][2][2]))
        state['time']=time.monotonic();state['captured']=False
handle=u.register_slate_post_tick_callback(tick)
