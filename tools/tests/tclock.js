(()=>{const out=[];
 st.clockX=1; GT.speed=undefined; const a0=GT.min; SIM(5,()=>{}); const d1=GT.min-a0;
 st.clockX=4; const b0=GT.min; SIM(5,()=>{}); const d4=GT.min-b0;
 st.rmot=1; sys.shake=0.5; SIM(0.5,()=>{}); out.push("shake after rmot: "+sys.shake.toFixed(3));
 st.clockX=1; st.rmot=0;
 return "clock 1x: "+d1.toFixed(2)+" min in 5 s; 4x: "+d4.toFixed(2)+" min in 5 s; hits "+(typeof hits!=="undefined"?hits:"n/a")+"\n"+out.join("\n");})()
