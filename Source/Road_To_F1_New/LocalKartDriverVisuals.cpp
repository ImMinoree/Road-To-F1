#include "LocalKartDriverVisuals.h"
#include "Animation/AnimSequence.h"
#include "Camera/CameraComponent.h"
#include "Components/MeshComponent.h"
#include "Components/SceneComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/LocalPlayer.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/World.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/PlayerController.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "HAL/FileManager.h"
#include "HAL/PlatformMisc.h"
#include "UnrealClient.h"

ULocalKartDriverVisuals::ULocalKartDriverVisuals()
{
 PrimaryComponentTick.bCanEverTick=true;
 PrimaryComponentTick.TickGroup=TG_PostPhysics;
 SetIsReplicatedByDefault(false);
 const FString Folder=TEXT("/Game/RoadToF1/PlayerVisuals/FirstPerson/");
 ArmsAsset=TSoftObjectPtr<USkeletalMesh>(FSoftObjectPath(Folder+TEXT("SK_FP_KartArms.SK_FP_KartArms")));
 SteeringAsset=TSoftObjectPtr<UAnimSequence>(FSoftObjectPath(Folder+TEXT("A_FP_KartSteering.A_FP_KartSteering")));
 WheelAsset=TSoftObjectPtr<UStaticMesh>(FSoftObjectPath(Folder+TEXT("SM_FP_SteeringWheel.SM_FP_SteeringWheel")));
 // Source art eye anchor (0,0,95) cm, scaled uniformly. Both arms and wheel share this space.
 const FRotator VisualPitch(12,0,0);
 CockpitVisualTransform=FTransform(VisualPitch,VisualPitch.RotateVector(FVector(0,0,-80.75)),FVector(.85));
}

bool ULocalKartDriverVisuals::IsEligibleLocalHuman() const
{
 const APawn* Pawn=Cast<APawn>(GetOwner());
 const APlayerController* PC=Pawn?Cast<APlayerController>(Pawn->GetController()):nullptr;
 return GetWorld() && GetWorld()->GetNetMode()!=NM_DedicatedServer && Pawn &&
  Pawn->IsLocallyControlled() && PC && PC->IsLocalController() && PC->GetLocalPlayer()!=nullptr;
}

void ULocalKartDriverVisuals::BeginPlay()
{
 Super::BeginPlay();
 if (GetOwner())
 {
  TArray<UMeshComponent*> Meshes;GetOwner()->GetComponents(Meshes);
  for (UMeshComponent* Mesh:Meshes) if(Mesh->ComponentHasTag(ThirdPersonDriverTag)) { SetThirdPersonDriver(Mesh);break; }
 }
 RefreshVisibility();
}

bool ULocalKartDriverVisuals::CreateLocalVisuals(UCameraComponent* Camera)
{
 if(Arms && Wheel) return true;
 if(bLoadAttempted || !Camera || !IsEligibleLocalHuman()) return false;
 bLoadAttempted=true;
 USkeletalMesh* Mesh=ArmsAsset.LoadSynchronous();
 UAnimSequence* Sequence=SteeringAsset.LoadSynchronous();
 UStaticMesh* WheelMesh=WheelAsset.LoadSynchronous();
 if(!Mesh || !Sequence || !WheelMesh || Mesh->GetSkeleton()!=Sequence->GetSkeleton())
 {
  UE_LOG(LogTemp,Warning,TEXT("LocalKartDriverVisuals: missing/incompatible FP assets; retaining third-person visibility."));
  return false;
 }
 AActor* Owner=GetOwner();
 ActiveSteeringSequence=Sequence;
 VisualRoot=NewObject<USceneComponent>(Owner,TEXT("LocalCockpitVisualRoot"),RF_Transient);
 Owner->AddInstanceComponent(VisualRoot);VisualRoot->SetupAttachment(Camera);
 VisualRoot->SetRelativeTransform(CockpitVisualTransform);VisualRoot->RegisterComponent();
 Arms=NewObject<USkeletalMeshComponent>(Owner,TEXT("LocalOnlyKartArms"),RF_Transient);
 Owner->AddInstanceComponent(Arms);Arms->SetupAttachment(VisualRoot);
 Arms->SetSkeletalMeshAsset(Mesh);Arms->SetOnlyOwnerSee(true);Arms->SetCastShadow(false);
 Arms->SetVisibleInRayTracing(false);Arms->SetCollisionEnabled(ECollisionEnabled::NoCollision);
 Arms->SetGenerateOverlapEvents(false);Arms->SetCanEverAffectNavigation(false);Arms->SetSimulatePhysics(false);
 Arms->SetIsReplicated(false);Arms->bReceivesDecals=false;
 Arms->VisibilityBasedAnimTickOption=EVisibilityBasedAnimTickOption::OnlyTickPoseWhenRendered;
 Arms->SetAnimationMode(EAnimationMode::AnimationSingleNode);Arms->RegisterComponent();
 Arms->PrimaryComponentTick.TickGroup=TG_PostPhysics;
 Arms->AddTickPrerequisiteComponent(this);
 Arms->SetAnimation(Sequence);Arms->SetPlayRate(0);Arms->SetPosition(Sequence->GetPlayLength()*.5f,false);
 Wheel=NewObject<UStaticMeshComponent>(Owner,TEXT("LocalOnlyCockpitWheel"),RF_Transient);
 Owner->AddInstanceComponent(Wheel);Wheel->SetupAttachment(VisualRoot);
 Wheel->SetStaticMesh(WheelMesh);Wheel->SetRelativeLocation(FVector(62,0,70));
 Wheel->SetOnlyOwnerSee(true);Wheel->SetCastShadow(false);Wheel->SetVisibleInRayTracing(false);
 Wheel->SetCollisionEnabled(ECollisionEnabled::NoCollision);Wheel->SetGenerateOverlapEvents(false);
 Wheel->SetCanEverAffectNavigation(false);Wheel->SetIsReplicated(false);Wheel->RegisterComponent();
 return true;
}

void ULocalKartDriverVisuals::SetThirdPersonDriver(UMeshComponent* Mesh)
{
 RestoreThirdPersonVisibility();
 // A renderer on another actor could have a different ownership chain. Require an explicit same-pawn renderer.
 ThirdPersonDriver=Mesh && Mesh->GetOwner()==GetOwner()?Mesh:nullptr;
 bOriginalCaptured=ThirdPersonDriver!=nullptr;
 if(ThirdPersonDriver) bOriginalOwnerNoSee=ThirdPersonDriver->bOwnerNoSee;
 RefreshVisibility();
}

void ULocalKartDriverVisuals::RestoreThirdPersonVisibility()
{
 if(bOriginalCaptured && IsValid(ThirdPersonDriver)) ThirdPersonDriver->SetOwnerNoSee(bOriginalOwnerNoSee);
}

void ULocalKartDriverVisuals::RefreshVisibility()
{
 APawn* Pawn=Cast<APawn>(GetOwner());
 APlayerController* PC=Pawn?Cast<APlayerController>(Pawn->GetController()):nullptr;
 UCameraComponent* Camera=Pawn?Pawn->FindComponentByClass<UCameraComponent>():nullptr;
 const bool bWantsLocalView=bCockpitEnabled && IsEligibleLocalHuman() && Camera && Camera->IsActive() && PC->GetViewTarget()==Pawn;
 bActiveForLocalPlayer=bWantsLocalView && CreateLocalVisuals(Camera);
 if(Arms) { Arms->SetHiddenInGame(!bActiveForLocalPlayer);Arms->SetComponentTickEnabled(bActiveForLocalPlayer); }
 if(Wheel) Wheel->SetHiddenInGame(!bActiveForLocalPlayer);
 // Per-view owner filtering, NEVER globally hide the body: other split-screen views still see it.
 if(IsValid(ThirdPersonDriver) && bOriginalCaptured)
  ThirdPersonDriver->SetOwnerNoSee(bActiveForLocalPlayer?true:bOriginalOwnerNoSee);
}

void ULocalKartDriverVisuals::SetSteeringInput(float Input)
{
 SteeringInput=FMath::IsFinite(Input)?FMath::Clamp(Input,-1.f,1.f):0.f;
}

void ULocalKartDriverVisuals::SetCockpitEnabled(bool bEnabled)
{
 bCockpitEnabled=bEnabled;RefreshVisibility();
}

void ULocalKartDriverVisuals::TickComponent(float Dt,ELevelTick TickType,FActorComponentTickFunction* ThisTickFunction)
{
 Super::TickComponent(Dt,TickType,ThisTickFunction);RefreshVisibility();
 if(!bActiveForLocalPlayer) return;
#if !UE_BUILD_SHIPPING
 // Opt-in visual-only capture. Never writes steering input back to gameplay or moves the pawn.
 const bool bCapture=FParse::Param(FCommandLine::Get(),TEXT("KartFPCapture"));
 if(bCapture)
 {
  CaptureElapsed+=FApp::GetDeltaTime();
  SteeringInput=CaptureElapsed<12.f?0.f:(CaptureElapsed<20.f?-1.f:1.f);
 }
#endif
 const float Degrees=SteeringInput*FMath::Clamp(MaximumSteeringDegrees,1.f,25.f);
 if(UAnimSequence* Sequence=ActiveSteeringSequence)
  Arms->SetPosition(((Degrees/25.f+1.f)*.5f)*Sequence->GetPlayLength(),false);
 Wheel->SetRelativeRotation(FRotator(0,0,Degrees));
#if !UE_BUILD_SHIPPING
 if(bCapture)
 {
  const float Times[]={10.f,18.f,26.f};const TCHAR* Names[]={TEXT("ue_center.png"),TEXT("ue_left.png"),TEXT("ue_right.png")};
  if(CaptureStage<3 && CaptureElapsed>Times[CaptureStage])
  {
   const FString Directory=FPaths::ProjectDir()/TEXT("Evidence/FirstPerson");IFileManager::Get().MakeDirectory(*Directory,true);
   FScreenshotRequest::RequestScreenshot(Directory/Names[CaptureStage],false,false);++CaptureStage;
  }
  if(CaptureElapsed>30.f)FPlatformMisc::RequestExit(false);
 }
#endif
}

void ULocalKartDriverVisuals::EndPlay(const EEndPlayReason::Type Reason)
{
 RestoreThirdPersonVisibility();
 if(Arms) Arms->DestroyComponent();if(Wheel) Wheel->DestroyComponent();if(VisualRoot) VisualRoot->DestroyComponent();
 Super::EndPlay(Reason);
}
