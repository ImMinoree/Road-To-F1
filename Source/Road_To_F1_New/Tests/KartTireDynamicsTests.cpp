#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../KartTireModel.h"
#include "../KartTireDynamics.h"
#include "../RaceCountdownPresentation.h"
#include "../ProofPawn.h"
#include "Components/BoxComponent.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "HAL/FileManager.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FKartForceScenarios,"RoadToF1.TireDynamics.ForceScenarios",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FKartForceScenarios::RunTest(const FString&){
 using namespace KartDynamics;
 const TCHAR* Names[]={TEXT("straight_brake"),TEXT("low_tight"),TEXT("fast_grip"),TEXT("excessive_corner"),TEXT("brake_entry"),TEXT("countersteer"),TEXT("surface_transition"),TEXT("parked_steering")};
 FString Summary=TEXT("case,max_beta_deg,max_yaw_deg_s,max_front_slip_deg,max_rear_slip_deg,end_speed_mps,end_beta_deg,end_yaw_deg_s,drift_steps\n");
 const FString Dir=FPaths::ProjectDir()/TEXT("Evidence/TireDynamics");IFileManager::Get().MakeDirectory(*Dir,true);
 for(int C=0;C<8;++C){Parameters P;State S;Contact Ground;Input I;if(C>=2&&C<=6)S.U=11;
  double MaxBeta=0,MaxYaw=0,MaxFront=0,MaxRear=0;int Drift=0;bool Valid=true;FString Csv=TEXT("t,u_mps,v_mps,beta_deg,yaw_deg_s,front_slip_deg,rear_slip_deg,front_fx_n,rear_fx_n,front_fy_n,rear_fy_n,front_use,rear_use,mu,drifting\n");
  for(int K=0;K<2400;++K){const double T=K*StepSeconds;I={};Ground={};
   if(C==0){I.Throttle=T<6?1:0;I.Brake=T>=6?1:0;}
   if(C==1){I.Throttle=.25;I.Steering=.8;}
   if(C==2){I.Throttle=.85;I.Steering=.08;}
   if(C==3){I.Throttle=.6;I.Steering=.9;}
   if(C==4||C==5){if(T<1){I.Throttle=.8;I.Steering=.12;}else if(T<1.6){I.Brake=1;I.Steering=.12;}else {I.Throttle=std::abs(S.Beta)>Rad(2)||std::abs(S.R)>.15?.3:.8;I.Steering=C==5?std::clamp(S.Beta*1.5-S.R*.12,-.8,.8):0;}}
   if(C==6){I.Throttle=.3;I.Steering=.1;if(T>2&&T<5)Ground.FrontMu=Ground.RearMu=.42;if(std::abs(S.Beta)>Rad(3)){I.Steering=std::clamp(S.Beta*1.5-S.R*.12,-.8,.8);I.Throttle=.15;}}
   if(C==7)I.Steering=1;
   Step(S,P,Ground,I);
   Valid=Valid&&std::isfinite(S.U)&&std::isfinite(S.V)&&std::isfinite(S.R)&&S.FrontUtilization<=1.000001&&S.RearUtilization<=1.000001;
   MaxBeta=std::max(MaxBeta,std::abs(Deg(S.Beta)));MaxYaw=std::max(MaxYaw,std::abs(Deg(S.R)));MaxFront=std::max(MaxFront,std::abs(Deg(S.FrontAlpha)));MaxRear=std::max(MaxRear,std::abs(Deg(S.RearAlpha)));if(S.Drifting)++Drift;
   if(K%4==0)Csv+=FString::Printf(TEXT("%.4f,%.5f,%.5f,%.4f,%.4f,%.4f,%.4f,%.2f,%.2f,%.2f,%.2f,%.5f,%.5f,%.3f,%d\n"),T,S.U,S.V,Deg(S.Beta),Deg(S.R),Deg(S.FrontAlpha),Deg(S.RearAlpha),S.FrontFx,S.RearFx,S.FrontFy,S.RearFy,S.FrontUtilization,S.RearUtilization,Ground.RearMu,S.Drifting?1:0);
  }
  TestTrue(FString(Names[C])+TEXT(": finite and within both friction circles"),Valid);
  if(C==0){TestTrue(TEXT("Straight braking stops without yaw or reverse"),std::hypot(S.U,S.V)<.05&&MaxYaw<.001);}
  if(C==1||C==2||C==7)TestEqual(FString(Names[C])+TEXT(": no false drift from steering/body angle alone"),Drift,0);
  if(C==3)TestTrue(TEXT("Held corner input stays controllable with the digital steering envelope"),MaxBeta<10&&S.U>1);
  if(C==4||C==5){TestTrue(TEXT("Normal brake entry does not force a drift or spin"),MaxBeta<10);TestTrue(TEXT("Grip recovers at driving speed without a spin"),std::abs(Deg(S.Beta))<1&&std::abs(Deg(S.R))<2&&S.U>6);}
  if(C==7)TestTrue(TEXT("Steering at rest never translates or yaws the kart"),S.X==0&&S.Y==0&&S.Heading==0);
  Summary+=FString::Printf(TEXT("%s,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%d\n"),Names[C],MaxBeta,MaxYaw,MaxFront,MaxRear,std::hypot(S.U,S.V),Deg(S.Beta),Deg(S.R),Drift);
  FFileHelper::SaveStringToFile(Csv,*(Dir/(FString(TEXT("engine_"))+Names[C]+TEXT(".csv"))));
 }
 FFileHelper::SaveStringToFile(Summary,*(Dir/TEXT("engine_scenarios.csv")));
 // Frame grouping changes neither the fixed-step integration nor a held input.
 State Reference;
 for(int Group:{2,4,8}){State S;Parameters P;Contact C;Input I{.7,.08,0};for(int Frame=0;Frame<2400/Group;++Frame)for(int J=0;J<Group;++J)Step(S,P,C,I);if(Group==2)Reference=S;else TestTrue(TEXT("30/60/120 Hz groupings reproduce the same state"),std::abs(S.X-Reference.X)<1e-9&&std::abs(S.Y-Reference.Y)<1e-9&&std::abs(S.R-Reference.R)<1e-9);}
 return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FKartSweptWorld,"RoadToF1.TireDynamics.GroundCollisionAndReset",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FKartSweptWorld::RunTest(const FString&){
 const UWorld::InitializationValues Init=UWorld::InitializationValues().AllowAudioPlayback(false).CreatePhysicsScene(true).CreateNavigation(false).CreateAISystem(false).ShouldSimulatePhysics(false).SetTransactional(false);
 UWorld* World=UWorld::CreateWorld(EWorldType::Game,false,FName(TEXT("TireForceWorld")),nullptr,true,ERHIFeatureLevel::Num,&Init);
 FWorldContext& Context=GEngine->CreateNewWorldContext(EWorldType::Game);Context.SetCurrentWorld(World);World->InitializeActorsForPlay(FURL());
 auto Box=[&](FVector Position,FVector Extent){auto* A=World->SpawnActor<AActor>();auto* C=NewObject<UBoxComponent>(A);A->SetRootComponent(C);A->AddInstanceComponent(C);C->SetBoxExtent(Extent);C->SetCollisionObjectType(ECC_WorldStatic);C->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);C->SetCollisionResponseToAllChannels(ECR_Block);C->RegisterComponent();A->SetActorLocation(Position);return A;};
 auto* Floor=Box(FVector(0,0,-50),FVector(20000,20000,50));Floor->Tags={TEXT("SurfaceAsphalt")};
 FActorSpawnParameters Spawn;Spawn.SpawnCollisionHandlingOverride=ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
 auto* Pawn=World->SpawnActor<AProofPawn>(AProofPawn::StaticClass(),FVector(0,0,31),FRotator::ZeroRotator,Spawn);auto* D=Pawn->GetTireDynamics();
 const FVector Grid=Pawn->GetActorLocation();for(int K=0;K<60;++K)D->HoldForStart(1.f/60,.5f);
 TestTrue(TEXT("Start gate holds position and all velocity state"),Pawn->GetActorLocation().Equals(Grid,.001)&&D->GetWorldVelocity().IsNearlyZero());
 for(int K=0;K<180;++K)D->Simulate(1.f/60,1,0,false);
 TestEqual(TEXT("All four axle samples find the supporting road"),D->Telemetry.GroundedWheels,4);
 TestTrue(TEXT("Movement emerges after release and stays above the road"),Pawn->GetActorLocation().X>500&&FMath::Abs(Pawn->GetActorLocation().Z-31)<.1);
 TestTrue(TEXT("Asphalt grip is read from existing surface tags"),FMath::IsNearlyEqual(D->Telemetry.RearGrip,1.05f,.01f));
 for(const auto& Surface:TArray<TPair<FName,float>>{{TEXT("SurfaceGrass"),.48f},{TEXT("SurfaceDirt"),.42f},{TEXT("SurfaceCurb"),.85f}}){Floor->Tags={Surface.Key};D->Simulate(1.f/60,.3f,0,false);TestTrue(TEXT("Ground transitions alter measured grip"),FMath::IsNearlyEqual(D->Telemetry.RearGrip,Surface.Value,.01f));}
 Floor->Tags={TEXT("SurfaceAsphalt")};Pawn->StageForRace(FTransform(FRotator::ZeroRotator,FVector(0,0,31)));
 TestTrue(TEXT("Restart clears lateral velocity, yaw rate and drift latch"),D->GetWorldVelocity().IsNearlyZero()&&!D->Telemetry.bDrifting&&D->Telemetry.YawRateDegrees==0);
 Box(FVector(300,0,100),FVector(10,2000,100));
 for(int K=0;K<240;++K)D->Simulate(1.f/60,1,0,false);
 TestTrue(TEXT("Existing sphere sweep blocks a wall without tunneling"),D->CollisionCount>0&&Pawn->GetActorLocation().X<290&&Pawn->GetActorLocation().X>100);
 Floor->SetActorEnableCollision(false);const float OldZ=Pawn->GetActorLocation().Z;for(int K=0;K<30;++K)D->Simulate(1.f/60,0,0,false);
 TestTrue(TEXT("Missing road support falls under gravity instead of resetting/teleporting"),Pawn->GetActorLocation().Z<OldZ-20);
 GEngine->DestroyWorldContext(World);World->DestroyWorld(false);return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FKartAssistedRecovery,"RoadToF1.TireDynamics.AssistedCornerRecovery",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FKartAssistedRecovery::RunTest(const FString&){
 using namespace KartDynamics;
 for(int Scenario:{0,1})for(double Sign:{-1.,1.}){
  Parameters P;State S;Contact C;S.U=Scenario?11:16;if(Scenario){S.V=-1.2*Sign;S.R=.7*Sign;}
  double Peak=0;bool Bounded=true;
  for(int K=0;K<2400;++K){const bool Turn=Scenario==0&&K<480;
   Input I{Turn?1.:(Scenario?.3:.35),Turn?Sign:std::clamp(S.Beta*1.5-S.R*.12,-.8,.8),0};Step(S,P,C,I);
   Peak=std::max(Peak,std::abs(Deg(S.Beta)));Bounded=Bounded&&std::isfinite(S.U)&&std::isfinite(S.V)&&std::isfinite(S.R)&&S.FrontUtilization<=1.000001&&S.RearUtilization<=1.000001;
  }
  TestTrue(TEXT("Both turn directions remain finite and friction bounded"),Bounded);
  TestTrue(TEXT("Full-key turn or established slide avoids a spin"),Peak<10);
  if(Scenario)TestTrue(TEXT("Recovery actually starts from significant sideslip"),Peak>6);
  TestTrue(TEXT("Countersteering recovers at forward speed"),std::abs(Deg(S.Beta))<1&&std::abs(Deg(S.R))<2&&S.U>3);
 }
 return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRaceCountdownFade,"RoadToF1.RaceStart.CountdownPresentation",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FRaceCountdownFade::RunTest(const FString&){
 using namespace RaceCountdownPresentation;
 for(int Reds=1;Reds<=5;++Reds){
  const double Duration=Reds==5?1.25:1;const auto Cue=Sample(Reds,.4,Duration,false);
  TestEqual(TEXT("Each authoritative red light presents the next descending number"),Cue.Number,6-Reds);
  TestTrue(TEXT("Number fades in, remains readable and fades out"),Sample(Reds,0,Duration,false).Alpha==0&&Cue.Alpha>.9&&Sample(Reds,Duration,Duration,false).Alpha==0);
 }
 TestTrue(TEXT("Pre-grid and reset have no stale numeral"),Sample(0,.4,1,false).Alpha==0&&Sample(1,-1,1,false).Alpha==0);
 TestEqual(TEXT("START is selected only from the lights-out state"),Sample(0,.4,1.1,true).Number,0);
 TestTrue(TEXT("START clears after its fade"),Sample(0,1.1,1.1,true).Alpha==0);
 return true;
}
#endif

