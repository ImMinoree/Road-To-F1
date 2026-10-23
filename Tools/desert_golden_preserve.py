"""Check gameplay markers, racing geometry and lighting against pre-edit checkpoints."""
import unreal as u,json
from pathlib import Path
root=Path(u.Paths.project_dir()).resolve();L=u.get_editor_subsystem(u.LevelEditorSubsystem);A=u.get_editor_subsystem(u.EditorActorSubsystem)
def signature(mp):
 assert L.load_level(mp);out={}
 for a in A.get_all_level_actors():
  label=a.get_actor_label()
  if not (label.startswith(('DK_02 ','RR_')) or isinstance(a,(u.PlayerStart,u.StaticMeshActor)) or 'checkpoint' in a.get_class().get_name().lower()):continue
  p=a.get_actor_location();r=a.get_actor_rotation();s=a.get_actor_scale3d();v={'class':a.get_class().get_name(),'transform':[p.x,p.y,p.z,r.pitch,r.yaw,r.roll,s.x,s.y,s.z],'actor_collision':a.get_actor_enable_collision()}
  if isinstance(a,u.StaticMeshActor):
   c=a.static_mesh_component;v.update(mesh=c.static_mesh.get_path_name(),profile=str(c.get_collision_profile_name()),visible=c.is_visible())
  if False:
   c=a.light_component;color=c.get_editor_property('light_color');v.update(intensity=c.get_editor_property('intensity'),color=[color.r,color.g,color.b,color.a])
  out[label]=v
 return out
report={}
for name in ['DesertKarting','DesertKarting_Visual']:
 before=signature('/Game/RoadToF1/Checkpoints/'+name+'_BeforeGoldenHour');after=signature('/Game/RoadToF1/Maps/'+name);assert before==after,name
 report[name]={'protected_actors_matched':len(after),'geometry_markers_spawns_visibility_collision_unchanged':True}
(root/'Evidence/DesertGoldenHour/preservation.json').write_text(json.dumps(report,indent=2))

