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
 const FString Folder=TEXT("/Game/RoadToF1/PlayerVisuals/CockpitReferenceV2/");
 ArmsAsset=TSoftObjectPtr<USkeletalMesh>(FSoftObjectPath(Folder+TEXT("SK_CV2_DriverPOV.SK_CV2_DriverPOV")));
 SteeringAsset=TSoftObjectPtr<UAnimSequence>(FSoftObjectPath(Folder+TEXT("A_CV2_Steering.A_CV2_Steering")));
 WheelAsset=TSoftObjectPtr<UStaticMesh>(FSoftObjectPath(Folder+TEXT("SM_CV2_SteeringWheel.SM_CV2_SteeringWheel")));
 ChassisAsset=TSoftObjectPtr<UStaticMesh>(FSoftObjectPath(Folder+TEXT("SM_CV2_PlayerChassis.SM_CV2_PlayerChassis")));
 // Full-size source kart: ground at pawn Z-31. The local eye is configured separately below.
 // Arms, wheel, seat and chassis share one measured source coordinate system.
 CockpitVisualTransform=FTransform(FRotator::ZeroRotator,FVector(0,0,-31));
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
 if(Arms && Wheel && Chassis) return true;
 if(bLoadAttempted || !Camera || !IsEligibleLocalHuman()) return false;
 bLoadAttempted=true;
 bUsingLegacy=!bReferenceCockpit || FParse::Param(FCommandLine::Get(),TEXT("CockpitBefore"));
 if(bUsingLegacy)
 {
  const FString Legacy=TEXT("/Game/RoadToF1/PlayerVisuals/FirstPerson/");
  ArmsAsset=TSoftObjectPtr<USkeletalMesh>(FSoftObjectPath(Legacy+TEXT("SK_FP_KartArms.SK_FP_KartArms")));
  SteeringAsset=TSoftObjectPtr<UAnimSequence>(FSoftObjectPath(Legacy+TEXT("A_FP_KartSteering.A_FP_KartSteering")));
  WheelAsset=TSoftObjectPtr<UStaticMesh>(FSoftObjectPath(Legacy+TEXT("SM_FP_SteeringWheel.SM_FP_SteeringWheel")));
  ChassisAsset=TSoftObjectPtr<UStaticMesh>(FSoftObjectPath(Legacy+TEXT("SM_PlayerKartChassis.SM_PlayerKartChassis")));
 }
 USkeletalMesh* Mesh=ArmsAsset.LoadSynchronous();
 UAnimSequence* Sequence=SteeringAsset.LoadSynchronous();
 UStaticMesh* WheelMesh=WheelAsset.LoadSynchronous();
 UStaticMesh* ChassisMesh=ChassisAsset.LoadSynchronous();
 if(!Mesh || !Sequence || !WheelMesh || !ChassisMesh || Mesh->GetSkeleton()!=Sequence->GetSkeleton())
 {
  UE_LOG(LogTemp,Warning,TEXT("LocalKartDriverVisuals: missing/incompatible FP assets; retaining third-person visibility."));
  return false;
 }
 AActor* Owner=GetOwner();
 CockpitCamera=Camera;OriginalCameraTransform=Camera->GetRelativeTransform();OriginalCameraFOV=Camera->FieldOfView;
 ActiveSteeringSequence=Sequence;
 VisualRoot=NewObject<USceneComponent>(Owner,TEXT("LocalCockpitVisualRoot"),RF_Transient);
 Owner->AddInstanceComponent(VisualRoot);VisualRoot->SetupAttachment(Owner->GetRootComponent());
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
 Wheel->SetStaticMesh(WheelMesh);Wheel->SetRelativeLocation(FVector(62,0,bUsingLegacy?70:67));
 Wheel->SetOnlyOwnerSee(true);Wheel->SetCastShadow(false);Wheel->SetVisibleInRayTracing(false);
 Wheel->SetCollisionEnabled(ECollisionEnabled::NoCollision);Wheel->SetGenerateOverlapEvents(false);
 Wheel->SetCanEverAffectNavigation(false);Wheel->SetIsReplicated(false);Wheel->RegisterComponent();
 Chassis=NewObject<UStaticMeshComponent>(Owner,TEXT("LocalOnlyKartChassis"),RF_Transient);
 Owner->AddInstanceComponent(Chassis);Chassis->SetupAttachment(VisualRoot);
 Chassis->SetStaticMesh(ChassisMesh);Chassis->SetOnlyOwnerSee(true);
 Chassis->SetCollisionEnabled(ECollisionEnabled::NoCollision);Chassis->SetGenerateOverlapEvents(false);
 Chassis->SetCanEverAffectNavigation(false);Chassis->SetIsReplicated(false);
 Chassis->SetCastShadow(false);Chassis->SetVisibleInRayTracing(false);Chassis->RegisterComponent();
 return true;
}

void ULocalKartDriverVisuals::ConfigureCockpitCamera(bool bActive)
{
 if(!CockpitCamera || bUsingLegacy)return;
 if(bActive && !bCameraAdjusted)
 {
  // Eye is 1.05m above kart ground; cosmetic view only, collision root remains untouched.
  CockpitCamera->SetRelativeTransform(FTransform(FRotator(-10,0,0),FVector(5,0,74)));
  CockpitCamera->SetFieldOfView(105.f);bCameraAdjusted=true;
 }
 else if(!bActive && bCameraAdjusted)
 {
  CockpitCamera->SetRelativeTransform(OriginalCameraTransform);CockpitCamera->SetFieldOfView(OriginalCameraFOV);bCameraAdjusted=false;
 }
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
 ConfigureCockpitCamera(bActiveForLocalPlayer);
 if(Arms) { Arms->SetHiddenInGame(!bActiveForLocalPlayer);Arms->SetComponentTickEnabled(bActiveForLocalPlayer); }
 if(Wheel) Wheel->SetHiddenInGame(!bActiveForLocalPlayer);
 if(Chassis) Chassis->SetHiddenInGame(!bActiveForLocalPlayer);
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
 const bool bReferenceCapture=FParse::Param(FCommandLine::Get(),TEXT("CockpitReferenceCapture"));
 if(bCapture)
 {
  CaptureElapsed+=FApp::GetDeltaTime();
  SteeringInput=CaptureElapsed<12.f?0.f:(CaptureElapsed<20.f?-1.f:1.f);
 }
 if(bReferenceCapture)
 {
  CaptureElapsed+=FApp::GetDeltaTime();
  const int32 Pose=FMath::Clamp(int32((CaptureElapsed-6.f)/6.f),0,4);
  const float Inputs[]={0.f,-1.f,1.f,-1.f,1.f};SteeringInput=Inputs[Pose];
  // Diagnostic camera rig at measured road samples. The pawn, race and physics are not moved.
  const bool Corner=Pose>=3;
  const FTransform RoadPose(FRotator(0,Corner?-47.06099f:-2.05271f,0),Corner?FVector(9034.8835,-1290.1299,31):FVector(-503.9471,21.3882,31));
  VisualRoot->SetWorldTransform(CockpitVisualTransform*RoadPose);
  const FTransform Eye=bUsingLegacy?OriginalCameraTransform:FTransform(FRotator(-10,0,0),FVector(5,0,74));
  CockpitCamera->SetWorldTransform(Eye*RoadPose);
 }
#endif
 const float Degrees=SteeringInput*FMath::Clamp(MaximumSteeringDegrees,1.f,25.f);
 if(UAnimSequence* Sequence=ActiveSteeringSequence)
  Arms->SetPosition(((Degrees/25.f+1.f)*.5f)*Sequence->GetPlayLength(),false);
 const FQuat Tilt(FVector::YAxisVector,FMath::DegreesToRadians(bUsingLegacy?0.f:18.f));
 Wheel->SetRelativeRotation(Tilt*FRotator(0,0,Degrees).Quaternion()*Tilt.Inverse());
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
 if(bReferenceCapture)
 {
  const float Times[]={10.f,16.f,22.f,28.f,34.f};
  const TCHAR* Names[]={TEXT("straight_center"),TEXT("straight_left"),TEXT("straight_right"),TEXT("corner_left"),TEXT("corner_right")};
  if(CaptureStage<5 && CaptureElapsed>Times[CaptureStage])
  {
   const FString Dir=FPaths::ProjectDir()/TEXT("Evidence/Cockpit_Reference_v2")/(bUsingLegacy?TEXT("Before"):TEXT("After"));
   IFileManager::Get().MakeDirectory(*Dir,true);FScreenshotRequest::RequestScreenshot(Dir/(FString(Names[CaptureStage])+TEXT(".png")),false,false);++CaptureStage;
  }
  if(CaptureElapsed>37.f)FPlatformMisc::RequestExit(false);
 }
#endif
}

void ULocalKartDriverVisuals::EndPlay(const EEndPlayReason::Type Reason)
{
 RestoreThirdPersonVisibility();
 ConfigureCockpitCamera(false);
 if(Arms) Arms->DestroyComponent();if(Wheel) Wheel->DestroyComponent();if(Chassis) Chassis->DestroyComponent();if(VisualRoot) VisualRoot->DestroyComponent();
 Super::EndPlay(Reason);
}
