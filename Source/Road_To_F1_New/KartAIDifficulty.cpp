#include "TrackRacingAI.h"
#include "HAL/IConsoleManager.h"
namespace {
TAutoConsoleVariable<int32> AIDifficultyVar(TEXT("kart.ai.Difficulty"),-1,TEXT("-1 uses component setting; 0 Rookie, 1 Amateur, 2 Intermediate, 3 Pro, 4 Elite"));
TAutoConsoleVariable<int32> AIOpponentsVar(TEXT("kart.ai.Opponents"),-1,TEXT("Opponent count 0..19, applied at next Play; -1 uses component default"));
}
FKartDifficultySettings UTrackRacingAI::Preset(EKartAIDifficulty Value){
 switch(Value){case EKartAIDifficulty::ROOKIE:return {.70f,.75f,.35f,.8f,3.f};case EKartAIDifficulty::AMATEUR:return {.85f,.5f,.28f,.65f,2.f};case EKartAIDifficulty::PRO:return {1.06f,.15f,.16f,.4f,.6f};case EKartAIDifficulty::ELITE:return {1.12f,.05f,.12f,.3f,.2f};default:return {1.f,.3f,.2f,.5f,1.f};}
}
void UTrackRacingAI::SetDifficulty(EKartAIDifficulty Value){Difficulty=Value;for(auto& S:Opponents)S.StrategyClock=1;}
void UTrackRacingAI::ApplyConsoleConfiguration(){const int32 V=AIDifficultyVar.GetValueOnGameThread();if(V!=LastConsoleDifficulty){LastConsoleDifficulty=V;if(V>=0)SetDifficulty(EKartAIDifficulty(FMath::Clamp(V,0,4)));}}
int32 UTrackRacingAI::ConfiguredOpponentCount()const{const int32 V=AIOpponentsVar.GetValueOnGameThread();return FMath::Clamp(V<0?OpponentCount:V,0,19);}
float UTrackRacingAI::DriverPace(FTrackOpponent& S,float Dt){
 S.MistakeTimer=FMath::Max(0.f,S.MistakeTimer-Dt);S.MistakeCooldown=FMath::Max(0.f,S.MistakeCooldown-Dt);
 const bool Eligible=TrackPlan.Samples.IsValidIndex(S.Segment)&&(TrackPlan.Samples[S.Segment].Zone==3||TrackPlan.Samples[S.Segment].BendDistance>1500);
 if(Eligible&&!S.bAlongside&&S.Intent==0&&S.MistakeCooldown<=0&&S.Random.FRand()<FMath::Clamp(S.Personality.MistakeLikelihood,0.f,.05f)*Preset(Difficulty).MistakeScale*Dt){S.MistakeTimer=.8f;S.MistakeCooldown=45;++S.Mistakes;}
 const float Consistency=FMath::Clamp(S.Personality.Consistency,0.f,1.f);const float Variation=1-(1-Consistency)*.03f*(.5f+.5f*FMath::Sin(S.Distance*.0002f+S.Slot));
 return FMath::Clamp(S.Personality.Pace,.65f,1.f)*Variation*(S.MistakeTimer>0?.78f:1.f);
}
