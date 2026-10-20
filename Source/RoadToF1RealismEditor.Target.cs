using UnrealBuildTool;
public class RoadToF1RealismEditorTarget : TargetRules { public RoadToF1RealismEditorTarget(TargetInfo Target) : base(Target) { Type = TargetType.Editor; DefaultBuildSettings = BuildSettingsVersion.Latest; ExtraModuleNames.Add("RoadToF1Realism"); } }
