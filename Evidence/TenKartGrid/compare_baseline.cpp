#include "KartTireModel.h"
#include <cstdio>
int main(){using namespace KartDynamics;for(int c=4;c<=5;c++){Parameters p;State s;Contact g;Input i;s.U=11;double mb=0;int drift=0;for(int k=0;k<2400;k++){double t=k*StepSeconds;i={};if(t<1){i.Throttle=.8;i.Steering=.12;}else if(t<1.6){i.Brake=1;i.Steering=.12;}else{i.Throttle=std::abs(s.Beta)>Rad(2)||std::abs(s.R)>.15?.3:.8;i.Steering=c==5?std::clamp(s.Beta*1.5-s.R*.12,-.8,.8):0;}Step(s,p,g,i);mb=std::max(mb,std::abs(Deg(s.Beta)));drift+=s.Drifting;}printf("case=%d max_beta=%.9f drift_steps=%d\n",c,mb,drift);}}
