#include "KartNavigationMap.h"
#include "TrackRacingAI.h"
#include "ProofPawn.h"
#include "Engine/Canvas.h"
#include "Engine/World.h"
#include "Engine/Font.h"
#include "CanvasItem.h"
#include "RenderUtils.h"
#include "Fonts/SlateFontInfo.h"
#include "GameFramework/HUD.h"
#include "GameFramework/PlayerController.h"
#include "Components/InputComponent.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "EngineUtils.h"
#include "InputCoreTypes.h"
#include "Kismet/GameplayStatics.h"
#include "UObject/ConstructorHelpers.h"

namespace {
FLinearColor Ink(uint8 R,uint8 G,uint8 B,float A=1){auto C=FLinearColor::FromSRGBColor(FColor(R,G,B));C.A=A;return C;}
const FLinearColor Ground=Ink(36,39,39),Road=Ink(174,180,176),Edge=Ink(214,219,215),Purple=Ink(183,117,230),PlayerColor=Ink(235,42,46),White=Ink(255,255,255),Muted=Ink(150,163,158);
void NavFillRect(UCanvas* C,FVector2D P,FVector2D Size,FLinearColor Color){FCanvasTileItem I(P,Size,Color);I.BlendMode=SE_BLEND_Translucent;C->DrawItem(I);}
void Line(UCanvas* C,FVector2D A,FVector2D B,FLinearColor Color,float Width=1){FCanvasLineItem I(A,B);I.SetColor(Color);I.LineThickness=Width;C->DrawItem(I);}
void Label(UCanvas* C,UFont* Font,const FString& Text,FVector2D P,float Size,FLinearColor Color,bool Center=false){FSlateFontInfo Info(Font,FMath::Max(10.f,Size),TEXT("Bold"));FCanvasTextItem I(P,FText::FromString(Text),Info,Color);I.bCentreX=Center;I.bCentreY=Center;C->DrawItem(I);}
void Triangle(TArray<FCanvasUVTri>& Out,FVector2D A,FVector2D B,FVector2D C,FLinearColor Color){FCanvasUVTri T;T.V0_Pos=A;T.V1_Pos=B;T.V2_Pos=C;T.V0_UV=T.V1_UV=T.V2_UV=FVector2D::ZeroVector;T.V0_Color=T.V1_Color=T.V2_Color=Color;Out.Add(T);}
void Fill(UCanvas* C,const TArray<FCanvasUVTri>& Tris){if(Tris.IsEmpty())return;FCanvasTriangleItem I(Tris,GWhiteTexture);I.BlendMode=SE_BLEND_Translucent;C->DrawItem(I);}
void Disc(UCanvas* C,FVector2D P,double R,FLinearColor Color){TArray<FCanvasUVTri> T;for(int32 I=0;I<16;++I){const double A=I*UE_TWO_PI/16,B=(I+1)*UE_TWO_PI/16;Triangle(T,P,P+FVector2D(FMath::Cos(A),FMath::Sin(A))*R,P+FVector2D(FMath::Cos(B),FMath::Sin(B))*R,Color);}Fill(C,T);}
// Joined strip with a one-pixel alpha fringe: no aliased line primitives or bright segment joins.
void SmoothLoop(UCanvas* C,const TArray<FVector2D>& P,float Width,FLinearColor Color,FVector2D Offset=FVector2D::ZeroVector){
 TArray<FCanvasUVTri> T;T.Reserve(P.Num()*6);const int32 N=P.Num();if(N<3)return;
 auto CrossSection=[&](int32 I,FVector2D (&Q)[4]){const FVector2D D=(P[(I+1)%N]-P[(I+N-1)%N]).GetSafeNormal(),Normal(-D.Y,D.X),Center=P[I]+Offset;Q[0]=Center-Normal*(Width*.5+1);Q[1]=Center-Normal*Width*.5;Q[2]=Center+Normal*Width*.5;Q[3]=Center+Normal*(Width*.5+1);};
 for(int32 I=0;I<N;++I){FVector2D A[4],B[4];CrossSection(I,A);CrossSection((I+1)%N,B);for(int32 J=0;J<3;++J){const int32 Start=T.Num();Triangle(T,A[J],B[J],B[J+1],Color);Triangle(T,A[J],B[J+1],A[J+1],Color);auto Clear=Color;Clear.A=0;
  if(J==0){T[Start].V0_Color=Clear;T[Start].V1_Color=Clear;T[Start+1].V0_Color=Clear;}if(J==2){T[Start].V2_Color=Clear;T[Start+1].V1_Color=Clear;T[Start+1].V2_Color=Clear;}
 }}Fill(C,T);
}
void SmoothDot(UCanvas* C,FVector2D P,double R,FLinearColor Color){TArray<FCanvasUVTri> T;auto Clear=Color;Clear.A=0;for(int32 I=0;I<32;++I){const double A=I*UE_TWO_PI/32,B=(I+1)*UE_TWO_PI/32;const FVector2D X(FMath::Cos(A),FMath::Sin(A)),Y(FMath::Cos(B),FMath::Sin(B));Triangle(T,P,P+X*R,P+Y*R,Color);int32 K=T.Num();Triangle(T,P+X*R,P+X*(R+1),P+Y*(R+1),Color);Triangle(T,P+X*R,P+Y*(R+1),P+Y*R,Color);T[K].V1_Color=T[K].V2_Color=T[K+1].V1_Color=Clear;}Fill(C,T);}
void BoundedLine(UCanvas* C,const KartNavigation::FView& V,FVector2D A,FVector2D B,FLinearColor Color,float Width){A=V.Project(A);B=V.Project(B);if(KartNavigation::ClipLine(A,B,V.Pixels))Line(C,A,B,Color,Width);}
bool Fits(const KartNavigation::FView& V,FVector2D P,double Margin){return P.X>V.Pixels.Min.X+Margin&&P.X<V.Pixels.Max.X-Margin&&P.Y>V.Pixels.Min.Y+Margin&&P.Y<V.Pixels.Max.Y-Margin;}
}
UKartNavigationMap::UKartNavigationMap(){
 PrimaryComponentTick.bCanEverTick=false;
 static ConstructorHelpers::FObjectFinder<UTrackEdgeRoute> Data(TEXT("/Game/RoadToF1/RacingAI/DA_DesertTrackEdges.DA_DesertTrackEdges"));Route=Data.Object;
}
void UKartNavigationMap::BeginPlay(){
 Super::BeginPlay();auto* HUD=Cast<AHUD>(GetOwner());auto* PC=HUD?HUD->GetOwningPlayerController():nullptr;
 if(!PC||!PC->IsLocalController()||!Route||!Route->IsUsable()||!GetWorld()->GetMapName().Contains(TEXT("DesertKarting")))return;
 Player=PC;for(const FVector& P:Route->Left)WorldBounds+=FVector2D(P);for(const FVector& P:Route->Right)WorldBounds+=FVector2D(P);PanCenter=WorldBounds.GetCenter();HUD->EnableInput(PC);
 if(auto* I=HUD->InputComponent.Get()){
  auto Bind=[&](FKey Key,EInputEvent Event,void(UKartNavigationMap::*Fn)()){auto& B=I->BindKey(Key,Event,this,Fn);B.bExecuteWhenPaused=true;};
  Bind(EKeys::M,IE_Pressed,&UKartNavigationMap::ToggleMap);Bind(EKeys::Escape,IE_Pressed,&UKartNavigationMap::CloseMap);
  Bind(EKeys::MouseScrollUp,IE_Pressed,&UKartNavigationMap::ZoomIn);Bind(EKeys::MouseScrollDown,IE_Pressed,&UKartNavigationMap::ZoomOut);
  Bind(EKeys::LeftMouseButton,IE_Pressed,&UKartNavigationMap::PickWaypoint);Bind(EKeys::RightMouseButton,IE_Pressed,&UKartNavigationMap::ClearWaypoint);Bind(EKeys::Home,IE_Pressed,&UKartNavigationMap::RecenterMap);
  for(EInputEvent Event:{IE_Pressed,IE_Repeat}){Bind(EKeys::Up,Event,&UKartNavigationMap::PanNorth);Bind(EKeys::Down,Event,&UKartNavigationMap::PanSouth);Bind(EKeys::Left,Event,&UKartNavigationMap::PanWest);Bind(EKeys::Right,Event,&UKartNavigationMap::PanEast);}
 }
 // Use the existing live pit modules as a landmark, rather than guessing a building location.
 FVector Sum=FVector::ZeroVector;int32 Count=0;
 for(TActorIterator<AActor> It(GetWorld());It;++It){TInlineComponentArray<UInstancedStaticMeshComponent*> Components(*It);for(auto* C:Components)if(C->GetStaticMesh()&&C->GetStaticMesh()->GetName()==TEXT("SM_DV_PitBay"))for(int32 I=0;I<C->GetInstanceCount();++I){FTransform T;C->GetInstanceTransform(I,T,true);Sum+=T.GetLocation();++Count;}}
 if(Count){PitPoint=FVector2D(Sum/Count);bHasPits=true;}
}
void UKartNavigationMap::EndPlay(const EEndPlayReason::Type Reason){CloseMap();Super::EndPlay(Reason);}
void UKartNavigationMap::ToggleMap(){
 auto* PC=Player.Get();if(!PC||!Route||!Route->IsUsable())return;if(bMapOpen){CloseMap();return;}
 bMapOpen=true;bPreviousCursor=PC->bShowMouseCursor;PC->bShowMouseCursor=true;
 FInputModeGameAndUI Mode;Mode.SetHideCursorDuringCapture(false);Mode.SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock);PC->SetInputMode(Mode);
 bPausedByMap=GetWorld()->GetNetMode()==NM_Standalone&&!UGameplayStatics::IsGamePaused(this)&&PC->SetPause(true);
}
void UKartNavigationMap::CloseMap(){
 if(!bMapOpen)return;bMapOpen=false;if(auto* PC=Player.Get()){if(bPausedByMap)PC->SetPause(false);PC->bShowMouseCursor=bPreviousCursor;PC->SetInputMode(FInputModeGameOnly());}bPausedByMap=false;
}
void UKartNavigationMap::RecenterMap(){if(!bMapOpen)return;FullMapZoom=1;PanCenter=WorldBounds.GetCenter();}
void UKartNavigationMap::PanMap(FVector2D Delta){if(!bMapOpen)return;PanCenter+=Delta;const FVector2D Pad(3500,3500);PanCenter.X=FMath::Clamp(PanCenter.X,WorldBounds.Min.X-Pad.X,WorldBounds.Max.X+Pad.X);PanCenter.Y=FMath::Clamp(PanCenter.Y,WorldBounds.Min.Y-Pad.Y,WorldBounds.Max.Y+Pad.Y);}
void UKartNavigationMap::PanNorth(){PanMap(FVector2D(600/FullMapZoom,0));}void UKartNavigationMap::PanSouth(){PanMap(FVector2D(-600/FullMapZoom,0));}
void UKartNavigationMap::PanWest(){PanMap(FVector2D(0,-600/FullMapZoom));}void UKartNavigationMap::PanEast(){PanMap(FVector2D(0,600/FullMapZoom));}
void UKartNavigationMap::ZoomBy(float Factor){
 if(!bMapOpen)return;const float Old=FullMapZoom;FullMapZoom=FMath::Clamp(FullMapZoom*Factor,1.f,4.f);if(Old==FullMapZoom)return;
 if(auto* PC=Player.Get()){float X,Y;if(PC->GetMousePosition(X,Y)&&FullView.Pixels.IsInside(FVector2D(X,Y))){const FVector2D Anchor=FullView.Unproject(FVector2D(X,Y));PanMap((Anchor-PanCenter)*(1.-Old/FullMapZoom));}}
}
void UKartNavigationMap::ZoomIn(){ZoomBy(1.25f);}void UKartNavigationMap::ZoomOut(){ZoomBy(.8f);}
void UKartNavigationMap::PickWaypoint(){if(!bMapOpen)return;if(auto* PC=Player.Get()){float X,Y;if(PC->GetMousePosition(X,Y)&&FullView.Pixels.IsInside(FVector2D(X,Y))){const FVector2D P=FullView.Unproject(FVector2D(X,Y));SetWaypointWorld(FVector(P.X,P.Y,0));}}}
void UKartNavigationMap::SetWaypointWorld(FVector Location){
 if(!Route||!Route->IsUsable()||!FMath::IsFinite(Location.X)||!FMath::IsFinite(Location.Y))return;
 Waypoint=KartNavigation::Nearest(Route->Center,FVector2D(Location));if(Waypoint.Segment==INDEX_NONE)return;WaypointWorld=FVector(Waypoint.Position.X,Waypoint.Position.Y,0);bHasWaypoint=true;
}
void UKartNavigationMap::ClearWaypoint(){bHasWaypoint=false;WaypointDistanceMeters=0;}
void UKartNavigationMap::DrawTrack(UCanvas* C,const KartNavigation::FView& V,float Scale){
 NavFillRect(C,V.Pixels.Min,V.Pixels.GetSize(),Ground);TArray<FCanvasUVTri> Tris;Tris.Reserve(Route->Center.Num()*2);
 // A restrained map grid supplies distance context without another rendered world camera.
 for(double X=FMath::FloorToDouble(WorldBounds.Min.X/2500)*2500;X<=WorldBounds.Max.X+2500;X+=2500)BoundedLine(C,V,{X,WorldBounds.Min.Y-3500},{X,WorldBounds.Max.Y+3500},Ink(48,52,51),1);
 for(double Y=FMath::FloorToDouble(WorldBounds.Min.Y/2500)*2500;Y<=WorldBounds.Max.Y+2500;Y+=2500)BoundedLine(C,V,{WorldBounds.Min.X-3500,Y},{WorldBounds.Max.X+3500,Y},Ink(48,52,51),1);
 for(int32 I=0;I<Route->Center.Num();++I){const int32 J=(I+1)%Route->Center.Num();TArray<FVector2D> P={V.Project(FVector2D(Route->Left[I])),V.Project(FVector2D(Route->Left[J])),V.Project(FVector2D(Route->Right[J])),V.Project(FVector2D(Route->Right[I]))};
  FBox2D B(ForceInit);bool Inside=true;for(const auto& Q:P){B+=Q;Inside&=V.Pixels.IsInside(Q);}if(!B.Intersect(V.Pixels))continue;if(!Inside)P=KartNavigation::ClipPolygon(MoveTemp(P),V.Pixels);for(int32 K=1;K+1<P.Num();++K)Triangle(Tris,P[0],P[K],P[K+1],Road);
 }
 Fill(C,Tris);
 for(int32 I=0;I<Route->Center.Num();++I){int32 J=(I+1)%Route->Center.Num();BoundedLine(C,V,FVector2D(Route->Left[I]),FVector2D(Route->Left[J]),Edge,FMath::Max(.7f,Scale));BoundedLine(C,V,FVector2D(Route->Right[I]),FVector2D(Route->Right[J]),Edge,FMath::Max(.7f,Scale));}
 if(bHasWaypoint){
  auto* PC=Player.Get();APawn* Pawn=PC?PC->GetPawn():nullptr;if(Pawn){const auto Start=KartNavigation::Nearest(Route->Center,FVector2D(Pawn->GetActorLocation()));WaypointDistanceMeters=KartNavigation::ForwardDistance(Route->Center,Start,Waypoint)/100;
   const int32 N=Route->Center.Num();int32 Steps=(Waypoint.Segment-Start.Segment+N)%N;if(!Steps&&Waypoint.Fraction<Start.Fraction)Steps=N;FVector2D Previous=Start.Position;
   for(int32 K=1;K<=Steps;++K){const FVector2D P(Route->Center[(Start.Segment+K)%N]);BoundedLine(C,V,Previous,P,Purple,4*Scale);Previous=P;}BoundedLine(C,V,Previous,Waypoint.Position,Purple,4*Scale);
  }
 }
}
void UKartNavigationMap::DrawBlips(UCanvas* C,UFont* Font,const KartNavigation::FView& V,AProofPawn* Pawn,float Scale,bool Full){
 if(GetWorld()->GetRealTimeSeconds()-LastKartRefresh>.5){LastKartRefresh=GetWorld()->GetRealTimeSeconds();Karts.Reset();for(TActorIterator<AProofPawn> It(GetWorld());It;++It)Karts.Add(*It);}
 DisplayedKartCount=0;for(auto& Weak:Karts)if(auto* Kart=Weak.Get()){++DisplayedKartCount;if(Kart==Pawn)continue;const FVector2D P=V.Project(FVector2D(Kart->GetActorLocation()));if(Fits(V,P,6*Scale)){SmoothDot(C,P,5*Scale,Ink(19,22,22));SmoothDot(C,P,3*Scale,White);}}
 const FVector2D Finish=V.Project(StartPoint);if(Fits(V,Finish,7*Scale)){
  NavFillRect(C,Finish-FVector2D(7,5)*Scale,FVector2D(14,10)*Scale,Ink(18,21,21));for(int32 Y=0;Y<2;++Y)for(int32 X=0;X<4;++X)if((X+Y)%2==0)NavFillRect(C,Finish+FVector2D(X*3-6,Y*4-4)*Scale,FVector2D(3,4)*Scale,White);
  if(Full)Label(C,Font,TEXT("START / FINISH"),Finish+FVector2D(10,8)*Scale,12*Scale,White);
 }
 if(Full){
  constexpr int32 Corners[]={64,220,329,439,505,593,724};for(int32 I=0;I<7;++I)if(Route->Center.IsValidIndex(Corners[I])){const FVector2D P=V.Project(FVector2D(Route->Center[Corners[I]]));if(Fits(V,P,12*Scale)){Disc(C,P,11*Scale,Ink(23,27,26));Label(C,Font,FString::Printf(TEXT("%d"),I+1),P,12*Scale,White,true);}}
  if(bHasPits){const auto P=V.Project(PitPoint);if(Fits(V,P,10*Scale)){NavFillRect(C,P-FVector2D(5,5)*Scale,FVector2D(10,10)*Scale,Muted);Label(C,Font,TEXT("PITS"),P+FVector2D(10,-5)*Scale,12*Scale,Muted);}}
 }
 if(bHasWaypoint){const auto P=V.Project(Waypoint.Position);if(Fits(V,P,9*Scale)){Disc(C,P,8*Scale,Ink(27,21,34));Disc(C,P,5*Scale,Purple);Disc(C,P,2*Scale,White);}}
 const FVector2D P=V.Project(FVector2D(Pawn->GetActorLocation()));if(Fits(V,P,8*Scale)){SmoothDot(C,P,7*Scale,Ink(15,15,15));SmoothDot(C,P,5*Scale,PlayerColor);}
}
void UKartNavigationMap::Draw(UCanvas* C,UFont* Font){
 auto* PC=Player.Get();auto* Pawn=PC?Cast<AProofPawn>(PC->GetPawn()):nullptr;if(!C||!Font||!Pawn||!Route||!Route->IsUsable()||!WorldBounds.bIsValid)return;
 const float S=FMath::Clamp(C->SizeY/1080.f,.65f,1.4f);
 if(bHasWaypoint&&FVector::Dist2D(Pawn->GetActorLocation(),WaypointWorld)<250&&KartNavigation::ForwardDistance(Route->Center,KartNavigation::Nearest(Route->Center,FVector2D(Pawn->GetActorLocation())),Waypoint)<500)ClearWaypoint();
 if(!bMapOpen){
  const FVector2D Size(360*S,285*S),P(28*S,C->SizeY-Size.Y-42*S);KartNavigation::FView V;V.Pixels=FBox2D(P,P+Size);V.WorldCenter=WorldBounds.GetCenter();V.PixelOrigin=P+Size*.5;
  const float Yaw=Pawn->GetActorRotation().Yaw;if(!bHeadingInitialized){MinimapHeading=Yaw;bHeadingInitialized=true;}
  MinimapHeading=FMath::UnwindDegrees(MinimapHeading+FMath::FindDeltaAngleDegrees(MinimapHeading,Yaw)*(1-FMath::Exp(-25.f*GetWorld()->GetDeltaSeconds())));V.YawDegrees=MinimapHeading;
  V.TiltScale=FMath::Clamp(MinimapTilt,.5f,1.f);V.Perspective=.0012;V.PixelsPerCm=FMath::Min(Size.X*.90,Size.Y*.90/V.TiltScale)/(WorldBounds.GetSize().Size()+4000);
  // Rotation-invariant scale avoids pumping/zoom changes as the circuit rotates.
  TArray<FVector2D> Path;Path.Reserve(Route->Center.Num());for(const auto& Point:Route->Center)Path.Add(V.Project(FVector2D(Point)));
  SmoothLoop(C,Path,7*S,Ink(9,12,15,.75f),FVector2D(0,4*S));SmoothLoop(C,Path,5*S,Ink(26,32,37));SmoothLoop(C,Path,2.8f*S,Ink(209,218,224));
  DrawBlips(C,Font,V,Pawn,S,false);
  Label(C,Font,TEXT("M  CIRCUIT MAP"),P+FVector2D(2*S,Size.Y+8*S),12*S,White);
  if(bHasWaypoint)Label(C,Font,FString::Printf(TEXT("%.0f m"),WaypointDistanceMeters),P+FVector2D(Size.X-62*S,Size.Y+8*S),12*S,Purple);
  return;
 }
 NavFillRect(C,FVector2D::ZeroVector,FVector2D(C->SizeX,C->SizeY),Ink(17,21,20,.98f));Label(C,Font,TEXT("DESERT KARTING"),FVector2D(36*S,26*S),28*S,White);Label(C,Font,TEXT("CIRCUIT MAP"),FVector2D(37*S,62*S),13*S,Muted);
 Label(C,Font,UGameplayStatics::IsGamePaused(this)?TEXT("RACE PAUSED"):TEXT("LIVE SESSION"),FVector2D(C->SizeX-205*S,38*S),14*S,PlayerColor);
 const FBox2D R(FVector2D(34*S,100*S),FVector2D(C->SizeX-280*S,C->SizeY-90*S));FullView.Pixels=R;FullView.WorldCenter=PanCenter;FullView.YawDegrees=0;FullView.PixelOrigin=R.GetCenter();const FVector2D Span=WorldBounds.GetSize()+FVector2D(3200,3200);FullView.PixelsPerCm=FMath::Min(R.GetSize().X/Span.Y,R.GetSize().Y/Span.X)*FullMapZoom;
 DrawTrack(C,FullView,S);DrawBlips(C,Font,FullView,Pawn,S,true);Label(C,Font,TEXT("N"),R.Min+FVector2D(20,22)*S,15*S,White,true);Line(C,R.Min+FVector2D(20,40)*S,R.Min+FVector2D(20,55)*S,White,2*S);
 const double X=C->SizeX-246*S;Label(C,Font,TEXT("LEGEND"),FVector2D(X,111*S),15*S,White);
 const TArray<FString> Names={TEXT("YOU"),TEXT("OTHER KARTS"),TEXT("START / FINISH"),TEXT("TURN NUMBERS"),TEXT("WAYPOINT")};const FLinearColor Colors[]={PlayerColor,White,White,Muted,Purple};
 for(int32 I=0;I<Names.Num();++I){const double Y=(151+I*34)*S;Disc(C,FVector2D(X+5*S,Y+5*S),4*S,Colors[I]);Label(C,Font,Names[I],FVector2D(X+20*S,Y),12*S,Colors[I]);}
 Label(C,Font,FString::Printf(TEXT("%d KARTS"),DisplayedKartCount),FVector2D(X,350*S),13*S,Muted);Label(C,Font,FString::Printf(TEXT("ZOOM  %.2fx"),FullMapZoom),FVector2D(X,380*S),13*S,Muted);
 if(bHasWaypoint){Label(C,Font,TEXT("FORWARD ROUTE"),FVector2D(X,425*S),12*S,Purple);Label(C,Font,FString::Printf(TEXT("%.0f m"),WaypointDistanceMeters),FVector2D(X,451*S),23*S,Purple);}
 Label(C,Font,TEXT("M  CLOSE     WHEEL  ZOOM     ARROWS  PAN     HOME  RESET VIEW"),FVector2D(36*S,C->SizeY-62*S),13*S,White);
 Label(C,Font,TEXT("LEFT CLICK  SET WAYPOINT     RIGHT CLICK  CLEAR     Route follows the racing direction"),FVector2D(36*S,C->SizeY-35*S),12*S,Muted);
}

