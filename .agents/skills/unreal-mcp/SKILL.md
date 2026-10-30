---
name: unreal-mcp
description: Use when changing, inspecting, or running a project in Unreal Editor through the connected Unreal MCP tools. Triggers include editing levels or actors, Blueprints, materials, Niagara, meshes, widgets, Control Rigs, Sequencer, gameplay systems, or running Unreal automation tests. Skip for conceptual Unreal questions that do not require project access.
---

# Unreal Editor through MCP

Use the connected Unreal Editor MCP tools for live project state. This skill adapts Epic Games' `unreal-mcp` workflow for Codex; it does not install or configure the Claude Code plugin. The tool interface available in this session uses the `mcp__unreal__` namespace.

## Discover and call tools

1. Call `mcp__unreal__list_toolsets` to find relevant toolsets. If the needed toolset is already known, call `mcp__unreal__describe_toolset` directly to inspect its current tool names and input schemas.
2. Dispatch the chosen operation with `mcp__unreal__call_tool`, passing the exact `toolset_name`, `tool_name`, and schema-matching `arguments` returned by discovery.
3. Read every result and verify explicit success before continuing. Do not guess tool names, property names, or enum values.
4. Treat the registered tool catalog as evidence of available tools, not proof that Unreal is currently responsive. Verify editor reachability with a harmless read-only operation before relying on live state.

## Protect project and editor state

- Inspect the active project, map, selection, and PIE status before editing. Preserve unrelated work and avoid conflicting calls against the same asset.
- Save or create a recoverable checkpoint before broad or multi-asset edits, then save the intended result and verify it afterward. MCP edits may not be undoable, especially across compilation.
- Serialize dependent mutations. Parallelize only independent read operations or operations documented as safe to overlap.
- If C++ or shader compilation is running, wait for it. Use the discovered Live Coding tool when appropriate and inspect compiler diagnostics before proceeding.
- Check Blueprint, material, widget, and asset creation results for explicit success; a tool response without an exception may still report failure.
- Check whether PIE is running before editor-only asset operations. Do not stop a user's PIE session or alter live state unless the task requires it.
- For destructive, irreversible, or wide-ranging changes, clarify scope and make a recovery point before proceeding.

## Project-specific workflow

Use this skill together with any relevant Unreal Agent Skills exposed by `AgentSkillToolset`. Discover those with `mcp__unreal__describe_toolset` for `ToolsetRegistry.AgentSkillToolset`, then use its current schemas to list and read applicable skills. Project-provided skill instructions take precedence for that project's conventions.

## Source

Adapted from Epic Games' [unreal-engine-skills-for-claude-code-plugin](https://github.com/EpicGames/unreal-engine-skills-for-claude-code-plugin), particularly its `skills/unreal-mcp/SKILL.md`. This Codex skill contains the live-editor workflow and safety guidance, not Claude-specific hooks or marketplace configuration.
