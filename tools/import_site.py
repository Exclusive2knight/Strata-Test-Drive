"""Convert a big static GLB scene (flat material colours, translation-only nodes) into game props.
   python3 tools/import_site.py in.glb key [--skip a,b] [--part name=key ...]
Positions are int16 with a scale k (stored in the file) so sites up to about 65 m from the origin fit; normals int8.
--skip drops nodes whose name starts with any of the given prefixes.
--part pulls one node out into its own prop props/<key>.json, centred on the node's own pivot (for animated parts)."""
import json,struct,sys,base64
import numpy as np
args=sys.argv[1:];src,key=args[0],args[1];skip=[];partmap={}
i=2
while i<len(args):
    if args[i]=='--skip':skip=args[i+1].split(',');i+=2
    elif args[i]=='--part':n,k=args[i+1].split('=');partmap[n]=k;i+=2
    else:i+=1
b=open(src,'rb').read();l=struct.unpack('<I',b[12:16])[0];J=json.loads(b[20:20+l]);o=20+l;bl=struct.unpack('<I',b[o:o+4])[0];BIN=b[o+8:o+8+bl]
CT={5126:np.float32,5123:np.uint16,5125:np.uint32,5121:np.uint8};NC={'SCALAR':1,'VEC3':3,'VEC2':2,'VEC4':4}
def acc(i):
    a=J['accessors'][i];bv=J['bufferViews'][a['bufferView']];off=bv.get('byteOffset',0)+a.get('byteOffset',0);n=NC[a['type']];dt=CT[a['componentType']]
    cnt=a['count'];stride=bv.get('byteStride',0);isz=np.dtype(dt).itemsize*n
    if stride and stride!=isz:
        raw=np.frombuffer(BIN,dtype=np.uint8,count=stride*cnt,offset=off).reshape(cnt,stride)[:,:isz].copy();return np.frombuffer(raw.tobytes(),dtype=dt).reshape(cnt,n)
    return np.frombuffer(BIN,dtype=dt,count=cnt*n,offset=off).reshape(cnt,n)
par={}
for i,n in enumerate(J['nodes']):
    for c in n.get('children',[]):par[c]=i
for n in J['nodes']:
    if 'rotation' in n or 'scale' in n or 'matrix' in n:sys.exit('node with rotation/scale: not supported')
def wt(i):
    t=np.array(J['nodes'][i].get('translation',[0,0,0]),float)
    while i in par:i=par[i];t+=np.array(J['nodes'][i].get('translation',[0,0,0]),float)
    return t
def matrow(M):
    pb=M.get('pbrMetallicRoughness',{});c=pb.get('baseColorFactor',[0.8,0.8,0.8,1]);nm=M.get('name','');em=M.get('emissiveFactor',[0,0,0])
    light=1 if any(w in nm.lower() for w in ['led','lights','indicator','lamp']) or max(em)>0.3 else 0
    return [round(c[0],4),round(c[1],4),round(c[2],4),round(c[3],3),light,round(pb.get('metallicFactor',0),2),round(pb.get('roughnessFactor',0.6),2),nm]
def build(nodes_sel,origin):
    mats=[];mi_of={};bymat={};allP=[]
    for i,T in nodes_sel:
        n=J['nodes'][i]
        for pr in J['meshes'][n['mesh']]['primitives']:
            P=acc(pr['attributes']['POSITION']).astype(float)+T-origin;N=acc(pr['attributes']['NORMAL']).astype(float)
            I=acc(pr['indices']).reshape(-1).astype(np.int64) if 'indices' in pr else np.arange(len(P))
            bymat.setdefault(pr.get('material',0),[]).append((P,N,I));allP.append(P)
    A=np.concatenate(allP);ext=float(np.abs(A).max());k=1000 if ext<32 else 500 if ext<64 else 250
    objs=[];cur=None
    def newobj():
        o={'P':[],'N':[],'I':[],'g':[],'nv':0,'ni':0};objs.append(o);return o
    cur=newobj()
    for m,lst in bymat.items():
        if m not in mi_of:mats.append(matrow(J['materials'][m]));mi_of[m]=len(mats)-1
        mi=mi_of[m]
        for P,N,I in lst:
            if cur['nv']+len(P)>65000:cur=newobj()
            st=cur['ni'];cur['I'].append(I+cur['nv']);cur['P'].append(P);cur['N'].append(N);cur['nv']+=len(P);cur['ni']+=len(I)
            if cur['g'] and cur['g'][-1][0]==mi and cur['g'][-1][1]+cur['g'][-1][2]==st:cur['g'][-1][2]+=len(I)
            else:cur['g'].append([mi,st,len(I)])
    out={'k':k,'objects':{},'mats':mats,'min':[round(float(v),3) for v in A.min(0)],'max':[round(float(v),3) for v in A.max(0)]}
    for j,o in enumerate(objs):
        P=np.concatenate(o['P']);N=np.concatenate(o['N']);I=np.concatenate(o['I'])
        nl=np.linalg.norm(N,axis=1,keepdims=True);nl[nl==0]=1;N=N/nl
        out['objects']['body' if j==0 else 'body%d'%(j+1)]={'p':base64.b64encode(np.clip(np.round(P*k),-32767,32767).astype('<i2').tobytes()).decode(),'n':base64.b64encode(np.clip(np.round(N*127),-127,127).astype('i1').tobytes()).decode(),'i':base64.b64encode(I.astype('<u2').tobytes()).decode(),'g':o['g']}
    return out
static=[];parts={};pivots={};bounds={}
for i,n in enumerate(J['nodes']):
    if 'mesh' not in n:continue
    nm=n.get('name',str(i));T=wt(i)
    A=np.concatenate([acc(p['attributes']['POSITION']).astype(float)+T for p in J['meshes'][n['mesh']]['primitives']]);bounds[nm]=[[round(float(v),3) for v in A.min(0)],[round(float(v),3) for v in A.max(0)]];pivots[nm]=[round(float(v),3) for v in T]
    if any(nm.startswith(s) for s in skip):continue
    hit=[p for p in partmap if nm==p or (p.endswith('*') and nm.startswith(p[:-1]))]
    if hit:parts.setdefault(partmap[hit[0]],[]).append((i,T,nm));continue
    static.append((i,T))
out=build(static,np.zeros(3));out['nodes']=pivots;out['parts']=bounds
json.dump(out,open(f'props/{key}.json','w'),separators=(',',':'))
print(key,'k',out['k'],'objects',len(out['objects']),'mats',len(out['mats']),'bytes',len(json.dumps(out)))
for pk,lst in parts.items():
    i,T,nm=lst[0];o=build([(i,T)],T);json.dump(o,open(f'props/{pk}.json','w'),separators=(',',':'));print(pk,'from',nm,'pivot',np.round(T,2),'bytes',len(json.dumps(o)))
