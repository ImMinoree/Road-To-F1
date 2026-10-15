#pragma once
#include "KartPawn.h"
#include "KartRaceDirector.h"
// Test-owned aggregates: no shipping log output or runtime allocation.
struct FPaceMetrics
{
    double Moving=0, Sum=0, Under20=0, Under25=0, Over30=0, Traffic=0, Corner=0, Obstruction=0, Guidance=0, Recovery=0, Braking=0;
    float Peak=0, Queue=0, LongestQueue=0;
    int32 BrakeEvents=0;
    bool WasBraking=false;
    void Sample(const FKartOpponentState& S, float Dt)
    {
        if(S.Progress.bFinished) return;
        const float Mph=FMath::Abs(S.Kart->GetSpeedKmh())*.621371f;
        Peak=FMath::Max(Peak,Mph);
        if(Mph>1) {Moving+=Dt;Sum+=Mph*Dt;Under20+=Mph<20?Dt:0;Under25+=Mph<25?Dt:0;Over30+=Mph>30?Dt:0;}
        const FString Reason=S.Pace.Reason;
        Traffic+=Reason==TEXT("Traffic")?Dt:0;Corner+=Reason==TEXT("Corner")?Dt:0;Obstruction+=Reason==TEXT("Obstruction")?Dt:0;
        Guidance+=Reason==TEXT("Guidance")?Dt:0;Recovery+=(Reason==TEXT("Contact")||Reason==TEXT("Reverse"))?Dt:0;
        const bool Brake=S.Kart->IsBrakeHeld(); Braking+=Brake?Dt:0;BrakeEvents+=Brake&&!WasBraking?1:0;WasBraking=Brake;
        Queue=S.bQueued&&Mph<10?Queue+Dt:0;LongestQueue=FMath::Max(LongestQueue,Queue);
    }
    FString Describe() const
    {
        return FString::Printf(TEXT("peak_mph=%.2f moving_avg_mph=%.2f under20_pct=%.1f under25_pct=%.1f over30_pct=%.1f traffic_s=%.1f corner_s=%.1f obstruction_s=%.1f guidance_s=%.1f recovery_s=%.1f brake_events=%d brake_s=%.1f longest_queue_s=%.1f"),Peak,Sum/FMath::Max(1.,Moving),100*Under20/FMath::Max(1.,Moving),100*Under25/FMath::Max(1.,Moving),100*Over30/FMath::Max(1.,Moving),Traffic,Corner,Obstruction,Guidance,Recovery,BrakeEvents,Braking,LongestQueue);
    }
};
