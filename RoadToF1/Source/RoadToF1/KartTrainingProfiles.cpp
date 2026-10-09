#include "KartTrainingProfiles.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"

bool FKartTrainingProfiles::Parse(const FString& Json, const FString& Track, TArray<FKartTrainingStyle>& Out)
{
    Out.Reset();
    TSharedPtr<FJsonObject> Root;
    if (!FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Json), Root) || !Root.IsValid()) return false;
    double Version;
    FString TrackName;
    const TArray<TSharedPtr<FJsonValue>>* Rows;
    const TSharedPtr<FJsonObject>* Training;
    FString Source;
    if (!Root->TryGetNumberField(TEXT("schema_version"), Version) || Version != 1
        || !Root->TryGetStringField(TEXT("track_id"), TrackName) || TrackName != Track
        || !Root->TryGetObjectField(TEXT("training"), Training)
        || !(*Training)->TryGetStringField(TEXT("source"), Source)
        || (Source != TEXT("telemetry") && Source != TEXT("observations"))
        || !Root->TryGetArrayField(TEXT("profiles"), Rows) || Rows->Num() != 19) return false;
    TArray<FKartTrainingStyle> Candidate;
    Candidate.SetNum(19);
    TSet<int32> Ids;
    TSet<FString> Distinct;
    for (const auto& Value : *Rows)
    {
        const TSharedPtr<FJsonObject>* Row;
        if (!Value->TryGetObject(Row)) return false;
        double Id, Aggression, Corner, Lane, Decision;
        if (!(*Row)->TryGetNumberField(TEXT("racer_index"), Id) || !FMath::IsFinite(Id) || Id < 1 || Id > 19 || Id != FMath::FloorToDouble(Id)
            || !(*Row)->TryGetNumberField(TEXT("aggression"), Aggression) || !FMath::IsFinite(Aggression) || Aggression < .25 || Aggression > .97
            || !(*Row)->TryGetNumberField(TEXT("corner_skill"), Corner) || !FMath::IsFinite(Corner) || Corner < .95 || Corner > 1
            || !(*Row)->TryGetNumberField(TEXT("preferred_lane_cm"), Lane) || !FMath::IsFinite(Lane) || Lane < -130 || Lane > 130
            || !(*Row)->TryGetNumberField(TEXT("decision_seconds"), Decision) || !FMath::IsFinite(Decision) || Decision < 1.2 || Decision > 3.5
            || Ids.Contains(int32(Id))) return false;
        Ids.Add(int32(Id));
        Candidate[int32(Id) - 1] = {float(Aggression), float(Corner), float(Lane), float(Decision)};
        Distinct.Add(FString::Printf(TEXT("%.5f %.5f %.3f %.5f"), Aggression, Corner, Lane, Decision));
    }
    if (Distinct.Num() != 19) return false;
    Out = MoveTemp(Candidate);
    return true;
}
