#include "RaceLoopWidget.h"
#include "RaceLoopSubsystem.h"
#include "KartPawn.h"
#include "KartRaceDirector.h"
#include "Kismet/GameplayStatics.h"
#include "Blueprint/WidgetTree.h"
#include "Components/Border.h"
#include "Components/Button.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/HorizontalBox.h"
#include "Components/HorizontalBoxSlot.h"
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
    const bool bKartTrack = GetWorld()->GetMapName().EndsWith(TEXT("SouthGarda_KartRace"));
    UBorder* Panel = WidgetTree->ConstructWidget<UBorder>();
    Panel->SetBrushColor(FLinearColor(0.015f, 0.025f, 0.045f, 0.92f));
    Panel->SetPadding(FMargin(18));
    WidgetTree->RootWidget = Panel;
    UVerticalBox* Lines = WidgetTree->ConstructWidget<UVerticalBox>();
    Panel->SetContent(Lines);
    if (bKartTrack)
    {
        UCanvasPanel* Canvas = WidgetTree->ConstructWidget<UCanvasPanel>();
        WidgetTree->RootWidget = Canvas;
        UCanvasPanelSlot* InfoSlot = Canvas->AddChildToCanvas(Panel);
        InfoSlot->SetAnchors(FAnchors(1, 0)); InfoSlot->SetAlignment(FVector2D(1, 0));
        InfoSlot->SetPosition(FVector2D(-20, 20)); InfoSlot->SetSize(FVector2D(340, 640));
        UBorder* Tower = WidgetTree->ConstructWidget<UBorder>();
        Tower->SetBrushColor(FLinearColor(.012f, .018f, .03f, .94f)); Tower->SetPadding(FMargin(10));
        UCanvasPanelSlot* TowerSlot = Canvas->AddChildToCanvas(Tower);
        TowerSlot->SetPosition(FVector2D(20, 20)); TowerSlot->SetSize(FVector2D(315, 620));
        UVerticalBox* Table = WidgetTree->ConstructWidget<UVerticalBox>(); Tower->SetContent(Table);
        AddLine(Table, TEXT("ROAD TO F1 | LIVE ORDER"), 16);
        AddLine(Table, TEXT("POS  KART     DRIVER                  SPEED"), 11);
        for (int32 Index = 0; Index < 20; ++Index)
        {
            UBorder* Row = WidgetTree->ConstructWidget<UBorder>(); Row->SetPadding(FMargin(5, 4));
            UHorizontalBox* Cells = WidgetTree->ConstructWidget<UHorizontalBox>(); Row->SetContent(Cells);
            auto Cell = [&](float Width, bool Fill)
            {
                UTextBlock* Text = WidgetTree->ConstructWidget<UTextBlock>();
                FSlateFontInfo Font = Text->GetFont(); Font.Size = 11; Text->SetFont(Font);
                Text->SetColorAndOpacity(FSlateColor(FLinearColor::White));
                UHorizontalBoxSlot* Slot = Cells->AddChildToHorizontalBox(Text);
                Slot->SetSize(FSlateChildSize(Fill ? ESlateSizeRule::Fill : ESlateSizeRule::Automatic));
                if (!Fill) Text->SetMinDesiredWidth(Width);
                return Text;
            };
            UTextBlock* Number = Cell(55, false);
            UTextBlock* Name = Cell(0, true);
            UTextBlock* SpeedText = Cell(60, false);
            StandingNumbers.Add(Number); StandingNames.Add(Name); StandingSpeeds.Add(SpeedText); StandingRows.Add(Row);
            Table->AddChildToVerticalBox(Row)->SetPadding(FMargin(0, 1));
        }
    }
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
        Position = AddLine(Lines, TEXT("Position 20 / 20"), 20);
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
    if (const AKartRaceDirector* Director = Cast<AKartRaceDirector>(UGameplayStatics::GetActorOfClass(GetWorld(), AKartRaceDirector::StaticClass())))
    {
        const auto Rows = Director->GetStandings();
        for (int32 Index = 0; Index < Rows.Num() && Index < StandingNames.Num(); ++Index)
        {
            const auto& Row = Rows[Index];
            StandingNumbers[Index]->SetText(FText::FromString(FString::Printf(TEXT("%02d #%02d"), Row.Position, Row.Number)));
            StandingNames[Index]->SetText(FText::FromString(Row.Name));
            StandingNames[Index]->SetColorAndOpacity(FSlateColor(Row.bPlayer ? FLinearColor::White : Row.Color.Desaturate(.45f) * 1.8f));
            StandingSpeeds[Index]->SetText(FText::FromString(FString::Printf(TEXT("%02d km/h"), FMath::RoundToInt(Row.SpeedKmh))));
            StandingRows[Index]->SetBrushColor(Row.bPlayer ? FLinearColor(.12f, .28f, .22f, 1) : Row.bIncident ? FLinearColor(.4f, .06f, .01f, 1) : FLinearColor(.03f, .04f, .06f, .8f));
        }
    }
    if (Position)
        if (const AKartRaceDirector* Director = Cast<AKartRaceDirector>(UGameplayStatics::GetActorOfClass(GetWorld(), AKartRaceDirector::StaticClass())))
            Position->SetText(FText::FromString(FString::Printf(TEXT("Position %d / 20"), Director->GetPlayerPlace())));
    if (Speed)
        if (const AKartPawn* Kart = Cast<AKartPawn>(UGameplayStatics::GetPlayerPawn(GetWorld(), 0)))
            Speed->SetText(FText::FromString(FString::Printf(TEXT("%d km/h"), FMath::RoundToInt(FMath::Abs(Kart->GetSpeedKmh())))));
    Status->SetText(FText::FromString(!Race->IsRaceAvailable() ? Race->GetStatusMessage() :
        P.bFinished ? TEXT("FINISHED - F5 to race again") : P.bStarted ? TEXT("RACING") : TEXT("Cross START to begin")));
    if (const AKartPawn* Kart = Cast<AKartPawn>(UGameplayStatics::GetPlayerPawn(GetWorld(), 0)))
        if (Kart->IsBurning()) Status->SetText(FText::FromString(TEXT("FIRE | recovering")));
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
