"""Report native MCP startup configuration without altering level or clients."""
import unreal as u,json
from pathlib import Path
u.EditorPythonScripting.set_keep_python_script_alive(True)
root=Path(u.Paths.project_dir()).resolve();out=root/'Evidence/UnrealMCP';out.mkdir(parents=True,exist_ok=True)
cls=u.load_class(None,'/Script/ModelContextProtocolEngine.ModelContextProtocolSettings');assert cls
settings=u.get_default_object(cls)
report={name:settings.get_editor_property(native) for name,native in [('auto_start_server','bAutoStartServer'),('server_port_number','ServerPortNumber'),('server_url_path','ServerUrlPath'),('enable_tool_search','bEnableToolSearch')]}
assert report['auto_start_server'] and report['server_port_number']==8000 and report['server_url_path']=='/mcp'
project=json.loads((root/'Road_To_F1_New.uproject').read_text())
report['plugins']={p['Name']:p['Enabled'] for p in project['Plugins'] if p['Name'] in ['ModelContextProtocol','AllToolsets']}
assert all(report['plugins'].values()) and len(report['plugins'])==2
(out/'editor_settings.json').write_text(json.dumps(report,indent=2))
u.log('UNREAL_MCP_CODEX_SETTINGS_VERIFIED '+json.dumps(report))
