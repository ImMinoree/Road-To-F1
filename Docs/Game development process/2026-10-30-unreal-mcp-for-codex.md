# Game development process - I connected Unreal MCP to Codex

**Date:** October 30, 2026

**Developer:** Me, the human project owner

**Assistance:** Codex assisted with configuration, protocol testing, and this report.

## What I set up

I enabled Epic's installed **Unreal MCP** and **All Toolsets** plugins for this project's Editor target. I enabled automatic server startup at `http://127.0.0.1:8000/mcp` and registered the endpoint in Codex's local configuration. I limited the client setup to Codex and left Claude Code configuration untouched.

I kept tool search enabled, so three discovery/dispatch tools provide access to the available toolsets on demand rather than registering every operation individually.

## How I checked it

The native settings check confirmed the plugin flags, port, endpoint and auto-start configuration. An actual MCP handshake negotiated protocol version 2025-11-25. Discovery returned **52 toolsets**, and read-only MCP calls successfully queried Play state and the editor camera transform. These calls did not change actors, assets, controls or Play state.

The [setup record](../../Evidence/UnrealMCP/README.md), [loaded settings](../../Evidence/UnrealMCP/editor_settings.json), [Play-state response](../../Evidence/UnrealMCP/probe_call_tool_IsPIERunning.json) and [camera response](../../Evidence/UnrealMCP/probe_call_tool_GetCameraTransform.json) preserve the verification.

## Files and remaining limitations

Project settings are in [Road_To_F1_New.uproject](../../Road_To_F1_New.uproject) and [DefaultEditorPerProjectUserSettings.ini](../../Config/DefaultEditorPerProjectUserSettings.ini). The Codex registration is local to my user configuration and is not a repository credential or a portable connection to a remote computer.

Unreal must be open for the local endpoint to respond, and only one Editor session can own port 8000. Existing Codex chats can need an MCP reload or restart after registration. All Toolsets is experimental; discovery does not certify every operation against this game's data. The initial GameFeatures scan-rule warning is documented in the setup record rather than hidden.
