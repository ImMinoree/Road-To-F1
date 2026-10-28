from pathlib import Path
p=Path(__file__).resolve().parent/'validate_player_vehicle_v4.py';s=p.read_text().replace("R/'Evidence/PlayerVehicle_v4'","R/'Evidence/PlayerVehicle_v4/Hands/Shading'").replace('E.mkdir(exist_ok=True)','E.mkdir(parents=True,exist_ok=True)')
s=s.replace("  assert mech and mech.get_editor_property('ready')", "  if (not mech or not mech.get_editor_property('ready')) and u.GameplayStatics.get_time_seconds(world)<1:return\n  assert mech and mech.get_editor_property('ready')")
branch='''  pawn.set_kart_test_input(0,0,False);camera((80,-90,85),(23,0,25))
  if t>1.5:shot('01_lit')
  if t>2.3:u.SystemLibrary.execute_console_command(world,'r.ContactShadows 0')
  if t>3:shot('02_no_contact_shadow')
  if t>3.8:u.SystemLibrary.execute_console_command(world,'r.ShadowQuality 0')
  if t>4.5:shot('03_no_shadow')
  if t>5.3:u.SystemLibrary.execute_console_command(world,'viewmode unlit')
  if t>6:shot('04_unlit')
  if t>6.8:
   level.editor_request_end_play();u.unregister_slate_post_tick_callback(handle);u.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')
'''
s=s[:s.index("  if phase=='grid_center':")]+branch+s[s.index(' except Exception:'):]
exec(compile(s,str(p),'exec'))

