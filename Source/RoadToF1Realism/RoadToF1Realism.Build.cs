using UnrealBuildTool;
public class RoadToF1Realism : ModuleRules { public RoadToF1Realism(ReadOnlyTargetRules Target) : base(Target) { PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs; PublicDependencyModuleNames.AddRange(new string[]{"Core","CoreUObject","Engine","InputCore"}); } }
