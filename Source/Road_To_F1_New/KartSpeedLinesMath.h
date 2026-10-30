#pragma once
#include "CoreMinimal.h"
namespace KartSpeedLines {
inline float Strength(float Speed,float Start=19,float Noticeable=34,float Strong=49,float Full=61){
 Noticeable=FMath::Max(Start+.1f,Noticeable);Strong=FMath::Max(Noticeable+.1f,Strong);Full=FMath::Max(Strong+.1f,Full);
 auto Ramp=[](float X,float A,float B){float T=FMath::Clamp((X-A)/(B-A),0.f,1.f);return T*T*(3-2*T);};
 return .15f*Ramp(Speed,Start,Noticeable)+.45f*Ramp(Speed,Noticeable,Strong)+.4f*Ramp(Speed,Strong,Full);
}
inline float Smooth(float Current,float Target,float Dt){return FMath::Lerp(Current,Target,1.f-FMath::Exp(-5.f*FMath::Max(0.f,Dt)));}
}
