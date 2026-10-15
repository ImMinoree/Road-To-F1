#if WITH_DEV_AUTOMATION_TESTS && WITH_EDITOR
#include "Misc/AutomationTest.h"
#include "RaceHUDVisibility.h"
#include "RaceLoopWidget.h"
#include "RaceLoopSubsystem.h"
#include "Tests/AutomationEditorCommon.h"
#include "Tests/AutomationCommon.h"
#include "Blueprint/WidgetBlueprintLibrary.h"
#include "Blueprint/WidgetTree.h"
#include "Components/Border.h"
#include "Engine/World.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/PlayerInput.h"
#include "InputCoreTypes.h"
#include "Kismet/GameplayStatics.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FHUDScheduleTest, "RoadToF1.HUD.VisibilitySchedule", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FHUDScheduleTest::RunTest(const FString& Parameters)
{
    FRaceHUDVisibility V; V.Reset(0);
    auto Run = [&](double Until, bool Started = false, int32 Place = 16, bool Tab = false)
    {
        while (V.LastTime < Until) V.Update(FMath::Min(Until, V.LastTime + .01), Started, Place, Tab, false);
    };
    Run(.25); TestTrue(TEXT("Panels fade in"), V.LeaderAlpha > .99f && V.BriefAlpha > .99f);
    Run(4.9); TestTrue(TEXT("Initial standings hold five seconds"), V.LeaderAlpha > .99f);
    Run(5.5); TestTrue(TEXT("Standings fade over one second"), V.LeaderAlpha > .4f && V.LeaderAlpha < .6f);
    Run(6.5); TestTrue(TEXT("Briefing fades one second after six-second hold"), V.BriefAlpha > .4f && V.BriefAlpha < .6f);
    Run(7.1); TestTrue(TEXT("Both side panels hide"), V.LeaderAlpha == 0 && V.BriefAlpha == 0);
    V.Reset(10); Run(10.1, true); const double Start = 10.01;
    Run(Start + 19.8, true); TestEqual(TEXT("No early periodic reveal"), V.LeaderAlpha, 0.f);
    Run(Start + 20.4, true); TestTrue(TEXT("Twenty-second recurring reveal"), V.LeaderAlpha > .99f);
    Run(Start + 24.2, true); TestEqual(TEXT("Periodic reveal lasts three seconds plus fade"), V.LeaderAlpha, 0.f);
    Run(Start + 24.6, true, 15); TestTrue(TEXT("Gaining position reveals standings"), V.LeaderAlpha > .99f);
    Run(Start + 25, true, 16); TestTrue(TEXT("Losing position extends the same reveal"), V.LeaderAlpha > .99f);
    Run(Start + 29.2, true, 16); TestEqual(TEXT("Retriggers do not leave stale visibility"), V.LeaderAlpha, 0.f);
    Run(Start + 29.6, true, 16, true); TestTrue(TEXT("Tab overrides hidden state"), V.LeaderAlpha > .99f);
    Run(Start + 30, true, 16, false); TestTrue(TEXT("Release resumes fade without new hold"), V.LeaderAlpha < .8f);
    V.Reset(100); TestTrue(TEXT("Reset clears old periodic and position state"), V.LastPlace == -1 && !V.bWasStarted);
    Run(100.3); TestTrue(TEXT("Restart briefing reappears"), V.BriefAlpha > .99f);
    TestEqual(TEXT("Window at front"), FRaceHUDVisibility::FirstRow(1, 20, false), 0);
    TestEqual(TEXT("Window follows middle player"), FRaceHUDVisibility::FirstRow(10, 20, false), 6);
    TestEqual(TEXT("Window at rear"), FRaceHUDVisibility::FirstRow(20, 20, false), 13);
    TestEqual(TEXT("Tab includes full field"), FRaceHUDVisibility::FirstRow(20, 20, true), 0);
    return true;
}

namespace
{
int32 BeforeResetSerial = 0;
URaceLoopWidget* HUD(UWorld* World)
{
    TArray<UUserWidget*> Widgets;
    if (World) UWidgetBlueprintLibrary::GetAllWidgetsOfClass(World, Widgets, URaceLoopWidget::StaticClass(), false);
    auto* Widget = Widgets.Num() ? Cast<URaceLoopWidget>(Widgets[0]) : nullptr;
    // Commandlet PIE has no painted Slate viewport; explicitly synchronize its native HUD frame.
    if (Widget) Widget->RefreshRaceData(Widget->GetCachedGeometry());
    return Widget;
}
}
DEFINE_LATENT_AUTOMATION_COMMAND_ONE_PARAMETER(FHUDPressTab, FAutomationTestBase*, Test);
bool FHUDPressTab::Update()
{
    UWorld* W = AutomationCommon::GetAnyGameWorld(); auto* Widget = HUD(W);
    if (!Widget) { Test->AddError(TEXT("HUD missing")); return true; }
    Test->TestEqual(TEXT("Compact view contains seven racers"), Widget->GetVisibleStandingCount(), 7);
    auto* PC = UGameplayStatics::GetPlayerController(W, 0);
    PC->InputKey(FInputKeyParams(EKeys::Tab, IE_Pressed, 1.));
    return true;
}
DEFINE_LATENT_AUTOMATION_COMMAND_ONE_PARAMETER(FHUDReleaseTab, FAutomationTestBase*, Test);
bool FHUDReleaseTab::Update()
{
    UWorld* W = AutomationCommon::GetAnyGameWorld(); auto* Widget = HUD(W);
    if (!Widget) { Test->AddError(TEXT("HUD missing")); return true; }
    Test->TestEqual(TEXT("Real held Tab shows all twenty racers"), Widget->GetVisibleStandingCount(), 20);
    auto* PC = UGameplayStatics::GetPlayerController(W, 0);
    PC->InputKey(FInputKeyParams(EKeys::Tab, IE_Released, 0.));
    return true;
}
DEFINE_LATENT_AUTOMATION_COMMAND_ONE_PARAMETER(FHUDRestart, FAutomationTestBase*, Test);
bool FHUDRestart::Update()
{
    UWorld* W = AutomationCommon::GetAnyGameWorld(); auto* Widget = HUD(W);
    if (!Widget) { Test->AddError(TEXT("HUD missing")); return true; }
    Test->TestEqual(TEXT("Release restores seven rows"), Widget->GetVisibleStandingCount(), 7);
    const double Now = W->GetTimeSeconds();
    for (int32 I = 0; I < 850; ++I) Widget->UpdatePresentation(Now + I * .01, false, 20, false, false);
    Test->TestEqual(TEXT("Applied UMG standings opacity reaches zero"), Widget->GetLeaderboardOpacity(), 0.f);
    Test->TestEqual(TEXT("Applied UMG briefing opacity reaches zero"), Widget->GetBriefingOpacity(), 0.f);
    for (const TCHAR* Name : {TEXT("PermanentRaceStats"), TEXT("PermanentSpeed")})
    {
        auto* Panel = Widget->WidgetTree->FindWidget(FName(Name));
        Test->TestTrue(TEXT("Permanent HUD survives side panel fades"), Panel && Panel->GetRenderOpacity() == 1);
    }
    BeforeResetSerial = Widget->GetPresentationResetSerial();
    UGameplayStatics::GetPlayerController(W, 0)->InputKey(FInputKeyParams(EKeys::F5, IE_Pressed, 1.));
    return true;
}
DEFINE_LATENT_AUTOMATION_COMMAND_ONE_PARAMETER(FHUDVerifyRestart, FAutomationTestBase*, Test);
bool FHUDVerifyRestart::Update()
{
    UWorld* W = AutomationCommon::GetAnyGameWorld(); auto* Widget = HUD(W);
    Test->TestTrue(TEXT("F5 invokes subsystem presentation reset"), Widget && Widget->GetPresentationResetSerial() > BeforeResetSerial);
    Test->TestTrue(TEXT("Actual F5 input restores briefing"), Widget && Widget->GetBriefingOpacity() > .9f);
    Test->TestTrue(TEXT("Actual F5 input restores standings"), Widget && Widget->GetLeaderboardOpacity() > .9f);
    auto* PC = UGameplayStatics::GetPlayerController(W, 0); PC->InputKey(FInputKeyParams(EKeys::F5, IE_Released, 0.));
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FHUDPIETest, "RoadToF1.HUD.InputAndResetPIE", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FHUDPIETest::RunTest(const FString& Parameters)
{
    ADD_LATENT_AUTOMATION_COMMAND(FEditorLoadMap(TEXT("/Game/RoadToF1/SouthGarda_KartRace")));
    ADD_LATENT_AUTOMATION_COMMAND(FStartPIECommand(false));
    ADD_LATENT_AUTOMATION_COMMAND(FWaitLatentCommand(1));
    ADD_LATENT_AUTOMATION_COMMAND(FHUDPressTab(this));
    ADD_LATENT_AUTOMATION_COMMAND(FWaitLatentCommand(.4f));
    ADD_LATENT_AUTOMATION_COMMAND(FHUDReleaseTab(this));
    ADD_LATENT_AUTOMATION_COMMAND(FWaitLatentCommand(.2f));
    ADD_LATENT_AUTOMATION_COMMAND(FHUDRestart(this));
    ADD_LATENT_AUTOMATION_COMMAND(FWaitLatentCommand(.5));
    ADD_LATENT_AUTOMATION_COMMAND(FHUDVerifyRestart(this));
    ADD_LATENT_AUTOMATION_COMMAND(FEndPlayMapCommand());
    return true;
}
#endif
#if WITH_DEV_AUTOMATION_TESTS && WITH_EDITOR
#include "HAL/IConsoleManager.h"
#include "Engine/GameViewportClient.h"
#include "TimerManager.h"
#include "Misc/Paths.h"
// Explicit development-only visual fixture. Never runs in normal play or shipping builds.
static FAutoConsoleCommandWithWorldAndArgs HUDCaptureCommand(
    TEXT("RoadToF1.HUDCapture"), TEXT("Capture HUD start, hidden, Tab and restart states to a directory."),
    FConsoleCommandWithWorldAndArgsDelegate::CreateLambda([](const TArray<FString>& Args, UWorld* World)
    {
        if (!World || Args.IsEmpty()) return;
        const FString Directory = Args[0];
        auto Later = [World](float Delay, TFunction<void()> Action)
        {
            FTimerHandle Handle;
            World->GetTimerManager().SetTimer(Handle, FTimerDelegate::CreateLambda([Action]() { Action(); }), Delay, false);
        };
        auto Shot = [Directory](const TCHAR* Name) { FScreenshotRequest::RequestScreenshot(FPaths::Combine(Directory, Name), true, false); };
        TWeakObjectPtr<UWorld> WeakWorld(World);
        auto Key = [WeakWorld](FKey Key, EInputEvent Event)
        {
            if (WeakWorld.IsValid()) if (auto* PC = UGameplayStatics::GetPlayerController(WeakWorld.Get(), 0))
                PC->InputKey(FInputKeyParams(Key, Event, Event == IE_Pressed ? 1. : 0.));
        };
        Later(2, [Shot]() { Shot(TEXT("Initial.png")); });
        Later(8, [Shot]() { Shot(TEXT("Minimal.png")); });
        Later(9, [Key]() { Key(EKeys::Tab, IE_Pressed); });
        Later(10, [Shot]() { Shot(TEXT("FullField.png")); });
        Later(11, [Key]() { Key(EKeys::Tab, IE_Released); });
        Later(12, [Key]() { Key(EKeys::F5, IE_Pressed); });
        Later(12.1f, [Key]() { Key(EKeys::F5, IE_Released); });
        Later(14, [Shot]() { Shot(TEXT("Restart.png")); });
    }));
#endif
