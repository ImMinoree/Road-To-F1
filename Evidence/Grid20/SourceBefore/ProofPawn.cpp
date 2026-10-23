#include "ProofPawn.h"
#include "LocalKartDriverVisuals.h"
#include "RaceStartGantry.h"
#include "TimerManager.h"
#include "EngineUtils.h"
#include "GameFramework/PlayerStart.h"
#include "GameFramework/PlayerController.h"
#include "UnrealClient.h"
#include "HAL/FileManager.h"
#include "Camera/CameraComponent.h"
#include "Components/SphereComponent.h"
#include "Components/InputComponent.h"
#include "Modules/ModuleManager.h"
#include "Engine/World.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "HAL/PlatformMisc.h"
AProofPawn::AProofPawn(){
 PrimaryActorTick.bCanEverTick=true;
 Body=CreateDefaultSubobject<USphereComponent>(TEXT("Collision")); RootComponent=Body;
 Body->InitSphereRadius(28); Body->SetCollisionProfileName(TEXT("Pawn"));
 Camera=CreateDefaultSubobject<UCameraComponent>(TEXT("DriverEye")); Camera->SetupAttachment(Body);
 Camera->SetRelativeLocation(FVector(0,0,49)); Camera->SetFieldOfView(85);
 LocalDriverVisuals=CreateDefaultSubobject<ULocalKartDriverVisuals>(TEXT("LocalDriverVisuals"));
 AutoPossessPlayer=EAutoReceiveInput::Player0;
}
void AProofPawn::SetupPlayerInputComponent(UInputComponent* I){
 Super::SetupPlayerInputComponent(I); I->BindAxis("Throttle",this,&AProofPawn::Drive);
 I->BindAxis("Steer",this,&AProofPawn::Turn); I->BindAction("Reset",IE_Pressed,this,&AProofPawn::Reset);
}
void AProofPawn::StageForRace(const FTransform& T){SetActorTransform(T,false,nullptr,ETeleportType::TeleportPhysics);Speed=0;}
void AProofPawn::Reset(){
 if(auto* GM=GetWorld()->GetAuthGameMode<AProofGameMode>())if(auto* Start=GM->FindPlayerStart(GetController())){FTransform T=Start->GetActorTransform();T.SetLocation(T.GetLocation()+FVector(0,0,-9));StageForRace(T);return;}
 SetActorLocationAndRotation(FVector(800,0,31),FRotator::ZeroRotator);Speed=0;
}
void AProofPawn::Tick(float Dt){
 Super::Tick(Dt); Dt=FMath::Min(Dt,0.05f);
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
 LocalDriverVisuals->SetSteeringInput(Steer);
 if(auto* GM=GetWorld()->GetAuthGameMode<AProofGameMode>())if(GM->IsStartGateClosed()){Speed=0;return;}
 Speed=FMath::Clamp(Speed+(Throttle*430.f-Speed*0.32f)*Dt,-350.f,1600.f);
 AddActorWorldRotation(FRotator(0,Steer*Speed/1600.f*65.f*Dt,0));
 FHitResult Hit; AddActorWorldOffset(GetActorForwardVector()*Speed*Dt,true,&Hit); if(Hit.bBlockingHit) Speed=0;
 FVector P=GetActorLocation(); FCollisionQueryParams Q;Q.AddIgnoredActor(this);
 if(GetWorld()->LineTraceSingleByChannel(Hit,P+FVector(0,0,200),P-FVector(0,0,500),ECC_Visibility,Q)){
 P.Z=Hit.ImpactPoint.Z+31; SetActorLocation(P);
 } else Reset();
}
AProofGameMode::AProofGameMode(){DefaultPawnClass=AProofPawn::StaticClass();HUDClass=ARaceStartHUD::StaticClass();}
AActor* AProofGameMode::ChoosePlayerStart_Implementation(AController* Player){
 for(TActorIterator<APlayerStart> It(GetWorld());It;++It)if(It->ActorHasTag(TEXT("RaceGridStart")))return *It;
 return Super::ChoosePlayerStart_Implementation(Player);
}
void AProofGameMode::BeginPlay(){
 Super::BeginPlay();bTesting=FParse::Param(FCommandLine::Get(),TEXT("RaceStartTest"));
 for(TActorIterator<ARaceStartGantry> It(GetWorld());It;++It){Gantry=*It;break;}
 for(TActorIterator<APlayerStart> It(GetWorld());It;++It)if(It->ActorHasTag(TEXT("RaceGridStart"))){bStartEnabled=true;break;}
 bStartEnabled=bStartEnabled||IsValid(Gantry);
 if(FParse::Param(FCommandLine::Get(),TEXT("RaceStartMissingGantry")))Gantry=nullptr;
 if(bTesting){IFileManager::Get().MakeDirectory(*(FPaths::ProjectDir()/TEXT("Evidence/RaceStart")),true);FFileHelper::SaveStringToFile(TEXT(""),*(FPaths::ProjectDir()/TEXT("Evidence/RaceStart/runtime_events.jsonl")));}
 if(bStartEnabled)RestartRaceStart();
}
void AProofGameMode::EndPlay(const EEndPlayReason::Type Reason){GetWorldTimerManager().ClearAllTimersForObject(this);Super::EndPlay(Reason);}
float AProofGameMode::GetRaceElapsedSeconds() const{return RaceStartWorldSeconds<0?0.f:float(GetWorld()->GetTimeSeconds()-RaceStartWorldSeconds);}
void AProofGameMode::RestartRaceStart(){
 if(!bStartEnabled)return;
 GetWorldTimerManager().ClearAllTimersForObject(this);RacePhase=ERaceStartPhase::PreGrid;RedLightCount=0;RaceStartWorldSeconds=-1;StartEventCount=0;++TestEpoch;
 if(IsValid(Gantry))Gantry->SetRedLightCount(0);else UE_LOG(LogTemp,Warning,TEXT("RACE_START: missing display; authoritative timer remains active"));
 for(FConstPlayerControllerIterator It=GetWorld()->GetPlayerControllerIterator();It;++It)if(auto* PC=It->Get())if(auto* P=Cast<AProofPawn>(PC->GetPawn()))if(auto* Start=FindPlayerStart(PC)){FTransform T=Start->GetActorTransform();T.SetLocation(T.GetLocation()+FVector(0,0,-9));P->StageForRace(T);}
 Record(TEXT("PRE_GRID"));GetWorldTimerManager().SetTimer(ReadyTimer,this,&AProofGameMode::WaitForGrid,.1f,true);
}
void AProofGameMode::WaitForGrid(){
 bool bHasPlayer=false;
 for(FConstPlayerControllerIterator It=GetWorld()->GetPlayerControllerIterator();It;++It){auto* PC=It->Get();if(!PC||!PC->GetPawn())return;bHasPlayer=true;}
 if(!bHasPlayer)return;
 GetWorldTimerManager().ClearTimer(ReadyTimer);
 for(FConstPlayerControllerIterator It=GetWorld()->GetPlayerControllerIterator();It;++It)if(auto* PC=It->Get())if(auto* P=Cast<AProofPawn>(PC->GetPawn()))if(auto* Start=FindPlayerStart(PC)){FTransform T=Start->GetActorTransform();T.SetLocation(T.GetLocation()+FVector(0,0,-9));P->StageForRace(T);}
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
 if(bTesting){if(TestEpoch==1)GetWorldTimerManager().SetTimer(TestCaptureTimer,FTimerDelegate::CreateWeakLambda(this,[this](){Capture(TEXT("LightsOut"));}),.12f,false);GetWorldTimerManager().SetTimer(TestControlTimer,this,&AProofGameMode::TestAfterRelease,1.5f,false);}
}
void AProofGameMode::EnterRacing(){RacePhase=ERaceStartPhase::Racing;Record(TEXT("RACING"));}
void AProofGameMode::Record(const TCHAR* Event){
 FVector P=FVector::ZeroVector;if(auto* PC=GetWorld()->GetFirstPlayerController())if(APawn* Pawn=PC->GetPawn())P=Pawn->GetActorLocation();
 if(bTesting&&RacePhase!=ERaceStartPhase::PreGrid&&RaceStartWorldSeconds<0&&FVector::Dist2D(P,TestGridPosition)>1.f)bTestMovedEarly=true;
 const FString Line=FString::Printf(TEXT("{\"event\":\"%s\",\"time\":%.4f,\"epoch\":%d,\"reds\":%d,\"start_events\":%d,\"x\":%.3f,\"y\":%.3f,\"moved_early\":%s}\n"),Event,GetWorld()->GetTimeSeconds(),TestEpoch,RedLightCount,StartEventCount,P.X,P.Y,bTestMovedEarly?TEXT("true"):TEXT("false"));
 UE_LOG(LogTemp,Display,TEXT("RACE_START %s"),*Line);
 if(bTesting)FFileHelper::SaveStringToFile(Line,*(FPaths::ProjectDir()/TEXT("Evidence/RaceStart/runtime_events.jsonl")),FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM,&IFileManager::Get(),FILEWRITE_Append);
}
void AProofGameMode::Capture(const TCHAR* Name){FScreenshotRequest::RequestScreenshot(FPaths::ProjectDir()/TEXT("Evidence/RaceStart")/(FString(Name)+TEXT(".png")),false,false);}
void AProofGameMode::TestAfterRelease(){
 FVector P=TestGridPosition;if(auto* PC=GetWorld()->GetFirstPlayerController())if(APawn* Pawn=PC->GetPawn())P=Pawn->GetActorLocation();
 const bool bPassed=!bTestMovedEarly&&StartEventCount==1&&FVector::Dist2D(P,TestGridPosition)>50.f;
 Record(bPassed?TEXT("TEST_PASS"):TEXT("TEST_FAIL"));
 if(TestEpoch==1)RestartRaceStart();else FPlatformMisc::RequestExit(false);
}


