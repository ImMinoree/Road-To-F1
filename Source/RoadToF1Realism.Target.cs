using UnrealBuildTool;
public class RoadToF1RealismTarget : TargetRules { public RoadToF1RealismTarget(TargetInfo Target) : base(Target) { Type = TargetType.Game; DefaultBuildSettings = BuildSettingsVersion.Latest; ExtraModuleNames.Add("RoadToF1Realism"); } }
