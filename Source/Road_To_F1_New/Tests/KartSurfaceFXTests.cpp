#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "Engine/StaticMesh.h"
#include "../KartSurfaceFX.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Engine/StaticMeshActor.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SphereComponent.h"
#include "Components/InstancedStaticMeshComponent.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FKartSurfaceFXTest,"RoadToF1.SurfaceFX.ContactAndPooling",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FKartSurfaceFXTest::RunTest(const FString&){
 TestTrue(TEXT("Grass classification"),UKartSurfaceFX::ClassifyNames(TEXT("SM_DK_grassdark"))==EKartLooseSurface::Grass);
 TestTrue(TEXT("Asphalt overrides underlying grass"),UKartSurfaceFX::ClassifyNames(TEXT("grass SurfaceAsphalt"))==EKartLooseSurface::None);
 TestTrue(TEXT("Sand classification"),UKartSurfaceFX::ClassifyNames(TEXT("M_sand"))==EKartLooseSurface::Dirt);
 TestTrue(TEXT("Unknown is quiet"),UKartSurfaceFX::ClassifyNames(TEXT("Metal"))==EKartLooseSurface::None);
 const auto Init=UWorld::InitializationValues().AllowAudioPlayback(false).CreatePhysicsScene(true).CreateNavigation(false).CreateAISystem(false).ShouldSimulatePhysics(false).SetTransactional(false);
 UWorld* World=UWorld::CreateWorld(EWorldType::Game,false,FName(TEXT("SurfaceFXTestWorld")),nullptr,true,ERHIFeatureLevel::Num,&Init);
 FWorldContext& Context=GEngine->CreateNewWorldContext(EWorldType::Game);Context.SetCurrentWorld(World);World->InitializeActorsForPlay(FURL());
 auto* Ground=World->SpawnActor<AStaticMeshActor>();Ground->GetStaticMeshComponent()->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Cube.Cube")));Ground->SetActorScale3D(FVector(20,10,.2));Ground->SetActorLocation(FVector(0,0,-10));Ground->GetStaticMeshComponent()->SetCollisionProfileName(TEXT("BlockAll"));Ground->Tags={TEXT("SurfaceGrass")};
 auto* Kart=World->SpawnActor<AActor>();auto* Root=NewObject<USphereComponent>(Kart);Kart->SetRootComponent(Root);Kart->AddInstanceComponent(Root);Root->SetCollisionEnabled(ECollisionEnabled::NoCollision);Root->RegisterComponent();Kart->SetActorLocation(FVector(0,0,31));
 auto* FX=NewObject<UKartSurfaceFX>(Kart);Kart->AddInstanceComponent(FX);FX->RegisterComponent();FX->BeginPlay();
 auto Advance=[&](int32 Frames,FVector Step){for(int32 I=0;I<Frames;++I){Kart->AddActorWorldOffset(Step);const FTransform Before=Kart->GetActorTransform();FX->TickComponent(1.f/60,LEVELTICK_All,nullptr);TestTrue(TEXT("Cosmetic tick never moves owner"),Before.Equals(Kart->GetActorTransform()));}};
 Advance(20,FVector(6,0,0));TestEqual(TEXT("Two wheels on grass"),FX->EmittingWheels,2);TestTrue(TEXT("Grass emits particles"),FX->TotalEmitted>0);TestTrue(TEXT("Pool capped"),FX->LiveParticles<=96);
 const int32 MovingTotal=FX->TotalEmitted;Advance(80,FVector::ZeroVector);TestEqual(TEXT("Stationary emission stops"),FX->TotalEmitted,MovingTotal);TestEqual(TEXT("All remnants expire"),FX->LiveParticles,0);
 Ground->Tags={TEXT("SurfaceAsphalt")};Advance(15,FVector(6,0,0));TestEqual(TEXT("Asphalt emits nothing"),FX->TotalEmitted,MovingTotal);
 Ground->Tags={TEXT("SurfaceDirt")};Advance(15,FVector(-6,0,0));TestEqual(TEXT("Reverse movement on soil emits"),FX->EmittingWheels,2);TestTrue(TEXT("Soil emitted"),FX->TotalEmitted>MovingTotal);
 Kart->SetActorLocation(FVector(0,530,31));Advance(1,FVector::ZeroVector);Advance(10,FVector(6,0,0));TestEqual(TEXT("Split surface, one wheel only"),FX->EmittingWheels,1);
 Kart->SetActorLocation(FVector(0,0,231));Advance(10,FVector(6,0,0));TestEqual(TEXT("Airborne produces no emission"),FX->EmittingWheels,0);
 FX->bEnabled=false;const int32 DisabledTotal=FX->TotalEmitted;Kart->SetActorLocation(FVector(0,0,31));Advance(10,FVector(6,0,0));TestEqual(TEXT("Disable switch"),FX->TotalEmitted,DisabledTotal);
 TArray<UInstancedStaticMeshComponent*> Pools;Kart->GetComponents(Pools);TestEqual(TEXT("Only three shared pools"),Pools.Num(),3);
 for(auto* P:Pools){TestEqual(TEXT("Fixed 32 slots per pool"),P->GetInstanceCount(),32);TestTrue(TEXT("No particle collision"),P->GetCollisionEnabled()==ECollisionEnabled::NoCollision);TestFalse(TEXT("No replication"),P->GetIsReplicated());}
 GEngine->DestroyWorldContext(World);World->DestroyWorld(false);return true;
}
#endif
