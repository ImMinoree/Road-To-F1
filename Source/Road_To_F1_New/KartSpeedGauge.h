#pragma once

#include "CoreMinimal.h"
#include "CanvasItem.h"
#include "Engine/Canvas.h"
#include "Engine/Font.h"
#include "Fonts/SlateFontInfo.h"
#include "HAL/IConsoleManager.h"
#include "ProofPawn.h"
#include "RenderUtils.h"

// A read-only speed display: no RPM/gear simulation, forces or input handling.
namespace KartSpeedGauge
{
inline TAutoConsoleVariable<int32> Enabled(TEXT("kart.SpeedGauge.Enabled"),1,TEXT("Show the kart speed gauge."));
inline TAutoConsoleVariable<int32> Mph(TEXT("kart.SpeedGauge.MPH"),0,TEXT("Display mph instead of km/h."));
inline TAutoConsoleVariable<float> MaxKmh(TEXT("kart.SpeedGauge.MaxKmh"),80.f,TEXT("Gauge face range in km/h; display only."));
inline TAutoConsoleVariable<int32> Debug(TEXT("kart.SpeedGauge.Debug"),0,TEXT("Log actual rendered speed for validation."));

inline FVector2D Point(FVector2D Center,float Radius,float Degrees)
{
 const float A=FMath::DegreesToRadians(Degrees);
 return Center+FVector2D(FMath::Cos(A),FMath::Sin(A))*Radius;
}
inline void Triangle(TArray<FCanvasUVTri>& Out,FVector2D A,FVector2D B,FVector2D C,FLinearColor CA,FLinearColor CB,FLinearColor CC)
{
 FCanvasUVTri T;T.V0_Pos=A;T.V1_Pos=B;T.V2_Pos=C;
 T.V0_UV=T.V1_UV=T.V2_UV=FVector2D::ZeroVector;T.V0_Color=CA;T.V1_Color=CB;T.V2_Color=CC;Out.Add(T);
}
inline void Arc(UCanvas* Canvas,FVector2D Center,float Radius,float Start,float End,float Width,FLinearColor Color)
{
 if(End<=Start)return;
 const int32 Segments=FMath::Max(1,FMath::CeilToInt((End-Start)/2.f));TArray<FCanvasUVTri> Tris;Tris.Reserve(Segments*6);
 const float Inner=Radius-Width*.5f,Outer=Radius+Width*.5f;auto Clear=Color;Clear.A=0;
 for(int32 I=0;I<Segments;++I)
 {
  const float A=FMath::Lerp(Start,End,float(I)/Segments),B=FMath::Lerp(Start,End,float(I+1)/Segments);
  auto P=[&](float R,float D){return Point(Center,R,D);};
  Triangle(Tris,P(Inner,A),P(Outer,A),P(Outer,B),Color,Color,Color);
  Triangle(Tris,P(Inner,A),P(Outer,B),P(Inner,B),Color,Color,Color);
  Triangle(Tris,P(Inner-1,A),P(Inner,A),P(Inner,B),Clear,Color,Color);
  Triangle(Tris,P(Inner-1,A),P(Inner,B),P(Inner-1,B),Clear,Color,Clear);
  Triangle(Tris,P(Outer,A),P(Outer+1,A),P(Outer+1,B),Color,Clear,Clear);
  Triangle(Tris,P(Outer,A),P(Outer+1,B),P(Outer,B),Color,Clear,Color);
 }
 FCanvasTriangleItem Item(Tris,GWhiteTexture);Item.BlendMode=SE_BLEND_Translucent;Canvas->DrawItem(Item);
}
inline void Text(UCanvas* Canvas,UFont* Font,const FString& Value,FVector2D P,float Size,FLinearColor Color,const FName Face=TEXT("Regular"))
{
 FCanvasTextItem Item(P,FText::FromString(Value),FSlateFontInfo(Font,Size,Face),Color);
 Item.bCentreX=true;Item.bCentreY=true;Item.EnableShadow(FLinearColor(0,0,0,.7f),FVector2D(1,1));Canvas->DrawItem(Item);
}
inline void Draw(UCanvas* Canvas,UFont* Font,const AProofPawn* Pawn)
{
 if(!Canvas||!Font||!Pawn||!Enabled.GetValueOnGameThread())return;
 const FVector Velocity=Pawn->GetVelocity();
 const double RawKmh=Velocity.Size2D()*.036;
 const float Kmh=FMath::IsFinite(RawKmh)?float(FMath::Max(0.,RawKmh)):0.f;
 const bool UseMph=Mph.GetValueOnGameThread()!=0;
 const float Units=UseMph?.621371192f:1.f,Speed=Kmh*Units;
 const float Range=FMath::Max(10.f,MaxKmh.GetValueOnGameThread()),Fraction=FMath::Clamp(Kmh/Range,0.f,1.f);
 const float S=FMath::Clamp(FMath::Min(Canvas->SizeX/1920.f,Canvas->SizeY/1080.f),.4f,1.6f);
 const FVector2D Center(Canvas->SizeX-148*S,Canvas->SizeY-153*S);const float Radius=100*S;
 const FLinearColor White(.94f,.96f,1.f,.94f),Muted(.72f,.77f,.82f,.52f),Red(.95f,.12f,.22f,.9f);
 Arc(Canvas,Center,Radius,135,405,5*S,FLinearColor(0,0,0,.22f));
 Arc(Canvas,Center,Radius,135,405,1.3f*S,Muted.CopyWithNewOpacity(.20f));
 Arc(Canvas,Center,Radius+4*S,351,405,2.8f*S,Red.CopyWithNewOpacity(.55f));
 Arc(Canvas,Center,Radius,135,135+270*Fraction,3.2f*S,White);
 if(Fraction>.8f)Arc(Canvas,Center,Radius,351,135+270*Fraction,3.2f*S,Red);
 for(int32 I=0;I<=8;++I)
 {
  const float A=135+I*33.75f;
  FCanvasLineItem Tick(Point(Center,Radius-5*S,A),Point(Center,Radius-(I%2?10:14)*S,A));Tick.SetColor(Muted);Tick.LineThickness=1.1f*S;Canvas->DrawItem(Tick);
  if(I>0&&I<8&&I%2==0)Text(Canvas,Font,FString::FromInt(FMath::RoundToInt(Range*Units*I/8)),Point(Center,Radius-26*S,A),10*S,Muted);
 }
 if(Fraction>.001f)
 {
  const float A=135+270*Fraction;FCanvasLineItem Tip(Point(Center,Radius-7*S,A),Point(Center,Radius+6*S,A));Tip.SetColor(Fraction>.8f?Red:White);Tip.LineThickness=2*S;Canvas->DrawItem(Tip);
 }
 const bool Reverse=FVector::DotProduct(Velocity,Pawn->GetActorForwardVector())<-10;
 Text(Canvas,Font,Reverse?TEXT("REVERSE"):TEXT("SPEED"),Center+FVector2D(0,-17*S),11*S,Muted);
 Text(Canvas,Font,UseMph?TEXT("MPH"):TEXT("KM/H"),Center+FVector2D(0,4*S),12*S,White.CopyWithNewOpacity(.65f));
 const int32 Digital=FMath::Clamp(FMath::RoundToInt(Speed),0,999);const FString Digits=FString::Printf(TEXT("%03d"),Digital);
 for(int32 I=0;I<3;++I)
 {
  const bool Leading=(I==0&&Digital<100)||(I==1&&Digital<10);
  Text(Canvas,Font,Digits.Mid(I,1),Center+FVector2D((I-1)*34*S,48*S),62*S,White.CopyWithNewOpacity(Leading?.22f:.98f),TEXT("Light"));
 }
 if(Debug.GetValueOnGameThread())
 {
  static double Last=-1;const double Now=Pawn->GetWorld()->GetRealTimeSeconds();
  if(Now<Last||Now-Last>.25){Last=Now;UE_LOG(LogTemp,Display,TEXT("SPEED_GAUGE kmh=%.5f shown=%d unit=%s fraction=%.5f reverse=%d canvas=%dx%d"),Kmh,Digital,UseMph?TEXT("mph"):TEXT("kmh"),Fraction,Reverse,Canvas->SizeX,Canvas->SizeY);}
 }
}
}
