#include "KartTrainingLearner.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"

FString FKartTrainingLearner::Propose(const FString& Track, int32 Seed, const FKartDrivingSummary& Summary)
{
    if (Summary.CleanSamples < 300 || Summary.CornerSamples < 20 || Summary.StraightSamples < 20
        || Summary.CornerSamples + Summary.StraightSamples != Summary.CleanSamples
        || !FMath::IsFinite(Summary.SumSpeed) || !FMath::IsFinite(Summary.SumThrottle)
        || !FMath::IsFinite(Summary.SumLane) || !FMath::IsFinite(Summary.SumCornerSpeed)) return FString();
    auto Root = MakeShared<FJsonObject>();
    Root->SetNumberField(TEXT("schema_version"), 1); Root->SetStringField(TEXT("track_id"), Track);
    Root->SetNumberField(TEXT("seed"), Seed);
    auto Training = MakeShared<FJsonObject>();
    Training->SetStringField(TEXT("source"), TEXT("telemetry"));
    Training->SetStringField(TEXT("method"), TEXT("native_aggregate_v1_experimental"));
    Training->SetNumberField(TEXT("clean_samples"), Summary.CleanSamples);
    Training->SetNumberField(TEXT("corner_samples"), Summary.CornerSamples);
    Training->SetNumberField(TEXT("straight_samples"), Summary.StraightSamples);
    Training->SetNumberField(TEXT("mean_speed_kmh"), Summary.SumSpeed / Summary.CleanSamples);
    Root->SetObjectField(TEXT("training"), Training);
    FRandomStream Random(Seed);
    TArray<TSharedPtr<FJsonValue>> Profiles;
    const double Pace = FMath::Clamp(Summary.SumSpeed / Summary.CleanSamples / 55., 0., 1.);
    for (int32 Index = 0; Index < 19; ++Index)
    {
        auto Style = MakeShared<FJsonObject>();
        Style->SetNumberField(TEXT("racer_index"), Index + 1);
        Style->SetNumberField(TEXT("aggression"), FMath::Clamp(.25 + .72 * (.5 * Pace + .5 * Summary.SumThrottle / Summary.CleanSamples) + Random.FRandRange(-.12f, .12f), .25, .97));
        Style->SetNumberField(TEXT("corner_skill"), FMath::Clamp(.95 + .05 * Summary.SumCornerSpeed / Summary.CornerSamples / 55. + Random.FRandRange(-.02f, .02f), .95, 1.));
        Style->SetNumberField(TEXT("preferred_lane_cm"), FMath::Clamp(Summary.SumLane / Summary.CleanSamples * .25 + ((Index * 13) % 19 - 9) * 13., -130., 130.));
        Style->SetNumberField(TEXT("decision_seconds"), 1.2 + ((Index * 7) % 19) / 18. * 2.3);
        Profiles.Add(MakeShared<FJsonValueObject>(Style));
    }
    Root->SetArrayField(TEXT("profiles"), Profiles);
    FString Json;
    FJsonSerializer::Serialize(Root, TJsonWriterFactory<>::Create(&Json));
    return Json;
}
