#include "LocalKartDriverVisuals.h"
#include "ProofPawn.h"
#include "KartTireDynamics.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Animation/AnimSequence.h"
#include "Camera/CameraComponent.h"
#include "Components/MeshComponent.h"
#include "Components/SceneComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
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
 SpeedBlurAsset=TSoftObjectPtr<UMaterialInterface>(FSoftObjectPath(TEXT("/Game/RoadToF1/SpeedEffects/M_KartPeripheralSpeed.M_KartPeripheralSpeed")));
 const FString Folder=TEXT("/Game/RoadToF1/PlayerVisuals/CockpitLayoutV5/");
 ArmsAsset=TSoftObjectPtr<USkeletalMesh>(FSoftObjectPath(Folder+TEXT("SK_CL5_DriverPOV.SK_CL5_DriverPOV")));
 SteeringAsset=TSoftObjectPtr<UAnimSequence>(FSoftObjectPath(Folder+TEXT("A_CL5_Steering.A_CL5_Steering")));
 WheelAsset=TSoftObjectPtr<UStaticMesh>(FSoftObjectPath(Folder+TEXT("SM_CL5_SteeringWheel.SM_CL5_SteeringWheel")));
 ChassisAsset=TSoftObjectPtr<UStaticMesh>(FSoftObjectPath(Folder+TEXT("SM_CL5_PlayerChassis.SM_CL5_PlayerChassis")));
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
 if(UMaterialInterface* Material=SpeedBlurAsset.LoadSynchronous())
 {
  SpeedBlur=UMaterialInstanceDynamic::Create(Material,this);
  SpeedBlur->SetScalarParameterValue(TEXT("SpeedStrength"),0.f);
  Camera->AddOrUpdateBlendable(SpeedBlur,1.f);
 }
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
 Wheel->SetStaticMesh(WheelMesh);Wheel->SetRelativeLocation(FVector(62,0,bUsingLegacy?70:52));
 Wheel->SetOnlyOwnerSee(true);Wheel->SetCastShadow(false);Wheel->SetVisibleInRayTracing(false);
 Wheel->SetCollisionEnabled(ECollisionEnabled::NoCollision);Wheel->SetGenerateOverlapEvents(false);
 Wheel->SetCanEverAffectNavigation(false);Wheel->SetIsReplicated(false);Wheel->RegisterComponent();
 Chassis=NewObject<UStaticMeshComponent>(Owner,TEXT("LocalOnlyKartChassis"),RF_Transient);
 Owner->AddInstanceComponent(Chassis);Chassis->SetupAttachment(VisualRoot);
 Chassis->SetStaticMesh(ChassisMesh);Chassis->SetOnlyOwnerSee(true);
 Chassis->SetCollisionEnabled(ECollisionEnabled::NoCollision);Chassis->SetGenerateOverlapEvents(false);
 Chassis->SetCanEverAffectNavigation(false);Chassis->SetIsReplicated(false);
 Chassis->SetCastShadow(false);Chassis->SetVisibleInRayTracing(false);Chassis->RegisterComponent();
 if(!bUsingLegacy)
 {
  // Real readouts attached to the rotating logger face. Cosmetic, owner-only and collision-free.
  auto AddReadout=[&](const TCHAR* Name,const FVector& SourcePoint,float Size)
  {
   auto* Text=NewObject<UTextRenderComponent>(Owner,Name,RF_Transient);Owner->AddInstanceComponent(Text);Text->SetupAttachment(Wheel);
   const FQuat Tilt(FVector::YAxisVector,FMath::DegreesToRadians(18.f));
   Text->SetRelativeLocation(Tilt.RotateVector(SourcePoint));
   Text->SetRelativeRotation(Tilt*FQuat(FVector::ZAxisVector,PI));
   Text->SetHorizontalAlignment(EHTA_Center);Text->SetVerticalAlignment(EVRTA_TextCenter);
   Text->SetWorldSize(Size);Text->SetTextRenderColor(FColor(12,24,14));Text->SetOnlyOwnerSee(true);Text->SetCastShadow(false);
   Text->SetVisibleInRayTracing(false);Text->SetCollisionEnabled(ECollisionEnabled::NoCollision);Text->SetGenerateOverlapEvents(false);
   Text->SetCanEverAffectNavigation(false);Text->SetIsReplicated(false);Text->RegisterComponent();return Text;
  };
  DashboardSpeed=AddReadout(TEXT("LocalLoggerSpeed"),FVector(-3.73,1.0,10.0),2.1f);
  DashboardTime=AddReadout(TEXT("LocalLoggerTime"),FVector(-3.73,1.0,7.2),1.15f);
 }
 return true;
}

void ULocalKartDriverVisuals::ConfigureCockpitCamera(bool bActive)
{
 if(!CockpitCamera || bUsingLegacy)return;
 if(bActive && !bCameraAdjusted)
 {
  // Eye remains above the shoulders; look down into the cockpit without scaling the kart or wheel.
  CockpitCamera->SetRelativeTransform(FTransform(FRotator(-10,0,0),FVector(5,0,44)));
  CockpitCamera->SetFieldOfView(95.f);bCameraAdjusted=true;
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
 if(DashboardSpeed)DashboardSpeed->SetHiddenInGame(!bActiveForLocalPlayer);
 if(DashboardTime)DashboardTime->SetHiddenInGame(!bActiveForLocalPlayer);
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
 RestoreSpeedCamera();
 bCockpitEnabled=bEnabled;RefreshVisibility();
}

void ULocalKartDriverVisuals::RestoreSpeedCamera()
{
 if(CockpitCamera && bSpeedCameraApplied)
 {
  CockpitCamera->SetRelativeTransform(SpeedBaseTransform);
  CockpitCamera->SetFieldOfView(SpeedBaseFOV);
 }
 bSpeedCameraApplied=false;
 if(SpeedBlur)SpeedBlur->SetScalarParameterValue(TEXT("SpeedStrength"),0.f);
}

void ULocalKartDriverVisuals::UpdateSpeedCamera(float Dt)
{
 const AProofPawn* Pawn=Cast<AProofPawn>(GetOwner());
 bool bEnabled=bSpeedEffectsEnabled && bActiveForLocalPlayer && Pawn && CockpitCamera;
#if !UE_BUILD_SHIPPING
 bEnabled=bEnabled && !FParse::Param(FCommandLine::Get(),TEXT("NoSpeedEffects")) &&
  !FParse::Param(FCommandLine::Get(),TEXT("KartFPCapture")) &&
  !FParse::Param(FCommandLine::Get(),TEXT("CockpitReferenceCapture")) &&
  !FParse::Param(FCommandLine::Get(),TEXT("CockpitTargetCapture")) &&
  !FParse::Param(FCommandLine::Get(),TEXT("WheelVisibilityCapture"));
#endif
 if(!bEnabled){SpeedBlend=0;return;}
 // Begin above 12.6 km/h; reach full effect at the existing drag-limited 48.4 km/h.
 float Target=FMath::Clamp((Pawn->GetDrivingSpeed()-350.f)/(430.f/.32f-350.f),0.f,1.f);
 Target=Target*Target*(3.f-2.f*Target);
 SpeedBlend=FMath::Lerp(SpeedBlend,Target,1.f-FMath::Exp(-3.f*FMath::Clamp(Dt,0.f,.1f)));
 // No lingering vibration/blur while staging or stopped, including a reset from full speed.
 if(Pawn->GetDrivingSpeed()<=1.f)SpeedBlend=0;
 SpeedBaseTransform=CockpitCamera->GetRelativeTransform();SpeedBaseFOV=CockpitCamera->FieldOfView;
 SpeedPhase+=FMath::Clamp(Dt,0.f,.1f);
 const float Intensity=SpeedBlend*SpeedBlend;
 float PhysicalBuffeting=0;
 if(Pawn->bUseTireDynamics)if(const auto* Dynamics=Pawn->GetTireDynamics()){
  const auto& Slip=Dynamics->Telemetry;
  PhysicalBuffeting=FMath::Clamp(FMath::Abs(Slip.LateralAccelerationG)*.25f+FMath::Max(0.f,FMath::Abs(Slip.RearSlipDegrees)-3.f)/15.f+
   FMath::Abs(Dynamics->VerticalAccelerationG)*.08f+Dynamics->LastContactImpulseNs/1000.f,0.f,1.f);
 }
 const float V=FMath::Clamp(Intensity*.35f+PhysicalBuffeting*.65f,0.f,1.f)*FMath::Clamp(SpeedVibrationScale,0.f,1.f);
 const double P=SpeedPhase*2*PI;
 const FRotator Rotation(.025f*V*FMath::Sin(P*14),.018f*V*FMath::Sin(P*19),.035f*V*FMath::Sin(P*11));
 FTransform View=SpeedBaseTransform;
 View.SetRotation(SpeedBaseTransform.GetRotation()*Rotation.Quaternion());
 View.AddToTranslation(SpeedBaseTransform.TransformVectorNoScale(FVector(0,.02f*V*FMath::Sin(P*13),.025f*V*FMath::Sin(P*17))));
 CockpitCamera->SetRelativeTransform(View);
 // Cap the cosmetic boost while keeping the authored cockpit FOV as its baseline.
 CockpitCamera->SetFieldOfView(SpeedBaseFOV+FMath::Min(FMath::Clamp(SpeedFOVBoost,0.f,8.f),FMath::Max(0.f,115.f-SpeedBaseFOV))*SpeedBlend);
 bSpeedCameraApplied=true;
 if(SpeedBlur)SpeedBlur->SetScalarParameterValue(TEXT("SpeedStrength"),Intensity*FMath::Clamp(PeripheralBlurScale,0.f,1.f));
}

void ULocalKartDriverVisuals::TickComponent(float Dt,ELevelTick TickType,FActorComponentTickFunction* ThisTickFunction)
{
 Super::TickComponent(Dt,TickType,ThisTickFunction);RestoreSpeedCamera();RefreshVisibility();
 if(!bActiveForLocalPlayer){SpeedBlend=0;return;}
#if !UE_BUILD_SHIPPING
 // Opt-in visual-only capture. Never writes steering input back to gameplay or moves the pawn.
 const bool bCapture=FParse::Param(FCommandLine::Get(),TEXT("KartFPCapture"));
 const bool bWheelVisibilityCapture=FParse::Param(FCommandLine::Get(),TEXT("WheelVisibilityCapture"));
 const bool bTargetCapture=FParse::Param(FCommandLine::Get(),TEXT("CockpitTargetCapture"));
 const bool bReferenceCapture=bTargetCapture || bWheelVisibilityCapture || FParse::Param(FCommandLine::Get(),TEXT("CockpitReferenceCapture"));
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
  const FTransform Eye=bUsingLegacy?OriginalCameraTransform:FTransform(FRotator(-10,0,0),FVector(5,0,44));
  CockpitCamera->SetWorldTransform(Eye*RoadPose);
 }
#endif
 const float Degrees=SteeringInput*FMath::Clamp(MaximumSteeringDegrees,1.f,25.f);
 if(UAnimSequence* Sequence=ActiveSteeringSequence)
  Arms->SetPosition(((Degrees/25.f+1.f)*.5f)*Sequence->GetPlayLength(),false);
 const FQuat Tilt(FVector::YAxisVector,FMath::DegreesToRadians(bUsingLegacy?0.f:18.f));
 Wheel->SetRelativeRotation(Tilt*FRotator(0,0,Degrees).Quaternion()*Tilt.Inverse());
 if(DashboardSpeed && DashboardTime)
 {
  const AProofPawn* Kart=Cast<AProofPawn>(GetOwner());
  const FString SpeedText=FString::FromInt(FMath::RoundToInt(Kart?FMath::Abs(Kart->GetDrivingSpeed())*.036f:0.f));
  const auto* Race=Cast<AProofGameMode>(GetWorld()->GetAuthGameMode());
  const float Seconds=FMath::Max(0.f,Race?Race->GetRaceElapsedSeconds():GetWorld()->GetTimeSeconds());
  const FString TimeText=FString::Printf(TEXT("%02d:%04.1f"),int32(Seconds)/60,FMath::Fmod(Seconds,60.f));
  if(SpeedText!=LastDashboardSpeed){DashboardSpeed->SetText(FText::FromString(SpeedText));LastDashboardSpeed=SpeedText;}
  if(TimeText!=LastDashboardTime){DashboardTime->SetText(FText::FromString(TimeText));LastDashboardTime=TimeText;}
 }
 UpdateSpeedCamera(Dt);
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
   const FString Dir=FPaths::ProjectDir()/(bTargetCapture?TEXT("Evidence/Cockpit_Layout_v5"):(bWheelVisibilityCapture?TEXT("Evidence/Wheel_Visibility_v3"):TEXT("Evidence/Cockpit_Reference_v2")))/(bUsingLegacy?TEXT("Before"):TEXT("After"));
   IFileManager::Get().MakeDirectory(*Dir,true);FScreenshotRequest::RequestScreenshot(Dir/(FString(Names[CaptureStage])+TEXT(".png")),false,false);++CaptureStage;
  }
  if(CaptureElapsed>37.f)FPlatformMisc::RequestExit(false);
 }
#endif
}

void ULocalKartDriverVisuals::EndPlay(const EEndPlayReason::Type Reason)
{
 RestoreSpeedCamera();
 if(CockpitCamera && SpeedBlur)CockpitCamera->RemoveBlendable(SpeedBlur);
 if(DashboardSpeed)DashboardSpeed->DestroyComponent();if(DashboardTime)DashboardTime->DestroyComponent();
 RestoreThirdPersonVisibility();
 ConfigureCockpitCamera(false);
 if(Arms) Arms->DestroyComponent();if(Wheel) Wheel->DestroyComponent();if(Chassis) Chassis->DestroyComponent();if(VisualRoot) VisualRoot->DestroyComponent();
 Super::EndPlay(Reason);
}



