#include "TrackRacingAI.h"
#include "ProofPawn.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Engine/World.h"
void UTrackRacingAI::UpdateHumanProgress(){
#if !UE_BUILD_SHIPPING
 if(bTesting&&FParse::Param(FCommandLine::Get(),TEXT("RacingAIPlayerTest")))return;
#endif
 auto* GM=Cast<AProofGameMode>(GetOwner());if(!GM||!Route)return;
 for(auto Weak:CachedTraffic){auto* P=Weak.Get();if(!P||!P->IsPlayerControlled())continue;auto& S=TestPlayer;S.Pawn=P;const FVector Pos=P->GetActorLocation();
  if(S.Segment==INDEX_NONE||GM->IsStartGateClosed()){S.Segment=NearestSegment(Pos,INDEX_NONE);S.StartArc=S.PreviousArc=SegmentArc(Pos,S.Segment);S.Previous=Pos;return;}
  S.Segment=NearestSegment(Pos,S.Segment);const float Arc=SegmentArc(Pos,S.Segment);float Advance=Arc-S.PreviousArc;if(Advance<-RouteLength*.5f)Advance+=RouteLength;if(Advance>RouteLength*.5f)Advance-=RouteLength;
  if(FVector::Dist2D(Pos,S.Previous)<350)S.Distance+=Advance;S.Previous=Pos;S.PreviousArc=Arc;const int32 Old=S.Laps;S.Laps=FMath::Max(S.Laps,FMath::FloorToInt(FMath::Max(0.f,S.Distance)/RouteLength));
  if(S.Laps>Old){const float Time=GM->GetRaceElapsedSeconds();S.LapTimes.Add(Time-S.LastLapSeconds);S.LastLapSeconds=Time;}return;
 }
}
bool UTrackRacingAI::PlayerRaceStatus(FKartRaceStatus& Out)const{
 if(!Route||!TestPlayer.Pawn.IsValid()||TestPlayer.Segment==INDEX_NONE)return false;
 Out=FKartRaceStatus();Out.Lap=TestPlayer.Laps+1;const float Progress=TestPlayer.StartArc+TestPlayer.Distance;
 for(const auto& S:Opponents)if(S.Pawn.IsValid()){++Out.Total;if(S.StartArc+S.Distance>Progress+5)++Out.Position;}
 if(const auto* GM=Cast<AProofGameMode>(GetOwner()))Out.CurrentSeconds=FMath::Max(0.f,GM->GetRaceElapsedSeconds()-TestPlayer.LastLapSeconds);
 for(float Lap:TestPlayer.LapTimes){Out.LastSeconds=Lap;Out.BestSeconds=Out.BestSeconds<0?Lap:FMath::Min(Out.BestSeconds,Lap);}return true;
}
