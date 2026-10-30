#include "TrackRacingAI.h"
#include "ProofPawn.h"
#include "Engine/Engine.h"
#include "DrawDebugHelpers.h"
#include "HAL/IConsoleManager.h"
namespace { TAutoConsoleVariable<int32> DebugAI(TEXT("kart.ai.Debug"),0,TEXT("Show AI controls and decisions")); TAutoConsoleVariable<int32> PathsAI(TEXT("kart.ai.Paths"),0,TEXT("Show racing trajectory and predictions")); }
void UTrackRacingAI::DrawAIDiagnostics(float Dt){
 const bool Text=bDebugAI||DebugAI.GetValueOnGameThread()!=0,Paths=bDrawAIPaths||PathsAI.GetValueOnGameThread()!=0;
 if(!Text&&!Paths)return;DebugClock+=Dt;if(DebugClock<.15f)return;DebugClock=0;
 if(Paths)for(int32 I=0;I+8<TrackPlan.Samples.Num();I+=8)DrawDebugLine(GetWorld(),TrackPlan.Samples[I].Position+FVector(0,0,20),TrackPlan.Samples[I+8].Position+FVector(0,0,20),FColor::Cyan,false,.2f,0,3);
 for(const auto& S:Opponents){auto* P=S.Pawn.Get();if(!P)continue;
 if(Text&&GEngine)GEngine->AddOnScreenDebugMessage(9100+S.Slot,.25f,FColor::White,FString::Printf(TEXT("AI%d %s %s %.0f/%.0fkmh T%.2f B%.2f S%.2f seg%d lane%.0f rival%s side%d TTC%.1f aggression%.2f"),S.Slot,*StaticEnum<EKartAIDifficulty>()->GetNameStringByValue(int64(Difficulty)),*StaticEnum<EKartAIState>()->GetNameStringByValue(int64(S.State)),P->GetDrivingSpeed()*.036f,S.DebugTargetSpeed*.036f,S.ThrottleCommand,S.BrakeCommand,S.Steering,S.Segment,S.Lane,S.PerceivedLeader.IsValid()?*S.PerceivedLeader->GetName():TEXT("none"),S.Intent,S.MinimumTTC,S.Personality.Aggressiveness));
 if(Paths&&S.Segment>=0){const int32 I=AheadIndex(S.Segment,600);const float Guide=Route->Guide.Num()==Route->Center.Num()?Lateral(Route->Guide[S.Segment],S.Segment):0;DrawDebugLine(GetWorld(),P->GetActorLocation(),Route->LanePoint(I,S.Lane-Guide,175)+FVector(0,0,30),FColor::Yellow,false,.2f,0,4);for(const auto& O:S.Nearby)DrawDebugSphere(GetWorld(),O.Predicted,65,8,FColor::Orange,false,.2f);}
 }
}
