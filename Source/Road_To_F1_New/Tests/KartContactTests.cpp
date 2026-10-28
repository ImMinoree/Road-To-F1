#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../KartTireModel.h"
#include "../KartTireDynamics.h"
#include "../ProofPawn.h"
#include "Components/BoxComponent.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "HAL/FileManager.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FKartContactImpulseTest,"RoadToF1.Contact.ImpulseAndSteering",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FKartContactImpulseTest::RunTest(const FString&){
 using namespace KartDynamics;Parameters P;
 auto Energy=[&](const State& S){return .5*P.Mass*(S.U*S.U+S.V*S.V)+.5*P.Inertia*S.R*S.R;};
 for(int Case=0;Case<3;++Case){State A,B;A.U=Case==0?1:13;B.U=Case==0?0:4;
  const double BX=Case==2?.5:1.8,BY=Case==2?1.2:0,NX=Case==2?0:-1,NY=Case==2?-1:0;
  if(Case==2){A.V=2;B.V=0;}
  const double E=Energy(A)+Energy(B),Momentum=P.Mass*(A.U+B.U),SideMomentum=P.Mass*(A.V+B.V);
  const double J=ResolveContact(A,P,&B,&P,0,0,BX,BY,BX*.5,BY*.5,NX,NY);
  TestTrue(TEXT("Rear/side impact transfers positive bounded impulse"),J>0&&J<3000);
  TestTrue(TEXT("Equal and opposite impulses conserve planar momentum"),std::abs(P.Mass*(A.U+B.U)-Momentum)<1e-8&&std::abs(P.Mass*(A.V+B.V)-SideMomentum)<1e-8);
  TestTrue(TEXT("Contact never creates kinetic energy"),Energy(A)+Energy(B)<=E+1e-8);
  for(int K=0;K<100;++K)ResolveContact(A,P,&B,&P,0,0,BX,BY,BX*.5,BY*.5,NX,NY);
  TestTrue(TEXT("Consecutive contacts remain finite and dissipative"),std::isfinite(A.R)&&std::isfinite(B.R)&&Energy(A)+Energy(B)<=E+1e-8);
 }
 State Wall;Wall.U=13;const double E=Energy(Wall);ResolveContact(Wall,P,nullptr,nullptr,0,0,0,0,.9,0,-1,0);
 TestTrue(TEXT("Centered barrier impact does not invent yaw or energy"),std::abs(Wall.R)<1e-9&&Energy(Wall)<E);
 State Steering;Steering.U=12;UpdateSteering(Steering,P,1,StepSeconds);
 TestTrue(TEXT("Sudden keyboard input is rate limited by the real steering rack"),Steering.Steer<=P.SteerRate*StepSeconds+1e-9);
 for(int K=0;K<240;++K)UpdateSteering(Steering,P,0,StepSeconds);
 TestTrue(TEXT("Steering release returns to center"),std::abs(Steering.Steer)<1e-9);
 TestTrue(TEXT("High speed reduces available rack angle"),MaxSteer(P,13)<MaxSteer(P,2));
 return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FKartContactWorldTest,"RoadToF1.Contact.SweepsKerbsAndTraffic",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FKartContactWorldTest::RunTest(const FString&){
 const UWorld::InitializationValues Init=UWorld::InitializationValues().AllowAudioPlayback(false).CreatePhysicsScene(true).CreateNavigation(false).CreateAISystem(false).ShouldSimulatePhysics(false).SetTransactional(false);
 UWorld* W=UWorld::CreateWorld(EWorldType::Game,false,FName(TEXT("KartContactWorld")),nullptr,true,ERHIFeatureLevel::Num,&Init);
 FWorldContext& C=GEngine->CreateNewWorldContext(EWorldType::Game);C.SetCurrentWorld(W);W->InitializeActorsForPlay(FURL());
 auto Box=[&](FVector Pos,FVector Extent){auto* A=W->SpawnActor<AActor>();auto* B=NewObject<UBoxComponent>(A);A->SetRootComponent(B);A->AddInstanceComponent(B);B->SetBoxExtent(Extent);B->SetCollisionObjectType(ECC_WorldStatic);B->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);B->SetCollisionResponseToAllChannels(ECR_Block);B->RegisterComponent();A->SetActorLocation(Pos);return A;};
 Box(FVector(0,0,-50),FVector(20000,20000,50));
 FActorSpawnParameters Spawn;Spawn.SpawnCollisionHandlingOverride=ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
 auto Kart=[&](FVector Pos){auto* A=W->SpawnActor<AProofPawn>(AProofPawn::StaticClass(),Pos,FRotator::ZeroRotator,Spawn);A->AutoPossessPlayer=EAutoReceiveInput::Disabled;A->bUseTireDynamics=true;A->GetTireDynamics()->ResetMotion();return A;};
 auto* A=Kart(FVector(0,0,31));auto* B=Kart(FVector(950,0,31));auto* DA=A->GetTireDynamics();auto* DB=B->GetTireDynamics();
 for(int K=0;K<600;++K){DA->Simulate(1.f/120,1,0,false);DB->Simulate(1.f/120,0,0,false);}
 TestTrue(TEXT("Rear-ended kart receives momentum through the actual swept contact"),B->GetActorLocation().X>1100&&DB->MaximumContactImpulseNs>1);
 TestTrue(TEXT("Full chassis boxes do not pass through each other"),B->GetActorLocation().X-A->GetActorLocation().X>175);
 const double RearImpulse=DB->MaximumContactImpulseNs;
 B->SetActorEnableCollision(false);A->StageForRace(FTransform(FRotator::ZeroRotator,FVector(0,1000,31)));
 Box(FVector(1200,1000,100),FVector(10,500,100));
 for(int K=0;K<960;++K)DA->Simulate(1.f/120,1,0,false);
 TestTrue(TEXT("Repeated throttle against barrier stays finite without tunneling or launch"),A->GetActorLocation().X<1105&&FMath::Abs(A->GetActorLocation().Z-31)<1&&FMath::IsFinite(DA->Telemetry.YawRateDegrees));
 A->StageForRace(FTransform(FRotator::ZeroRotator,FVector(0,2500,31)));
 Box(FVector(600,2500,4),FVector(80,300,4));
 double MaxZ=31,MaxJump=0;FVector Previous=A->GetActorLocation();bool Grounded=true;
 for(int K=0;K<480;++K){DA->Simulate(1.f/120,.65f,0,false);FVector Pos=A->GetActorLocation();MaxZ=FMath::Max(MaxZ,Pos.Z);MaxJump=FMath::Max(MaxJump,FMath::Abs(Pos.Z-Previous.Z));Previous=Pos;Grounded&=FMath::IsFinite(Pos.Z)&&Pos.Z>15&&Pos.Z<60;}
 TestTrue(TEXT("Kerb traversal responds vertically without a teleport or launch"),Grounded&&A->GetActorLocation().X>900&&MaxZ>32&&MaxJump<3);
 A->StageForRace(FTransform(FRotator::ZeroRotator,FVector(0,4000,31)));
 Box(FVector(9000,4000,100),FVector(10,500,100));double PeakSpeed=0;
 for(int K=0;K<1800;++K){DA->Simulate(1.f/120,1,0,false);PeakSpeed=FMath::Max(PeakSpeed,double(DA->Telemetry.LongitudinalSpeedMps));}
 TestTrue(TEXT("Near-top-speed barrier hit is swept and settles without launch or spurious yaw"),PeakSpeed>12&&A->GetActorLocation().X<8905&&FMath::Abs(A->GetActorLocation().Z-31)<1&&FMath::Abs(DA->Telemetry.YawRateDegrees)<1&&DA->MaximumContactImpulseNs>1000);
 const double HighSpeedImpulse=DA->MaximumContactImpulseNs;
 A->StageForRace(FTransform(FRotator::ZeroRotator,FVector(0,6000,31)));
 B->SetActorEnableCollision(true);B->StageForRace(FTransform(FRotator(0,90,0),FVector(1000,6000,31)));
 for(int K=0;K<600;++K){DA->Simulate(1.f/120,1,0,false);DB->Simulate(1.f/120,0,0,false);}
 TestTrue(TEXT("Kart side contact transfers momentum without tunneling or launch"),DB->MaximumContactImpulseNs>1&&B->GetActorLocation().X>1100&&FMath::Abs(B->GetActorLocation().Z-31)<1&&FMath::IsFinite(DB->Telemetry.YawRateDegrees));
 const double SideImpulse=DB->MaximumContactImpulseNs;B->SetActorEnableCollision(false);
 Box(FVector(1200,8000,100),FVector(10,500,100));FVector Reference;double FrameError=0;
 for(int32 Rate:{30,60,120}){
  A->StageForRace(FTransform(FRotator::ZeroRotator,FVector(0,8000,31)));
  for(int K=0;K<Rate*6;++K)DA->Simulate(1.f/Rate,1,0,false);
  if(Rate==30)Reference=A->GetActorLocation();else FrameError=FMath::Max(FrameError,FVector::Dist(Reference,A->GetActorLocation()));
 }
 TestTrue(TEXT("Actual component sweep/contact results agree across 30/60/120 Hz"),FrameError<.1);
 FString Result=FString::Printf(TEXT("{\"rear_contact_impulse_ns\":%.4f,\"side_contact_impulse_ns\":%.4f,\"barrier_entry_mps\":%.4f,\"barrier_impulse_ns\":%.4f,\"kerb_peak_z_cm\":%.4f,\"maximum_vertical_step_cm\":%.4f,\"max_penetration_cm\":%.4f,\"frame_group_position_error_cm\":%.6f}"),RearImpulse,SideImpulse,PeakSpeed,HighSpeedImpulse,MaxZ,MaxJump,DA->MaximumPenetrationCm,FrameError);
 const FString Dir=FPaths::ProjectDir()/TEXT("Evidence/HandlingRefinement");IFileManager::Get().MakeDirectory(*Dir,true);FFileHelper::SaveStringToFile(Result,*(Dir/TEXT("world_contact_metrics.json")));
 AddInfo(FString::Printf(TEXT("High-speed barrier: %.3f m/s, %.3f N s; side-contact impulse: %.3f N s"),PeakSpeed,HighSpeedImpulse,DB->MaximumContactImpulseNs));
 GEngine->DestroyWorldContext(W);W->DestroyWorld(false);return true;
}
#endif
