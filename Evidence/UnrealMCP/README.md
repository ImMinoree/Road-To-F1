# Unreal MCP for Codex only

Enabled Epic's installed `ModelContextProtocol` (Unreal MCP) and `AllToolsets` plugins for the Editor target in Road_To_F1_New.uproject. Project defaults in `Config/DefaultEditorPerProjectUserSettings.ini` enable automatic startup at `http://127.0.0.1:8000/mcp`, with tool search enabled. `editor_settings.json` verifies the loaded native settings. No Claude Code config was generated or edited.

Codex registration was made using its bundled executable: `codex mcp add unreal --url http://127.0.0.1:8000/mcp`. It is enabled in the user's global `C:/Users/GBURG-4/.codex/config.toml`; other Codex configuration is preserved. Reload MCP servers or restart Codex to load the new tool definitions into an existing chat. Unreal must remain open for the endpoint to be available.

Verified over the actual MCP HTTP transport: initialization negotiated protocol 2025-11-25, tools/list advertised list_toolsets / describe_toolset / call_tool, list_toolsets returned 52 discoverable toolsets, and describe_toolset returned the native EditorApp schema. Two actual read-only call_tool requests succeeded: IsPIERunning and GetCameraTransform. The camera and active Play state were queried only; no actor, asset, input or Play state was changed by these requests. Probe JSON files contain the responses. The owning listener was verified as process 26788 running this project's uproject. At the final listener check that Editor session had closed; the endpoint follows the Editor lifetime and returns when this project reopens.

The 3 native tools are discovery/dispatch gateways, not a limit of 3 available operations. Toolsets cover actors, assets, materials, meshes, Blueprints, physics, animation, editor UI and other systems. All Toolsets is experimental; availability does not certify every tool against this game's assets. GameFeatures reports a missing optional GameFeatureData asset-manager scan rule; existing game asset-manager settings were left untouched.

The first settings probe used unbound snake-case property names and was corrected to native C++ names. Duplicate Editor startups encountered port contention; the working endpoint was verified against the project and the duplicate verification Editor was closed. Only one session can own port 8000 at a time.

Recheck with `Tools/check_unreal_mcp.py`; e.g. `call_tool '{"toolset_name":"EditorToolset.EditorAppToolset","tool_name":"IsPIERunning","arguments":{}}'`. The script uses standard Python HTTP/JSON and requires no extra packages.

Rollback: `codex mcp remove unreal`, disable the two newly added project plugin entries, and remove the MCP settings section from the project defaults. No gameplay, vehicle physics, track map or Claude configuration was modified. No commit or push was performed for this setup.
