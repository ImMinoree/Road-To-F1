#include "KartMechanicalVisuals.h"
#include "KartVisualKinematics.h"
#include "KartRaceSettings.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "ProofPawn.h"
#include "KartTireDynamics.h"
#include "LocalKartDriverVisuals.h"
#include "Animation/AnimSequence.h"
#include "Camera/CameraComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/PoseableMeshComponent.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "GameFramework/PlayerController.h"
#include "Engine/World.h"
#include "Engine/StaticMesh.h"
#include "Engine/SkeletalMesh.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"

namespace {const FString MechanicalAssetFolder=TEXT("/Game/RoadToF1/PlayerVehicleV4/");constexpr float FrontRadius=17.589f,RearRadius=20.938f;
void Cosmetic(UMeshComponent* C){C->SetCollisionEnabled(ECollisionEnabled::NoCollision);C->SetGenerateOverlapEvents(false);C->SetCanEverAffectNavigation(false);C->SetIsReplicated(false);}
}
UKartMechanicalVisuals::UKartMechanicalVisuals(){PrimaryComponentTick.bCanEverTick=true;PrimaryComponentTick.TickGroup=TG_PostUpdateWork;SetIsReplicatedByDefault(false);}
UStaticMeshComponent* UKartMechanicalVisuals::Add(const FString& Name,USceneComponent* Parent,const FVector& Location){
 auto* Mesh=LoadObject<UStaticMesh>(nullptr,*(MechanicalAssetFolder+TEXT("SM_V4_")+Name+TEXT(".SM_V4_")+Name));if(!Mesh)return nullptr;
 auto* C=NewObject<UStaticMeshComponent>(GetOwner(),*FString::Printf(TEXT("V4_%s_%d"),*Name,Parts.Num()));GetOwner()->AddInstanceComponent(C);C->SetupAttachment(Parent);C->SetStaticMesh(Mesh);C->SetRelativeLocation(Location);Cosmetic(C);C->RegisterComponent();Parts.Add(C);return C;
}
void UKartMechanicalVisuals::BeginPlay(){
 Super::BeginPlay();auto* Pawn=Cast<AProofPawn>(GetOwner());
 if(!bEnabled||!Pawn||GetNetMode()==NM_DedicatedServer||FParse::Param(FCommandLine::Get(),TEXT("LegacyKartVisuals")))return;
 // Validate every reference before touching the existing renderer.
 for(const TCHAR* N:{TEXT("Chassis"),TEXT("Column"),TEXT("Pitman"),TEXT("KnuckleFL"),TEXT("KnuckleFR"),TEXT("WheelFL"),TEXT("WheelFR"),TEXT("WheelRL"),TEXT("WheelRR"),TEXT("TieRod"),TEXT("RearAxle"),TEXT("BrakeDisc"),TEXT("Sprocket"),TEXT("Caliper"),TEXT("Pedall"),TEXT("Pedalr"),TEXT("SteeringWheel"),TEXT("ChainLink")}){
  const FString Path=MechanicalAssetFolder+TEXT("SM_V4_")+N;if(!LoadObject<UStaticMesh>(nullptr,*(Path+TEXT(".SM_V4_")+N))){UE_LOG(LogTemp,Error,TEXT("V4 visual asset missing: %s; preserving legacy"),*Path);return;}
 }
 auto* Full=LoadObject<USkeletalMesh>(nullptr,*(MechanicalAssetFolder+TEXT("SK_V4_DriverFull.SK_V4_DriverFull")));auto* Cockpit=Pawn->bRacingAI?Full:LoadObject<USkeletalMesh>(nullptr,*(MechanicalAssetFolder+TEXT("SK_V4_DriverPOV.SK_V4_DriverPOV")));Steering=LoadObject<UAnimSequence>(nullptr,*(MechanicalAssetFolder+TEXT("A_V4_Steering.A_V4_Steering")));
 if(!Full||!Cockpit||!Steering||!Full->GetSkeleton()||!Cockpit->GetSkeleton()||!Steering->GetSkeleton()||Full->GetSkeleton()!=Steering->GetSkeleton()||Cockpit->GetSkeleton()!=Steering->GetSkeleton()){UE_LOG(LogTemp,Error,TEXT("V4 incompatible driver skeleton; preserving legacy"));return;}
 Root=NewObject<USceneComponent>(Pawn,TEXT("V4_Assembly"));Pawn->AddInstanceComponent(Root);Root->SetupAttachment(Pawn->GetRootComponent());Root->SetRelativeLocation(FVector(0,0,-31));Root->RegisterComponent();AddTickPrerequisiteActor(Pawn);
 Add(TEXT("Chassis"),Root);Add(TEXT("Column"),Root,KartVisual::WheelCenter());Add(TEXT("Pitman"),Root,KartVisual::ColumnBottom());
 auto* Left=Add(TEXT("KnuckleFL"),Root,KartVisual::Kingpin(-1));Add(TEXT("WheelFL"),Left,FVector(0,-7,0));
 auto* Right=Add(TEXT("KnuckleFR"),Root,KartVisual::Kingpin(1));Add(TEXT("WheelFR"),Right,FVector(0,7,0));
 Add(TEXT("TieRod"),Root);Add(TEXT("TieRod"),Root);
 auto* Axle=Add(TEXT("RearAxle"),Root,FVector(-44,0,RearRadius));Add(TEXT("WheelRL"),Axle,FVector(0,-53,0));Add(TEXT("WheelRR"),Axle,FVector(0,53,0));Add(TEXT("BrakeDisc"),Axle,FVector(0,-30,0));Add(TEXT("Sprocket"),Axle,FVector(0,36,0));
 Add(TEXT("Caliper"),Root);Add(TEXT("Pedall"),Root,FVector(66,-17,22.3));Add(TEXT("Pedalr"),Root,FVector(66,17,22.3));
 Add(TEXT("SteeringWheel"),Root,KartVisual::WheelCenter());
 auto* Clutch=Add(TEXT("Sprocket"),Root,FVector(-22,36,35));Clutch->SetRelativeScale3D(FVector(.45));
 // Four ball ends articulate with the actual rod endpoints.
 for(int I=0;I<4;++I){auto* C=NewObject<UStaticMeshComponent>(Pawn,*FString::Printf(TEXT("V4_RodEnd%d"),I));Pawn->AddInstanceComponent(C);C->SetupAttachment(Root);C->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Sphere.Sphere")));C->SetRelativeScale3D(FVector(.022));C->SetMaterial(0,Parts[1]->GetMaterial(0));Cosmetic(C);C->RegisterComponent();Parts.Add(C);}
 Sampler=NewObject<USkeletalMeshComponent>(Pawn,TEXT("V4_DriverPoseSampler"));Pawn->AddInstanceComponent(Sampler);Sampler->SetupAttachment(Root);Sampler->SetSkeletalMeshAsset(Full);Sampler->SetAnimationMode(EAnimationMode::AnimationSingleNode);Cosmetic(Sampler);Sampler->SetVisibility(false);Sampler->VisibilityBasedAnimTickOption=EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;Sampler->RegisterComponent();Sampler->SetAnimation(Steering);Sampler->SetPlayRate(0);Sampler->SetComponentTickEnabled(false);
 auto CreateDriver=[&](const TCHAR* Name,USkeletalMesh* Mesh){auto* C=NewObject<UPoseableMeshComponent>(Pawn,Name);Pawn->AddInstanceComponent(C);C->SetupAttachment(Root);C->SetSkinnedAssetAndUpdate(Mesh);Cosmetic(C);C->RegisterComponent();return C;};
 Driver=CreateDriver(TEXT("V4_SeatedDriver"),Full);Driver->SetOwnerNoSee(!Pawn->bRacingAI);
 if(!Pawn->bRacingAI){POV=CreateDriver(TEXT("V4_CockpitDriver"),Cockpit);POV->SetOnlyOwnerSee(true);POV->SetCastShadow(false);}
 Chain=NewObject<UInstancedStaticMeshComponent>(Pawn,TEXT("V4_Chain"));Pawn->AddInstanceComponent(Chain);Chain->SetupAttachment(Root);Chain->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,*(MechanicalAssetFolder+TEXT("SM_V4_ChainLink.SM_V4_ChainLink"))));Cosmetic(Chain);Chain->RegisterComponent();for(int I=0;I<70;++I)Chain->AddInstance(FTransform::Identity);
 bReady=true;
 if(auto* Old=Pawn->FindComponentByClass<ULocalKartDriverVisuals>())Old->SetCockpitEnabled(false);
 // Eye is fitted to the lowered seated head; preserve camera switching and chase rig.
 TArray<UCameraComponent*> Cameras;if(!Pawn->bRacingAI)Pawn->GetComponents(Cameras);for(auto* Camera:Cameras)if(Camera->GetName()==TEXT("DriverEye")){Camera->SetRelativeLocation(FVector(-31.6,0,61.4));Camera->SetRelativeRotation(FRotator(-10,0,0));Camera->SetFieldOfView(95);if(auto* Old=Pawn->FindComponentByClass<ULocalKartDriverVisuals>())Old->UseMechanicalCamera(Camera);}
 TickComponent(0,LEVELTICK_All,nullptr);
}
void UKartMechanicalVisuals::PoseLeg(UPoseableMeshComponent* Mesh,const TCHAR* Side,const FVector& Pivot,float Degrees){
 const FName Up(*FString::Printf(TEXT("thigh_%s"),Side)),Low(*FString::Printf(TEXT("calf_%s"),Side)),End(*FString::Printf(TEXT("foot_%s"),Side));
 FTransform A=Mesh->GetBoneTransformByName(Up,EBoneSpaces::ComponentSpace),B=Mesh->GetBoneTransformByName(Low,EBoneSpaces::ComponentSpace),C=Mesh->GetBoneTransformByName(End,EBoneSpaces::ComponentSpace);
 const FQuat Q(FVector::YAxisVector,FMath::DegreesToRadians(Degrees));const FVector Hip=A.GetLocation(),Knee=B.GetLocation(),OldFoot=C.GetLocation(),Foot=Pivot+Q.RotateVector(OldFoot-Pivot);
 const float L1=FVector::Dist(Hip,Knee),L2=FVector::Dist(Knee,OldFoot),D=FVector::Dist(Hip,Foot);if(D<.01f||D>=L1+L2-.01f)return;
 const FVector Dir=(Foot-Hip)/D;FVector Pole=Knee-Hip;Pole=(Pole-Dir*FVector::DotProduct(Pole,Dir)).GetSafeNormal();const float Along=(L1*L1-L2*L2+D*D)/(2*D);const FVector NewKnee=Hip+Dir*Along+Pole*FMath::Sqrt(FMath::Max(0.f,L1*L1-Along*Along));
 A.SetRotation(FQuat::FindBetweenNormals((Knee-Hip).GetSafeNormal(),(NewKnee-Hip).GetSafeNormal())*A.GetRotation());Mesh->SetBoneTransformByName(Up,A,EBoneSpaces::ComponentSpace);
 B.SetLocation(NewKnee);B.SetRotation(FQuat::FindBetweenNormals((OldFoot-Knee).GetSafeNormal(),(Foot-NewKnee).GetSafeNormal())*B.GetRotation());Mesh->SetBoneTransformByName(Low,B,EBoneSpaces::ComponentSpace);C.SetLocation(Foot);C.SetRotation(Q*C.GetRotation());Mesh->SetBoneTransformByName(End,C,EBoneSpaces::ComponentSpace);
}
void UKartMechanicalVisuals::TickComponent(float Dt,ELevelTick Type,FActorComponentTickFunction* Tick){
 Super::TickComponent(Dt,Type,Tick);auto* Pawn=Cast<AProofPawn>(GetOwner());if(!bReady||!Pawn)return;
 const int32 Slot=Pawn->AssignedGridPosition>0?Pawn->AssignedGridPosition:(Pawn->PreferredGridPosition>0?Pawn->PreferredGridPosition:KartRace::PlayerGridPosition);
 if(Slot!=LiverySlot)ApplyLivery(Slot);
 const auto* Dynamics=Pawn->bUseTireDynamics?Pawn->GetTireDynamics():nullptr;
 const float Steer=Dynamics?FMath::RadiansToDegrees(float(Dynamics->GetState().Steer)):Pawn->GetSteeringVisualInput()*24;
 const auto S=KartVisual::Solve(Steer);ColumnDegrees=S.Column;LeftSteeringDegrees=S.Left;RightSteeringDegrees=S.Right;
 const float WheelDegrees=KartVisual::SteeringWheelDegrees(ColumnDegrees);
 const FQuat Column(KartVisual::ColumnAxis(),FMath::DegreesToRadians(WheelDegrees));Parts[1]->SetRelativeRotation(Column);Parts[17]->SetRelativeRotation(Column);
 // Preserve the solved pitman and tie-rod endpoints independently of the cockpit rotation.
 Parts[2]->SetRelativeRotation(FQuat(KartVisual::ColumnAxis(),FMath::DegreesToRadians(ColumnDegrees)));
 Parts[3]->SetRelativeRotation(FRotator(0,S.Left,0));Parts[5]->SetRelativeRotation(FRotator(0,S.Right,0));MaximumRodErrorCm=0;
 for(int I=0;I<2;++I){const int Side=I?1:-1;FVector A=KartVisual::Pin(S.Column),B=KartVisual::Pickup(Side,I?S.Right:S.Left);auto* Rod=Parts[7+I].Get();Rod->SetRelativeLocation(A);Rod->SetRelativeRotation((B-A).Rotation());Rod->SetRelativeScale3D(FVector(FVector::Dist(A,B)/100,1,1));MaximumRodErrorCm=FMath::Max(MaximumRodErrorCm,FMath::Abs(FVector::Dist(A,B)-KartVisual::RodLength(Side)));Parts[19+I*2]->SetRelativeLocation(A);Parts[20+I*2]->SetRelativeLocation(B);}
 const float U=Pawn->GetDrivingSpeed(),V=Dynamics?float(Dynamics->GetState().V*100):0,R=Dynamics?float(Dynamics->GetState().R):0;
 const float Step=FMath::Clamp(Dt,0.f,.1f);RearPhase=FMath::Fmod(RearPhase+U/RearRadius*Step,2*PI);RearRollingDegrees=FMath::RadiansToDegrees(RearPhase);Parts[9]->SetRelativeRotation(FQuat(FVector::YAxisVector,RearPhase));Parts[18]->SetRelativeRotation(FQuat(FVector::YAxisVector,RearPhase*10/4.5));
 for(int I=0;I<2;++I){const float A=FMath::DegreesToRadians(I?S.Right:S.Left),Y=I?53.f:-53.f;const float Speed=(U-R*Y)*FMath::Cos(A)+(V+R*60)*FMath::Sin(A);FrontPhase[I]=FMath::Fmod(FrontPhase[I]+Speed/FrontRadius*Step,2*PI);Parts[I?6:4]->SetRelativeRotation(FQuat(FVector::YAxisVector,FrontPhase[I]));}
 ThrottlePedal=FMath::Clamp(Pawn->GetVisualThrottle(),0.f,1.f);BrakePedal=Pawn->GetVisualBrake();Parts[15]->SetRelativeRotation(FRotator(BrakePedal*12,0,0));Parts[16]->SetRelativeRotation(FRotator(ThrottlePedal*12,0,0));
 Sampler->SetPosition((1-FMath::Clamp(WheelDegrees/45.f,-1.f,1.f))*.5f*Steering->GetPlayLength(),false);Sampler->TickAnimation(0,false);Sampler->RefreshBoneTransforms();
 for(auto* Mesh:{Driver.Get(),POV.Get()})if(Mesh){Mesh->CopyPoseFromSkeletalComponent(Sampler);PoseLeg(Mesh,TEXT("l"),FVector(66,-17,22.3),-BrakePedal*12);PoseLeg(Mesh,TEXT("r"),FVector(66,17,22.3),-ThrottlePedal*12);}
 const bool External=Pawn->IsThirdPersonView();Driver->SetOwnerNoSee(!Pawn->bRacingAI&&!External);if(POV)POV->SetHiddenInGame(External);
 // Convex support polygon of unequal sprockets, sampled by arc length. Link count stays fixed.
 TArray<FVector> Path;TArray<float> Length;float Total=0;const FVector Rear(-44,36,RearRadius),Engine(-22,36,35);
 for(int I=0;I<=128;++I){const float A=I*2*PI/128;FVector N(FMath::Cos(A),0,FMath::Sin(A));Path.Add(FVector::DotProduct(N,Engine-Rear)>5.5f?Engine+N*4.5f:Rear+N*10);if(I)Total+=FVector::Dist(Path[I-1],Path[I]);Length.Add(Total);}
 const int Count=Chain->GetInstanceCount();const float Pitch=Total/Count;auto Sample=[&](float Distance){Distance=FMath::Fmod(Distance+Total*10000,Total);int I=1;while(I<Length.Num()-1&&Length[I]<Distance)++I;return FMath::Lerp(Path[I-1],Path[I],(Distance-Length[I-1])/FMath::Max(.001f,Length[I]-Length[I-1]));};
 for(int I=0;I<Count;++I){const float D=I*Pitch-float(RearPhase)*10;const FVector A=Sample(D),B=Sample(D+.2f);FTransform T((B-A).Rotation(),A,FVector(Pitch/1.27f,1,1));Chain->UpdateInstanceTransform(I,T,false,I==Count-1,true);}
}




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
 for(const auto& Part:Parts)Apply(Part.Get(),false);Apply(Driver,true);Apply(POV,true);
}

