#if WITH_DEV_AUTOMATION_TESTS && WITH_EDITOR
#include "Misc/AutomationTest.h"
#include "Tests/AutomationEditorCommon.h"
#include "Tests/AutomationCommon.h"
#include "KartRaceDirector.h"
#include "KartPawn.h"
#include "RaceLoopSubsystem.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/World.h"
DEFINE_LATENT_AUTOMATION_COMMAND_ONE_PARAMETER(FPackedIncidentMeasure,FAutomationTestBase*,Test);
bool FPackedIncidentMeasure::Update()
{
    auto* W=AutomationCommon::GetAnyGameWorld();
    auto* D=Cast<AKartRaceDirector>(UGameplayStatics::GetActorOfClass(W,AKartRaceDirector::StaticClass()));
    auto* P=Cast<AKartPawn>(UGameplayStatics::GetPlayerPawn(W,0));auto* R=W?W->GetSubsystem<URaceLoopSubsystem>():nullptr;
    if(!D||!P||!R){Test->AddError(TEXT("Incident fixture unavailable"));return true;}
    D->bPaceDiagnostics=true;auto& States=const_cast<TArray<FKartOpponentState>&>(D->GetOpponents());
    for(bool OneSide:{false,true})
    {
        R->Tick(0);R->RestartRace();P->SetDriveInput(1,0);P->Tick(.1f);D->Tick(.05f);P->ResetKart();P->SetActorLocation(FVector(0,-17000,25));
        for(int32 I=0;I<19;++I)
        {
            auto& S=States[I];auto* K=S.Kart.Get();K->SetActorLocation(FVector(I*400,-18000,25));
            if(I>=10){S.Progress.bFinished=true;K->SetRaceFinished();continue;}
            K->SetActorLocation(FVector(-14000,-5280,25));K->SetActorRotation(FRotator::ZeroRotator);
            if(I>0 && !(OneSide && I==1))for(int32 F=0;F<150 && K->GetSpeedKmh()<30;++F){K->SetDriveInput(1,0);K->Tick(.05f);}
            K->SetActorLocation(FVector(I==0?-2000:-2500-I*500,-5280,25));
            if(OneSide && I==1)K->SetActorLocation(FVector(-2000,-5580,25));
            S.Previous=K->GetActorLocation();
            int32 Nearest=0;double Best=1e30;for(int32 J=0;J<D->RoutePoints.Num();++J){const double Dist=FVector::DistSquared2D(K->GetActorLocation(),D->RoutePoints[J]);if(Dist<Best){Best=Dist;Nearest=J;}}
            S.RouteIndex=Nearest;
            const FVector T=(D->RoutePoints[(Nearest+1)%D->RoutePoints.Num()]-D->RoutePoints[Nearest]).GetSafeNormal2D();
            S.Lane=S.DesiredLane=S.ActualLane=FVector::DotProduct(K->GetActorLocation()-D->RoutePoints[Nearest],FVector(-T.Y,T.X,0));S.PreferredLane=0;
            S.FilteredTrafficSpeed=55.f/.036f;S.LaunchSeconds=10;S.LaunchDistance=2000;S.DecisionCooldown=0;
        }
        bool Passed[10]={},Left[10]={},Right[10]={};float Min[10];for(float& V:Min)V=100;
        float ClearTime=0,Recovery[10]={},PassedAt[10]={};int32 First=OneSide?2:1;
        for(int32 F=0;F<720;++F)
        {
            D->Tick(.05f);States[0].Kart->SetDriveInput(0,0,true);if(OneSide)States[1].Kart->SetDriveInput(0,0,true);
            for(int32 I=First;I<10;++I)
            {
                auto& S=States[I];auto* K=S.Kart.Get();K->Tick(.05f);
                if((F%100==0 || F==719))Test->AddInfo(FString::Printf(TEXT("INC_TRACE side%d t%.1f npc%d speed%.1f target%.0f actual%.0f lane%.0f desired%.0f reason%s pos%s contacts%d"),OneSide,F*.05f,I,K->GetSpeedKmh(),S.TargetSpeed,S.ActualLane,S.Lane,S.DesiredLane,S.Pace.Reason,*K->GetActorLocation().ToString(),K->GetCollisionCount()));
                Min[I]=FMath::Min(Min[I],FMath::Abs(K->GetSpeedKmh()));
                if(!Passed[I]){Left[I]|=S.DesiredLane<-200;Right[I]|=S.DesiredLane>200;}
                if(!Passed[I] && K->GetActorLocation().X>-1650){Passed[I]=true;PassedAt[I]=ClearTime=(F+1)*.05f;}
                if(Passed[I] && !Recovery[I] && K->GetSpeedKmh()>49.5f)Recovery[I]=(F+1)*.05f;
            }
        }
        int32 Contacts=0,PassCount=0,L=0,RR=0;float Lowest=100;
        for(int32 I=First;I<10;++I){Contacts+=States[I].Kart->GetCollisionCount();PassCount+=Passed[I];L+=Left[I];RR+=Right[I];Lowest=FMath::Min(Lowest,Min[I]);
            Test->AddInfo(FString::Printf(TEXT("INCIDENT_NPC one_side=%d npc=%d passed=%d min_kmh=%.2f contacts=%d recovered_at_s=%.2f queue_s=%.2f clear_to_90pct_s=%.2f"),OneSide,I,Passed[I],Min[I],States[I].Kart->GetCollisionCount(),Recovery[I],States[I].Battle.LongestQueue,Recovery[I]>0?Recovery[I]-PassedAt[I]:-1.f));}
        Test->AddInfo(FString::Printf(TEXT("INCIDENT one_side=%d passed=%d expected=%d contacts=%d clear_s=%.2f left=%d right=%d min_kmh=%.2f"),OneSide,PassCount,10-First,Contacts,ClearTime,L,RR,Lowest));
        Test->TestEqual(TEXT("Packed incident followers all clear obstruction"),PassCount,10-First);
        Test->TestEqual(TEXT("Packed incident creates no secondary contact"),Contacts,0);
        Test->TestTrue(TEXT("All followers clear within the 30-second incident window"),ClearTime<30);
        for(int32 I=First;I<10;++I)Test->TestTrue(TEXT("Cleared follower recovers 90 percent cap within 10 seconds"),Recovery[I]>0 && Recovery[I]-PassedAt[I]<10);
        if(!OneSide)Test->TestTrue(TEXT("Multiple available bypass corridors are used"),L>0 && RR>0);
    }
    R->RestartRace();for(const auto& S:States)Test->TestTrue(TEXT("F5 clears incident and rejoin state"),S.Battle.IncidentReservation==0 && S.Battle.IncidentEvents==0 && !S.Battle.bRejoining);
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FPackedIncidentTest,"RoadToF1.Racecraft.PackedIncident",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FPackedIncidentTest::RunTest(const FString&)
{
    ADD_LATENT_AUTOMATION_COMMAND(FEditorLoadMap(TEXT("/Game/RoadToF1/SouthGarda_KartRace")));
    ADD_LATENT_AUTOMATION_COMMAND(FStartPIECommand(false));ADD_LATENT_AUTOMATION_COMMAND(FWaitLatentCommand(1));
    ADD_LATENT_AUTOMATION_COMMAND(FPackedIncidentMeasure(this));ADD_LATENT_AUTOMATION_COMMAND(FEndPlayMapCommand());return true;
}
#endif
