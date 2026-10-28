from pathlib import Path
P=Path('Source/Road_To_F1_New')
def edit(name,changes):
 p=P/name;t=p.read_text()
 for old,new in changes:
  assert old in t,(name,old[:90]);t=t.replace(old,new)
 p.write_text(t)
edit('ProofPawn.cpp',[
 ('#include "KartMechanicalVisuals.h"','#include "KartMechanicalVisuals.h"\n#include "KartRaceSettings.h"'),
 ('  for(auto* Slot:Slots)if(!Used.Contains(Slot->PositionNumber)){ControllerGridSlots.Add(Player,Slot->PositionNumber);return Slot;}','  if(GetWorld()->GetMapName().Contains(TEXT("DesertKarting"))&&!FParse::Param(FCommandLine::Get(),TEXT("Grid20Test"))&&!Used.Contains(KartRace::PlayerGridPosition))\n   for(auto* Slot:Slots)if(Slot->PositionNumber==KartRace::PlayerGridPosition){ControllerGridSlots.Add(Player,Slot->PositionNumber);return Slot;}\n  for(auto* Slot:Slots)if(!Used.Contains(Slot->PositionNumber)){ControllerGridSlots.Add(Player,Slot->PositionNumber);return Slot;}'),
 ('Throttle*430.f-Speed*0.32f','Throttle*600.f-Speed*0.32f'),
 ('*Dt,-350.f,1600.f)','*Dt,-350.f,float(KartRace::TopSpeedCmps))')])
edit('TrackRacingAI.cpp',[
 ('#include "ProofPawn.h"','#include "ProofPawn.h"\n#include "KartMechanicalVisuals.h"\n#include "KartTireDynamics.h"\n#include "KartRaceSettings.h"'),
 ('FMath::Clamp(OpponentCount,0,4)','FMath::Clamp(OpponentCount,0,KartRace::OpponentCount)'),
 ('Slots[I+1]->GetActorTransform()','Slots[I]->GetActorTransform()'),
 ('P->ConfigureRacingAI(I+2)','P->ConfigureRacingAI(I+1)'),
 ('S.Slot=I+2;S.CruiseSpeed=1060.f-I*35.f','S.Slot=I+1;S.CruiseSpeed=float(KartRace::TopSpeedCmps)'),
 (' auto* P=S.Pawn.Get();if(!P)return;',' auto* P=S.Pawn.Get();if(!P)return;\n if(auto* Mechanical=P->FindComponentByClass<UKartMechanicalVisuals>())if(Mechanical->bReady)return;'),
 ('TestPlayer.CruiseSpeed=1120','TestPlayer.CruiseSpeed=float(KartRace::TopSpeedCmps)'),
 ('float Throttle=FMath::Clamp((TargetSpeed-Speed)*.006f+TargetSpeed*.32f/430.f,-1.f,1.f);','const auto* Power=P->GetTireDynamics();\n  const float FeedForward=Power?(TargetSpeed*Power->LinearDragPerSecond+Power->RollingResistanceN/Power->MassKg*100)/(Power->EngineForceN/Power->MassKg*100):TargetSpeed*.32f/600.f;\n  float Throttle=FMath::Clamp((TargetSpeed-Speed)*.006f+FeedForward,-1.f,1.f);'),
 ('Opponents.Num()==4','Opponents.Num()==FMath::Clamp(OpponentCount,0,KartRace::OpponentCount)'),
 ('S.Driver.IsValid()&&S.Driver->GetSkeletalMeshAsset()?TEXT("true"):TEXT("false")','P&&((P->FindComponentByClass<UKartMechanicalVisuals>()&&P->FindComponentByClass<UKartMechanicalVisuals>()->bReady)||(S.Driver.IsValid()&&S.Driver->GetSkeletalMeshAsset()))?TEXT("true"):TEXT("false")')])
edit('KartMechanicalVisuals.h',[
 ('private:\n',' UPROPERTY(BlueprintReadOnly,Category="Kart livery") int32 LiverySlot=0;\n UPROPERTY(BlueprintReadOnly,Category="Kart livery") FLinearColor KartColor;\n UPROPERTY(BlueprintReadOnly,Category="Kart livery") FLinearColor DriverColor;\nprivate:\n void ApplyLivery(int32 Slot);\n')])
edit('KartMechanicalVisuals.cpp',[
 ('#include "KartVisualKinematics.h"','#include "KartVisualKinematics.h"\n#include "KartRaceSettings.h"\n#include "Materials/MaterialInstanceDynamic.h"'),
 ('!bEnabled||!Pawn||Pawn->bRacingAI||','!bEnabled||!Pawn||'),
 ('auto* Cockpit=LoadObject<USkeletalMesh>(nullptr,*(Folder+TEXT("SK_V4_DriverPOV.SK_V4_DriverPOV")));','auto* Cockpit=Pawn->bRacingAI?Full:LoadObject<USkeletalMesh>(nullptr,*(Folder+TEXT("SK_V4_DriverPOV.SK_V4_DriverPOV")));'),
 ('Driver=CreateDriver(TEXT("V4_SeatedDriver"),Full);POV=CreateDriver(TEXT("V4_CockpitDriver"),Cockpit);Driver->SetOwnerNoSee(true);POV->SetOnlyOwnerSee(true);POV->SetCastShadow(false);','Driver=CreateDriver(TEXT("V4_SeatedDriver"),Full);Driver->SetOwnerNoSee(!Pawn->bRacingAI);\n if(!Pawn->bRacingAI){POV=CreateDriver(TEXT("V4_CockpitDriver"),Cockpit);POV->SetOnlyOwnerSee(true);POV->SetCastShadow(false);}'),
 (' TArray<UCameraComponent*> Cameras;Pawn->GetComponents(Cameras);',' TArray<UCameraComponent*> Cameras;if(!Pawn->bRacingAI)Pawn->GetComponents(Cameras);'),
 ('for(auto* Mesh:{Driver.Get(),POV.Get()}){Mesh->CopyPoseFromSkeletalComponent','for(auto* Mesh:{Driver.Get(),POV.Get()})if(Mesh){Mesh->CopyPoseFromSkeletalComponent'),
 ('Driver->SetOwnerNoSee(!External);POV->SetHiddenInGame(External);','Driver->SetOwnerNoSee(!Pawn->bRacingAI&&!External);if(POV)POV->SetHiddenInGame(External);'),
 ('const auto* Dynamics=Pawn->bUseTireDynamics?','const int32 Slot=Pawn->AssignedGridPosition>0?Pawn->AssignedGridPosition:(Pawn->PreferredGridPosition>0?Pawn->PreferredGridPosition:KartRace::PlayerGridPosition);\n if(Slot!=LiverySlot)ApplyLivery(Slot);\n const auto* Dynamics=Pawn->bUseTireDynamics?')])
with (P/'KartMechanicalVisuals.cpp').open('a') as f:f.write(r'''
void UKartMechanicalVisuals::ApplyLivery(int32 Slot){
 static const FLinearColor Palette[]={
  FLinearColor(.72f,.015f,.025f),FLinearColor(1.f,.18f,.008f),FLinearColor(.95f,.68f,.01f),
  FLinearColor(.38f,.85f,.015f),FLinearColor(.008f,.40f,.12f),FLinearColor(.005f,.72f,.82f),
  FLinearColor(.015f,.055f,.8f),FLinearColor(.30f,.02f,.65f),FLinearColor(.85f,.01f,.30f),FLinearColor(.85f,.88f,.94f)};
 const int32 Index=(FMath::Max(1,Slot)-1)%UE_ARRAY_COUNT(Palette);
 auto* Paint=LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/RoadToF1/RaceLiveries/M_GridPaint.M_GridPaint"));
 auto* Fabric=LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/RoadToF1/RaceLiveries/M_GridFabric.M_GridFabric"));
 if(!Paint||!Fabric)return;
 KartColor=Palette[Index];DriverColor=Palette[(Index+3)%UE_ARRAY_COUNT(Palette)];LiverySlot=Slot;
 auto Apply=[&](UMeshComponent* Mesh,bool Human){
  if(!Mesh)return;const auto Names=Mesh->GetMaterialSlotNames();
  for(int32 I=0;I<Mesh->GetNumMaterials();++I){
   const FString Name=(Names.IsValidIndex(I)?Names[I].ToString():FString()).ToLower();
   const bool Body=!Human&&(Name.Contains(TEXT("bodygraphite"))||Name.Contains(TEXT("racingred")));
   const bool Helmet=Human&&Name.Contains(TEXT("helmet"))&&(Name.Contains(TEXT("paint"))||Name.Contains(TEXT("crimson")));
   const bool Cloth=Human&&(Name.Contains(TEXT("charcoal"))||Name.Contains(TEXT("crimson"))||Name.Contains(TEXT("redknit"))||Name.Contains(TEXT("graphitenomex"))||Name.Contains(TEXT("legnomex"))||Name.Contains(TEXT("red glove")));
   if(!Body&&!Helmet&&!Cloth)continue;
   auto* MID=UMaterialInstanceDynamic::Create(Cloth?Fabric:Paint,this);
   FLinearColor Color=Human?DriverColor:KartColor;
   if(Cloth&&(Name.Contains(TEXT("charcoal"))||Name.Contains(TEXT("graphitenomex"))||Name.Contains(TEXT("legnomex"))))Color=Color*.40f;
   Color.A=1;MID->SetVectorParameterValue(TEXT("LiveryColor"),Color);Mesh->SetMaterial(I,MID);
  }
 };
 for(auto* Part:Parts)Apply(Part,false);Apply(Driver,true);Apply(POV,true);
}
''')
