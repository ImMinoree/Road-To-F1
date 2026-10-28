#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../TrackRacingAI.h"
#include "../ProofPawn.h"
#include "Engine/SkeletalMesh.h"
#include "Animation/AnimSequence.h"
#include "UObject/Package.h"
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTrackEdgesTest,"RoadToF1.RacingAI.EdgesAndPresentation",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FTrackEdgesTest::RunTest(const FString&){
 auto* Route=LoadObject<UTrackEdgeRoute>(nullptr,TEXT("/Game/RoadToF1/RacingAI/DA_DesertTrackEdges.DA_DesertTrackEdges"));
 TestNotNull(TEXT("Measured actual asphalt boundaries exist"),Route);if(!Route)return false;
 TestTrue(TEXT("All paired edges and center samples form a usable corridor"),Route->IsUsable());
 TestEqual(TEXT("Complete source circuit sample count"),Route->Center.Num(),748);
 for(int32 I=0;I<Route->Center.Num();++I){
  for(float Lane:{-10000.f,0.f,10000.f}){
   const FVector P=Route->LanePoint(I,Lane),N=FVector::CrossProduct(FVector::UpVector,Route->Tangent(I));
   TestTrue(TEXT("Lane remains inset from both actual polygon boundaries"),FVector::DotProduct(Route->Left[I]-P,N)>=139.9&&FVector::DotProduct(P-Route->Right[I],N)>=139.9);
  }
 }
 auto* Bad=DuplicateObject<UTrackEdgeRoute>(Route,GetTransientPackage());Swap(Bad->Left,Bad->Right);TestFalse(TEXT("Swapped or misaligned boundaries fail closed"),Bad->IsUsable());
 auto* Driver=LoadObject<USkeletalMesh>(nullptr,TEXT("/Game/RoadToF1/RacingAI/SK_AI_KartDriver.SK_AI_KartDriver"));
 auto* Anim=LoadObject<UAnimSequence>(nullptr,TEXT("/Game/RoadToF1/PlayerVisuals/FirstPerson/A_FP_KartSteering.A_FP_KartSteering"));
 TestNotNull(TEXT("Existing full V5 driver is imported"),Driver);TestNotNull(TEXT("Original baked steering clip exists"),Anim);
 if(Driver&&Anim)TestTrue(TEXT("Full-body opponents reuse the existing steering skeleton"),Driver->GetSkeleton()==Anim->GetSkeleton());
 const auto* Pawn=GetDefault<AProofPawn>();TestTrue(TEXT("Shared human/AI turning radius permits tight circuit bends"),1.f/Pawn->GetMaximumSteeringCurvature()<400.f);
 return true;
}
#endif
