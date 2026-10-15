#if WITH_DEV_AUTOMATION_TESTS && WITH_EDITOR
#include "Misc/AutomationTest.h"
#include "Tests/AutomationEditorCommon.h"
#include "Tests/AutomationCommon.h"
#include "KartRaceDirector.h"
#include "KartPawn.h"
#include "KartTrainingRecorder.h"
#include "Misc/FileHelper.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "RaceLoopSubsystem.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/World.h"

DEFINE_LATENT_AUTOMATION_COMMAND_ONE_PARAMETER(FMeasureBattles, FAutomationTestBase*, Test);
bool FMeasureBattles::Update()
{
    UWorld* W=AutomationCommon::GetAnyGameWorld();
    auto* D=Cast<AKartRaceDirector>(UGameplayStatics::GetActorOfClass(W,AKartRaceDirector::StaticClass()));
    auto* P=Cast<AKartPawn>(UGameplayStatics::GetPlayerPawn(W,0));
    auto* R=W?W->GetSubsystem<URaceLoopSubsystem>():nullptr;
    if(!D||!P||!R){Test->AddError(TEXT("Battle fixture unavailable"));return true;}
    D->bPaceDiagnostics=true;
    auto& States=const_cast<TArray<FKartOpponentState>&>(D->GetOpponents());
    auto& S=States[0];auto* K=S.Kart.Get();
    auto Prepare=[&](float NpcSpeed,float PlayerSpeed,FVector Relative)
    {
        R->Tick(0);R->RestartRace();P->SetDriveInput(1,0);P->Tick(.1f);D->Tick(.05f);P->ResetKart();
        P->SetActorLocation(FVector(0,-17000,25));
        for(int32 I=0;I<19;++I)
        {
            auto& A=States[I];auto* C=A.Kart.Get();C->SetActorLocation(FVector(I*400,-18000,25));
            if(I){A.Progress.bFinished=true;C->SetRaceFinished();}
        }
        auto Warm=[&](AKartPawn* C,float V,float Y)
        {
            C->SetActorLocation(FVector(-14000,Y,25));C->SetActorRotation(FRotator::ZeroRotator);
            for(int32 F=0;F<200 && C->GetSpeedKmh()<V;++F){C->SetDriveInput(1,0);C->Tick(.05f);}
        };
        Warm(K,NpcSpeed,-5280);Warm(P,PlayerSpeed,-4900);
        K->SetActorLocation(FVector(-6500,-5280,25));P->SetActorLocation(K->GetActorLocation()+Relative);
        S.Previous=K->GetActorLocation();S.RouteIndex=0;S.Lane=S.DesiredLane=S.ActualLane=S.PreferredLane=0;
        S.LaunchSeconds=10;S.LaunchDistance=2000;S.DecisionCooldown=0;S.FilteredTrafficSpeed=55.f/.036f;
    };
    Prepare(55,57,FVector(-630,180,0));D->Tick(.05f);
    Test->TestEqual(TEXT("Real 57 versus 55 cap advantage triggers defense before overlap"),S.Battle.Defenses,1);
    float DefenseMin=100;const float Chosen=S.DesiredLane;
    for(int32 F=0;F<130;++F)
    {
        D->Tick(.05f);K->Tick(.05f);P->SetDriveInput(1,0);P->Tick(.05f);DefenseMin=FMath::Min(DefenseMin,K->GetSpeedKmh());
        if(S.Battle.Defense==EKartDefense::Holding)Test->TestTrue(TEXT("Defense retains one selected side"),S.DesiredLane*Chosen>=0);
    }
    Test->AddInfo(FString::Printf(TEXT("DEFENSE_CAP held=%d late=%d alongside=%d min_kmh=%.2f movement_cm=%.2f delay_s=%.2f contacts=%d"),S.Battle.DefenseOutcomes[1],S.Battle.DefenseOutcomes[2],S.Battle.DefenseOutcomes[3],DefenseMin,S.Battle.DefenseMovement,S.Battle.DefenseMoveDelay,K->GetCollisionCount()+P->GetCollisionCount()));
    Test->TestTrue(TEXT("Defender retains useful race speed"),DefenseMin>45);
    Test->TestTrue(TEXT("Controlled cap-speed threat is held through defense window"),S.Battle.DefenseOutcomes[1]>0);
    Test->TestEqual(TEXT("Cap-speed defense remains contact-free"),K->GetCollisionCount()+P->GetCollisionCount(),0);
    Prepare(55,57,FVector(-2500,0,0));D->Tick(.05f);Test->TestEqual(TEXT("Distant attacker does not trigger defense"),S.Battle.Defenses,0);
    Prepare(55,50,FVector(-700,0,0));D->Tick(.05f);Test->TestEqual(TEXT("Non-closing rival does not trigger defense"),S.Battle.Defenses,0);
    Prepare(35,45,FVector(-1250,0,0));D->Tick(.05f);
    Test->TestEqual(TEXT("Closing rear attacker activates bounded defense"),S.Battle.Defenses,1);
    const float DefensiveLane=S.DesiredLane;
    for(int32 F=0;F<30;++F)D->Tick(.05f);
    Test->TestTrue(TEXT("Defense holds one side instead of weaving"),FMath::IsNearlyEqual(S.DesiredLane,DefensiveLane,1) && S.Battle.Defenses==1);
    P->SetActorLocation(K->GetActorLocation()+FVector(0,260,0));D->Tick(.05f);
    Test->TestTrue(TEXT("Defense releases when rival becomes alongside"),S.Battle.Defense!=EKartDefense::Holding && S.Battle.bAlongside);
    Prepare(35,45,FVector(-1250,0,0));
    for(int32 F=0;F<50;++F)
    {
        D->Tick(.05f);K->Tick(.05f);P->SetDriveInput(P->GetSpeedKmh()<45?.7f:0,0,P->GetSpeedKmh()>46);P->Tick(.05f);
    }
    Test->TestEqual(TEXT("Defensive move does not collide with closing attacker"),K->GetCollisionCount()+P->GetCollisionCount(),0);
    Prepare(40,40,FVector(0,280,0));
    float Minimum=100;bool Emergency=false;
    for(int32 F=0;F<60;++F)
    {
        D->Tick(.05f);K->Tick(.05f);P->SetDriveInput(P->GetSpeedKmh()<K->GetSpeedKmh()?1:0,0);P->Tick(.05f);
        Minimum=FMath::Min(Minimum,K->GetSpeedKmh());Emergency|=S.Pace.Obstruction<=400;
    }
    Test->AddInfo(FString::Printf(TEXT("SIDE min_kmh=%.2f contacts=%d alongside_s=%.2f defenses=%d"),Minimum,K->GetCollisionCount()+P->GetCollisionCount(),S.Battle.AlongsideSeconds,S.Battle.Defenses));
    Test->TestEqual(TEXT("Already alongside rival does not trigger a block"),S.Battle.Defenses,0);
    Test->TestEqual(TEXT("Separate physical corridors avoid contact"),K->GetCollisionCount()+P->GetCollisionCount(),0);
    Test->TestFalse(TEXT("Moving player beside NPC is not emergency obstruction"),Emergency);
    Test->TestTrue(TEXT("Alongside racer retains meaningful speed"),Minimum>35);
    Prepare(40,35,FVector(0,280,0));S.PassPhase=EKartPassPhase::Committed;S.PassTarget=P;S.PassSeconds=8;
    D->Tick(.05f);
    Test->TestTrue(TEXT("Committed pass survives safe side overlap"),S.PassPhase==EKartPassPhase::Passing && S.PassTarget.Get()==P);
    S.PassSeconds=.01f;D->Tick(.05f);
    Test->TestTrue(TEXT("Safe advancing alongside pass gets bounded extra clearance time"),S.PassPhase==EKartPassPhase::Passing && S.Battle.PassExtension>0 && S.Battle.PassExtension<=3);
    // The loss transition is deliberately arranged; subsequent driving uses the real controller.
    Prepare(45,30,FVector(-350,0,0));D->Tick(.05f);
    P->SetActorLocation(K->GetActorLocation()+FVector(600,0,0));S.DecisionCooldown=0;
    bool Complete=false;
    for(int32 F=0;F<240;++F)
    {
        D->Tick(.05f);K->Tick(.05f);P->SetDriveInput(P->GetSpeedKmh()<30?.5f:0,0,P->GetSpeedKmh()>31);P->Tick(.05f);
        Complete|=S.Battle.RepassCompletions>0;
    }
    Test->AddInfo(FString::Printf(TEXT("REPASS losses=%d attempts=%d completed=%d contacts=%d"),S.Battle.PositionsLost,S.Battle.RepassAttempts,S.Battle.RepassCompletions,K->GetCollisionCount()+P->GetCollisionCount()));
    Test->TestTrue(TEXT("Recent loss opens a safe repass attempt"),S.Battle.RepassAttempts>0);
    Test->TestTrue(TEXT("NPC completes moving-player repass"),Complete);
    Test->TestEqual(TEXT("Open lane repass has no contact"),K->GetCollisionCount()+P->GetCollisionCount(),0);
    Prepare(40,30,FVector(-350,0,0));D->Tick(.05f);P->SetActorLocation(K->GetActorLocation()+FVector(3000,0,0));D->Tick(.05f);
    Test->TestTrue(TEXT("Remote player never opens repass window"),S.Battle.RepassSeconds==0 && S.Battle.RepassAttempts==0);
    Prepare(25,25,FVector(0,-50,0));K->SetActorLocation(K->GetActorLocation()+FVector(0,250,0));S.DesiredLane=-200;D->Tick(.05f);
    Test->TestTrue(TEXT("Displaced kart stabilizes without rejoining through occupied lane"),S.Battle.bRejoining && S.DesiredLane>150 && S.Lane>150);
    // Corner entry retains an occupied lateral corridor instead of recentering.
    Prepare(25,25,FVector(0,280,0));const int32 Bend=110;
    const FVector Forward=(D->RoutePoints[Bend+1]-D->RoutePoints[Bend]).GetSafeNormal2D();const FVector Side(-Forward.Y,Forward.X,0);
    K->SetActorLocation(D->RoutePoints[Bend]-Side*140);K->SetActorRotation(Forward.Rotation());
    P->SetActorLocation(D->RoutePoints[Bend]+Side*140);P->SetActorRotation(Forward.Rotation());
    S.RouteIndex=Bend;S.Previous=K->GetActorLocation();S.Lane=S.DesiredLane=-140;D->Tick(.05f);
    Test->TestTrue(TEXT("Corner overlap preserves assigned corridor"),S.Battle.bAlongside && S.DesiredLane < -100);
    S.Progress.bFinished=true;D->Tick(.05f);
    Test->TestFalse(TEXT("Finisher is not removed at line"),K->IsHidden());
    for(int32 F=0;F<120;++F){D->Tick(.05f);K->Tick(.05f);}
    Test->TestTrue(TEXT("Stopped finisher presentation retires after cooldown"),K->IsHidden() && S.FinishPlace>0);
    R->RestartRace();
    for(const auto& A:States)Test->TestTrue(TEXT("Restart restores presentation and all battle state"),!A.Kart->IsHidden() && A.Battle.Defenses==0 && A.Battle.RepassSeconds==0 && A.Battle.FinishSeconds==0 && !A.Battle.bAlongside);
    if(FParse::Param(FCommandLine::Get(),TEXT("RaceBattleDebug")))
    {
        auto* Recorder=D->GetTrainingRecorder();
        Test->TestTrue(TEXT("Existing F9 capture starts"),Recorder->StartCapture());
        const FString Original=Recorder->GetCapturePath();D->Tick(.25f);Recorder->StopCapture();D->Tick(0);
        FString Debug,Training;FFileHelper::LoadFileToString(Debug,*(Original+TEXT(".battle-v2.csv")));FFileHelper::LoadFileToString(Training,*Original);
        Test->TestTrue(TEXT("Optional battle snapshot flushes separately"),Debug.Contains(TEXT("schema,time,player_position")) && Debug.Contains(TEXT("2,0.250,")));
        TArray<FString> Rows;Debug.ParseIntoArrayLines(Rows);
        for(const FString& Row:Rows){TArray<FString> Columns;Row.ParseIntoArray(Columns,TEXT(","),false);Test->TestEqual(TEXT("Battle v2 column alignment"),Columns.Num(),74);}
        Test->TestTrue(TEXT("Original training header stays unchanged"),Training.StartsWith(TEXT("time_seconds,session_id,track_id,route_index,lane_cm,speed_kmh,")) && !Training.Contains(TEXT("player_position")));
    }
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBattlesTest,"RoadToF1.Racecraft.Battles",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FBattlesTest::RunTest(const FString&)
{
    ADD_LATENT_AUTOMATION_COMMAND(FEditorLoadMap(TEXT("/Game/RoadToF1/SouthGarda_KartRace")));
    ADD_LATENT_AUTOMATION_COMMAND(FStartPIECommand(false));ADD_LATENT_AUTOMATION_COMMAND(FWaitLatentCommand(1));
    ADD_LATENT_AUTOMATION_COMMAND(FMeasureBattles(this));ADD_LATENT_AUTOMATION_COMMAND(FEndPlayMapCommand());return true;
}
#endif
