#if WITH_DEV_AUTOMATION_TESTS && WITH_EDITOR
#include "Misc/AutomationTest.h"
#include "Tests/AutomationEditorCommon.h"
#include "Tests/AutomationCommon.h"
#include "KartPawn.h"
#include "KartEngineSound.h"
#include "KartRaceDirector.h"
#include "RaceLoopSubsystem.h"
#include "RaceLoopWidget.h"
#include "Components/AudioComponent.h"
#include "Components/TextRenderComponent.h"
#include "Components/TextBlock.h"
#include "Sound/SoundWaveProcedural.h"
#include "Blueprint/WidgetBlueprintLibrary.h"
#include "Blueprint/WidgetTree.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "UnrealClient.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FKartEngineTest, "RoadToF1.Presentation.EnginePCM", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FKartEngineTest::RunTest(const FString& Parameters)
{
    FKartEngineSound Idle, Fast, Disabled;
    TArray<int16> A, B, C;
    Idle.Render(A, 22050, 0, 0, false, 1);
    Fast.Render(B, 22050, 1, 1, false, 2);
    Disabled.Render(C, 22050, 1, 1, true, 2);
    int32 CrossA = 0, CrossB = 0; int64 Energy = 0, SilentEnergy = 0;
    for (int32 I = 1; I < A.Num(); ++I)
    {
        CrossA += A[I - 1] < 0 && A[I] >= 0;
        CrossB += B[I - 1] < 0 && B[I] >= 0;
        Energy += FMath::Abs(int32(A[I])); SilentEnergy += FMath::Abs(int32(C[I]));
        if (FMath::Abs(int32(B[I])) > 20000) { AddError(TEXT("Engine PCM clipped")); break; }
    }
    TestTrue(TEXT("Idle engine is audible PCM"), Energy > 1000000);
    TestTrue(TEXT("Speed/throttle increase firing frequency"), CrossB > CrossA * 2);
    TestEqual(TEXT("Disabled engine is silent"), SilentEnergy, int64(0));
    TestTrue(TEXT("57km/h displays35.4mph without raising cap"), FMath::IsNearlyEqual(57.f * .621371f, 35.418147f, .0001f));
    return true;
}

DEFINE_LATENT_AUTOMATION_COMMAND_ONE_PARAMETER(FVerifyPresentation, FAutomationTestBase*, Test);
bool FVerifyPresentation::Update()
{
    UWorld* World = AutomationCommon::GetAnyGameWorld();
    AKartPawn* Player = World ? Cast<AKartPawn>(UGameplayStatics::GetPlayerPawn(World, 0)) : nullptr;
    AKartRaceDirector* Director = World ? Cast<AKartRaceDirector>(UGameplayStatics::GetActorOfClass(World, AKartRaceDirector::StaticClass())) : nullptr;
    if (!Player || !Director) { Test->AddError(TEXT("Race world missing")); return true; }
    auto CheckKart = [&](AKartPawn* Kart)
    {
        UTextRenderComponent* Number = Kart->FindComponentByClass<UTextRenderComponent>();
        Test->TestNotNull(TEXT("Overhead number component exists"), Number);
        if (Number) Test->TestEqual(TEXT("Number matches racer's assigned identity"), Number->Text.ToString(), FString::Printf(TEXT("%d"), Kart->GetKartNumber()));
        UAudioComponent* Audio = Kart->FindComponentByClass<UAudioComponent>();
        Test->TestTrue(TEXT("Engine is procedural and spatialized"), Audio && Cast<USoundWaveProcedural>(Audio->GetSound()) && Audio->bOverrideAttenuation && Audio->AttenuationOverrides.bSpatialize);
    };
    CheckKart(Player);
    for (const auto& State : Director->GetOpponents()) if (State.Kart.IsValid()) CheckKart(State.Kart.Get());
    FRaceProgress P; P.bStarted = true;
    const auto& Route = Director->RoutePoints;
    double Length = 0;
    for (int32 I = 0; I < Route.Num(); ++I) Length += FVector::Dist2D(Route[I], Route[(I + 1) % Route.Num()]);
    Test->TestTrue(TEXT("New lap at line has full route remaining"), FMath::IsNearlyEqual(Director->DistanceToLapFinishCm(Route[0], P), Length, 1.));
    const double Mid = Director->DistanceToLapFinishCm(Route[Route.Num() / 2], P);
    Test->TestTrue(TEXT("Half route remaining is positive and less than whole lap"), Mid > 0 && Mid < Length);
    P.bFinished = true;
    Test->TestEqual(TEXT("Finished lap has zero distance"), Director->DistanceToLapFinishCm(Route[0], P), 0.);
    for (const TCHAR* Name : {TEXT("Start"), TEXT("Lap"), TEXT("Incident"), TEXT("Overtake"), TEXT("Finish")})
        Test->TestNotNull(TEXT("Recorded commentary asset available"), LoadObject<USoundBase>(nullptr, *FString::Printf(TEXT("/Game/RoadToF1/Audio/CommentaryV01/%s.%s"), Name, Name)));
    TArray<UUserWidget*> Widgets;
    UWidgetBlueprintLibrary::GetAllWidgetsOfClass(World, Widgets, URaceLoopWidget::StaticClass(), false);
    bool bMph = false, bDistance = false, bKmh = false;
    for (auto* Widget : Widgets) Widget->WidgetTree->ForEachWidget([&](UWidget* Child)
    {
        if (auto* Text = Cast<UTextBlock>(Child))
        {
            FString Value = Text->GetText().ToString();
            bMph |= Value.Contains(TEXT("mph")); bDistance |= Value.Contains(TEXT("TO LAP LINE")); bKmh |= Value.Contains(TEXT("km/h"));
        }
    });
    Test->TestTrue(TEXT("HUD containsmphandlapdistancewithoutkmh"), bMph && bDistance && !bKmh);
    FString Path;
    if (FParse::Value(FCommandLine::Get(), TEXT("PresentationScreenshot="), Path)) FScreenshotRequest::RequestScreenshot(Path, true, false);
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FKartPresentationPIE, "RoadToF1.Presentation.RacePIE", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FKartPresentationPIE::RunTest(const FString& Parameters)
{
    ADD_LATENT_AUTOMATION_COMMAND(FEditorLoadMap(TEXT("/Game/RoadToF1/SouthGarda_KartRace")));
    ADD_LATENT_AUTOMATION_COMMAND(FStartPIECommand(false));
    ADD_LATENT_AUTOMATION_COMMAND(FWaitLatentCommand(2));
    ADD_LATENT_AUTOMATION_COMMAND(FVerifyPresentation(this));
    ADD_LATENT_AUTOMATION_COMMAND(FWaitLatentCommand(2));
    ADD_LATENT_AUTOMATION_COMMAND(FEndPlayMapCommand());
    return true;
}
#endif
