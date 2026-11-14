(async()=>{const r=[];const ks=Object.keys(TRIMS).filter(k=>/^Chevrolet/.test(TRIMS[k].group||""));
 r.push(ks.length+" Chevy trims");const bad=[];
 for(const k of ["chv_silverado_1500_ctb","chv_silverado_2500_hd_cus","chv_traverse_hc","chv_trax_lt2","chv_trailblazer_lt","chv_c8_2lt","chv_c8_3lt","chv_eray","chv_z06","chv_zr1"]){if(!TRIMS[k])bad.push("missing "+k)}
 for(const k of ks){const T=TRIMS[k];if(!PRICE[k])bad.push("noprice "+k);if(!DRIVES[k])bad.push("nodrive "+k)}
 // drive a couple of the changed ones for a few seconds
 for(const k of ["chv_silverado_1500_ctb","chv_trailblazer_ls","chv_zr1","chv_tahoe_z71","chv_colorado_wt"]){try{setTrim(k,true);await loadModel(TRIMS[k].model);st.gear="D";st.started=true;st.power=true;sys.epb=false;car.vx=0;SIM(6,()=>{inp.thr=1});r.push(k+" "+(car.vx*2.237).toFixed(0)+" mph after 6 s, "+(TRIMS[k].desc))}catch(e){bad.push(k+" "+e)}}
 r.push(bad.length?bad.join("; "):"no problems");
 r.push(ks.map(k=>TRIMS[k].short+" $"+PRICE[k]).join(" | "));return r.join("\n")})()
