#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../LocalKartDriverVisuals.h"
#include "../ProofPawn.h"
#include "Animation/AnimSingleNodeInstance.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/Engine.h"
#include "Engine/LocalPlayer.h"
#include "Engine/World.h"
#include "GameFramework/PlayerController.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FKartLocalVisualOwnershipTest,
 "RoadToF1.PlayerVisuals.OwnershipAndSteering",
 EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FKartLocalVisualOwnershipTest::RunTest(const FString&)
{
 const UWorld::InitializationValues Init=UWorld::InitializationValues().AllowAudioPlayback(false).CreatePhysicsScene(true)
  .CreateNavigation(false).CreateAISystem(false).ShouldSimulatePhysics(false).SetTransactional(false);
 UWorld* World=UWorld::CreateWorld(EWorldType::Game,false,FName(TEXT("LocalVisualOwnershipTest")),nullptr,true,ERHIFeatureLevel::Num,&Init);
 FWorldContext& Context=GEngine->CreateNewWorldContext(EWorldType::Game);Context.SetCurrentWorld(World);
 World->InitializeActorsForPlay(FURL());
 auto SpawnPawn=[&]() { FActorSpawnParameters Params;Params.SpawnCollisionHandlingOverride=ESpawnActorCollisionHandlingMethod::AlwaysSpawn;auto* P=World->SpawnActor<AProofPawn>(AProofPawn::StaticClass(),FTransform::Identity,Params);P->AutoPossessPlayer=EAutoReceiveInput::Disabled;return P; };
 auto LocalController=[&]() {auto* PC=World->SpawnActor<APlayerController>();PC->Player=NewObject<ULocalPlayer>(GEngine);return PC;};
 AProofPawn* First=SpawnPawn();AProofPawn* Second=SpawnPawn();AProofPawn* Remote=SpawnPawn();AProofPawn* NPC=SpawnPawn();
 APlayerController* PC1=LocalController();APlayerController* PC2=LocalController();auto* RemotePC=World->SpawnActor<APlayerController>();
 PC1->Possess(First);PC1->SetViewTarget(First);PC2->Possess(Second);PC2->SetViewTarget(Second);RemotePC->Possess(Remote);
 auto* V1=First->FindComponentByClass<ULocalKartDriverVisuals>();auto* V2=Second->FindComponentByClass<ULocalKartDriverVisuals>();
 auto* VR=Remote->FindComponentByClass<ULocalKartDriverVisuals>();auto* VN=NPC->FindComponentByClass<ULocalKartDriverVisuals>();
 TestTrue(TEXT("First local human eligible"),V1->IsEligibleLocalHuman());
 TestTrue(TEXT("Second split-screen local human eligible"),V2->IsEligibleLocalHuman());
 TestFalse(TEXT("Remote controller without ULocalPlayer is excluded"),VR->IsEligibleLocalHuman());
 TestFalse(TEXT("NPC/unpossessed pawn is excluded"),VN->IsEligibleLocalHuman());
 V1->SetCockpitEnabled(true);V2->SetCockpitEnabled(true);VR->SetCockpitEnabled(true);VN->SetCockpitEnabled(true);
 TestTrue(TEXT("First cockpit active with imported assets"),V1->IsFirstPersonActive());
 TestTrue(TEXT("Second cockpit active with imported assets"),V2->IsFirstPersonActive());
 TestNull(TEXT("Remote pawn does not create first-person mesh"),VR->GetFirstPersonArms());
 TestNull(TEXT("NPC does not create first-person mesh"),VN->GetFirstPersonArms());
 if(USkeletalMeshComponent* Arms=V1->GetFirstPersonArms())
 {
  TestTrue(TEXT("Per-view OnlyOwnerSee is set"),Arms->bOnlyOwnerSee);
  TestTrue(TEXT("Owner chain identifies the correct local controller"),Arms->GetOwner()->IsOwnedBy(PC1));
  TestFalse(TEXT("The other local view is not an owner"),Arms->GetOwner()->IsOwnedBy(PC2));
  TestEqual(TEXT("Visual has no collision"),Arms->GetCollisionEnabled(),ECollisionEnabled::NoCollision);
  TestFalse(TEXT("Visual mesh is not replicated"),Arms->GetIsReplicated());
  TestFalse(TEXT("Visual component is not replicated"),V1->GetIsReplicated());
  // Compare imported/compressed bone samples to Blender source coordinates in cm (Y is mirrored).
  const FVector LeftSamples[] = {{48,-19.878164,61.282319},{48,-21.329737,65.977365},{48,-21.699965,70.499963},{48,-21.031319,75.368589},{48,-19.455564,79.623955}};
  const FVector RightSamples[] = {{48,19.455531,79.623979},{48,21.121818,75.000745},{48,21.699958,70.499986},{48,21.256277,65.605766},{48,19.878161,61.282349}};
  for(int32 Sample=0;Sample<5;++Sample)
  {
   V1->SetSteeringInput(-1.f+Sample*.5f);V1->TickComponent(0.f,LEVELTICK_All,nullptr);
   Arms->TickAnimation(0.f,false);Arms->RefreshBoneTransforms();
   const FVector L=Arms->GetSocketTransform(TEXT("hand_l"),RTS_Component).GetLocation();
   const FVector R=Arms->GetSocketTransform(TEXT("hand_r"),RTS_Component).GetLocation();
   AddInfo(FString::Printf(TEXT("Steering sample %d: L=%s R=%s"),Sample,*L.ToString(),*R.ToString()));
   TestTrue(TEXT("Imported left grip follows baked source within 5 mm"),L.Equals(LeftSamples[Sample],.5f));
   TestTrue(TEXT("Imported right grip follows baked source within 5 mm"),R.Equals(RightSamples[Sample],.5f));
  }
  const FVector PawnBefore=First->GetActorLocation();
  for(float Input:{-1.f,0.f,1.f})
  {
   V1->SetSteeringInput(Input);V1->TickComponent(0.f,LEVELTICK_All,nullptr);
   TestTrue(TEXT("Wheel follows the visual steering input"),FMath::IsNearlyEqual(V1->GetFirstPersonWheel()->GetRelativeRotation().Roll,Input*25,.01f));
   auto* Anim=Arms->GetSingleNodeInstance();
   TestNotNull(TEXT("Independent baked steering clip is present"),Anim);
   if(Anim) TestTrue(TEXT("Animation position follows the same steering sample"),FMath::IsNearlyEqual(Anim->GetCurrentTime(),(Input+1)*.5f*Anim->GetLength(),.001f));
  }
  TestTrue(TEXT("Changing visuals did not move the pawn"),PawnBefore.Equals(First->GetActorLocation()));
  auto* Third=NewObject<USkeletalMeshComponent>(First);First->AddInstanceComponent(Third);Third->RegisterComponent();
  V1->SetThirdPersonDriver(Third);TestTrue(TEXT("Third-person renderer hidden only from its owner"),Third->bOwnerNoSee);
  TestFalse(TEXT("Third-person renderer was not globally hidden"),Third->bHiddenInGame);
  V1->SetCockpitEnabled(false);TestFalse(TEXT("Third-person owner visibility restored in third-person mode"),Third->bOwnerNoSee);
  TestTrue(TEXT("FP mesh hidden when cockpit disabled"),Arms->bHiddenInGame);
  V1->SetCockpitEnabled(true);PC1->UnPossess();V1->TickComponent(0.f,LEVELTICK_All,nullptr);
  TestFalse(TEXT("Unpossession deactivates local visual"),V1->IsFirstPersonActive());
  TestTrue(TEXT("Unpossessed FP mesh is hidden"),Arms->bHiddenInGame);
  TestFalse(TEXT("Unpossession restores third-person visibility"),Third->bOwnerNoSee);
 }
 GEngine->DestroyWorldContext(World);World->DestroyWorld(false);
 return true;
}
#endif
