#include "RaceStartGantry.h"
#include "ProofPawn.h"
#include "RaceCountdownPresentation.h"
#include "KartNavigationMap.h"
#include "KartRaceAwareness.h"
#include "CanvasItem.h"
#include "Fonts/SlateFontInfo.h"
#include "Engine/Font.h"
#include "UObject/ConstructorHelpers.h"
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
ARaceStartHUD::ARaceStartHUD(){
 static ConstructorHelpers::FObjectFinder<UFont> Font(TEXT("/Engine/EngineFonts/Roboto.Roboto"));
 CountdownFont=Font.Object;
 NavigationMap=CreateDefaultSubobject<UKartNavigationMap>(TEXT("NavigationMap"));
 RaceAwareness=CreateDefaultSubobject<UKartRaceAwareness>(TEXT("RaceAwareness"));
}
void ARaceStartHUD::DrawHUD(){
 Super::DrawHUD();
 if(RaceAwareness)RaceAwareness->Draw(Canvas,CountdownFont,NavigationMap&&NavigationMap->IsMapOpen());
 if(NavigationMap){NavigationMap->Draw(Canvas,CountdownFont);if(NavigationMap->IsMapOpen())return;}
 auto* GM=GetWorld()->GetAuthGameMode<AProofGameMode>();
 if(!Canvas||!GM||!GEngine||!CountdownFont||!GM->bShowLightsOutCue)return;
 const bool Started=GM->RaceStartWorldSeconds>=0;
 if(!Started&&(!GM->IsStartGateClosed()||GM->CountdownCueWorldSeconds<0))return;
 const double Age=Started?GM->GetRaceElapsedSeconds():GetWorld()->GetTimeSeconds()-GM->CountdownCueWorldSeconds;
 const double Duration=Started?1.35:FMath::Max(.1f,GM->RedLightCount==5?GM->AllRedHold:GM->RedInterval);
 const auto Cue=RaceCountdownPresentation::Sample(GM->RedLightCount,Age,Duration,Started);
 if(Cue.Alpha<=0)return;
 const FString Text=Cue.Number==0?TEXT("START"):FString::FromInt(Cue.Number);
 // Rasterize at the displayed size, rather than enlarging the small engine bitmap font.
 const float FontPixels=FMath::Min(Canvas->SizeY*(Started?.12f:.24f),Canvas->SizeX*(Started?.18f:.72f));
 // Canvas requires the UFont asset as well as the runtime typeface/size.
 const FSlateFontInfo Font(CountdownFont.Get(),FMath::Max(12.f,FontPixels*1.5f),TEXT("Bold"));
 FLinearColor Color=FLinearColor::FromSRGBColor(Started?FColor(133,184,146):FColor(225,214,194));
 Color.A=float(Cue.Alpha);
 FCanvasTextItem Item(FVector2D(Canvas->SizeX*.5f,Canvas->SizeY*.43f),FText::FromString(Text),Font,Color);
 Item.Scale=FVector2D(1.f/1.5f);Item.bCentreX=true;Item.bCentreY=true;
 Item.bOutlined=false;
 Item.EnableShadow(FLinearColor(0,0,0,float(Cue.Alpha)*.25f),FVector2D(1,2));Canvas->DrawItem(Item);
}
