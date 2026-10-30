#include "KartSpeedLines.h"
#include "KartSpeedLinesMath.h"
#include "KartNavigationMap.h"
#include "ProofPawn.h"
#include "LocalKartDriverVisuals.h"
#include "GameFramework/HUD.h"
#include "GameFramework/PlayerController.h"
#include "Camera/CameraComponent.h"
#include "Components/InputComponent.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "UObject/ConstructorHelpers.h"
UKartSpeedLines::UKartSpeedLines(){PrimaryComponentTick.bCanEverTick=true;PrimaryComponentTick.TickGroup=TG_PostUpdateWork;}
void UKartSpeedLines::BeginPlay(){
 Super::BeginPlay();Material=LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/RoadToF1/SpeedEffects/M_KartAnimeSpeedLines.M_KartAnimeSpeedLines"));
 if(auto* H=Cast<AHUD>(GetOwner()))if(auto* P=H->GetOwningPlayerController()){H->EnableInput(P);if(H->InputComponent)H->InputComponent->BindKey(EKeys::F3,IE_Pressed,this,&UKartSpeedLines::ToggleSpeedVisuals).bExecuteWhenPaused=true;}
}
void UKartSpeedLines::Detach(){if(Camera.IsValid()&&MaterialInstance)Camera->RemoveBlendable(MaterialInstance);Camera.Reset();MaterialInstance=nullptr;SmoothedStrength=0;}
void UKartSpeedLines::ToggleSpeedVisuals(){
 bEnabled=!bEnabled;
 if(ExistingVisuals.IsValid()){
  if(!bEnabled){bSavedExistingEnabled=ExistingVisuals->bSpeedEffectsEnabled;ExistingVisuals->bSpeedEffectsEnabled=false;bOwnsExistingToggle=true;}
  else if(bOwnsExistingToggle){ExistingVisuals->bSpeedEffectsEnabled=bSavedExistingEnabled;bOwnsExistingToggle=false;}
 }
 if(!bEnabled){SmoothedStrength=0;if(MaterialInstance)MaterialInstance->SetScalarParameterValue(TEXT("LineStrength"),0);}
}
void UKartSpeedLines::TickComponent(float Dt,ELevelTick Type,FActorComponentTickFunction* Function){
 Super::TickComponent(Dt,Type,Function);auto* H=Cast<AHUD>(GetOwner());auto* PC=H?H->GetOwningPlayerController():nullptr;auto* Pawn=PC?Cast<AProofPawn>(PC->GetPawn()):nullptr;
 UCameraComponent* Eye=nullptr;if(Pawn&&PC->IsLocalController()){TArray<UCameraComponent*> Cameras;Pawn->GetComponents(Cameras);for(auto* C:Cameras)if(C->GetName()==TEXT("DriverEye"))Eye=C;ExistingVisuals=Pawn->FindComponentByClass<ULocalKartDriverVisuals>();}
 if(Camera.Get()!=Eye){Detach();Camera=Eye;if(Eye&&Material){MaterialInstance=UMaterialInstanceDynamic::Create(Material,this);Eye->AddOrUpdateBlendable(MaterialInstance,1);}}
 if(!MaterialInstance||!Pawn||!Eye)return;
 const auto* Map=H->FindComponentByClass<UKartNavigationMap>();const bool Visible=bEnabled&&Eye->IsActive()&&!Pawn->IsThirdPersonView()&&!(Map&&Map->IsMapOpen());
 ActualSpeedKmh=Pawn->GetVelocity().Size2D()*.036f;
 const float Target=Visible?KartSpeedLines::Strength(ActualSpeedKmh,StartKmh,NoticeableKmh,StrongKmh,FullKmh):0;
 SmoothedStrength=Visible&&ActualSpeedKmh>StartKmh?KartSpeedLines::Smooth(SmoothedStrength,Target,Dt):0;
 PhaseSeconds+=FMath::Max(0.f,Dt);
 MaterialInstance->SetScalarParameterValue(TEXT("LineStrength"),SmoothedStrength*FMath::Clamp(Intensity,0.f,2.f));
 MaterialInstance->SetScalarParameterValue(TEXT("LineCount"),FMath::Clamp(StreakCount,8,160));
 MaterialInstance->SetScalarParameterValue(TEXT("Thickness"),FMath::Clamp(ThicknessPixels,.3f,3.f));
 MaterialInstance->SetScalarParameterValue(TEXT("LineOpacity"),FMath::Clamp(Opacity,0.f,.7f));
 MaterialInstance->SetScalarParameterValue(TEXT("AnimationTime"),PhaseSeconds*FMath::Clamp(AnimationSpeed,.1f,3.f));
 MaterialInstance->SetScalarParameterValue(TEXT("Blur"),FMath::Clamp(PeripheralBlur,0.f,1.f));
 MaterialInstance->SetVectorParameterValue(TEXT("VanishingPoint"),FLinearColor(FMath::Clamp(float(VanishingPoint.X),.25f,.75f),FMath::Clamp(float(VanishingPoint.Y),.2f,.6f),0,0));
}
void UKartSpeedLines::EndPlay(const EEndPlayReason::Type Reason){if(bOwnsExistingToggle&&ExistingVisuals.IsValid())ExistingVisuals->bSpeedEffectsEnabled=bSavedExistingEnabled;Detach();Super::EndPlay(Reason);}
