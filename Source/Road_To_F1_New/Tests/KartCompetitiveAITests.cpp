#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../TrackRacingAI.h"
#include "../KartTireDynamics.h"
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FCompetitivePlanTest,"RoadToF1.CompetitiveAI.PhysicalPlanAndPresets",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FCompetitivePlanTest::RunTest(const FString&){
 auto* Route=LoadObject<UTrackEdgeRoute>(nullptr,TEXT("/Game/RoadToF1/RacingAI/DA_DesertTrackEdges.DA_DesertTrackEdges"));if(!TestNotNull(TEXT("Existing boundary asset"),Route))return false;
 FKartAITrackPlan Plan;Plan.Build(Route,GetDefault<UKartTireDynamics>(),GetDefault<UTrackRacingAI>()->CornerAccelerationCmps2,GetDefault<UTrackRacingAI>()->ExitAccelerationCmps2);TestEqual(TEXT("Every segment planned"),Plan.Samples.Num(),Route->Center.Num());
 for(int32 I=0;I<Plan.Samples.Num();++I){const auto& A=Plan.Samples[I];const auto& B=Plan.Samples[(I+1)%Plan.Samples.Num()];if(!TestTrue(TEXT("Feasible backward braking envelope"),A.Speed*A.Speed<=B.Speed*B.Speed+2*FMath::Max(100.f,Plan.BrakeDeceleration+981.f*A.Grade)*FVector::Dist2D(A.Position,B.Position)+1))break;}
 float Last=0,Reaction=1;for(int32 I=0;I<5;++I){const auto P=UTrackRacingAI::Preset(EKartAIDifficulty(I));TestTrue(TEXT("Increasing bounded corner confidence"),P.LateralScale>Last&&P.LateralScale<=1.12f);TestTrue(TEXT("Reaction decreases with difficulty"),P.Reaction<Reaction);Last=P.LateralScale;Reaction=P.Reaction;}
 return true;
}
#endif
