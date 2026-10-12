// park assist on an upper tier: B1 heading west (uphill) and A2 heading east
(async()=>[await PAT("garage B1 west uphill, right",()=>{GREF=garZ(-1,1,21);resetCar({free:true,x:GAR.cx+21,y:GAR.cy-12,h:Math.PI,z:garZ(-1,1,21)})},1),await PAT("garage A2 east, left",()=>{GREF=garZ(1,2,-21);resetCar({free:true,x:GAR.cx-21,y:GAR.cy+12,h:0,z:garZ(1,2,-21)})},-1)].join("\n"))()
