"""Convert a static GLB (flat material colours, no textures) into a game prop: props/<key>.json
   python3 tools/import_prop.py in.glb key
Positions int16 mm, normals int8, uint16 indices; one group per material; all nodes merged (translation only)."""
import json,struct,sys,base64
import numpy as np
src,key=sys.argv[1],sys.argv[2]
b=open(src,'rb').read();l=struct.unpack('<I',b[12:16])[0];J=json.loads(b[20:20+l]);o=20+l;bl=struct.unpack('<I',b[o:o+4])[0];BIN=b[o+8:o+8+bl]
CT={5126:np.float32,5123:np.uint16,5125:np.uint32,5121:np.uint8};NC={'SCALAR':1,'VEC3':3,'VEC2':2,'VEC4':4}
def acc(i):
    a=J['accessors'][i];bv=J['bufferViews'][a['bufferView']];off=bv.get('byteOffset',0)+a.get('byteOffset',0);n=NC[a['type']];dt=CT[a['componentType']]
    cnt=a['count'];stride=bv.get('byteStride',0);isz=np.dtype(dt).itemsize*n
    if stride and stride!=isz:
        raw=np.frombuffer(BIN,dtype=np.uint8,count=stride*cnt,offset=off).reshape(cnt,stride)[:,:isz].copy();return np.frombuffer(raw.tobytes(),dtype=dt).reshape(cnt,n)
    return np.frombuffer(BIN,dtype=dt,count=cnt*n,offset=off).reshape(cnt,n)
# world translation of every node
par={}
for i,n in enumerate(J['nodes']):
    for c in n.get('children',[]):par[c]=i
def wt(i):
    t=np.array(J['nodes'][i].get('translation',[0,0,0]),float)
    while i in par:i=par[i];t+=np.array(J['nodes'][i].get('translation',[0,0,0]),float)
    return t
mats=[];bymat={}
nodes={}
for i,n in enumerate(J['nodes']):
    nodes[n.get('name',str(i))]=[round(float(v),3) for v in wt(i)]
    if 'mesh' not in n:continue
    T=wt(i)
    for pr in J['meshes'][n['mesh']]['primitives']:
        P=acc(pr['attributes']['POSITION']).astype(float)+T;N=acc(pr['attributes']['NORMAL']).astype(float)
        I=acc(pr['indices']).reshape(-1).astype(np.int64) if 'indices' in pr else np.arange(len(P))
        m=pr.get('material',0);bymat.setdefault(m,[]).append((P,N,I))
# per-node bounds of named parts (for couplers, bogies, wheels)
parts={}
for i,n in enumerate(J['nodes']):
    if 'mesh' not in n:continue
    T=wt(i);ps=[acc(pr['attributes']['POSITION']).astype(float)+T for pr in J['meshes'][n['mesh']]['primitives']]
    A=np.concatenate(ps);parts[n.get('name',str(i))]=[[round(float(v),3) for v in A.min(0)],[round(float(v),3) for v in A.max(0)]]
objs={};cur=None;oi=0
def newobj():
    global cur,oi
    cur={'P':[],'N':[],'I':[],'g':[],'nv':0};objs['body' if oi==0 else 'body%d'%(oi+1)]=cur;oi+=1
newobj()
allP=[]
for m,lst in bymat.items():
    M=J['materials'][m];pb=M.get('pbrMetallicRoughness',{});c=pb.get('baseColorFactor',[0.8,0.8,0.8,1]);em=M.get('emissiveFactor',[0,0,0])
    nm=M.get('name','');light=1 if any(w in nm.lower() for w in ['headlight','brake light','indicator','lamp']) else 0
    mats.append([round(c[0],4),round(c[1],4),round(c[2],4),round(c[3],3),light,round(pb.get('metallicFactor',0),2),round(pb.get('roughnessFactor',0.6),2),nm]);mi=len(mats)-1
    for P,N,I in lst:
        if cur['nv']+len(P)>65000:newobj()
        st=len(cur['I'])
        cur['I'].append(I+cur['nv']);cur['P'].append(P);cur['N'].append(N);cur['nv']+=len(P);allP.append(P)
        if cur['g'] and cur['g'][-1][0]==mi and cur['g'][-1][1]+cur['g'][-1][2]==st:cur['g'][-1][2]+=len(I)
        else:cur['g'].append([mi,int(sum(len(x) for x in cur['I'][:-1])),len(I)])
out={'objects':{},'mats':mats,'nodes':nodes,'parts':parts}
for k,o in objs.items():
    if not o['P']:continue
    P=np.concatenate(o['P']);N=np.concatenate(o['N']);I=np.concatenate(o['I'])
    nl=np.linalg.norm(N,axis=1,keepdims=True);nl[nl==0]=1;N=N/nl
    out['objects'][k]={'p':base64.b64encode(np.round(P*1000).astype('<i2').tobytes()).decode(),'n':base64.b64encode(np.clip(np.round(N*127),-127,127).astype('i1').tobytes()).decode(),
        'i':base64.b64encode(I.astype('<u2').tobytes()).decode(),'g':o['g']}
A=np.concatenate(allP);out['min']=[round(float(v),3) for v in A.min(0)];out['max']=[round(float(v),3) for v in A.max(0)]
json.dump(out,open('props/%s.json'%key,'w'),separators=(',',':'))
print(key,'verts',len(A),'objs',len(out['objects']),'bounds',out['min'],out['max'])
