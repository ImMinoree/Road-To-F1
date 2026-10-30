#include "KartRaceAwareness.h"
#include "KartRaceAwarenessMath.h"
#include "KartNavigationMath.h"
#include "ProofPawn.h"
#include "TrackRacingAI.h"
#include "GameFramework/HUD.h"
#include "GameFramework/PlayerController.h"
#include "Components/InputComponent.h"
#include "Components/SceneCaptureComponent2D.h"
#include "Camera/CameraComponent.h"
#include "Engine/TextureRenderTarget2D.h"
#include "Engine/Canvas.h"
#include "EngineUtils.h"
#include "CanvasItem.h"
#include "Fonts/SlateFontInfo.h"
#include "UObject/ConstructorHelpers.h"

namespace {
void Panel(UCanvas* C,FVector2D P,FVector2D S,FLinearColor Color){FCanvasTileItem I(P,S,Color);I.BlendMode=SE_BLEND_Translucent;C->DrawItem(I);}
void Stroke(UCanvas* C,FVector2D A,FVector2D B,FLinearColor Color,float W=2){FCanvasLineItem I(A,B);I.SetColor(Color);I.LineThickness=W;C->DrawItem(I);}
void Label(UCanvas* C,UFont* F,FVector2D P,const FString& Text,float Size,FLinearColor Color){if(!F)return;FCanvasTextItem I(P,FText::FromString(Text),FSlateFontInfo(F,Size,TEXT("Bold")),Color);C->DrawItem(I);}
}
UKartRaceAwareness::UKartRaceAwareness(){
 PrimaryComponentTick.bCanEverTick=false;
 static ConstructorHelpers::FObjectFinder<UTrackEdgeRoute> R(TEXT("/Game/RoadToF1/RacingAI/DA_DesertTrackEdges.DA_DesertTrackEdges"));Route=R.Object;
}
void UKartRaceAwareness::BeginPlay(){
 Super::BeginPlay();auto* HUD=Cast<AHUD>(GetOwner());auto* PC=HUD?HUD->GetOwningPlayerController():nullptr;
 if(!PC||!PC->IsLocalController())return;
 HUD->EnableInput(PC);auto* Input=HUD->InputComponent.Get();if(!Input)return;
 Input->BindKey(EKeys::C,IE_Pressed,this,&UKartRaceAwareness::BeginLookBack);
 Input->BindKey(EKeys::C,IE_Released,this,&UKartRaceAwareness::EndLookBack).bExecuteWhenPaused=true;
 Input->BindKey(EKeys::F2,IE_Pressed,this,&UKartRaceAwareness::ToggleMirror).bExecuteWhenPaused=true;
}
void UKartRaceAwareness::SelectCamera(bool Rear){
 if(!Driver.IsValid())return;
 TArray<UCameraComponent*> Cameras;Driver->GetComponents(Cameras);
 const FString Wanted=Driver->IsThirdPersonView()?TEXT("ChaseCamera"):TEXT("DriverEye");
 for(auto* C:Cameras)C->SetActive(Rear?C==BackCamera:C->GetName()==Wanted);
}
void UKartRaceAwareness::BeginLookBack(){if(!bSuppressed&&BackCamera&&Driver.IsValid()){bLookingBack=true;SelectCamera(true);}}
void UKartRaceAwareness::EndLookBack(){if(bLookingBack){bLookingBack=false;SelectCamera(false);}}
void UKartRaceAwareness::AttachDriver(AProofPawn* Pawn){
 EndLookBack();if(Capture)Capture->DestroyComponent();if(BackCamera)BackCamera->DestroyComponent();Capture=nullptr;BackCamera=nullptr;Driver=Pawn;
 if(!Pawn)return;
 MirrorTarget=NewObject<UTextureRenderTarget2D>(this);MirrorTarget->RenderTargetFormat=RTF_RGBA8;MirrorTarget->ClearColor=FLinearColor::Black;MirrorTarget->InitAutoFormat(640,160);
 Capture=NewObject<USceneCaptureComponent2D>(Pawn,TEXT("KartRearMirror"));Capture->SetupAttachment(Pawn->GetRootComponent());Capture->SetRelativeLocation(FVector(-125,0,88));Capture->SetRelativeRotation(FRotator(-4,180,0));
 Capture->FOVAngle=95;Capture->TextureTarget=MirrorTarget;Capture->CaptureSource=SCS_FinalColorLDR;Capture->bCaptureEveryFrame=false;Capture->bCaptureOnMovement=false;Capture->bAlwaysPersistRenderingState=true;Capture->MaxViewDistanceOverride=15000;Capture->LODDistanceFactor=2;Capture->ShowFlags.SetMotionBlur(false);Capture->ShowFlags.SetDepthOfField(false);Capture->HideActorComponents(Pawn,true);Capture->RegisterComponent();
 BackCamera=NewObject<UCameraComponent>(Pawn,TEXT("KartLookBackCamera"));BackCamera->SetAutoActivate(false);BackCamera->SetupAttachment(Pawn->GetRootComponent());BackCamera->SetRelativeLocation(FVector(-125,0,76));BackCamera->SetRelativeRotation(FRotator(-4,180,0));BackCamera->FieldOfView=95;BackCamera->PostProcessSettings.bOverride_MotionBlurAmount=true;BackCamera->PostProcessSettings.MotionBlurAmount=0;BackCamera->RegisterComponent();BackCamera->Deactivate();LastCapture=-1;
}
void UKartRaceAwareness::EndPlay(const EEndPlayReason::Type Reason){AttachDriver(nullptr);MirrorTarget=nullptr;Super::EndPlay(Reason);}
void UKartRaceAwareness::Draw(UCanvas* C,UFont* Font,bool Suppressed){
 bSuppressed=Suppressed;auto* HUD=Cast<AHUD>(GetOwner());auto* PC=HUD?HUD->GetOwningPlayerController():nullptr;auto* Pawn=PC?Cast<AProofPawn>(PC->GetPawn()):nullptr;
 if(Pawn!=Driver.Get())AttachDriver(Pawn);
 if(Suppressed){EndLookBack();return;}if(!C||!Pawn)return;
 if(bLookingBack)SelectCamera(true);
 const float S=FMath::Clamp(C->SizeY/1080.f,.65f,1.4f);
 if(bMirrorEnabled&&!bLookingBack&&Capture){
  const double Now=GetWorld()->GetRealTimeSeconds();if(Now-LastCapture>=1./FMath::Clamp(MirrorHz,1.f,30.f)){Capture->CaptureScene();LastCapture=Now;++RearCaptureCount;}
  const FVector2D Size(480*S,120*S),P((C->SizeX-Size.X)*0.5f,12*S);
  Panel(C,P-FVector2D(3,3),Size+FVector2D(6,6),FLinearColor(0.015f,0.018f,0.02f,0.95f));
  FCanvasTileItem I(P,MirrorTarget->GetResource(),Size,FVector2D(1,0),FVector2D(0,1),FLinearColor::White);I.BlendMode=SE_BLEND_Opaque;C->DrawItem(I);
  Label(C,Font,P+FVector2D(6,4),TEXT("REAR  |  F2"),12*S,FLinearColor(0.8f,0.85f,0.86f));
 }
 TrackedOpponentCount=0;const auto OwnerRoute=Route?KartNavigation::Nearest(Route->Center,FVector2D(Pawn->GetActorLocation())):KartNavigation::FRoutePoint();
 int32 SectorRisk[8]={-1,-1,-1,-1,-1,-1,-1,-1};
 for(TActorIterator<AProofPawn> It(GetWorld());It;++It){
  if(*It==Pawn)continue;const FVector D=It->GetActorLocation()-Pawn->GetActorLocation();if(D.SizeSquared2D()>2500.*2500.)continue;
  double Gap=0;if(Route){const auto Q=KartNavigation::Nearest(Route->Center,FVector2D(It->GetActorLocation()));Gap=FMath::Min(KartNavigation::ForwardDistance(Route->Center,OwnerRoute,Q),KartNavigation::ForwardDistance(Route->Center,Q,OwnerRoute));}
  const FVector Local=Pawn->GetActorQuat().UnrotateVector(D),V=Pawn->GetActorQuat().UnrotateVector(It->GetVelocity()-Pawn->GetVelocity());const int32 Risk=KartAwareness::Risk(Local,V,Gap);if(Risk<0)continue;++TrackedOpponentCount;
  if(Local.Size2D()<900&&(Risk>0||FMath::Abs(Local.Y)>100||Local.X<-100)){const double Bearing=FMath::Atan2(Local.Y,Local.X);const int32 Sector=(FMath::RoundToInt(Bearing/(PI/4))+8)%8;SectorRisk[Sector]=FMath::Max(SectorRisk[Sector],Risk+1);}
 }
 const double WarningTime=GetWorld()->GetRealTimeSeconds();
 for(int32 I=0;I<8;++I){
  if(SectorRisk[I]>0){WarningUntil[I]=WarningTime+0.25f;WarningRisk[I]=SectorRisk[I];}
  if(WarningUntil[I]<=WarningTime)continue;
  const double A=I*PI/4;const FVector2D Direction(FMath::Sin(A),-FMath::Cos(A)),Side(-Direction.Y,Direction.X);const FVector2D Tip=FVector2D(C->SizeX*0.5f,C->SizeY*0.53f)+FVector2D(Direction.X*C->SizeX*0.26f,Direction.Y*C->SizeY*0.23f);
  auto Color=WarningRisk[I]==3?FLinearColor(1.f,.1f,.045f):WarningRisk[I]==2?FLinearColor(1.f,.55f,.05f):FLinearColor::White;Color.A=FMath::Clamp(float((WarningUntil[I]-WarningTime)/0.15f),0.f,1.f);
  Stroke(C,Tip-Direction*13*S+Side*7*S,Tip,Color,4*S);Stroke(C,Tip,Tip-Direction*13*S-Side*7*S,Color,4*S);
 }
 if(bLookingBack)Label(C,Font,FVector2D(C->SizeX*0.5f-45*S,18*S),TEXT("LOOKING BACK"),14*S,FLinearColor::White);
}
