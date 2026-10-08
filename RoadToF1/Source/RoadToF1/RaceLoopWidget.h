#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "RaceLoopWidget.generated.h"

class UTextBlock;

UCLASS()
class ROADTOF1_API URaceLoopWidget : public UUserWidget
{
    GENERATED_BODY()
protected:
    virtual void NativeOnInitialized() override;
    virtual void NativeTick(const FGeometry& Geometry, float DeltaTime) override;
private:
    UTextBlock* AddLine(class UVerticalBox* Box, const FString& Text, int32 FontSize);
    UFUNCTION()
    void OnRestartClicked();
    UPROPERTY(Transient) TObjectPtr<UTextBlock> Status;
    UPROPERTY(Transient) TObjectPtr<UTextBlock> Lap;
    UPROPERTY(Transient) TObjectPtr<UTextBlock> Checkpoints;
    UPROPERTY(Transient) TObjectPtr<UTextBlock> LapTimer;
    UPROPERTY(Transient) TObjectPtr<UTextBlock> RaceTimer;
    UPROPERTY(Transient) TObjectPtr<UTextBlock> LastLap;
    UPROPERTY(Transient) TObjectPtr<UTextBlock> Speed;
    UPROPERTY(Transient) TObjectPtr<UTextBlock> Position;
};
