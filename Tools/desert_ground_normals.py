"""Ground-cover backfaces must use the engine's default tangent-space geometry normal."""
import unreal as u,ast,json
from pathlib import Path
ROOT=Path(u.Paths.project_dir()).resolve();ART=ROOT/'Art/DesertVisual';G=json.loads((ART/'manifest.json').read_text());BASE='/Game/RoadToF1/DesertVisual';E=u.EditorAssetLibrary;L=u.MaterialEditingLibrary;T=u.AssetToolsHelpers.get_asset_tools()
for n in ast.parse((ROOT/'Tools/desert_visual_import.py').read_text()).body:
 if isinstance(n,ast.FunctionDef):exec(compile(ast.Module(body=[n],type_ignores=[]),'visual_helpers','exec'))
master('Paint',False,True)
for name in ['grass','grassdark']:
 m=u.load_asset(BASE+'/Materials/MI_DV_'+name);assert m.get_editor_property('parent').get_name()=='M_DV_PaintGround'
u.log('GROUND_DEFAULT_TANGENT_NORMAL_SAVED')
