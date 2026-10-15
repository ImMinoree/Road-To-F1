#if WITH_DEV_AUTOMATION_TESTS && WITH_EDITOR
#include "Misc/AutomationTest.h"
#include "Tests/AutomationEditorCommon.h"
#include "Tests/AutomationCommon.h"
#include "PaceMetrics.h"
#include "RaceLoopSubsystem.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/World.h"

DEFINE_LATENT_AUTOMATION_COMMAND_ONE_PARAMETER(FMeasureRacePace, FAutomationTestBase*, Test);
bool FMeasureRacePace::Update()
{
    UWorld* W=AutomationCommon::GetAnyGameWorld();
    auto* D=Cast<AKartRaceDirector>(UGameplayStatics::GetActorOfClass(W,AKartRaceDirector::StaticClass()));
    auto* P=Cast<AKartPawn>(UGameplayStatics::GetPlayerPawn(W,0));
    auto* R=W?W->GetSubsystem<URaceLoopSubsystem>():nullptr;
    if(!D||!P||!R){Test->AddError(TEXT("Pace fixture unavailable"));return true;}
    D->bPaceDiagnostics=true;
    auto& States=const_cast<TArray<FKartOpponentState>&>(D->GetOpponents());
    auto Prepare=[&](int32 Count,float InitialKmh)
    {
        R->Tick(0);R->RestartRace();P->SetDriveInput(1,0);P->Tick(.1f);D->Tick(.05f);P->ResetKart();P->SetActorLocation(FVector(0,-16000,25));
        for(int32 I=0;I<19;++I)
        {
            auto& S=States[I]; auto* K=S.Kart.Get();K->SetActorLocation(FVector(I*400,-17000,25));
            if(I>=Count){S.Progress.bFinished=true;K->SetRaceFinished();continue;}
            // Warm up on the real straight, then seed identical starting speed/position.
            K->SetActorLocation(FVector(-12000,-5280,25));K->SetActorRotation(FRotator::ZeroRotator);
            while(K->GetSpeedKmh()<InitialKmh){K->SetDriveInput(1,0);K->Tick(.05f);}
            K->SetActorLocation(FVector(-6500-I*500,-5280,25));
            S.Previous=K->GetActorLocation();S.RouteIndex=(600-I*3)%600;
            S.FilteredTrafficSpeed=55.f/.036f;
            S.Lane=S.DesiredLane=S.ActualLane=S.PreferredLane=0;S.LaunchSeconds=10;S.LaunchDistance=2000;S.DecisionCooldown=0;
        }
    };
    Prepare(1,0);
    auto& S=States[0];auto* K=S.Kart.Get();float T90=-1,T95=-1,D90=0,D95=0;const FVector Start=K->GetActorLocation();
    for(int32 F=0;F<180;++F){D->Tick(.05f);K->Tick(.05f);if(T90<0&&K->GetSpeedKmh()>=49.5f){T90=(F+1)*.05f;D90=FVector::Dist2D(Start,K->GetActorLocation());}if(T95<0&&K->GetSpeedKmh()>=52.25f){T95=(F+1)*.05f;D95=FVector::Dist2D(Start,K->GetActorLocation());}}
    Test->AddInfo(FString::Printf(TEXT("CLEAR speed_kmh=%.2f t90=%.2f d90_cm=%.0f t95=%.2f d95_cm=%.0f"),K->GetSpeedKmh(),T90,D90,T95,D95));
    Test->TestTrue(TEXT("Clear air reaches existing cap without changing it"),K->GetSpeedKmh()>53 && K->GetSpeedKmh()<=55.01f);
    // Authored exit samples following three different bends; identical 25 km/h entry.
    for(int32 Exit:{120,210,300})
    {
        Prepare(1,25);K->SetActorLocation(D->RoutePoints[Exit]);K->SetActorRotation((D->RoutePoints[Exit+1]-D->RoutePoints[Exit]).Rotation());S.RouteIndex=Exit;S.Previous=K->GetActorLocation();
        const float Apex=K->GetSpeedKmh();const FVector ExitStart=K->GetActorLocation();float Speeds[3]={};T90=T95=-1;D90=D95=0;
        for(int32 F=0;F<240;++F){D->Tick(.05f);K->Tick(.05f);if(F==19||F==39||F==59)Speeds[(F+1)/20-1]=K->GetSpeedKmh();if(T90<0&&K->GetSpeedKmh()>=49.5f){T90=(F+1)*.05f;D90=FVector::Dist2D(ExitStart,K->GetActorLocation());}if(T95<0&&K->GetSpeedKmh()>=52.25f){T95=(F+1)*.05f;D95=FVector::Dist2D(ExitStart,K->GetActorLocation());}}
        Test->AddInfo(FString::Printf(TEXT("EXIT%d apex_kmh=%.2f one=%.2f two=%.2f three=%.2f t90=%.2f d90_cm=%.0f t95=%.2f d95_cm=%.0f contacts=%d"),Exit,Apex,Speeds[0],Speeds[1],Speeds[2],T90,D90,T95,D95,K->GetCollisionCount()));
        Test->TestTrue(TEXT("Corner exit recovers cap with no contact"),T95>0 && K->GetCollisionCount()==0);
    }
    // Similar-speed six-kart train. Leader eases to 40 km/h, then accelerates.
    Prepare(6,44);float Minimum[6];FPaceMetrics Train[6];for(float& V:Minimum)V=100;
    for(int32 F=0;F<200;++F)
    {
        D->Tick(.05f);float LeadTarget=F<80?40.f:55.f;
        States[0].Kart->SetDriveInput(States[0].Kart->GetSpeedKmh()<LeadTarget?.8f:0,0,States[0].Kart->GetSpeedKmh()>LeadTarget+1);
        for(int32 I=0;I<6;++I){auto* C=States[I].Kart.Get();Train[I].Sample(States[I],.05f);C->Tick(.05f);Minimum[I]=FMath::Min(Minimum[I],C->GetSpeedKmh());
            if(F%20==0)Test->AddInfo(FString::Printf(TEXT("TRACE t%.1f racer%d speed%.1f target%.0f reason%s traffic%.0f guide%.0f ahead%.0f rel%.0f lane%.0f desired%.0f actual%.0f phase%d pos%s"),F*.05,I,C->GetSpeedKmh(),States[I].TargetSpeed,States[I].Pace.Reason,States[I].Pace.Traffic,States[I].Pace.Guidance,States[I].Pace.Ahead,States[I].Pace.RelativeSpeed,States[I].Lane,States[I].DesiredLane,States[I].ActualLane,int(States[I].PassPhase),*C->GetActorLocation().ToString()));}
    }
    for(int32 I=0;I<6;++I){Test->AddInfo(FString::Printf(TEXT("TRAIN%d min_kmh=%.2f final_kmh=%.2f contacts=%d ahead_cm=%.1f closing_cms=%.1f %s"),I,Minimum[I],States[I].Kart->GetSpeedKmh(),States[I].Kart->GetCollisionCount(),States[I].Pace.Ahead,States[I].Pace.RelativeSpeed,*Train[I].Describe()));}
    Test->TestTrue(TEXT("Train tail does not collapse below moderate leader speed"),Minimum[5]>32);
    Test->TestTrue(TEXT("Train releases slowdown when leader accelerates"),States[5].Kart->GetSpeedKmh()>48);
    // A normal 30 km/h competitor, not an emergency obstruction.
    Prepare(2,40);auto* Lead=States[0].Kart.Get();auto& Follower=States[1];auto* Follow=Follower.Kart.Get();
    int32 Flips=0;float LastSign=0;bool Passed=false,EmergencyLimit=false;
    for(int32 F=0;F<220;++F)
    {
        D->Tick(.05f);Lead->SetDriveInput(Lead->GetSpeedKmh()<30?.5f:0,0,Lead->GetSpeedKmh()>31);
        Follow->Tick(.05f);Lead->Tick(.05f);
        if(FMath::Abs(Follower.DesiredLane)>80){float Sign=FMath::Sign(Follower.DesiredLane);if(LastSign!=0&&Sign!=LastSign)++Flips;LastSign=Sign;}
        EmergencyLimit|=Follower.Pace.Obstruction<=400;Passed|=Follow->GetActorLocation().X>Lead->GetActorLocation().X+250;
    }
    Test->AddInfo(FString::Printf(TEXT("PASS success=%d flips=%d contacts=%d emergency=%d final_kmh=%.2f attempts=%d completed=%d"),Passed,Flips,Follow->GetCollisionCount(),EmergencyLimit,Follow->GetSpeedKmh(),Follower.PassAttempts,Follower.CompletedPasses));
    Test->TestTrue(TEXT("Faster follower completes normal overtake"),Passed);
    Test->TestTrue(TEXT("Normal pass uses explicit intent and completion"),Follower.PassAttempts>0 && Follower.CompletedPasses>0);
    Test->TestFalse(TEXT("Normal pass never inherits stopped-object cap"),EmergencyLimit);
    Test->TestEqual(TEXT("Normal overtake has no contact"),Follow->GetCollisionCount(),0);
    Test->TestTrue(TEXT("Pass commitment avoids repeated left-right changes"),Flips<=1);
    Prepare(2,35);
    auto* Obstacle=States[0].Kart.Get();auto* Recovering=States[1].Kart.Get();
    Obstacle->ResetKart();Obstacle->SetActorLocation(Recovering->GetActorLocation()+FVector(400,0,0));
    D->Tick(.05f);const float BlockedLimit=States[1].Pace.Traffic;
    Obstacle->SetActorLocation(FVector(0,-16000,25));
    for(int32 I=0;I<40;++I)D->Tick(.05f);
    Test->AddInfo(FString::Printf(TEXT("RELEASE blocked_cms=%.1f clear_cms=%.1f after_s=2"),BlockedLimit,States[1].Pace.Traffic));
    Test->TestTrue(TEXT("Temporary traffic slowdown clears within two seconds"),BlockedLimit<1000 && States[1].Pace.Traffic>1500);
    R->RestartRace();
    for(const auto& A:States)Test->TestTrue(TEXT("Reset clears passing and filtered traffic state"),A.PassPhase==EKartPassPhase::Follow && A.PassAttempts==0 && A.CompletedPasses==0 && A.FilteredTrafficSpeed>1500);
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRacePaceTest,"RoadToF1.Racecraft.Pace",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FRacePaceTest::RunTest(const FString&)
{
    ADD_LATENT_AUTOMATION_COMMAND(FEditorLoadMap(TEXT("/Game/RoadToF1/SouthGarda_KartRace")));
    ADD_LATENT_AUTOMATION_COMMAND(FStartPIECommand(false));ADD_LATENT_AUTOMATION_COMMAND(FWaitLatentCommand(1));
    ADD_LATENT_AUTOMATION_COMMAND(FMeasureRacePace(this));ADD_LATENT_AUTOMATION_COMMAND(FEndPlayMapCommand());return true;
}
#endif
