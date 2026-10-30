#pragma once
#include "CoreMinimal.h"
namespace KartRacecraft {
inline float SignedGap(float Other,float Own,float Length){return FMath::Fmod(Other-Own+Length*1.5f,Length)-Length*.5f;}
inline bool Conflict(float Gap,float OtherSpeed,float OwnSpeed,float OtherLane,float Lane){
 for(float T:{0.f,.5f,1.f,1.5f})if(FMath::Abs(Gap+(OtherSpeed-OwnSpeed)*T)<270&&FMath::Abs(OtherLane-Lane)<205)return true;
 return false;
}
inline bool MayDefend(float Gap,bool Alongside,float Cooldown,float Bend){return !Alongside&&Cooldown<=0&&Gap<-350&&Gap>-1400&&FMath::Abs(Bend)>.15f;}
inline bool MayBackOff(bool Blocked,bool Alongside,int32 Attempts){return !Alongside&&Attempts<(Blocked?1:2);}
}
