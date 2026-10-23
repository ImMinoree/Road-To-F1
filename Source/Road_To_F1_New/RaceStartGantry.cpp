#include "RaceStartGantry.h"
#include "ProofPawn.h"
#include "Components/SceneComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/Canvas.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
ARaceStartGantry::ARaceStartGantry(){
 RootComponent=CreateDefaultSubobject<USceneComponent>(TEXT("Mount"));
 Housings=CreateDefaultSubobject<UInstancedStaticMeshComponent>(TEXT("FiveHousings"));Housings->SetupAttachment(RootComponent);
 Housings->SetRelativeLocation(FVector(0,0,560));Housings->SetCollisionProfileName(TEXT("NoCollision"));
 Frame=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("MountFrame"));Frame->SetupAttachment(Housings);Frame->SetCollisionProfileName(TEXT("NoCollision"));
 for(int32 I=0;I<5;++I){auto* C=CreateDefaultSubobject<UStaticMeshComponent>(*FString::Printf(TEXT("RedLens%d"),I+1));C->SetupAttachment(RootComponent);C->SetRelativeLocation(FVector(0,(I-2)*95.f,560));C->SetCollisionProfileName(TEXT("NoCollision"));C->SetCastShadow(false);Lenses.Add(C);}
 SetActorEnableCollision(false);
}
void ARaceStartGantry::OnConstruction(const FTransform& T){Super::OnConstruction(T);RefreshDisplay();}
void ARaceStartGantry::BeginPlay(){Super::BeginPlay();RefreshDisplay();SetRedLightCount(0);}
void ARaceStartGantry::RefreshDisplay(){
 Housings->SetStaticMesh(HousingMesh);Housings->ClearInstances();
 for(int32 I=0;I<5;++I)Housings->AddInstance(FTransform(FVector(0,(I-2)*95.f,0)));
 Frame->SetStaticMesh(FrameMesh);LensInstances.Reset();
 for(auto C:Lenses){C->SetStaticMesh(LensMesh);C->SetMaterial(0,LensMaterial);LensInstances.Add(LensMaterial?C->CreateDynamicMaterialInstance(0,LensMaterial):nullptr);}
 SetRedLightCount(PreviewRedLights);
}
void ARaceStartGantry::SetRedLightCount(int32 Count){
 Count=FMath::Clamp(Count,0,5);
 for(int32 I=0;I<LensInstances.Num();++I)if(LensInstances[I])LensInstances[I]->SetScalarParameterValue(TEXT("Emission"),I<Count?LitEmission:.015f);
}
void ARaceStartGantry::PlayCue(bool bLightsOut){if(bEnableAudio)if(USoundBase* S=bLightsOut?LightsOutSound.Get():CountdownSound.Get())UGameplayStatics::PlaySound2D(this,S,.18f);}
void ARaceStartHUD::DrawHUD(){
 Super::DrawHUD();auto* GM=GetWorld()->GetAuthGameMode<AProofGameMode>();
 if(Canvas&&GM&&GM->bShowLightsOutCue&&GM->RaceStartWorldSeconds>=0&&GM->GetRaceElapsedSeconds()<1.1f){
  const FString Text=TEXT("LIGHTS OUT");float W,H;GetTextSize(Text,W,H,GEngine->GetMediumFont(),1.2f);DrawText(Text,FLinearColor(.9f,.9f,.86f), (Canvas->SizeX-W)*.5f,Canvas->SizeY*.75f,GEngine->GetMediumFont(),1.2f);
 }
}

