#include "TrackRacingAI.h"
#include "ProofPawn.h"
#include "KartMechanicalVisuals.h"
#include "KartTireDynamics.h"
#include "KartRaceSettings.h"
#include "KartRacecraftMath.h"
#include "GridStartSlot.h"
#include "EngineUtils.h"
#include "Animation/AnimSequence.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/StaticMesh.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/World.h"
#include "Engine/GameViewportClient.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "HAL/FileManager.h"
#include "HAL/PlatformMisc.h"
#include "HAL/PlatformTime.h"

bool UTrackEdgeRoute::IsUsable() const {
 if(Center.Num()<100||Left.Num()!=Center.Num()||Right.Num()!=Center.Num())return false;
 for(int32 I=0;I<Center.Num();++I){
  if(Center[I].ContainsNaN()||Left[I].ContainsNaN()||Right[I].ContainsNaN())return false;
  const FVector N=FVector::CrossProduct(FVector::UpVector,Tangent(I));
  if(FVector::DotProduct(Left[I]-Center[I],N)<160||FVector::DotProduct(Right[I]-Center[I],N)>-160)return false;
  if(FVector::Dist2D(Center[I],Center[(I+1)%Center.Num()])<1)return false;
 }
 return true;
}
FVector UTrackEdgeRoute::Tangent(int32 I) const {const int32 N=Center.Num();return (Center[(I+1)%N]-Center[(I+N-1)%N]).GetSafeNormal2D();}
float UTrackEdgeRoute::ClampLane(int32 I,float Lane,float Margin) const {
 const FVector N=FVector::CrossProduct(FVector::UpVector,Tangent(I));
 return FMath::Clamp(Lane,float(FVector::DotProduct(Right[I]-Center[I],N))+Margin,float(FVector::DotProduct(Left[I]-Center[I],N))-Margin);
}
FVector UTrackEdgeRoute::LanePoint(int32 I,float Lane,float Margin) const {I=(I%Center.Num()+Center.Num())%Center.Num();const FVector N=FVector::CrossProduct(FVector::UpVector,Tangent(I));const float Base=Guide.Num()==Center.Num()?FVector::DotProduct(Guide[I]-Center[I],N):0;return Center[I]+N*ClampLane(I,Base+Lane,Margin);}

UTrackRacingAI::UTrackRacingAI(){
 PrimaryComponentTick.TickInterval=.05f;PrimaryComponentTick.bCanEverTick=true;PrimaryComponentTick.TickGroup=TG_PrePhysics;
 for(int32 I=0;I<4;++I){FKartDriverPersonality D;const float A[]={.4f,.75f,.6f,.85f},B[]={.82f,.94f,.88f,1.f},P[]={-1.f,1.f,0.f,-.5f};D.Aggressiveness=A[I];D.BrakingConfidence=B[I];D.PassingPreference=P[I];D.Consistency=.88f+I*.03f;Drivers.Add(D);}
 RouteAsset=TSoftObjectPtr<UTrackEdgeRoute>(FSoftObjectPath(TEXT("/Game/RoadToF1/RacingAI/DA_DesertTrackEdges.DA_DesertTrackEdges")));
}
void UTrackRacingAI::InitializeOpponents(){
 OpponentCount=ConfiguredOpponentCount();
#if !UE_BUILD_SHIPPING
 if(FParse::Param(FCommandLine::Get(),TEXT("CompetitiveAITest"))){int32 Count=OpponentCount,Level=int32(Difficulty);FParse::Value(FCommandLine::Get(),TEXT("KartTestOpponents="),Count);FParse::Value(FCommandLine::Get(),TEXT("KartTestDifficulty="),Level);OpponentCount=FMath::Clamp(Count,0,19);Difficulty=EKartAIDifficulty(FMath::Clamp(Level,0,4));}
#endif
 if(!GetOwner()->HasAuthority()||!GetWorld()->GetMapName().Contains(TEXT("DesertKarting"))||OpponentCount<=0||FParse::Param(FCommandLine::Get(),TEXT("NoRacingAI"))||FParse::Param(FCommandLine::Get(),TEXT("Grid20Test")))return;
 Route=RouteAsset.LoadSynchronous();if(!Route||!Route->IsUsable()){UE_LOG(LogTemp,Error,TEXT("RACING_AI: missing/invalid actual asphalt edge route; no opponents spawned"));return;}
 bTesting=FParse::Param(FCommandLine::Get(),TEXT("RacingAITest"));
 Arcs.Add(0);for(int32 I=0;I<Route->Center.Num();++I){RouteLength+=FVector::Dist2D(Route->Center[I],Route->Center[(I+1)%Route->Center.Num()]);Arcs.Add(RouteLength);}
 TArray<AGridStartSlot*> Slots;for(TActorIterator<AGridStartSlot> It(GetWorld());It;++It)Slots.Add(*It);
 if(Slots.Num()!=20){UE_LOG(LogTemp,Error,TEXT("RACING_AI: expected existing 20-slot grid"));return;}
 Slots.Sort([](const AGridStartSlot& A,const AGridStartSlot& B){return A.PositionNumber<B.PositionNumber;});
 for(int32 I=0;I<FMath::Clamp(OpponentCount,0,19);++I){
  const int32 Grid=I+1>=KartRace::PlayerGridPosition?I+2:I+1;FTransform T=Slots[Grid-1]->GetActorTransform();T.AddToTranslation(FVector(0,0,-9));
  auto* P=GetWorld()->SpawnActorDeferred<AProofPawn>(AProofPawn::StaticClass(),T,nullptr,nullptr,ESpawnActorCollisionHandlingMethod::AlwaysSpawn);
  if(!P)continue;P->ConfigureRacingAI(Grid);P->FinishSpawning(T);P->AddTickPrerequisiteComponent(this);
  FTrackOpponent S;S.Pawn=P;S.Slot=Grid;S.CruiseSpeed=float(KartRace::TopSpeedCmps);S.Preference=0;
#if !UE_BUILD_SHIPPING
  if(FParse::Param(FCommandLine::Get(),TEXT("CompetitiveAITest"))){int32 Slow=0;float Pace=.68f;FParse::Value(FCommandLine::Get(),TEXT("KartTestSlowSlot="),Slow);FParse::Value(FCommandLine::Get(),TEXT("KartTestPace="),Pace);if(S.Slot==Slow)S.CruiseSpeed*=FMath::Clamp(Pace,.4f,1.f);}
#endif
  if(Drivers.Num())S.Personality=Drivers[I%Drivers.Num()];Opponents.Add(S);CreatePresentation(Opponents.Last());
 }
 if(Opponents.Num()&&Opponents[0].Pawn.IsValid())TrackPlan.Build(Route,Opponents[0].Pawn->GetTireDynamics());
 UE_LOG(LogTemp,Display,TEXT("RACING_AI: %d opponents, %d paired asphalt-edge samples, %.1fm circuit"),Opponents.Num(),Route->Center.Num(),RouteLength/100);
}
void UTrackRacingAI::CreatePresentation(FTrackOpponent& S){
 auto* P=S.Pawn.Get();if(!P)return;
 if(auto* Mechanical=P->FindComponentByClass<UKartMechanicalVisuals>())if(Mechanical->bReady)return;
 const FString FP=TEXT("/Game/RoadToF1/PlayerVisuals/FirstPerson/");
 auto* Chassis=NewObject<UStaticMeshComponent>(P);P->AddInstanceComponent(Chassis);Chassis->SetupAttachment(P->GetRootComponent());Chassis->SetRelativeLocation(FVector(0,0,-31));
 Chassis->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,*(FP+TEXT("SM_PlayerKartChassis.SM_PlayerKartChassis"))));Chassis->SetCollisionEnabled(ECollisionEnabled::NoCollision);Chassis->SetGenerateOverlapEvents(false);Chassis->SetCanEverAffectNavigation(false);Chassis->RegisterComponent();
 auto* Driver=NewObject<USkeletalMeshComponent>(P);P->AddInstanceComponent(Driver);Driver->SetupAttachment(Chassis);
 Driver->SetSkeletalMeshAsset(LoadObject<USkeletalMesh>(nullptr,TEXT("/Game/RoadToF1/RacingAI/SK_AI_KartDriver.SK_AI_KartDriver")));
 Driver->SetCollisionEnabled(ECollisionEnabled::NoCollision);Driver->SetGenerateOverlapEvents(false);Driver->SetCanEverAffectNavigation(false);Driver->SetAnimationMode(EAnimationMode::AnimationSingleNode);Driver->RegisterComponent();
 auto* Sequence=LoadObject<UAnimSequence>(nullptr,*(FP+TEXT("A_FP_KartSteering.A_FP_KartSteering")));Driver->SetAnimation(Sequence);Driver->SetPlayRate(0);Driver->SetPosition(Sequence?Sequence->GetPlayLength()*.5f:0,false);Driver->PrimaryComponentTick.TickGroup=TG_PostPhysics;Driver->AddTickPrerequisiteActor(P);S.Driver=Driver;
 auto* Wheel=NewObject<UStaticMeshComponent>(P);P->AddInstanceComponent(Wheel);Wheel->SetupAttachment(Chassis);Wheel->SetRelativeLocation(FVector(62,0,70));Wheel->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,*(FP+TEXT("SM_FP_SteeringWheel.SM_FP_SteeringWheel"))));Wheel->SetCollisionEnabled(ECollisionEnabled::NoCollision);Wheel->SetGenerateOverlapEvents(false);Wheel->SetCanEverAffectNavigation(false);Wheel->RegisterComponent();S.Wheel=Wheel;
 if(!Chassis->GetStaticMesh()||!Driver->GetSkeletalMeshAsset()||!Wheel->GetStaticMesh()||!Sequence)UE_LOG(LogTemp,Error,TEXT("RACING_AI: required opponent presentation asset missing"));
}
void UTrackRacingAI::ResetRace(){
 for(auto& S:Opponents){S.StrategyClock=1;S.CachedTrafficLimit=S.CruiseSpeed;S.SteeringCommand=0;S.Nearby.Reset();S.PerceivedLeader.Reset();S.PerceptionHold=0;S.State=EKartAIState::FOLLOW_RACING_LINE;for(auto& Count:S.StateEntries)Count=0;S.MistakeTimer=0;S.MistakeCooldown=20;S.Mistakes=0;S.LapTimes.Reset();S.LastLapSeconds=0;S.Segment=INDEX_NONE;S.Distance=0;S.Laps=0;S.Visited.Reset();S.Recoveries=S.OffTrackFrames=0;S.MaximumEdgeExcess=S.MaximumGridMovement=S.MaximumSpeed=0;S.ReverseTime=S.Cooldown=S.StuckTime=S.DecisionTime=0;S.Intent=S.PassAttempts=S.PassesCompleted=S.AbortedPasses=S.DefensiveHolds=S.ReverseAttempts=0;S.IntentAge=S.RacecraftCooldown=S.BlockedSeconds=S.RecoveryWindow=0;S.Rival.Reset();S.bAlongside=false;}
 SenseClock=0;TrafficRefreshClock=1;CpuTotalMs=CpuMaxMs=0;CpuSamples=0;bGateCaptured=false;bReported=false;TestRaceSeconds=ReportClock=0;
 TestPlayer=FTrackOpponent();
}
int32 UTrackRacingAI::NearestSegment(const FVector& P,int32 Previous) const {
 int32 Best=0;double Distance=MAX_dbl;const int32 N=Route->Center.Num();
 const int32 Lo=Previous==INDEX_NONE?0:Previous-10,Hi=Previous==INDEX_NONE?N-1:Previous+16;
 for(int32 J=Lo;J<=Hi;++J){const int32 I=(J%N+N)%N;const FVector Closest=FMath::ClosestPointOnSegment(P,Route->Center[I],Route->Center[(I+1)%N]);const double D=FVector::DistSquared2D(P,Closest);if(D<Distance){Distance=D;Best=I;}}
 return Best;
}
float UTrackRacingAI::SegmentArc(const FVector& P,int32 I) const {const FVector A=Route->Center[I],D=Route->Center[(I+1)%Route->Center.Num()]-A;return Arcs[I]+FMath::Clamp(float(FVector::DotProduct(P-A,D)/D.SizeSquared2D()),0.f,1.f)*(Arcs[I+1]-Arcs[I]);}
float UTrackRacingAI::Lateral(const FVector& P,int32 I) const {return FVector::DotProduct(P-Route->Center[I],FVector::CrossProduct(FVector::UpVector,Route->Tangent(I)));}
int32 UTrackRacingAI::AheadIndex(int32 I,float D) const {const int32 N=Route->Center.Num();float Sum=0;for(int32 J=0;J<N-1;++J){Sum+=FVector::Dist2D(Route->Center[I],Route->Center[(I+1)%N]);I=(I+1)%N;if(Sum>=D)break;}return I;}
void UTrackRacingAI::TickComponent(float Dt,ELevelTick Type,FActorComponentTickFunction* Function){
 Super::TickComponent(Dt,Type,Function);if(!Route||Opponents.IsEmpty())return;
 auto* GM=Cast<AProofGameMode>(GetOwner());if(!GM)return;const double CpuStart=FPlatformTime::Seconds();Dt=FMath::Min(Dt,.1f);ApplyConsoleConfiguration();const auto Tuning=Preset(Difficulty);
 TrafficRefreshClock+=Dt;if(TrafficRefreshClock>=.5f){TrafficRefreshClock=0;CachedTraffic.Reset();for(TActorIterator<AProofPawn> It(GetWorld());It;++It)CachedTraffic.Add(*It);}TArray<AProofPawn*> Traffic;for(auto Weak:CachedTraffic)if(auto* Kart=Weak.Get())Traffic.Add(Kart);
 TArray<FTrackOpponent*> Agents;for(auto& S:Opponents)Agents.Add(&S);
#if !UE_BUILD_SHIPPING
 if(bTesting&&FParse::Param(FCommandLine::Get(),TEXT("RacingAIPlayerTest"))){for(auto* P:Traffic)if(P->IsPlayerControlled()){TestPlayer.Pawn=P;TestPlayer.CruiseSpeed=float(KartRace::TopSpeedCmps);TestPlayer.Preference=0;Agents.Add(&TestPlayer);break;}}
#endif
 TMap<AProofPawn*,float> TrafficArc;for(auto* P:Traffic){int32 Segment=INDEX_NONE;for(auto* Agent:Agents)if(Agent->Pawn.Get()==P){Segment=Agent->Segment;break;}TrafficArc.Add(P,SegmentArc(P->GetActorLocation(),NearestSegment(P->GetActorLocation(),Segment)));}
 SenseClock+=Dt;if(SenseClock>=.1f){for(auto* Agent:Agents)ObserveOpponents(*Agent,Traffic,TrafficArc,SenseClock);SenseClock=0;}
 const bool Gate=GM->IsStartGateClosed();
 for(auto* Agent:Agents){auto& S=*Agent;
  auto* P=S.Pawn.Get();if(!P)continue;const FVector Pos=P->GetActorLocation();const float Speed=FMath::Abs(P->GetDrivingSpeed());
  if(S.Segment==INDEX_NONE){S.Segment=NearestSegment(Pos,INDEX_NONE);S.StartArc=S.PreviousArc=SegmentArc(Pos,S.Segment);S.Lane=S.DesiredLane=Lateral(Pos,S.Segment);S.GridPosition=Pos;S.Previous=Pos;S.Random.Initialize(303+S.Slot*997);}
  auto Input=[&](float Throttle,float Steering,float Brake=0.f){if(P->bRacingAI)P->SetAutonomousControls(Throttle,Steering,Brake);else P->SetRacingDiagnosticControls(Throttle,Steering,Brake);};
  if(Gate){S.MaximumGridMovement=FMath::Max(S.MaximumGridMovement,float(FVector::Dist(Pos,S.GridPosition)));Input(bTesting?1.f:0.f,0);continue;}
  if(GM->GetRaceElapsedSeconds()<Tuning.Reaction+S.Personality.ReactionDelay){Input(0,0,1);continue;}
  S.Segment=NearestSegment(Pos,S.Segment);const float Arc=SegmentArc(Pos,S.Segment);float Advance=Arc-S.PreviousArc;if(Advance<-RouteLength*.5f)Advance+=RouteLength;if(Advance>RouteLength*.5f)Advance-=RouteLength;
  if(FVector::Dist2D(Pos,S.Previous)<350.f)S.Distance+=Advance;
  S.Previous=Pos;S.PreviousArc=Arc;const int32 OldLaps=S.Laps;S.Laps=FMath::Max(S.Laps,FMath::FloorToInt(FMath::Max(0.f,S.Distance)/RouteLength));S.Visited.Add(S.Segment*64/Route->Center.Num());if(S.Laps>OldLaps){S.LapTimes.Add(GM->GetRaceElapsedSeconds()-S.LastLapSeconds);S.LastLapSeconds=GM->GetRaceElapsedSeconds();}
  const float ActualLane=Lateral(Pos,S.Segment);const FVector Normal=FVector::CrossProduct(FVector::UpVector,Route->Tangent(S.Segment));
  const float L=FVector::DotProduct(Route->Left[S.Segment]-Route->Center[S.Segment],Normal),R=FVector::DotProduct(Route->Right[S.Segment]-Route->Center[S.Segment],Normal);
  const float Excess=FMath::Max(ActualLane+75-L,R-ActualLane+75);S.MaximumEdgeExcess=FMath::Max(S.MaximumEdgeExcess,Excess);if(Excess>5)++S.OffTrackFrames;
  S.MaximumSpeed=FMath::Max(S.MaximumSpeed,Speed);S.DecisionTime-=Dt;S.Cooldown=FMath::Max(0.f,S.Cooldown-Dt);
  float TrafficSpeed=S.CruiseSpeed;bool StoppedLeader=false;
  if(bUseAdvancedPlanner&&!bEnableRacecraft){S.DesiredLane=Route->Guide.Num()==Route->Center.Num()?Lateral(Route->Guide[S.Segment],S.Segment):0;S.Lane=FMath::FInterpConstantTo(S.Lane,S.DesiredLane,Dt,110);}
  else if(bEnableRacecraft){S.StrategyClock+=Dt;if(S.StrategyClock>=FMath::Max(.1f,.1f+Tuning.Reaction*.15f+S.Personality.ReactionDelay)){S.CachedTrafficLimit=PlanRacecraft(S,Traffic,TrafficArc,Arc,Speed,S.StrategyClock);S.StrategyClock=0;}TrafficSpeed=S.CachedTrafficLimit;StoppedLeader=S.BlockedSeconds>0;S.Lane=FMath::FInterpConstantTo(S.Lane,S.DesiredLane,Dt,85+S.Personality.Aggressiveness*40);}
  else {
  auto ClearLane=[&](float Lane){if(!FMath::IsNearlyEqual(Route->ClampLane(S.Segment,Lane),Lane,1.f))return false;for(auto* Other:Traffic){if(Other==P)continue;const FVector D=Other->GetActorLocation()-Pos;const float Ahead=FVector::DotProduct(D,Route->Tangent(S.Segment));const float Side=ActualLane+FVector::DotProduct(D,Normal);if(Ahead>-500&&Ahead<750&&FMath::Abs(Side-Lane)<190)return false;}return true;};
  const bool CanDecide=S.DecisionTime<=0;
  bool CanPass=true;for(float D:{700.f,1400.f,2200.f,2800.f}){const int32 I=AheadIndex(S.Segment,D);if(FMath::Abs(FMath::Atan2(FVector::CrossProduct(Route->Tangent(S.Segment),Route->Tangent(I)).Z,FVector::DotProduct(Route->Tangent(S.Segment),Route->Tangent(I))))>.12f)CanPass=false;}
  if(CanDecide){S.DesiredLane=Route->ClampLane(S.Segment,S.Preference);S.DecisionTime=2.5f;}
  if(!CanPass&&ClearLane(0))S.DesiredLane=0;

  for(auto* Other:Traffic){if(Other==P)continue;const FVector D=Other->GetActorLocation()-Pos;float Ahead=TrafficArc[Other]-Arc;if(Ahead<0)Ahead+=RouteLength;const float Side=FVector::DotProduct(D,Normal);
   if(Ahead>0&&Ahead<1600&&FMath::Abs(Side)<210){
    if(Ahead<500&&FMath::Abs(Other->GetDrivingSpeed())<10)StoppedLeader=true;
    if(CanPass&&CanDecide&&Other->GetDrivingSpeed()<S.CruiseSpeed-40){
     for(float Candidate:{ActualLane+Side+300.f,ActualLane+Side-300.f})if(ClearLane(Candidate)){S.DesiredLane=Candidate;S.DecisionTime=3.f;break;}
    }
    if(FMath::Abs(ActualLane+Side-S.DesiredLane)<200||FMath::Abs(Side)<165)TrafficSpeed=FMath::Min(TrafficSpeed,FMath::Max(0.f,Other->GetDrivingSpeed()+(Ahead-290.f)*.65f));
   }
  }
  S.DesiredLane=Route->ClampLane(S.Segment,S.DesiredLane);S.Lane=FMath::FInterpConstantTo(S.Lane,S.DesiredLane,Dt,110.f);
  }
  // Fast safety layer between retained tactical updates: no planned lane may cross an occupied body.
  if(bEnableRacecraft){const float OwnWidth=90*FMath::Abs(FVector::DotProduct(P->GetActorForwardVector(),Normal))+60*FMath::Abs(FVector::DotProduct(P->GetActorRightVector(),Normal));
   for(auto* Other:Traffic){if(Other==P)continue;const float Gap=KartRacecraft::SignedGap(TrafficArc[Other],Arc,RouteLength);if(FMath::Abs(Gap)>2000||FVector::Dist2D(Pos,Other->GetActorLocation())>2400)continue;
    const int32 OI=NearestSegment(Other->GetActorLocation(),S.Segment);const float Side=Lateral(Other->GetActorLocation(),OI);
    const FVector ON=FVector::CrossProduct(FVector::UpVector,Route->Tangent(OI));const float OtherWidth=90*FMath::Abs(FVector::DotProduct(Other->GetActorForwardVector(),ON))+60*FMath::Abs(FVector::DotProduct(Other->GetActorRightVector(),ON));const float Room=OwnWidth+OtherWidth+MinimumRacingRoomCm;
    if(FMath::Abs(Gap)<360&&FMath::Abs(Side-S.DesiredLane)<Room&&FMath::Abs(Side-S.DesiredLane)<FMath::Abs(Side-ActualLane)){S.DesiredLane=ActualLane;S.bAlongside=true;}
    if(Gap>0&&(FMath::Abs(Side-ActualLane)<Room||FMath::Abs(Side-S.Lane)<Room)){const float Clearance=350+Speed*.15f;TrafficSpeed=FMath::Min(TrafficSpeed,FMath::Max(0.f,Other->GetDrivingSpeed()+(Gap-Clearance)*.6f));}
   }
  }
  float LookAhead=FMath::Clamp(350.f+Speed*.45f,400.f,900.f);
  if(bUseAdvancedPlanner&&TrackPlan.Samples.IsValidIndex(S.Segment)){const auto& Plan=TrackPlan.Samples[S.Segment];LookAhead=FMath::Clamp(320.f+Speed*.34f,350.f,Plan.BendDistance<1000?550.f:800.f);}
  const int32 TargetIndex=AheadIndex(S.Segment,LookAhead);
  const float GuideLane=Route->Guide.Num()==Route->Center.Num()?Lateral(Route->Guide[S.Segment],S.Segment):0;
  const FVector Target=(bEnableRacecraft||bUseAdvancedPlanner)?Route->LanePoint(TargetIndex,S.Lane-GuideLane,175):Route->LanePoint(TargetIndex,S.Lane);const FVector Local=P->GetActorRotation().UnrotateVector(Target-Pos);
  const float Curvature=2.f*Local.Y/FMath::Max(1.f,float(Local.SizeSquared2D()));
  S.Steering=P->SteeringForCurvature(Curvature);
  float TargetSpeed=FMath::Min(S.CruiseSpeed,TrafficSpeed);
  for(float Ahead:{350.f,650.f,1000.f,1500.f,2100.f}){const int32 I=AheadIndex(S.Segment,Ahead);const float Bend=FMath::Abs(FMath::Atan2(FVector::CrossProduct(Route->Tangent(S.Segment),Route->Tangent(I)).Z,FVector::DotProduct(Route->Tangent(S.Segment),Route->Tangent(I))));if(Bend>.12f)TargetSpeed=FMath::Min(TargetSpeed,FMath::Sqrt(210.f*Ahead/FMath::Max(.12f,Bend)));}
  if(bEnableRacecraft){const float Confidence=FMath::Clamp(S.Personality.BrakingConfidence,.75f,1.f);const float Consistency=FMath::Clamp(S.Personality.Consistency,0.f,1.f);TargetSpeed*=FMath::Lerp(Confidence,1.f,FMath::Clamp(TargetSpeed/S.CruiseSpeed,0.f,1.f))*(1-(1-Consistency)*.05f*(.5f+.5f*FMath::Sin(GetWorld()->GetTimeSeconds()*.3f+S.Slot)));}
  if(FMath::Abs(FMath::Atan2(Local.Y,Local.X))>.7f)TargetSpeed=FMath::Min(TargetSpeed,420.f);
  if(Excess>0)TargetSpeed=FMath::Min(TargetSpeed,420.f);
  S.GripEstimate=1;
  if(bUseAdvancedPlanner&&TrackPlan.Samples.IsValidIndex(S.Segment)){const auto* D=P->GetTireDynamics();S.GripEstimate=D?FMath::Clamp(FMath::Min(D->Telemetry.FrontGrip,D->Telemetry.RearGrip)/FMath::Max(.1f,D->AsphaltGrip),.25f,1.f):1;const int32 BrakeIndex=AheadIndex(S.Segment,Speed*(Tuning.BrakeMargin+(1-S.Personality.BrakingConfidence)*.4f));TargetSpeed=FMath::Min(S.CruiseSpeed,FMath::Min(TrackPlan.Samples[S.Segment].Speed,TrackPlan.Samples[BrakeIndex].Speed)*FMath::Sqrt(Tuning.LateralScale))*DriverPace(S,Dt)*FMath::Sqrt(S.GripEstimate);TargetSpeed=FMath::Min(TargetSpeed,TrafficSpeed);if(Excess>0)TargetSpeed=FMath::Min(TargetSpeed,350.f);}
  if(bUseAdvancedPlanner&&TrackPlan.Samples.IsValidIndex(S.Segment)){const float K=TrackPlan.Samples[S.Segment].Curvature;TargetSpeed*=FMath::Sqrt(FMath::Clamp(1-K*(S.Lane-GuideLane),.5f,1.f));}
  if(Excess>5||Local.X<0){S.State=EKartAIState::RECOVER_TO_TRACK;TargetSpeed=FMath::Min(TargetSpeed,200.f+150.f*FMath::Clamp(S.Personality.RecoverySkill,0.f,1.f));}
  if(S.Intent==4&&FMath::Abs(ActualLane-S.DesiredLane)>80&&TrackPlan.Samples.IsValidIndex(S.Segment)&&TrackPlan.Samples[S.Segment].BendDistance<1200)TargetSpeed=FMath::Min(TargetSpeed,150.f);
  S.LineError=ActualLane-S.Lane;S.DebugTargetSpeed=TargetSpeed;
  S.StuckTime=Speed<30&&(TargetSpeed>150||StoppedLeader)?S.StuckTime+Dt:0;
  bool RearClear=true;for(auto* Other:Traffic){if(Other==P)continue;const FVector LocalOther=P->GetActorRotation().UnrotateVector(Other->GetActorLocation()-Pos);if(LocalOther.X<150&&LocalOther.X>-650&&FMath::Abs(LocalOther.Y)<190)RearClear=false;if(LocalOther.X<0&&LocalOther.X>-2000&&FMath::Abs(LocalOther.Y)<220&&Other->GetDrivingSpeed()-Speed>0&&(-LocalOther.X)/(Other->GetDrivingSpeed()-Speed)<2.5f)RearClear=false;}
  FHitResult RearHit;FCollisionQueryParams Query;Query.AddIgnoredActor(P);if(GetWorld()->SweepSingleByChannel(RearHit,Pos,Pos-P->GetActorForwardVector()*450,P->GetActorQuat(),ECC_Visibility,FCollisionShape::MakeSphere(28),Query))RearClear=false;
  if(bEnableRacecraft){S.RecoveryWindow+=Dt;if(S.RecoveryWindow>60){S.RecoveryWindow=0;S.ReverseAttempts=0;}}
  if(S.StuckTime>3&&S.Cooldown<=0&&RearClear&&(!bEnableRacecraft||KartRacecraft::MayBackOff(StoppedLeader,S.bAlongside,S.ReverseAttempts))){++S.ReverseAttempts;S.ReverseTime=StoppedLeader?1.8f:1.2f;S.Cooldown=bEnableRacecraft?15:8;S.StuckTime=0;++S.Recoveries;}
  const auto* Power=P->GetTireDynamics();
  const float FeedForward=Power?float(KartDynamics::ThrottleForDriveForce(Power->EngineForceN,TargetSpeed*.01f*Power->MassKg*Power->LinearDragPerSecond+Power->RollingResistanceN)):TargetSpeed*.32f/600.f;
  float Throttle=FMath::Clamp((TargetSpeed-Speed)*.006f+FeedForward,-1.f,1.f);
  if(S.ReverseTime>0&&RearClear){S.ReverseTime-=Dt;Throttle=-.8f;S.Steering=-S.Steering;}else S.ReverseTime=0;
  float Brake=0;
  if(bUseAdvancedPlanner&&S.ReverseTime<=0){Brake=Speed>TargetSpeed+25?FMath::Clamp((Speed-TargetSpeed)*.003f,0.f,1.f):0;Throttle=Brake>0?0:FMath::Clamp(Throttle,0.f,1.f);S.SteeringCommand=FMath::FInterpConstantTo(S.SteeringCommand,S.Steering,Dt,FMath::Lerp(4.f,1.5f,(Tuning.Smoothness+S.Personality.SteeringSmoothness)*.5f));S.Steering=S.SteeringCommand;}
  if(TargetSpeed<20&&S.ReverseTime<=0){Brake=1;Throttle=0;}
  S.ThrottleCommand=Throttle;S.BrakeCommand=Brake;Input(Throttle,S.Steering,Brake);
  const float VisualSteer=P->GetSteeringVisualInput();
  if(auto* Driver=S.Driver.Get())if(auto* Anim=Cast<UAnimSequence>(Driver->AnimationData.AnimToPlay))Driver->SetPosition((VisualSteer+1.f)*.5f*Anim->GetPlayLength(),false);
  if(auto* Wheel=S.Wheel.Get())Wheel->SetRelativeRotation(FRotator(0,0,VisualSteer*25));
 }
 const double CpuMs=(FPlatformTime::Seconds()-CpuStart)*1000;CpuTotalMs+=CpuMs;CpuMaxMs=FMath::Max(CpuMaxMs,CpuMs);++CpuSamples;DrawAIDiagnostics(Dt);
 if(bTesting){
  ReportClock+=Dt;if(!Gate)TestRaceSeconds+=Dt;
  if(Gate&&GM->RedLightCount==5&&!bGateCaptured){bGateCaptured=true;WriteEvidence(false);if(auto* V=GetWorld()->GetGameViewport())V->Exec(GetWorld(),*FString::Printf(TEXT("HighResShot 1600x900 filename=%s"),*(FPaths::ProjectDir()/TEXT("Evidence/RacingAI/grid.png"))),*GLog);}
  if(ReportClock>5){ReportClock=0;WriteEvidence(false);}
  bool Completed=Opponents.Num()==FMath::Clamp(OpponentCount,0,19);for(const auto& S:Opponents)Completed=Completed&&S.Laps>=2;
  if(!bReported&&(Completed||TestRaceSeconds>420)){bReported=true;WriteEvidence(true);if(GetWorld()->WorldType!=EWorldType::PIE)FPlatformMisc::RequestExit(false);}
 }
}
void UTrackRacingAI::WriteEvidence(bool Final){
 const FString Dir=FPaths::ProjectDir()/TEXT("Evidence/RacingAI");IFileManager::Get().MakeDirectory(*Dir,true);auto* GM=Cast<AProofGameMode>(GetOwner());
 bool Passed=Final&&Opponents.Num()==FMath::Clamp(OpponentCount,0,19)&&GM&&GM->StartEventCount==1&&bGateCaptured;
 FString Rows;for(const auto& S:Opponents){Passed=Passed&&S.Laps>=2&&S.Visited.Num()==64&&S.MaximumGridMovement<1&&S.MaximumEdgeExcess<5;
  if(!Rows.IsEmpty())Rows+=TEXT(",");auto* P=S.Pawn.Get();const FVector Pos=P?P->GetActorLocation():FVector::ZeroVector;
  Rows+=FString::Printf(TEXT("{\"slot\":%d,\"laps\":%d,\"distance_cm\":%.2f,\"visited_sectors\":%d,\"maximum_grid_movement_cm\":%.3f,\"maximum_edge_excess_cm\":%.3f,\"off_track_frames\":%d,\"recoveries\":%d,\"maximum_speed_cms\":%.2f,\"x\":%.2f,\"y\":%.2f,\"driver_visible\":%s}"),S.Slot,S.Laps,S.Distance,S.Visited.Num(),S.MaximumGridMovement,S.MaximumEdgeExcess,S.OffTrackFrames,S.Recoveries,S.MaximumSpeed,Pos.X,Pos.Y,P&&((P->FindComponentByClass<UKartMechanicalVisuals>()&&P->FindComponentByClass<UKartMechanicalVisuals>()->bReady)||(S.Driver.IsValid()&&S.Driver->GetSkeletalMeshAsset()))?TEXT("true"):TEXT("false"));
 }
 const FString PlayerDebug=FString::Printf(TEXT("{\"segment\":%d,\"distance\":%.1f,\"speed\":%.1f,\"target\":%.1f,\"steer\":%.3f,\"x\":%.1f,\"y\":%.1f,\"recoveries\":%d}"),TestPlayer.Segment,TestPlayer.Distance,TestPlayer.Pawn.IsValid()?TestPlayer.Pawn->GetDrivingSpeed():0,TestPlayer.DebugTargetSpeed,TestPlayer.Steering,TestPlayer.Pawn.IsValid()?TestPlayer.Pawn->GetActorLocation().X:0,TestPlayer.Pawn.IsValid()?TestPlayer.Pawn->GetActorLocation().Y:0,TestPlayer.Recoveries);
 const FString Data=FString::Printf(TEXT("{\"final\":%s,\"passed\":%s,\"world_type\":%d,\"race_seconds\":%.2f,\"opponents\":%d,\"staged\":%d,\"start_events\":%d,\"five_red_gate_captured\":%s,\"route_samples\":%d,\"route_length_cm\":%.2f,\"test_player\":%s,\"racers\":[%s]}"),Final?TEXT("true"):TEXT("false"),Passed?TEXT("true"):TEXT("false"),int32(GetWorld()->WorldType),TestRaceSeconds,Opponents.Num(),GM?GM->StagedParticipantCount:0,GM?GM->StartEventCount:0,bGateCaptured?TEXT("true"):TEXT("false"),Route->Center.Num(),RouteLength,*PlayerDebug,*Rows);
 FFileHelper::SaveStringToFile(Data,*(Dir/(Final?TEXT("race_result.json"):TEXT("progress.json"))));if(Final)UE_LOG(LogTemp,Display,TEXT("RACING_AI_TEST %s"),*Data);
}

FString UTrackRacingAI::GetTrackPlanTelemetry() const {
 float Minimum=MAX_flt,Maximum=0,Width=MAX_flt,Violation=0;
 for(int32 I=0;I<TrackPlan.Samples.Num();++I){const auto& A=TrackPlan.Samples[I];const auto& B=TrackPlan.Samples[(I+1)%TrackPlan.Samples.Num()];Minimum=FMath::Min(Minimum,A.Speed);Maximum=FMath::Max(Maximum,A.Speed);Width=FMath::Min(Width,A.Width);const float Ds=FVector::Dist2D(A.Position,B.Position);Violation=FMath::Max(Violation,FMath::Square(A.Speed)-FMath::Square(B.Speed)-2*FMath::Max(100.f,TrackPlan.BrakeDeceleration+981.f*A.Grade)*Ds);}
 const FString Cost=FString::Printf(TEXT("\"ai_cpu_mean_ms\":%.5f,\"ai_cpu_max_ms\":%.5f,\"control_hz\":20,\"perception_hz\":10,\"difficulty\":%d,"),CpuSamples?CpuTotalMs/CpuSamples:0,CpuMaxMs,int32(Difficulty));
 return TEXT("{")+Cost+FString::Printf(TEXT("\"samples\":%d,\"minimum_speed_cms\":%.3f,\"maximum_speed_cms\":%.3f,\"minimum_width_cm\":%.2f,\"lateral_budget_cms2\":%.3f,\"braking_budget_cms2\":%.3f,\"braking_envelope_violation\":%.3f}"),TrackPlan.Samples.Num(),Minimum,Maximum,Width,TrackPlan.LateralAcceleration,TrackPlan.BrakeDeceleration,Violation);
}