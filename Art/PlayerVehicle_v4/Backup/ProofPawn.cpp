#include "ProofPawn.h"
#include "KartSurfaceFX.h"
#include "KartTireDynamics.h"
#include "LocalKartDriverVisuals.h"
#include "TrackRacingAI.h"
#include "RaceStartGantry.h"
#include "GridStartSlot.h"
#include "TimerManager.h"
#include "EngineUtils.h"
#include "GameFramework/PlayerStart.h"
#include "GameFramework/PlayerController.h"
#include "UnrealClient.h"
#include "HAL/FileManager.h"
#include "Camera/CameraComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/SkeletalMesh.h"
#include "Animation/AnimSequence.h"
#include "Components/BoxComponent.h"
#include "Components/InputComponent.h"
#include "Modules/ModuleManager.h"
#include "Engine/World.h"
#include "Engine/GameViewportClient.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "HAL/PlatformMisc.h"
AProofPawn::AProofPawn(){
 PrimaryActorTick.bCanEverTick=true;
 Body=CreateDefaultSubobject<UBoxComponent>(TEXT("Collision")); RootComponent=Body;
 Body->InitBoxExtent(FVector(90,60,16)); Body->SetCollisionProfileName(TEXT("Pawn"));
 Camera=CreateDefaultSubobject<UCameraComponent>(TEXT("DriverEye")); Camera->SetupAttachment(Body);
 Camera->SetRelativeLocation(FVector(0,0,64)); Camera->SetFieldOfView(90);
 Camera->SetRelativeRotation(FRotator(-4,0,0));
 Camera->PostProcessSettings.bOverride_MotionBlurAmount=true;Camera->PostProcessSettings.MotionBlurAmount=0;
 ChaseArm=CreateDefaultSubobject<USpringArmComponent>(TEXT("ChaseArm"));ChaseArm->SetupAttachment(Body);
 ChaseArm->SetRelativeLocation(FVector(0,0,100));ChaseArm->SetRelativeRotation(FRotator(-14,0,0));
 ChaseArm->TargetArmLength=360.f;ChaseArm->ProbeSize=15.f;ChaseArm->bDoCollisionTest=true;
 ChaseArm->bUsePawnControlRotation=false;ChaseArm->bEnableCameraLag=false;
 ChaseArm->bEnableCameraRotationLag=true;ChaseArm->CameraRotationLagSpeed=16.f;ChaseArm->bUseCameraLagSubstepping=true;ChaseArm->CameraLagMaxTimeStep=1.f/120.f;
 ChaseArm->PrimaryComponentTick.TickGroup=TG_PostPhysics;ChaseArm->AddTickPrerequisiteActor(this);
 ChaseCamera=CreateDefaultSubobject<UCameraComponent>(TEXT("ChaseCamera"));ChaseCamera->SetupAttachment(ChaseArm,USpringArmComponent::SocketName);
 ChaseCamera->SetFieldOfView(85.f);ChaseCamera->SetAutoActivate(false);
 ChaseCamera->PostProcessSettings.bOverride_MotionBlurAmount=true;ChaseCamera->PostProcessSettings.MotionBlurAmount=0;
 LocalDriverVisuals=CreateDefaultSubobject<ULocalKartDriverVisuals>(TEXT("LocalDriverVisuals"));
 SurfaceFX=CreateDefaultSubobject<UKartSurfaceFX>(TEXT("RearTireSurfaceFX"));
 TireDynamics=CreateDefaultSubobject<UKartTireDynamics>(TEXT("TireDynamics"));
 bUseTireDynamics=!FParse::Param(FCommandLine::Get(),TEXT("LegacyKartMovement"));
 AutoPossessPlayer=EAutoReceiveInput::Player0;
}
void AProofPawn::SetupPlayerInputComponent(UInputComponent* I){
 Super::SetupPlayerInputComponent(I); I->BindAxis("Throttle",this,&AProofPawn::Drive);
 I->BindAxis("Steer",this,&AProofPawn::Turn); I->BindAction("Reset",IE_Pressed,this,&AProofPawn::Reset);
 I->BindAction("Brake",IE_Pressed,this,&AProofPawn::BrakePressed);I->BindAction("Brake",IE_Released,this,&AProofPawn::BrakeReleased);
 I->BindAction("ToggleCamera",IE_Pressed,this,&AProofPawn::ToggleCameraView);
}
bool AProofPawn::CreateExteriorVisuals(){
 if(ExteriorChassis)return true;
 const FString FP=TEXT("/Game/RoadToF1/PlayerVisuals/FirstPerson/");
 auto* ChassisMesh=LoadObject<UStaticMesh>(nullptr,*(FP+TEXT("SM_PlayerKartChassis.SM_PlayerKartChassis")));
 auto* DriverMesh=LoadObject<USkeletalMesh>(nullptr,TEXT("/Game/RoadToF1/RacingAI/SK_AI_KartDriver.SK_AI_KartDriver"));
 auto* WheelMesh=LoadObject<UStaticMesh>(nullptr,*(FP+TEXT("SM_FP_SteeringWheel.SM_FP_SteeringWheel")));
 auto* Sequence=LoadObject<UAnimSequence>(nullptr,*(FP+TEXT("A_FP_KartSteering.A_FP_KartSteering")));
 if(!ChassisMesh||!DriverMesh||!WheelMesh||!Sequence){UE_LOG(LogTemp,Warning,TEXT("Chase camera: existing exterior kart assets unavailable"));return false;}
 ExteriorChassis=NewObject<UStaticMeshComponent>(this,TEXT("PlayerExteriorChassis"));AddInstanceComponent(ExteriorChassis);ExteriorChassis->SetupAttachment(Body);
 ExteriorChassis->SetRelativeLocation(FVector(0,0,-31));ExteriorChassis->SetStaticMesh(ChassisMesh);
 ExteriorDriver=NewObject<USkeletalMeshComponent>(this,TEXT("PlayerExteriorDriver"));AddInstanceComponent(ExteriorDriver);ExteriorDriver->SetupAttachment(ExteriorChassis);
 ExteriorDriver->SetSkeletalMeshAsset(DriverMesh);ExteriorDriver->SetAnimationMode(EAnimationMode::AnimationSingleNode);
 ExteriorWheel=NewObject<UStaticMeshComponent>(this,TEXT("PlayerExteriorWheel"));AddInstanceComponent(ExteriorWheel);ExteriorWheel->SetupAttachment(ExteriorChassis);
 ExteriorWheel->SetRelativeLocation(FVector(62,0,70));ExteriorWheel->SetStaticMesh(WheelMesh);
 for(UMeshComponent* Mesh:{static_cast<UMeshComponent*>(ExteriorChassis.Get()),static_cast<UMeshComponent*>(ExteriorDriver.Get()),static_cast<UMeshComponent*>(ExteriorWheel.Get())}){
  Mesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);Mesh->SetGenerateOverlapEvents(false);Mesh->SetCanEverAffectNavigation(false);Mesh->RegisterComponent();
 }
 ExteriorDriver->SetAnimation(Sequence);ExteriorDriver->SetPlayRate(0);UpdateExteriorSteering();
 return true;
}
void AProofPawn::ToggleCameraView(){
 if(!IsLocallyControlled()||bRacingAI)return;
 if(!bThirdPersonView&&!CreateExteriorVisuals())return;
 bThirdPersonView=!bThirdPersonView;
 LocalDriverVisuals->SetCockpitEnabled(!bThirdPersonView);
 Camera->SetActive(!bThirdPersonView);ChaseCamera->SetActive(bThirdPersonView);
 if(ExteriorChassis)ExteriorChassis->SetVisibility(bThirdPersonView,true);
 if(ExteriorDriver)ExteriorDriver->SetComponentTickEnabled(bThirdPersonView);
}
void AProofPawn::UpdateExteriorSteering(){
 const float Input=GetSteeringVisualInput();
 if(ExteriorDriver)if(auto* Anim=Cast<UAnimSequence>(ExteriorDriver->AnimationData.AnimToPlay))ExteriorDriver->SetPosition((Input+1.f)*.5f*Anim->GetPlayLength(),false);
 if(ExteriorWheel)ExteriorWheel->SetRelativeRotation(FRotator(0,0,Input*25.f));
}
void AProofPawn::StageForRace(const FTransform& T){SetActorTransform(T,false,nullptr,ETeleportType::TeleportPhysics);Speed=0;if(TireDynamics)TireDynamics->ResetMotion();}
float AProofPawn::GetDrivingSpeed()const{return bUseTireDynamics&&TireDynamics?TireDynamics->GetForwardSpeedCm():Speed;}
FVector AProofPawn::GetVelocity()const{return bUseTireDynamics&&TireDynamics?TireDynamics->GetWorldVelocity():GetActorForwardVector()*Speed;}
float AProofPawn::GetMaximumSteeringCurvature()const{return bUseTireDynamics&&TireDynamics?TireDynamics->GetMaximumCurvatureCm():FMath::DegreesToRadians(GetSteeringYawRate())/1600.f;}
float AProofPawn::SteeringForCurvature(float K)const{return bUseTireDynamics&&TireDynamics?TireDynamics->SteeringForCurvature(K):FMath::Clamp(K/GetMaximumSteeringCurvature(),-1.f,1.f);}
float AProofPawn::GetSteeringVisualInput()const{return bUseTireDynamics&&TireDynamics?TireDynamics->GetSteeringVisualInput():Steer;}
void AProofPawn::SetKartTestInput(float InThrottle,float InSteer,bool bBrake){
#if !UE_BUILD_SHIPPING
 if(!FParse::Param(FCommandLine::Get(),TEXT("KartDynamicsTest")))return;
 KartTestThrottle=FMath::IsFinite(InThrottle)?FMath::Clamp(InThrottle,-1.f,1.f):0;KartTestSteering=FMath::IsFinite(InSteer)?FMath::Clamp(InSteer,-1.f,1.f):0;bKartTestBrake=bBrake;bKartTestInputActive=true;
#endif
}
void AProofPawn::ConfigureRacingAI(int32 GridPosition){bRacingAI=true;AutoPossessPlayer=EAutoReceiveInput::Disabled;PreferredGridPosition=GridPosition;}
void AProofPawn::SetAutonomousInput(float InThrottle,float InSteer){if(!bRacingAI||!HasAuthority()||IsPlayerControlled())return;Throttle=FMath::IsFinite(InThrottle)?FMath::Clamp(InThrottle,-1.f,1.f):0;Steer=FMath::IsFinite(InSteer)?FMath::Clamp(InSteer,-1.f,1.f):0;}
void AProofPawn::SetRacingDiagnosticInput(float InThrottle,float InSteer){
#if !UE_BUILD_SHIPPING
 if(!IsPlayerControlled()||!FParse::Param(FCommandLine::Get(),TEXT("RacingAIPlayerTest")))return;
 Throttle=FMath::IsFinite(InThrottle)?FMath::Clamp(InThrottle,-1.f,1.f):0;Steer=FMath::IsFinite(InSteer)?FMath::Clamp(InSteer,-1.f,1.f):0;
#endif
}
void AProofPawn::Reset(){
 if(auto* GM=GetWorld()->GetAuthGameMode<AProofGameMode>())if(auto* Start=GM->GetGridSlotForPawn(this)?static_cast<APlayerStart*>(GM->GetGridSlotForPawn(this)):GM->FindPlayerStart(GetController())){FTransform T=Start->GetActorTransform();T.SetLocation(T.GetLocation()+FVector(0,0,-9));StageForRace(T);return;}
 StageForRace(FTransform(FRotator::ZeroRotator,FVector(800,0,31)));
}
void AProofPawn::Tick(float Dt){
 Super::Tick(Dt); const float FrameDt=Dt;Dt=FMath::Min(Dt,0.05f);
 if(FParse::Param(FCommandLine::Get(),TEXT("ProofSmokeTest"))){
  const float Actual=FApp::GetDeltaTime();TestTime+=Actual;
  Throttle=TestTime<12 ? .35f : (TestTime<15 ? -1.f : 0.f);
  Steer=(TestTime>7 && TestTime<12) ? .15f : 0.f;
  if(TestTime>10){SampleTime+=Actual;SampleFrames++;}
  if(TestTime>20){
   const FString Result=FString::Printf(TEXT("{\"frames\":%d,\"seconds\":%.4f,\"average_ms\":%.3f,\"fps\":%.2f,\"position_cm\":[%.2f,%.2f,%.2f],\"scope\":\"temporary driving pawn, incomplete art, co-running editor\"}"),SampleFrames,SampleTime,SampleTime*1000/SampleFrames,SampleFrames/SampleTime,GetActorLocation().X,GetActorLocation().Y,GetActorLocation().Z);
   FFileHelper::SaveStringToFile(Result,*(FPaths::ProjectDir()/TEXT("Evidence/Runtime.json")));
   UE_LOG(LogTemp,Display,TEXT("PROOF_SMOKE_TEST %s"),*Result);
   FPlatformMisc::RequestExit(false);
  }
 }
 if(FParse::Param(FCommandLine::Get(),TEXT("RaceStartTest"))){Throttle=1.f;Steer=0.f;}
#if !UE_BUILD_SHIPPING
 // A latched opt-in diagnostic input survives the local controller's zero-axis callbacks.
 if(bKartTestInputActive){Throttle=KartTestThrottle;Steer=KartTestSteering;bBrakeHeld=bKartTestBrake;}
#endif
 TickIntegrationEvidence();
 
 LocalDriverVisuals->SetSteeringInput(Steer);
 if(auto* GM=GetWorld()->GetAuthGameMode<AProofGameMode>())if(GM->IsStartGateClosed()){Speed=0;if(bUseTireDynamics){TireDynamics->HoldForStart(FrameDt,Steer);LocalDriverVisuals->SetSteeringInput(GetSteeringVisualInput());}if(bThirdPersonView)UpdateExteriorSteering();return;}
 if(bUseTireDynamics){TireDynamics->Simulate(FrameDt,Throttle,Steer,bBrakeHeld);Speed=TireDynamics->GetForwardSpeedCm();LocalDriverVisuals->SetSteeringInput(GetSteeringVisualInput());if(bThirdPersonView)UpdateExteriorSteering();return;}
 if(bThirdPersonView)UpdateExteriorSteering();
 if(bBrakeHeld)Speed=FMath::FInterpConstantTo(Speed,0.f,Dt,550.f);
 else Speed=FMath::Clamp(Speed+(Throttle*430.f-Speed*0.32f)*Dt,-350.f,1600.f);
 AddActorWorldRotation(FRotator(0,Steer*Speed/1600.f*GetSteeringYawRate()*Dt,0));
 FHitResult Hit; AddActorWorldOffset(GetActorForwardVector()*Speed*Dt,true,&Hit); if(Hit.bBlockingHit) Speed=0;
 FVector P=GetActorLocation(); FCollisionQueryParams Q;Q.AddIgnoredActor(this);
 if(GetWorld()->LineTraceSingleByChannel(Hit,P+FVector(0,0,200),P-FVector(0,0,500),ECC_Visibility,Q)){
 P.Z=Hit.ImpactPoint.Z+31; SetActorLocation(P);
 } else Reset();
}
void AProofPawn::TickIntegrationEvidence(){
#if !UE_BUILD_SHIPPING
 if(!IsPlayerControlled()||!FParse::Param(FCommandLine::Get(),TEXT("KartIntegrationTest")))return;
 auto* GM=GetWorld()->GetAuthGameMode<AProofGameMode>();if(!GM)return;
 const float T=GetWorld()->GetTimeSeconds();
 if(!bIntegrationGridCaptured&&AssignedGridPosition>0){IntegrationGridPosition=GetActorLocation();bIntegrationGridCaptured=true;}
 Throttle=1.f;Steer=(T>2.f&&T<4.f)?-1.f:((T>=4.f&&T<6.f)?1.f:0.f);
 if(bIntegrationGridCaptured&&GM->IsStartGateClosed()&&FVector::Dist(GetActorLocation(),IntegrationGridPosition)>1.f)bIntegrationMovedEarly=true;
 const float Times[]={3.5f,5.5f,6.7f,11.f,14.f};
 const TCHAR* Names[]={TEXT("steering_left"),TEXT("steering_right"),TEXT("pre_start"),TEXT("driving"),TEXT("driving_later")};
 if(IntegrationCaptureStage<5&&T>Times[IntegrationCaptureStage]){
  const FString Dir=FPaths::ProjectDir()/TEXT("Evidence/Integration");IFileManager::Get().MakeDirectory(*Dir,true);
  const FString Name=Names[IntegrationCaptureStage++];
  if(auto* Viewport=GetWorld()->GetGameViewport())Viewport->Exec(GetWorld(),*FString::Printf(TEXT("HighResShot 1600x900 filename=%s"),*(Dir/(Name+TEXT(".png")))),*GLog);
  const FString Data=FString::Printf(TEXT("{\"time\":%.3f,\"reds\":%d,\"gate_closed\":%s,\"start_events\":%d,\"moved_early\":%s,\"distance_cm\":%.3f,\"steer\":%.2f,\"cockpit_active\":%s,\"world_type\":%d,\"x\":%.3f,\"y\":%.3f,\"z\":%.3f}"),T,GM->RedLightCount,GM->IsStartGateClosed()?TEXT("true"):TEXT("false"),GM->StartEventCount,bIntegrationMovedEarly?TEXT("true"):TEXT("false"),FVector::Dist(GetActorLocation(),IntegrationGridPosition),Steer,LocalDriverVisuals->IsFirstPersonActive()?TEXT("true"):TEXT("false"),int32(GetWorld()->WorldType),GetActorLocation().X,GetActorLocation().Y,GetActorLocation().Z);
  FFileHelper::SaveStringToFile(Data,*(Dir/(Name+TEXT(".json"))));
 }
#endif
}
AProofGameMode::AProofGameMode(){DefaultPawnClass=AProofPawn::StaticClass();HUDClass=ARaceStartHUD::StaticClass();RacingAI=CreateDefaultSubobject<UTrackRacingAI>(TEXT("TrackRacingAI"));}
AActor* AProofGameMode::ChoosePlayerStart_Implementation(AController* Player){
 const auto Slots=FindGridSlots();
 if(Slots.Num()){
  if(const int32* Number=ControllerGridSlots.Find(Player))for(auto* Slot:Slots)if(Slot->PositionNumber==*Number)return Slot;
  TSet<int32> Used;for(const auto& E:ControllerGridSlots)if(E.Key.IsValid())Used.Add(E.Value);for(const auto& E:GridAssignments)if(E.Key.IsValid())Used.Add(E.Value);
  for(auto* Slot:Slots)if(!Used.Contains(Slot->PositionNumber)){ControllerGridSlots.Add(Player,Slot->PositionNumber);return Slot;}
  return nullptr;
 }
 for(TActorIterator<APlayerStart> It(GetWorld());It;++It)if(It->ActorHasTag(TEXT("RaceGridStart")))return *It;
 return Super::ChoosePlayerStart_Implementation(Player);
}
void AProofGameMode::BeginPlay(){
 Super::BeginPlay();bTesting=FParse::Param(FCommandLine::Get(),TEXT("RaceStartTest"));
 for(TActorIterator<ARaceStartGantry> It(GetWorld());It;++It){Gantry=*It;break;}
 for(TActorIterator<APlayerStart> It(GetWorld());It;++It)if(It->ActorHasTag(TEXT("RaceGridStart"))){bStartEnabled=true;break;}
 bStartEnabled=bStartEnabled||IsValid(Gantry);
 if(FParse::Param(FCommandLine::Get(),TEXT("RaceStartMissingGantry")))Gantry=nullptr;
 if(bTesting){IFileManager::Get().MakeDirectory(*(StartEvidenceDirectory()),true);FFileHelper::SaveStringToFile(TEXT(""),*(StartEvidenceDirectory()/TEXT("runtime_events.jsonl")));}
 if(FParse::Param(FCommandLine::Get(),TEXT("Grid20Test"))){
  // Explicit test-only participants; never populate empty slots during normal Play.
  const auto Slots=FindGridSlots();for(auto* Slot:Slots)if(Slot->PositionNumber>1){FTransform T=Slot->GetActorTransform();T.SetLocation(T.GetLocation()+FVector(0,0,-9));auto* P=GetWorld()->SpawnActorDeferred<AProofPawn>(AProofPawn::StaticClass(),T,nullptr,nullptr,ESpawnActorCollisionHandlingMethod::AlwaysSpawn);if(P){P->AutoPossessPlayer=EAutoReceiveInput::Disabled;P->PreferredGridPosition=Slot->PositionNumber;P->FinishSpawning(T);}}
 }
 if(bStartEnabled){RacingAI->InitializeOpponents();RestartRaceStart();}
}
void AProofGameMode::EndPlay(const EEndPlayReason::Type Reason){GetWorldTimerManager().ClearAllTimersForObject(this);Super::EndPlay(Reason);}
float AProofGameMode::GetRaceElapsedSeconds() const{return RaceStartWorldSeconds<0?0.f:float(GetWorld()->GetTimeSeconds()-RaceStartWorldSeconds);}
void AProofGameMode::RestartRaceStart(){
 if(!bStartEnabled)return;
 RacingAI->ResetRace();
 GetWorldTimerManager().ClearAllTimersForObject(this);RacePhase=ERaceStartPhase::PreGrid;RedLightCount=0;RaceStartWorldSeconds=-1;StartEventCount=0;++TestEpoch;
 if(IsValid(Gantry))Gantry->SetRedLightCount(0);else UE_LOG(LogTemp,Warning,TEXT("RACE_START: missing display; authoritative timer remains active"));
 StageGridParticipants();
 Record(TEXT("PRE_GRID"));GetWorldTimerManager().SetTimer(ReadyTimer,this,&AProofGameMode::WaitForGrid,.1f,true);
}
void AProofGameMode::WaitForGrid(){
 bool bHasPlayer=false;
 for(FConstPlayerControllerIterator It=GetWorld()->GetPlayerControllerIterator();It;++It){auto* PC=It->Get();if(!PC||!PC->GetPawn())return;bHasPlayer=true;}
 if(!bHasPlayer)return;
 if(!StageGridParticipants())return;
 GetWorldTimerManager().ClearTimer(ReadyTimer);
 if(auto* PC=GetWorld()->GetFirstPlayerController())if(APawn* P=PC->GetPawn())TestGridPosition=P->GetActorLocation();
 Record(TEXT("GRID_READY"));GetWorldTimerManager().SetTimer(SequenceTimer,this,&AProofGameMode::AddRed,FMath::Max(.1f,StagingDelay),false);
}
void AProofGameMode::AddRed(){
 if(RaceStartWorldSeconds>=0)return;
 RacePhase=ERaceStartPhase::Countdown;RedLightCount=FMath::Min(5,RedLightCount+1);
 if(IsValid(Gantry)){Gantry->SetRedLightCount(RedLightCount);Gantry->PlayCue(false);}Record(TEXT("RED_ON"));
 if(RedLightCount==5){RacePhase=ERaceStartPhase::AllRed;Record(TEXT("ALL_RED"));GetWorldTimerManager().SetTimer(SequenceTimer,this,&AProofGameMode::ReleaseRace,FMath::Max(.1f,AllRedHold),false);if(bTesting&&TestEpoch==1)GetWorldTimerManager().SetTimer(TestCaptureTimer,FTimerDelegate::CreateWeakLambda(this,[this](){Capture(TEXT("AllRed"));}),.35f,false);}
 else GetWorldTimerManager().SetTimer(SequenceTimer,this,&AProofGameMode::AddRed,FMath::Max(.1f,RedInterval),false);
}
void AProofGameMode::ReleaseRace(){
 if(StartEventCount!=0||RaceStartWorldSeconds>=0)return;
 if(IsValid(Gantry)){Gantry->SetRedLightCount(0);Gantry->PlayCue(true);}
 RedLightCount=0;RacePhase=ERaceStartPhase::LightsOut;RaceStartWorldSeconds=GetWorld()->GetTimeSeconds();++StartEventCount;
 OnLightsOut.Broadcast(RaceStartWorldSeconds);Record(TEXT("LIGHTS_OUT"));GetWorldTimerManager().SetTimerForNextTick(this,&AProofGameMode::EnterRacing);
 if(bTesting){if(TestEpoch==1)GetWorldTimerManager().SetTimer(TestCaptureTimer,FTimerDelegate::CreateWeakLambda(this,[this](){Capture(TEXT("LightsOut"));}),.12f,false);GetWorldTimerManager().SetTimer(TestControlTimer,this,&AProofGameMode::TestAfterRelease,FindGridSlots().Num()?3.f:1.5f,false);}
}
void AProofGameMode::EnterRacing(){RacePhase=ERaceStartPhase::Racing;Record(TEXT("RACING"));}
void AProofGameMode::Record(const TCHAR* Event){
 FVector P=FVector::ZeroVector;if(auto* PC=GetWorld()->GetFirstPlayerController())if(APawn* Pawn=PC->GetPawn())P=Pawn->GetActorLocation();
 if(bTesting&&RacePhase!=ERaceStartPhase::PreGrid&&RaceStartWorldSeconds<0&&FVector::Dist2D(P,TestGridPosition)>1.f)bTestMovedEarly=true;
 FString Line=FString::Printf(TEXT("{\"event\":\"%s\",\"time\":%.4f,\"epoch\":%d,\"reds\":%d,\"start_events\":%d,\"x\":%.3f,\"y\":%.3f,\"moved_early\":%s}\n"),Event,GetWorld()->GetTimeSeconds(),TestEpoch,RedLightCount,StartEventCount,P.X,P.Y,bTestMovedEarly?TEXT("true"):TEXT("false"));
 if(bTesting&&RaceStartWorldSeconds<0)for(const auto& E:StagedPositions)if(E.Key.IsValid()&&FVector::Dist2D(E.Key->GetActorLocation(),E.Value)>1.f)bTestMovedEarly=true;
 Line=Line.Replace(TEXT("}\n"),*FString::Printf(TEXT(",\"staged\":%d,\"grid_slot\":%d}\n"),StagedParticipantCount,GetWorld()->GetFirstPlayerController()&&Cast<AProofPawn>(GetWorld()->GetFirstPlayerController()->GetPawn())?Cast<AProofPawn>(GetWorld()->GetFirstPlayerController()->GetPawn())->AssignedGridPosition:0));
 UE_LOG(LogTemp,Display,TEXT("RACE_START %s"),*Line);
 if(bTesting)FFileHelper::SaveStringToFile(Line,*(StartEvidenceDirectory()/TEXT("runtime_events.jsonl")),FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM,&IFileManager::Get(),FILEWRITE_Append);
}
void AProofGameMode::Capture(const TCHAR* Name){FScreenshotRequest::RequestScreenshot(StartEvidenceDirectory()/(FString(Name)+TEXT(".png")),false,false);}
void AProofGameMode::TestAfterRelease(){
 FVector P=TestGridPosition;if(auto* PC=GetWorld()->GetFirstPlayerController())if(APawn* Pawn=PC->GetPawn())P=Pawn->GetActorLocation();
 bool bPassed=!bTestMovedEarly&&StartEventCount==1&&FVector::Dist2D(P,TestGridPosition)>50.f;
 for(const auto& E:StagedPositions)if(E.Key.IsValid()&&FVector::Dist2D(E.Key->GetActorLocation(),E.Value)<50.f)bPassed=false;
 for(TActorIterator<AActor> It(GetWorld());It;++It)if(It->ActorHasTag(TEXT("GridFinish"))){FVector C,E;It->GetActorBounds(false,C,E);if(P.X>C.X)Record(TEXT("GRID_FINISH_CROSSED"));}
 Record(bPassed?TEXT("TEST_PASS"):TEXT("TEST_FAIL"));
 if(TestEpoch==1)RestartRaceStart();else FPlatformMisc::RequestExit(false);
}



TArray<AGridStartSlot*> AProofGameMode::FindGridSlots() const {
 TArray<AGridStartSlot*> Slots;for(TActorIterator<AGridStartSlot> It(GetWorld());It;++It)Slots.Add(*It);
 Slots.Sort([](const AGridStartSlot& A,const AGridStartSlot& B){return A.PositionNumber<B.PositionNumber;});return Slots;
}
AGridStartSlot* AProofGameMode::GetGridSlotForPawn(AProofPawn* Pawn) const {
 if(const int32* Number=GridAssignments.Find(Pawn))for(auto* Slot:FindGridSlots())if(Slot->PositionNumber==*Number)return Slot;
 return nullptr;
}
bool AProofGameMode::RegisterGridParticipant(AProofPawn* Pawn,int32 RequestedPosition){
 if(!IsValid(Pawn)||RacePhase!=ERaceStartPhase::PreGrid)return false;
 if(GridAssignments.Contains(Pawn))return RequestedPosition==0||GridAssignments[Pawn]==RequestedPosition;
 const auto Slots=FindGridSlots();if(Slots.Num()!=20)return false;
 if(!RequestedPosition)RequestedPosition=Pawn->PreferredGridPosition;
 if(!RequestedPosition)if(const int32* Pending=ControllerGridSlots.Find(Pawn->GetController()))RequestedPosition=*Pending;
 TSet<int32> Used;for(const auto& E:GridAssignments)if(E.Key.IsValid())Used.Add(E.Value);
 for(const auto& E:ControllerGridSlots)if(E.Key.IsValid()&&E.Key.Get()!=Pawn->GetController())Used.Add(E.Value);
 if(!RequestedPosition)for(auto* Slot:Slots)if(!Used.Contains(Slot->PositionNumber)){RequestedPosition=Slot->PositionNumber;break;}
 if(RequestedPosition<1||RequestedPosition>20||Used.Contains(RequestedPosition))return false;
 GridAssignments.Add(Pawn,RequestedPosition);if(Pawn->IsPlayerControlled())ControllerGridSlots.Add(Pawn->GetController(),RequestedPosition);Pawn->AssignedGridPosition=RequestedPosition;return true;
}
bool AProofGameMode::StageGridParticipants(){
 const auto Slots=FindGridSlots();
 if(!Slots.Num()){
  for(FConstPlayerControllerIterator It=GetWorld()->GetPlayerControllerIterator();It;++It)if(auto* PC=It->Get())if(auto* P=Cast<AProofPawn>(PC->GetPawn()))if(auto* Start=FindPlayerStart(PC)){FTransform T=Start->GetActorTransform();T.SetLocation(T.GetLocation()+FVector(0,0,-9));P->StageForRace(T);}return true;
 }
 if(Slots.Num()!=20)return false;
 for(int32 I=0;I<20;++I)if(Slots[I]->PositionNumber!=I+1)return false;
 for(auto It=GridAssignments.CreateIterator();It;++It)if(!It.Key().IsValid())It.RemoveCurrent();
 TArray<AProofPawn*> Participants;for(TActorIterator<AProofPawn> It(GetWorld());It;++It)Participants.Add(*It);
 Participants.Sort([](const AProofPawn& A,const AProofPawn& B){if(A.IsPlayerControlled()!=B.IsPlayerControlled())return A.IsPlayerControlled();return A.GetName()<B.GetName();});
 StagedParticipantCount=0;StagedPositions.Reset();
 for(auto* Pawn:Participants){
  if(!RegisterGridParticipant(Pawn))return false;
  auto* Slot=GetGridSlotForPawn(Pawn);if(!Slot)return false;FTransform T=Slot->GetActorTransform();T.SetLocation(T.GetLocation()+FVector(0,0,-9));Pawn->StageForRace(T);
  if(FVector::DistSquared(Pawn->GetActorLocation(),T.GetLocation())>1.f)return false;StagedPositions.Add(Pawn,Pawn->GetActorLocation());++StagedParticipantCount;
 }
 return StagedParticipantCount>0;
}

FString AProofGameMode::StartEvidenceDirectory() const{return FPaths::ProjectDir()/ (FParse::Param(FCommandLine::Get(),TEXT("Grid20Test"))?TEXT("Evidence/Grid20"):TEXT("Evidence/RaceStart"));}
