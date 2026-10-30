#pragma once
#include <algorithm>

// Presentation only. RaceStartGantry/HUD samples the authoritative light events;
// this helper never advances a timer or releases driving controls.
namespace RaceCountdownPresentation {
struct Frame { int Number=-1; double Alpha=0,Scale=1; }; // 0 means START.
inline Frame Sample(int RedCount,double Age,double Duration,bool Started){
 Frame Result;
 if(Duration<=0 || Age<0 || Age>=Duration || (!Started && (RedCount<1 || RedCount>5)))return Result;
 Result.Number=Started?0:6-RedCount;
 const double T=Age/Duration;
 auto Ease=[](double X){X=std::clamp(X,0.0,1.0);return X*X*X*(X*(X*6-15)+10);};
 Result.Alpha=Ease(T/.18)*(1-Ease((T-.42)/.58));
 Result.Scale=1;
 return Result;
}
}

