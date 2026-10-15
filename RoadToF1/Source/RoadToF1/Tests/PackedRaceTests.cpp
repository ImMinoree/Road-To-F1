#if WITH_DEV_AUTOMATION_TESTS && WITH_EDITOR
#include "Misc/AutomationTest.h"
#include "Tests/AutomationEditorCommon.h"
#include "Tests/AutomationCommon.h"
#include "KartPawn.h"
#include "KartRaceDirector.h"
#include "RaceLoopSubsystem.h"
#include "Engine/World.h"
#include "Components/PrimitiveComponent.h"
#include "Kismet/GameplayStatics.h"

DEFINE_LATENT_AUTOMATION_COMMAND_ONE_PARAMETER(FVerifyPackedRace, FAutomationTestBase*, Test);
bool FVerifyPackedRace::Update()
{
    UWorld* W = AutomationCommon::GetAnyGameWorld();
    auto* D = Cast<AKartRaceDirector>(UGameplayStatics::GetActorOfClass(W, AKartRaceDirector::StaticClass()));
    auto* P = Cast<AKartPawn>(UGameplayStatics::GetPlayerPawn(W, 0));
    auto* R = W ? W->GetSubsystem<URaceLoopSubsystem>() : nullptr;
    if (!D || !P || !R) { Test->AddError(TEXT("Packed race fixture missing")); return true; }
    R->Tick(0); R->RestartRace();
    P->SetDriveInput(-1, 0); P->Tick(.1f); D->Tick(.05f);
    Test->TestFalse(TEXT("Reverse player movement must not release field"), D->HasStarted());
    R->RestartRace(); P->SetDriveInput(1, 0); P->Tick(.1f); D->Tick(.05f);
    Test->TestTrue(TEXT("Intentional forward throttle releases field"), D->HasStarted());
    float MaxLaunchError = 0;
    for (const auto& S : D->GetOpponents())
    {
        const auto I = S.RouteIndex;
        const FVector T = (D->RoutePoints[(I+1)%D->RoutePoints.Num()] - D->RoutePoints[I]).GetSafeNormal2D();
        const float Actual = FVector::DotProduct(S.Kart->GetActorLocation()-D->RoutePoints[I], FVector(-T.Y,T.X,0));
        MaxLaunchError = FMath::Max(MaxLaunchError, FMath::Abs(Actual-S.Lane));
    }
    Test->AddInfo(FString::Printf(TEXT("Initial lane mismatch %.1f cm"), MaxLaunchError));
    Test->TestTrue(TEXT("Launch lanes match physical grid corridors"), MaxLaunchError < 5);
    // Hold traffic still to model a legitimate queue with an occupied rear corridor.
    P->ResetKart(); P->SetActorLocation(FVector(0,-12000,25));
    auto* Follower = D->GetOpponents()[2].Kart.Get();
    auto* Front = D->GetOpponents()[0].Kart.Get();
    auto* Rear = D->GetOpponents()[4].Kart.Get();
    Follower->SetActorLocation(FVector(-9000,-5400,25)); Follower->SetActorRotation(FRotator::ZeroRotator);
    Front->SetActorLocation(FVector(-8740,-5400,25)); Rear->SetActorLocation(FVector(-9260,-5400,25));
    bool Reversed = false;
    for(int32 I=0; I<240; ++I) { D->Tick(.05f); Reversed |= Follower->GetThrottleInput()<0; }
    Test->TestFalse(TEXT("Queued NPC must not reverse into rear traffic"), Reversed);

    R->RestartRace();
    P->SetDriveInput(1,0); P->Tick(.1f); P->SetDriveInput(0,0); D->Tick(.05f);
    Test->TestFalse(TEXT("Forward rolling without throttle cannot release field"), D->HasStarted());
    R->RestartRace(); P->SetActorRotation(FRotator(0,180,0)); P->SetDriveInput(1,0); P->Tick(.1f); D->Tick(.05f);
    Test->TestFalse(TEXT("Throttle pointing against grid direction cannot release field"), D->HasStarted());
    R->RestartRace(); P->ReceiveCollision(200,FVector(0,1,0)); P->SetDriveInput(1,0); D->Tick(.05f);
    Test->TestFalse(TEXT("Contact cannot release field"), D->HasStarted());
    R->RestartRace();
    float EarlyLaneDrift = 0; int32 LaunchContacts = 0; bool ReportedContact=false;
    TArray<float> InitialLanes;
    for(const auto& S:D->GetOpponents()) InitialLanes.Add(S.Lane);
    for(int32 Frame=0;Frame<160;++Frame)
    {
        P->SetDriveInput(1,0); P->Tick(.05f); R->Tick(.05f); D->Tick(.05f);
        if(P->GetCollisionCount()>0 && !ReportedContact) {Test->AddInfo(FString::Printf(TEXT("Player launch contact at %.2fs at %s"),Frame*.05,*P->GetActorLocation().ToString()));ReportedContact=true;}
        for(int32 I=0;I<19;++I)
        {
            const auto& S=D->GetOpponents()[I]; S.Kart->Tick(.05f);
            if(Frame<20) EarlyLaneDrift=FMath::Max(EarlyLaneDrift,FMath::Max(FMath::Abs(S.Lane-InitialLanes[I]),FMath::Abs(S.ActualLane-InitialLanes[I])));
        }
    }
    for(const auto& S:D->GetOpponents()) {LaunchContacts+=S.Kart->GetCollisionCount(); if(S.Kart->GetCollisionCount()) Test->AddInfo(FString::Printf(TEXT("Launch contact NPC%d lane%.0f pos%s"),S.Kart->GetKartNumber(),S.Lane,*S.Kart->GetActorLocation().ToString()));}
    Test->AddInfo(FString::Printf(TEXT("20-kart 8s launch: contacts %d, first-second lane drift %.1f cm"),LaunchContacts,EarlyLaneDrift));
    Test->TestTrue(TEXT("Launch has no synchronized inward lane collapse"),EarlyLaneDrift<15);
    Test->TestEqual(TEXT("Controlled normal 20-kart launch has no contacts"),LaunchContacts+P->GetCollisionCount(),0);

    // Seed controlled occupancy fixtures, deliberately including stale planner state after a shove.
    auto& S=const_cast<FKartOpponentState&>(D->GetOpponents()[0]);
    AKartPawn* Subject=S.Kart.Get();
    auto Fixture=[&]()
    {
        R->RestartRace(); P->SetDriveInput(1,0); P->Tick(.1f); D->Tick(.05f);
        P->ResetKart(); P->SetActorLocation(FVector(0,-15000,25));
        for(int32 I=0;I<19;++I) D->GetOpponents()[I].Kart->SetActorLocation(FVector(I*400,-16000,25));
        Subject->SetActorLocation(FVector(-10000,-5280,25)); Subject->SetActorRotation(FRotator::ZeroRotator);
        int32 Near=0; double Best=1e30;
        for(int32 I=0;I<D->RoutePoints.Num();++I) { const double Dist=FVector::DistSquared2D(Subject->GetActorLocation(),D->RoutePoints[I]); if(Dist<Best){Best=Dist;Near=I;} }
        S.RouteIndex=Near; S.Previous=Subject->GetActorLocation(); S.LaunchSeconds=10; S.LaunchDistance=2000;
        S.Lane=S.DesiredLane=S.PreferredLane=0; S.DecisionCooldown=0;
    };
    Fixture(); bool SawReverse=false;
    for(int32 I=0;I<90;++I) { D->Tick(.05f); SawReverse |= Subject->GetThrottleInput()<0; }
    Test->TestTrue(TEXT("Genuinely immobilized unqueued kart requests bounded recovery"),SawReverse);
    auto* Blocker=D->GetOpponents()[1].Kart.Get();
    Blocker->SetActorLocation(Subject->GetActorLocation()-Subject->GetActorForwardVector()*280);
    D->Tick(.05f);
    Test->TestTrue(TEXT("New rear traffic aborts active reverse immediately"),Subject->GetThrottleInput()>=0 && S.RecoverySeconds==0);
    Test->TestTrue(TEXT("Recovery abort starts hysteresis cooldown"),S.RecoveryCooldown>0);
    Fixture();
    const FVector RecoveryStart=Subject->GetActorLocation();
    for(int32 I=0;I<70;++I) D->Tick(.05f);
    for(int32 I=0;I<200;++I) {D->Tick(.05f);Subject->Tick(.05f);}
    Test->TestTrue(TEXT("Freed stuck kart resumes real forward progress after bounded reverse"),Subject->GetActorLocation().X>RecoveryStart.X+500);
    Fixture(); Blocker->SetActorLocation(Subject->GetActorLocation()-Subject->GetActorForwardVector()*280);
    SawReverse=false;
    for(int32 I=0;I<160;++I){D->Tick(.05f);SawReverse|=Subject->GetThrottleInput()<0;}
    Test->TestFalse(TEXT("Stuck kart cannot begin reverse into rear occupancy"),SawReverse);
    Fixture(); Subject->ReceiveCollision(200,FVector(0,1,0)); D->Tick(.05f);
    Test->TestTrue(TEXT("Contact recovery brakes instead of reversing"),Subject->IsBrakeHeld() && S.RecoverySeconds==0);
    Subject->Tick(.25f); D->Tick(.05f);
    Test->TestTrue(TEXT("Light-contact recovery resumes forward driving"),Subject->GetThrottleInput()>0);

    Fixture();
    const FVector Center=Subject->GetActorLocation();
    Subject->SetActorLocation(Center+FVector(0,240,0));
    S.Lane=S.DesiredLane=-200; S.DecisionCooldown=5;
    Blocker->SetActorLocation(Center);
    D->Tick(.05f);
    Test->TestTrue(TEXT("Displaced kart measures its real positive lateral position"),S.ActualLane>200);
    Test->TestTrue(TEXT("Displaced kart does not cross occupied middle to old planned lane"),S.DesiredLane>150 && S.Lane>150);

    auto Avoid=[&](bool Two, bool Slow)
    {
        Fixture();
        const FVector Start=Subject->GetActorLocation();
        Blocker->SetActorLocation(Start+FVector(650,Two ? -80:0,0)); Blocker->SetActorRotation(FRotator::ZeroRotator);
        auto* Second=D->GetOpponents()[2].Kart.Get();
        if(Two) {Second->SetActorLocation(Start+FVector(650,80,0));Second->SetActorRotation(FRotator::ZeroRotator);}
        bool ReversedInQueue=false;
        for(int32 I=0;I<360;++I)
        {
            D->Tick(.05f); Subject->Tick(.05f);
            if(Slow) { Blocker->SetDriveInput(Blocker->GetSpeedKmh()<12 ? .25f:0,0,Blocker->GetSpeedKmh()>13); Blocker->Tick(.05f); }
            if(I%60==0) Test->AddInfo(FString::Printf(TEXT("Avoid frame%d lane%.0f desired%.0f actual%.0f speed%.1f target%.0f yaw%.0f gap%s"),I,S.Lane,S.DesiredLane,S.ActualLane,Subject->GetSpeedKmh(),S.TargetSpeed,Subject->GetActorRotation().Yaw,*(Blocker->GetActorLocation()-Subject->GetActorLocation()).ToString()));
            ReversedInQueue |= S.bQueued && Subject->GetThrottleInput()<0;
        }
        Test->AddInfo(FString::Printf(TEXT("Avoid two=%d slow=%d: travel %.0f contacts %d lane %.0f"),Two,Slow,Subject->GetActorLocation().X-Start.X,Subject->GetCollisionCount(),S.Lane));
        Test->TestTrue(Two ? TEXT("Navigates two non-burning stopped karts where road is open") : TEXT("Passes non-burning slow/stopped kart"), Subject->GetActorLocation().X>Blocker->GetActorLocation().X+250);
        Test->TestFalse(TEXT("Obstruction following never reverses in queue"),ReversedInQueue);
        Test->TestEqual(TEXT("Controlled blockage avoidance has no impact"),Subject->GetCollisionCount(),0);
    };
    Avoid(false,false); Avoid(false,true); Avoid(true,false);

    Fixture();
    for(int32 I=0;I<80;++I){Subject->SetDriveInput(1,0);Subject->Tick(.05f);}
    const float BeforeFinish=Subject->GetSpeedKmh();
    S.Progress.CrossGate(0,0);
    for(int32 Lap=0;Lap<3;++Lap){for(int32 Gate=1;Gate<=12;++Gate)S.Progress.CrossGate(Gate,10+Lap*20+Gate);S.Progress.CrossGate(0,30+Lap*20);}
    D->Tick(.05f); const int32 FinishPlace=S.FinishPlace;
    Test->TestTrue(TEXT("Finished NPC enters post-finish state"),Subject->IsRaceFinished() && Subject->GetThrottleInput()==0);
    Subject->Tick(.05f);
    Test->TestTrue(TEXT("Finisher decelerates progressively"),Subject->GetSpeedKmh()>0 && Subject->GetSpeedKmh()<BeforeFinish);
    Blocker->SetActorLocation(Subject->GetActorLocation()+Subject->GetActorForwardVector()*300);
    const int32 Contacts=Subject->GetCollisionCount();
    for(int32 I=0;I<120;++I){D->Tick(.05f);Subject->Tick(.05f);}
    Test->TestEqual(TEXT("Finisher coasts to rest without hitting stopped racer"),Subject->GetCollisionCount(),Contacts);
    Test->TestTrue(TEXT("Finisher stops"),FMath::Abs(Subject->GetSpeedKmh())<.1f);
    Test->TestEqual(TEXT("Official finishing place remains frozen"),S.FinishPlace,FinishPlace);
    // Exercise the player's real ordered-gate path to finish and verify its frozen rank.
    R->RestartRace();
    P->SetDriveInput(1,0); P->Tick(.1f); D->Tick(.05f);
    auto Cross=[&](int32 I){const auto& G=R->GetGates()[I]; const FVector C=G.Transform.GetLocation(), V=G.Transform.GetUnitAxis(EAxis::X)*250;
        P->SetActorLocation(C-V);R->Tick(0);P->SetActorLocation(C+V);R->Tick(0);};
    Cross(0);for(int32 Lap=0;Lap<3;++Lap){for(int32 I=1;I<=12;++I)Cross(I);Cross(0);}D->Tick(.05f);
    const int32 Place=D->GetPlayerPlace(); const double Time=R->GetProgress().TotalTime(W->GetTimeSeconds());
    Test->TestEqual(TEXT("Player receives first official place after a valid race launch"),Place,1);
    P->SetActorLocation(FVector(0,-15000,25)); D->Tick(.05f);
    Test->TestTrue(TEXT("Player finisher receives collision-safe state"),P->IsRaceFinished());
    Test->TestEqual(TEXT("Player final place stays frozen"),D->GetPlayerPlace(),Place);
    Test->TestEqual(TEXT("Player final time stays frozen"),R->GetProgress().TotalTime(W->GetTimeSeconds()+100),Time);
    R->RestartRace();
    Test->TestFalse(TEXT("F5 reset restores player racing state"),P->IsRaceFinished());
    Test->TestTrue(TEXT("F5 restores player kart collision"),Cast<UPrimitiveComponent>(P->GetRootComponent())->GetCollisionResponseToChannel(ECC_Pawn)==ECR_Block);
    for(const auto& A:D->GetOpponents()) Test->TestTrue(TEXT("F5 clears opponent finish/recovery/launch state"),!A.Kart->IsRaceFinished() && A.FinishPlace==0 && A.RecoveryCooldown==0 && A.RecoverySeconds==0 && A.LaunchSeconds==0);

    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FPackedRaceTest, "RoadToF1.Racecraft.PackedSafety", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FPackedRaceTest::RunTest(const FString& Parameters)
{
    ADD_LATENT_AUTOMATION_COMMAND(FEditorLoadMap(TEXT("/Game/RoadToF1/SouthGarda_KartRace")));
    ADD_LATENT_AUTOMATION_COMMAND(FStartPIECommand(false));
    ADD_LATENT_AUTOMATION_COMMAND(FWaitLatentCommand(1));
    ADD_LATENT_AUTOMATION_COMMAND(FVerifyPackedRace(this));
    ADD_LATENT_AUTOMATION_COMMAND(FEndPlayMapCommand());
    return true;
}
#endif
