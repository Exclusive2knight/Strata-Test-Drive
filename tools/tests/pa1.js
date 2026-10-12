// park assist in the two-bay dual helix garage: the lowest north bay (A0) heading east, both rows
(async()=>[await PAT("garage A0 east, right (inner row)",()=>{GREF=0;resetCar({free:true,x:GAR.cx-21,y:GAR.cy+12,h:0,z:garZ(1,0,-21)})},1),await PAT("garage A0 east, left (outer row)",()=>{GREF=0;resetCar({free:true,x:GAR.cx-21,y:GAR.cy+12,h:0,z:garZ(1,0,-21)})},-1)].join("\n"))()
