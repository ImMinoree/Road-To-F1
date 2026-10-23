#include "ProofPawn.h"
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
 AutoPossessPlayer=EAutoReceiveInput::Player0;
}
void AProofPawn::SetupPlayerInputComponent(UInputComponent* I){
 Super::SetupPlayerInputComponent(I); I->BindAxis("Throttle",this,&AProofPawn::Drive);
 I->BindAxis("Steer",this,&AProofPawn::Turn); I->BindAction("Reset",IE_Pressed,this,&AProofPawn::Reset);
}
void AProofPawn::Reset(){SetActorLocationAndRotation(FVector(800,0,31),FRotator::ZeroRotator);Speed=0;}
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
 Speed=FMath::Clamp(Speed+(Throttle*430.f-Speed*0.32f)*Dt,-350.f,1600.f);
 AddActorWorldRotation(FRotator(0,Steer*Speed/1600.f*65.f*Dt,0));
 FHitResult Hit; AddActorWorldOffset(GetActorForwardVector()*Speed*Dt,true,&Hit); if(Hit.bBlockingHit) Speed=0;
 FVector P=GetActorLocation(); FCollisionQueryParams Q;Q.AddIgnoredActor(this);
 if(GetWorld()->LineTraceSingleByChannel(Hit,P+FVector(0,0,200),P-FVector(0,0,500),ECC_Visibility,Q)){
 P.Z=Hit.ImpactPoint.Z+31; SetActorLocation(P);
 } else Reset();
}
AProofGameMode::AProofGameMode(){DefaultPawnClass=AProofPawn::StaticClass();}
