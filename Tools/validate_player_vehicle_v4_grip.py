from pathlib import Path
p=Path(__file__).resolve().parent/'validate_player_vehicle_v4.py'
s=p.read_text().replace("R/'Evidence/PlayerVehicle_v4'","R/'Evidence/PlayerVehicle_v4/Hands'").replace('E.mkdir(exist_ok=True)','E.mkdir(parents=True,exist_ok=True)').replace('camera((180,0,230),(30,0,0))','camera((80,-90,85),(23,0,25))').replace('camera((160,-150,120),(50,0,0))','camera((80,-90,85),(23,0,25))').replace('camera((160,150,120),(50,0,0))','camera((80,90,85),(23,0,25))')
s=s.replace("grips=[wt.inverse_transform_location(sampler.get_socket_location('hand_'+side)) for side in ['l','r']]", "grips=[wt.inverse_transform_location(sampler.get_socket_location(bone+side)) for side in ['l','r'] for bone in ['hand_','thumb_03_','index_03_','middle_03_','ring_03_','pinky_03_']]")
s=s.replace('for i in range(2));state[', 'for i in range(len(grips)));state[')
s=s.replace("  assert mech and mech.get_editor_property('ready')", "  if (not mech or not mech.get_editor_property('ready')) and u.GameplayStatics.get_time_seconds(world)<1:return\n  assert mech and mech.get_editor_property('ready')")
exec(compile(s,str(p),'exec'))


