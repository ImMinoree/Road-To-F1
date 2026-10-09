#if WITH_DEV_AUTOMATION_TESTS && WITH_EDITOR
#include "Misc/AutomationTest.h"
#include "Tests/AutomationEditorCommon.h"
#include "Tests/AutomationCommon.h"
#include "KartPawn.h"
#include "KartTrainingProfiles.h"
#include "KartTrainingLearner.h"
#include "KartTrainingRecorder.h"
#include "KartRaceDirector.h"
#include "RaceLoopSubsystem.h"
#include "RaceLoopWidget.h"
#include "Blueprint/WidgetBlueprintLibrary.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "UnrealClient.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"

DEFINE_LATENT_AUTOMATION_COMMAND_ONE_PARAMETER(FVerifyKartTrack, FAutomationTestBase*, Test);
bool FVerifyKartTrack::Update()
{
    UWorld* World = AutomationCommon::GetAnyGameWorld();
    if (!World) { Test->AddError(TEXT("PIE world missing")); return true; }
    AKartPawn* Kart = Cast<AKartPawn>(UGameplayStatics::GetPlayerPawn(World, 0));
    URaceLoopSubsystem* Race = World->GetSubsystem<URaceLoopSubsystem>();
    if (!Kart || !Race) { Test->AddError(TEXT("Playable kart or subsystem missing")); return true; }
    Race->Tick(0);
    Test->TestTrue(TEXT("Native track gates activate race"), Race->IsRaceAvailable());
    if (!Race->IsRaceAvailable()) return true;
    Test->TestEqual(TEXT("South Garda has 12 ordered checkpoints"), Race->GetGates().Num(), 13);
    TArray<UUserWidget*> Widgets;
    UWidgetBlueprintLibrary::GetAllWidgetsOfClass(World, Widgets, URaceLoopWidget::StaticClass(), false);
    Test->TestEqual(TEXT("Kart race HUD is present"), Widgets.Num(), 1);
    Race->RestartRace();
    AKartRaceDirector* Director = Cast<AKartRaceDirector>(UGameplayStatics::GetActorOfClass(World, AKartRaceDirector::StaticClass()));
    Test->TestNotNull(TEXT("Race field director exists"), Director);
    if (!Director) return true;
    Test->TestEqual(TEXT("19 opponents spawned"), Director->GetOpponents().Num(), 19);
    Test->TestEqual(TEXT("Player starts twentieth"), Director->GetPlayerPlace(), 20);
    Test->TestEqual(TEXT("Player limit is 57 km/h"), Kart->GetSpeedLimitKmh(), 57.f);
    Test->TestEqual(TEXT("Player has six loaded driver meshes"), Kart->GetDriverMeshCount(), 6);
    TSet<FString> SuitColors;
    SuitColors.Add(Kart->GetSuitColor().ToString());
    for (const auto& State : Director->GetOpponents())
    {
        Test->TestEqual(TEXT("Opponent limit is 55 km/h"), State.Kart->GetSpeedLimitKmh(), 55.f);
        Test->TestEqual(TEXT("Opponent has six driver mesh components"), State.Kart->GetDriverMeshCount(), 6);
        Test->TestFalse(TEXT("Suit differs from player's suit"), State.Kart->GetSuitColor().Equals(Kart->GetSuitColor()));
        SuitColors.Add(State.Kart->GetSuitColor().ToString());
        // Isolate the existing movement/rules regression from parked traffic.
        State.Kart->SetActorEnableCollision(false);
    }
    Test->TestEqual(TEXT("Every racer has a distinct suit colour"), SuitColors.Num(), 20);
    const FVector Start = Kart->GetActorLocation();
    for (int32 Frame = 0; Frame < 600; ++Frame) { Kart->SetDriveInput(1, 0); Kart->Tick(1.f / 60.f); Race->Tick(1.f / 60.f); }
    Test->TestTrue(TEXT("Throttle drives kart along ground"), FVector::Dist2D(Start, Kart->GetActorLocation()) > 900);
    Test->TestTrue(TEXT("Physical movement crosses start and starts timing"), Race->GetProgress().bStarted);
    Test->TestTrue(TEXT("Kart stays at road height"), FMath::Abs(Kart->GetActorLocation().Z - 25) < 15);
    Test->TestTrue(TEXT("Throttle increases speed"), Kart->GetSpeedKmh() > 15);
    for (int32 Frame = 0; Frame < 120; ++Frame) { Kart->SetDriveInput(0, 0, true); Kart->Tick(1.f / 60.f); }
    Test->TestTrue(TEXT("Brake brings kart to rest"), FMath::Abs(Kart->GetSpeedKmh()) < .1f);
    Race->RestartRace();
    Kart->SetActorLocation(FVector(-12000, -5200, 24.5));
    Kart->SetActorRotation(FRotator::ZeroRotator);
    for (int32 Frame = 0; Frame < 600; ++Frame) { Kart->SetDriveInput(1, 0); Kart->Tick(1.f / 60.f); }
    Test->TestTrue(TEXT("Kart passes all grid boxes and finish paint without stopping"), Kart->GetActorLocation().X > -3000);
    Test->TestTrue(TEXT("Full throttle respects player speed limit"), Kart->GetSpeedKmh() <= 57.01f && Kart->GetSpeedKmh() > 55);
    const float BeforeTurn = Kart->GetActorRotation().Yaw;
    Kart->SetDriveInput(1, 1); Kart->Tick(1.f / 60.f);
    const float FirstTurn = FMath::FindDeltaAngleDegrees(BeforeTurn, Kart->GetActorRotation().Yaw);
    Test->TestTrue(TEXT("Digital steering ramps in rather than snapping"), FirstTurn > 0 && FirstTurn < .1f);
    const float AfterFirst = Kart->GetActorRotation().Yaw;
    Kart->Tick(1.f / 60.f);
    Test->TestTrue(TEXT("Steering response builds smoothly across frames"), FMath::FindDeltaAngleDegrees(AfterFirst, Kart->GetActorRotation().Yaw) > FirstTurn);
    Race->RestartRace();
    // Trace the entire exported centreline independently of the gate rules: verify that
    // the imported mesh offers a continuous drivable surface rather than just visuals.
    FString JsonText;
    TSharedPtr<FJsonObject> Manifest;
    const FString Path = FPaths::Combine(FPaths::ProjectDir(), TEXT("../Art/KartLab/exports/manifest.json"));
    if (!FFileHelper::LoadFileToString(JsonText, *Path) || !FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(JsonText), Manifest))
        Test->AddError(TEXT("Track validation path missing"));
    else
    {
        int32 Unsupported = 0;
        FCollisionQueryParams Query(SCENE_QUERY_STAT(KartCircuitValidation), true, Kart);
        for (const auto& Point : Manifest->GetArrayField(TEXT("drivePath")))
        {
            const auto& Values = Point->AsArray();
            FVector P(Values[0]->AsNumber(), Values[1]->AsNumber(), 250);
            FHitResult Hit;
            if (!World->LineTraceSingleByChannel(Hit, P, P - FVector(0, 0, 500), ECC_Visibility, Query) || Hit.ImpactNormal.Z < .9 || FMath::Abs(Hit.ImpactPoint.Z - 2.5) > 10) ++Unsupported;
        }
        Test->TestEqual(TEXT("All 600 route samples have road collision"), Unsupported, 0);
        const auto& Route = Manifest->GetArrayField(TEXT("drivePath"));
        int32 FailedRejoins = 0;
        // Drive across both grass/road edges around the complete circuit, in
        // forward and reverse. This exercises swept body movement, not teleport
        // crossings or a centreline-only collision trace.
        for (int32 Index = 0; Index < Route.Num(); Index += 50)
        {
            const auto& A = Route[Index]->AsArray();
            const auto& B = Route[(Index + 1) % Route.Num()]->AsArray();
            const FVector Center(A[0]->AsNumber(), A[1]->AsNumber(), 18);
            const FVector Tangent = FVector(B[0]->AsNumber() - Center.X, B[1]->AsNumber() - Center.Y, 0).GetSafeNormal();
            const FVector Normal(-Tangent.Y, Tangent.X, 0);
            for (float Side : {-1.f, 1.f}) for (bool ReverseDrive : {false, true})
            {
                Kart->ResetKart();
                const FVector Offroad = Center + Normal * Side * 700;
                const FVector Inward = Normal * -Side;
                Kart->SetActorLocation(Offroad);
                Kart->SetActorRotation((ReverseDrive ? -Inward : Inward).Rotation());
                Kart->SetDriveInput(ReverseDrive ? -1 : 1, 0);
                for (int32 Frame = 0; Frame < 180; ++Frame) Kart->Tick(1.f / 60.f);
                if (FVector::DotProduct(Kart->GetActorLocation() - Offroad, Inward) < 650) ++FailedRejoins;
            }
        }
        Test->TestEqual(TEXT("48 driven grass-to-road rejoins succeed in forward and reverse"), FailedRejoins, 0);
        Race->RestartRace();
    }
    const auto Cross = [&](int32 Index, bool bForward = true)
    {
        const auto& Gate = Race->GetGates()[Index];
        const FVector Center = Gate.Transform.GetLocation();
        const FVector Offset = Gate.Transform.GetUnitAxis(EAxis::X) * 250;
        Kart->SetActorLocation(Center + (bForward ? -Offset : Offset)); Race->Tick(0);
        Kart->SetActorLocation(Center + (bForward ? Offset : -Offset)); Race->Tick(0);
    };
    Cross(0, false);
    Test->TestFalse(TEXT("Reverse crossing cannot start"), Race->GetProgress().bStarted);
    Cross(0); Cross(2); Cross(0);
    Test->TestEqual(TEXT("Skipping a gate cannot complete a lap"), Race->GetProgress().CompletedLaps, 0);
    for (int32 Lap = 0; Lap < 3; ++Lap)
    {
        for (int32 Gate = 1; Gate < 13; ++Gate) { Cross(Gate); Cross(Gate); }
        Cross(0);
    }
    Test->TestTrue(TEXT("Three ordered laps finish on the actual map"), Race->GetProgress().bFinished);
    const double Finished = Race->GetProgress().TotalTime(World->GetTimeSeconds());
    Test->TestEqual(TEXT("Finish freezes total time"), Race->GetProgress().TotalTime(World->GetTimeSeconds() + 60), Finished);
    Kart->SetDriveInput(1, 0); Kart->Tick(.1f);
    Race->RestartRace();
    Test->TestFalse(TEXT("Reset clears finish"), Race->GetProgress().bFinished);
    Test->TestTrue(TEXT("Reset returns kart to spawn"), Kart->GetActorLocation().Equals(Start, 2));
    Test->TestEqual(TEXT("Reset clears kart speed"), Kart->GetSpeedKmh(), 0.f);
    for (const auto& State : Director->GetOpponents()) State.Kart->SetActorEnableCollision(true);
    return true;
}

DEFINE_LATENT_AUTOMATION_COMMAND_ONE_PARAMETER(FVerifyAIRace, FAutomationTestBase*, Test);
bool FVerifyAIRace::Update()
{
    UWorld* World = AutomationCommon::GetAnyGameWorld();
    if (!World) { Test->AddError(TEXT("AI PIE world missing")); return true; }
    AKartPawn* Player = Cast<AKartPawn>(UGameplayStatics::GetPlayerPawn(World, 0));
    AKartRaceDirector* Director = Cast<AKartRaceDirector>(UGameplayStatics::GetActorOfClass(World, AKartRaceDirector::StaticClass()));
    URaceLoopSubsystem* Race = World->GetSubsystem<URaceLoopSubsystem>();
    if (!Director || !Player || !Race) { Test->AddError(TEXT("AI field not available")); return true; }
    Race->Tick(0); Race->RestartRace();
    TSet<FString> Names;
    TSet<int32> Numbers;
    TSet<FString> Profiles;
    for (const auto& Row : Director->GetStandings()) { Names.Add(Row.Name); Numbers.Add(Row.Number); }
    for (const auto& State : Director->GetOpponents()) Profiles.Add(FString::Printf(TEXT("%.4f %.4f %.4f"), State.Aggression, State.CornerSkill, State.PreferredLane));
    Test->TestEqual(TEXT("20 unique driver names in standings"), Names.Num(), 20);
    Test->TestEqual(TEXT("20 unique kart numbers in standings"), Numbers.Num(), 20);
    Test->TestEqual(TEXT("19 individual driving profiles"), Profiles.Num(), 19);
    Director->Tick(.05f);
    Test->TestFalse(TEXT("Field waits for player throttle"), Director->HasStarted());
    Player->SetDriveInput(1, 0); Player->Tick(.1f); Director->Tick(.05f);
    Test->TestTrue(TEXT("Player throttle releases opponents"), Director->HasStarted());
    // Park the player safely off-track while testing actual autonomous driving.
    Player->ResetKart(); Player->SetActorLocation(FVector(0, -12000, 25));
    float PeakSpeed = 0;
    for (int32 Frame = 0; Frame < 12000; ++Frame)
    {
        Director->Tick(.05f);
        for (const auto& State : Director->GetOpponents())
        {
            State.Kart->Tick(.05f);
            PeakSpeed = FMath::Max(PeakSpeed, State.Kart->GetSpeedKmh());
        }
    }
    Director->Tick(0);
    int32 Finished = 0;
    for (const auto& State : Director->GetOpponents())
    {
        if (State.Progress.bFinished) ++Finished;
        Test->AddInfo(FString::Printf(TEXT("AI: laps %d, CP %d, speed %.1f, contacts %d, route %d, lane %.0f, pos %s"), State.Progress.CompletedLaps, State.Progress.NextCheckpoint, State.Kart->GetSpeedKmh(), State.Kart->GetCollisionCount(), State.RouteIndex, State.Lane, *State.Kart->GetActorLocation().ToString()));
    }
    Test->TestEqual(TEXT("All 19 AI drive three ordered laps within ten simulated minutes"), Finished, 19);
    Test->TestTrue(TEXT("AI never exceeds 55 km/h"), PeakSpeed <= 55.01f && PeakSpeed > 50);
    Test->TestEqual(TEXT("Finished AI rank ahead of parked player"), Director->GetPlayerPlace(), 20);
    Race->RestartRace();
    Test->TestFalse(TEXT("F5 reset holds AI field again"), Director->HasStarted());
    for (int32 Index = 0; Index < Director->GetOpponents().Num(); ++Index)
    {
        const auto& State = Director->GetOpponents()[Index];
        Test->TestTrue(TEXT("AI returns to its grid box"), State.Kart->GetActorLocation().Equals(Director->Grid[Index].GetLocation(), 2));
        Test->TestEqual(TEXT("AI lap progress resets"), State.Progress.CompletedLaps, 0);
    }
    return true;
}

DEFINE_LATENT_AUTOMATION_COMMAND_ONE_PARAMETER(FVerifyIncidents, FAutomationTestBase*, Test);
bool FVerifyIncidents::Update()
{
    UWorld* World = AutomationCommon::GetAnyGameWorld();
    if (!World) { Test->AddError(TEXT("Incident test world missing")); return true; }
    AKartPawn* Player = Cast<AKartPawn>(UGameplayStatics::GetPlayerPawn(World, 0));
    AKartRaceDirector* Director = Cast<AKartRaceDirector>(UGameplayStatics::GetActorOfClass(World, AKartRaceDirector::StaticClass()));
    URaceLoopSubsystem* Race = World->GetSubsystem<URaceLoopSubsystem>();
    if (!Player || !Director || Director->GetOpponents().Num() != 19 || !Race) { Test->AddError(TEXT("Incident field missing")); return true; }
    Race->Tick(0); Race->RestartRace();
    for (const auto& State : Director->GetOpponents()) State.Kart->SetActorEnableCollision(false);
    AKartPawn* Other = Director->GetOpponents()[0].Kart.Get();
    Other->SetActorEnableCollision(true);
    Other->SetActorLocation(FVector(-8500, -5200, 24.5)); Other->SetActorRotation(FRotator::ZeroRotator);
    Player->SetActorLocation(FVector(-10000, -5200, 24.5)); Player->SetActorRotation(FRotator::ZeroRotator);
    Player->SetDriveInput(1, 0);
    for (int32 Frame = 0; Frame < 400 && Player->GetCollisionCount() == 0; ++Frame) Player->Tick(1.f / 60.f);
    Test->TestTrue(TEXT("Actual swept rear-end impact registers on both karts"), Player->GetCollisionCount() > 0 && Other->GetCollisionCount() > 0);
    Test->TestTrue(TEXT("Hard impact ignites both karts"), Player->IsBurning() && Other->IsBurning());
    Player->ResetKart();
    Player->ReceiveCollision(200, FVector(-1, 0, 0));
    Test->TestFalse(TEXT("Light bump cannot ignite a kart"), Player->IsBurning());
    Player->ReceiveCollision(1000, FVector(-1, 0, 0));
    Test->TestEqual(TEXT("Contact cooldown prevents duplicate incidents"), Player->GetCollisionCount(), 1);
    Race->RestartRace();
    Test->TestFalse(TEXT("Restart clears fire"), Other->IsBurning());
    const TArray<FTransform> OriginalGrid = Director->Grid;
    Director->Grid[0] = FTransform(FRotator::ZeroRotator, FVector(-7500, -5340, 24.5));
    Director->Grid[1] = FTransform(FRotator::ZeroRotator, FVector(-7500, -5060, 24.5));
    Director->Grid[2] = FTransform(FRotator::ZeroRotator, FVector(-8700, -5200, 24.5));
    Director->ResetField();
    for (int32 Index = 3; Index < 19; ++Index) Director->GetOpponents()[Index].Kart->SetActorLocation(FVector(Index * 400, -12000, 25));
    Player->SetDriveInput(1, 0); Player->Tick(.1f); Director->Tick(.05f);
    Player->ResetKart(); Player->SetActorLocation(FVector(0, -12000, 25));
    for (int32 Index : {0, 1})
    {
        AKartPawn* Blocker = Director->GetOpponents()[Index].Kart.Get();
        Blocker->SetActorEnableCollision(true); Blocker->ReceiveCollision(1000, FVector(-1, 0, 0));
    }
    AKartPawn* Follower = Director->GetOpponents()[2].Kart.Get();
    Follower->SetActorEnableCollision(true);
    float PeakApproach = 0;
    for (int32 Frame = 0; Frame < 100; ++Frame)
    {
        Director->Tick(.05f); Follower->Tick(.05f);
        PeakApproach = FMath::Max(PeakApproach, Follower->GetSpeedKmh());
    }
    Test->TestTrue(TEXT("AI slows for burning collision ahead"), PeakApproach <= 18.5f);
    Test->TestEqual(TEXT("Follower avoids adding another crash to blocked incident"), Follower->GetCollisionCount(), 0);
    Director->Grid = OriginalGrid; Race->RestartRace();
    for (const auto& State : Director->GetOpponents()) State.Kart->SetActorEnableCollision(true);
    Test->TestEqual(TEXT("Leaderboard remains complete after incidents/reset"), Director->GetStandings().Num(), 20);
    FString ScreenshotPath;
    if (FParse::Value(FCommandLine::Get(), TEXT("RacecraftScreenshot="), ScreenshotPath))
    {
        // Optional rendered QA after the collision assertions; never alters saved assets.
        Player->ReceiveCollision(1000, FVector(-1, 0, 0));
        Player->Tick(.1f);
        FScreenshotRequest::RequestScreenshot(ScreenshotPath, true, false);
    }
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FKartIncidentPIETest, "RoadToF1.Kart.IncidentsPIE", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FKartIncidentPIETest::RunTest(const FString& Parameters)
{
    ADD_LATENT_AUTOMATION_COMMAND(FEditorLoadMap(TEXT("/Game/RoadToF1/SouthGarda_KartRace")));
    ADD_LATENT_AUTOMATION_COMMAND(FStartPIECommand(false));
    ADD_LATENT_AUTOMATION_COMMAND(FWaitLatentCommand(2));
    ADD_LATENT_AUTOMATION_COMMAND(FVerifyIncidents(this));
    if (FParse::Param(FCommandLine::Get(), TEXT("RacecraftVisualQA")))
        ADD_LATENT_AUTOMATION_COMMAND(FWaitLatentCommand(2));
    ADD_LATENT_AUTOMATION_COMMAND(FEndPlayMapCommand());
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FKartAIRacePIETest, "RoadToF1.Kart.AIRacePIE", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FKartAIRacePIETest::RunTest(const FString& Parameters)
{
    ADD_LATENT_AUTOMATION_COMMAND(FEditorLoadMap(TEXT("/Game/RoadToF1/SouthGarda_KartRace")));
    ADD_LATENT_AUTOMATION_COMMAND(FStartPIECommand(false));
    ADD_LATENT_AUTOMATION_COMMAND(FWaitLatentCommand(2));
    ADD_LATENT_AUTOMATION_COMMAND(FVerifyAIRace(this));
    ADD_LATENT_AUTOMATION_COMMAND(FEndPlayMapCommand());
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FKartTrackPIETest, "RoadToF1.Kart.SouthGardaPIE", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FKartTrackPIETest::RunTest(const FString& Parameters)
{
    ADD_LATENT_AUTOMATION_COMMAND(FEditorLoadMap(TEXT("/Game/RoadToF1/SouthGarda_KartRace")));
    ADD_LATENT_AUTOMATION_COMMAND(FStartPIECommand(false));
    ADD_LATENT_AUTOMATION_COMMAND(FWaitLatentCommand(2));
    ADD_LATENT_AUTOMATION_COMMAND(FVerifyKartTrack(this));
    ADD_LATENT_AUTOMATION_COMMAND(FEndPlayMapCommand());
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTrainingProfilesTest, "RoadToF1.Training.ProfileValidation", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FTrainingProfilesTest::RunTest(const FString& Parameters)
{
    auto Root = MakeShared<FJsonObject>();
    Root->SetNumberField(TEXT("schema_version"), 1);
    Root->SetStringField(TEXT("track_id"), TEXT("SouthGarda_KartRace"));
    auto Training = MakeShared<FJsonObject>(); Training->SetStringField(TEXT("source"), TEXT("telemetry"));
    Root->SetObjectField(TEXT("training"), Training);
    TArray<TSharedPtr<FJsonValue>> Rows;
    for (int32 Index = 0; Index < 19; ++Index)
    {
        auto Row = MakeShared<FJsonObject>();
        Row->SetNumberField(TEXT("racer_index"), Index + 1);
        Row->SetNumberField(TEXT("aggression"), .3 + Index * .03);
        Row->SetNumberField(TEXT("corner_skill"), .95 + Index * .002);
        Row->SetNumberField(TEXT("preferred_lane_cm"), (Index - 9) * 13);
        Row->SetNumberField(TEXT("decision_seconds"), 1.3 + Index * .1);
        Rows.Add(MakeShared<FJsonValueObject>(Row));
    }
    Root->SetArrayField(TEXT("profiles"), Rows);
    auto Encode = [&]() { FString Text; FJsonSerializer::Serialize(Root, TJsonWriterFactory<>::Create(&Text)); return Text; };
    TArray<FKartTrainingStyle> Profiles;
    TestTrue(TEXT("19 valid varied styles accepted"), FKartTrainingProfiles::Parse(Encode(), TEXT("SouthGarda_KartRace"), Profiles));
    TestEqual(TEXT("19 styles loaded"), Profiles.Num(), 19);
    TestFalse(TEXT("Wrong track rejected"), FKartTrainingProfiles::Parse(Encode(), TEXT("OtherTrack"), Profiles));
    Rows[0]->AsObject()->SetNumberField(TEXT("aggression"), 2);
    TestFalse(TEXT("Unsafe profile rejected atomically"), FKartTrainingProfiles::Parse(Encode(), TEXT("SouthGarda_KartRace"), Profiles));
    TestTrue(TEXT("Rejected profile leaves no partial styles"), Profiles.IsEmpty());
    Rows[0]->AsObject()->SetNumberField(TEXT("aggression"), .3);
    Rows[1]->AsObject()->SetNumberField(TEXT("racer_index"), 1);
    TestFalse(TEXT("Duplicate racer rejected"), FKartTrainingProfiles::Parse(Encode(), TEXT("SouthGarda_KartRace"), Profiles));
    Rows[1]->AsObject()->SetNumberField(TEXT("racer_index"), 2);
    Training->SetStringField(TEXT("source"), TEXT("synthetic_demo"));
    TestFalse(TEXT("Synthetic demo cannot be deployed as learned driving"), FKartTrainingProfiles::Parse(Encode(), TEXT("SouthGarda_KartRace"), Profiles));
    return true;
}

DEFINE_LATENT_AUTOMATION_COMMAND_ONE_PARAMETER(FVerifyTrainingCapture, FAutomationTestBase*, Test);
bool FVerifyTrainingCapture::Update()
{
    UWorld* World = AutomationCommon::GetAnyGameWorld();
    if (!World) { Test->AddError(TEXT("Training PIE world missing")); return true; }
    AKartPawn* Player = Cast<AKartPawn>(UGameplayStatics::GetPlayerPawn(World, 0));
    AKartRaceDirector* Director = Cast<AKartRaceDirector>(UGameplayStatics::GetActorOfClass(World, AKartRaceDirector::StaticClass()));
    if (!Player || !Director) { Test->AddError(TEXT("Training race missing")); return true; }
    UKartTrainingRecorder* Recorder = Director->GetTrainingRecorder();
    Test->TestFalse(TEXT("Collection is off by default"), Recorder->IsRecording());
    Test->TestTrue(TEXT("Explicit capture starts"), Recorder->StartCapture());
    const FString First = Recorder->GetCapturePath();
    Player->SetDriveInput(1, .1f);
    for (int32 Frame = 0; Frame < 20; ++Frame) { Player->Tick(.1f); Recorder->TickComponent(.1f, LEVELTICK_All, nullptr); }
    Recorder->StopCapture();
    Test->TestFalse(TEXT("Capture stop is respected"), Recorder->IsRecording());
    Test->TestTrue(TEXT("Insufficient coverage cannot propose a learned policy"), Recorder->GetCandidatePath().IsEmpty());
    FString Csv;
    Test->TestTrue(TEXT("Native gameplay CSV is readable"), FFileHelper::LoadFileToString(Csv, *First));
    TArray<FString> Lines; Csv.ParseIntoArrayLines(Lines);
    Test->TestEqual(TEXT("10Hz capture plus first sample and CSV header"), Lines.Num(), 22);
    Test->TestTrue(TEXT("Recorder includes context and controls"), Lines[0].Contains(TEXT("curvature,nearest_ahead_cm,relative_speed_kmh")));
    for (const FString& Line : Lines) { TArray<FString> Columns; Line.ParseIntoArray(Columns, TEXT(","), false); Test->TestEqual(TEXT("CSV column alignment"), Columns.Num(), 19); }
    Recorder->StartCapture();
    const FString BeforeReset = Recorder->GetCapturePath();
    for (int32 Frame = 0; Frame < 12; ++Frame) Recorder->TickComponent(.1f, LEVELTICK_All, nullptr);
    World->GetSubsystem<URaceLoopSubsystem>()->RestartRace();
    Test->TestTrue(TEXT("F5 rotates capture into a new session"), Recorder->IsRecording() && Recorder->GetCapturePath() != BeforeReset);
    for (int32 Frame = 0; Frame < 12; ++Frame) Recorder->TickComponent(.1f, LEVELTICK_All, nullptr);
    Recorder->StopCapture();
    Test->TestFalse(TEXT("No approved profiles means unchanged default NPC styles"), Director->HasLearnedStyles());
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTrainingCapturePIETest, "RoadToF1.Training.CapturePIE", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FTrainingCapturePIETest::RunTest(const FString& Parameters)
{
    ADD_LATENT_AUTOMATION_COMMAND(FEditorLoadMap(TEXT("/Game/RoadToF1/SouthGarda_KartRace")));
    ADD_LATENT_AUTOMATION_COMMAND(FStartPIECommand(false));
    ADD_LATENT_AUTOMATION_COMMAND(FWaitLatentCommand(2));
    ADD_LATENT_AUTOMATION_COMMAND(FVerifyTrainingCapture(this));
    ADD_LATENT_AUTOMATION_COMMAND(FEndPlayMapCommand());
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FNativeLearningTest, "RoadToF1.Training.NativeLearning", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FNativeLearningTest::RunTest(const FString& Parameters)
{
    FKartDrivingSummary Summary;
    TestTrue(TEXT("No data produces no candidate"), FKartTrainingLearner::Propose(TEXT("SouthGarda_KartRace"), 42, Summary).IsEmpty());
    Summary = {600, 200, 400, 600 * 38., 600 * .7, 600 * 20., 200 * 25.};
    const FString Proposal = FKartTrainingLearner::Propose(TEXT("SouthGarda_KartRace"), 42, Summary);
    TArray<FKartTrainingStyle> Styles;
    TestTrue(TEXT("Native proposal satisfies deployment schema and diversity"), FKartTrainingProfiles::Parse(Proposal, TEXT("SouthGarda_KartRace"), Styles));
    TestEqual(TEXT("Native proposal contains 19 distinct bounded racers"), Styles.Num(), 19);
    TestEqual(TEXT("Same aggregate and seed are reproducible"), FKartTrainingLearner::Propose(TEXT("SouthGarda_KartRace"), 42, Summary), Proposal);
    TestTrue(TEXT("Different seed changes driver field"), FKartTrainingLearner::Propose(TEXT("SouthGarda_KartRace"), 43, Summary) != Proposal);
    TestFalse(TEXT("Proposal contains no recorded control timeline"), Proposal.Contains(TEXT("steering")) || Proposal.Contains(TEXT("route_index")) || Proposal.Contains(TEXT("time_seconds")));
    Summary.CornerSamples = 0; Summary.StraightSamples = 600;
    TestTrue(TEXT("Straight-only data cannot establish corner skills"), FKartTrainingLearner::Propose(TEXT("SouthGarda_KartRace"), 42, Summary).IsEmpty());
    return true;
}
#endif
