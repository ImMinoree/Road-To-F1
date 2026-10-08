#include "RaceLoopWidget.h"
#include "RaceLoopSubsystem.h"
#include "KartPawn.h"
#include "Kismet/GameplayStatics.h"
#include "Blueprint/WidgetTree.h"
#include "Components/Border.h"
#include "Components/Button.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"
#include "Engine/World.h"

namespace
{
FString FormatRaceTime(double Seconds)
{
    const int64 Milliseconds = FMath::FloorToInt64(Seconds * 1000.0);
    return FString::Printf(TEXT("%02lld:%02lld.%03lld"), Milliseconds / 60000, (Milliseconds / 1000) % 60, Milliseconds % 1000);
}
}

UTextBlock* URaceLoopWidget::AddLine(UVerticalBox* Box, const FString& Text, int32 FontSize)
{
    UTextBlock* Line = WidgetTree->ConstructWidget<UTextBlock>();
    Line->SetText(FText::FromString(Text));
    FSlateFontInfo Font = Line->GetFont();
    Font.Size = FontSize;
    Line->SetFont(Font);
    Line->SetColorAndOpacity(FSlateColor(FLinearColor::White));
    Line->SetAutoWrapText(true);
    Box->AddChildToVerticalBox(Line)->SetPadding(FMargin(0, 3));
    return Line;
}

void URaceLoopWidget::NativeOnInitialized()
{
    Super::NativeOnInitialized();
    UBorder* Panel = WidgetTree->ConstructWidget<UBorder>();
    Panel->SetBrushColor(FLinearColor(0.015f, 0.025f, 0.045f, 0.92f));
    Panel->SetPadding(FMargin(18));
    WidgetTree->RootWidget = Panel;
    UVerticalBox* Lines = WidgetTree->ConstructWidget<UVerticalBox>();
    Panel->SetContent(Lines);
    const bool bKartTrack = GetWorld()->GetMapName().EndsWith(TEXT("SouthGarda_KartRace"));
    AddLine(Lines, bKartTrack ? TEXT("ROAD TO F1 | SOUTH GARDA") : TEXT("ROAD TO F1 | RACE PROTOTYPE"), 18);
    Status = AddLine(Lines, TEXT("Cross START to begin"), 20);
    Lap = AddLine(Lines, TEXT("Lap 0 / 3"), 24);
    Checkpoints = AddLine(Lines, TEXT("Checkpoints 0 / 3"), 18);
    LapTimer = AddLine(Lines, TEXT("Lap    00:00.000"), 22);
    RaceTimer = AddLine(Lines, TEXT("Total  00:00.000"), 22);
    LastLap = AddLine(Lines, TEXT("Last lap --:--.---"), 18);
    AddLine(Lines, TEXT("Pass checkpoints in order. Follow the green gate."), 14);
    if (bKartTrack)
    {
        Speed = AddLine(Lines, TEXT("0 km/h"), 20);
        AddLine(Lines, TEXT("W: accelerate | S: brake / reverse\nA/D: steer | Space: brake | F5: restart"), 14);
    }
    UButton* Restart = WidgetTree->ConstructWidget<UButton>();
    UTextBlock* Label = WidgetTree->ConstructWidget<UTextBlock>();
    Label->SetText(FText::FromString(TEXT("Restart race [F5]")));
    Label->SetColorAndOpacity(FSlateColor(FLinearColor::Black));
    Restart->SetContent(Label);
    Restart->OnClicked.AddDynamic(this, &URaceLoopWidget::OnRestartClicked);
    Lines->AddChildToVerticalBox(Restart)->SetPadding(FMargin(0, 10, 0, 0));
}

void URaceLoopWidget::NativeTick(const FGeometry& Geometry, float DeltaTime)
{
    Super::NativeTick(Geometry, DeltaTime);
    const URaceLoopSubsystem* Race = GetWorld()->GetSubsystem<URaceLoopSubsystem>();
    if (!Race || !Status) return;
    const FRaceProgress& P = Race->GetProgress();
    const double Now = GetWorld()->GetTimeSeconds();
    if (Speed)
        if (const AKartPawn* Kart = Cast<AKartPawn>(UGameplayStatics::GetPlayerPawn(GetWorld(), 0)))
            Speed->SetText(FText::FromString(FString::Printf(TEXT("%d km/h"), FMath::RoundToInt(FMath::Abs(Kart->GetSpeedKmh())))));
    Status->SetText(FText::FromString(!Race->IsRaceAvailable() ? Race->GetStatusMessage() :
        P.bFinished ? TEXT("FINISHED - F5 to race again") : P.bStarted ? TEXT("RACING") : TEXT("Cross START to begin")));
    Status->SetColorAndOpacity(FSlateColor(P.bFinished ? FLinearColor(0.2f, 1, 0.5f) : FLinearColor::White));
    Lap->SetText(FText::FromString(FString::Printf(TEXT("Lap %d / %d"), P.CurrentLap(), P.TargetLaps)));
    Checkpoints->SetText(FText::FromString(P.bFinished ? TEXT("All laps complete") :
        FString::Printf(TEXT("Checkpoints %d / %d | Next: %s"), P.NextCheckpoint, P.CheckpointCount,
            P.bStarted && P.NextCheckpoint < P.CheckpointCount ? *FString::Printf(TEXT("CP%d"), P.NextCheckpoint + 1) : TEXT("START / FINISH"))));
    LapTimer->SetText(FText::FromString(TEXT("Lap    ") + FormatRaceTime(P.LapTime(Now))));
    RaceTimer->SetText(FText::FromString(TEXT("Total  ") + FormatRaceTime(P.TotalTime(Now))));
    LastLap->SetText(FText::FromString(TEXT("Last lap ") + (P.LapTimes.IsEmpty() ? FString(TEXT("--:--.---")) : FormatRaceTime(P.LapTimes.Last()))));
}

void URaceLoopWidget::OnRestartClicked()
{
    if (URaceLoopSubsystem* Race = GetWorld()->GetSubsystem<URaceLoopSubsystem>()) Race->RestartRace();
}
