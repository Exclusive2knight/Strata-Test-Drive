(()=>{const S=window.__gs={dc:0,tri:0,buf:0,bufB:0,tex:0,texPx:0,frames:0};const P=WebGLRenderingContext.prototype,P2=window.WebGL2RenderingContext&&WebGL2RenderingContext.prototype;
for(const Q of [P,P2]){if(!Q)continue;const de=Q.drawElements,da=Q.drawArrays,bd=Q.bufferData,ti=Q.texImage2D,ts=Q.texSubImage2D;
Q.drawElements=function(m,c,t,o){S.dc++;S.tri+=c/3;if(S.big)S.big.push([c/3,new Error().stack.split('
')[2].trim().slice(0,90)]);return de.apply(this,arguments)};Q.drawArrays=function(m,f,c){S.dc++;S.tri+=c/3;return da.apply(this,arguments)};
Q.bufferData=function(t,d){S.buf++;S.bufB+=d&&d.byteLength||0;return bd.apply(this,arguments)};Q.texImage2D=function(){S.tex++;const a=arguments,el=a[a.length-1];S.texPx+=(el&&el.width?el.width*el.height:(a[3]*a[4]||0));return ti.apply(this,arguments)};
Q.texSubImage2D=function(){S.tex++;return ts.apply(this,arguments)}}})()