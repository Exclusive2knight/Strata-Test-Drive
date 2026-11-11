"""Sign pack -> the overhead structures the game builds from (gantries, cantilever, message boards).
   python3 tools/import_signs.py <folder with the pack's GLBs>   ->  prints the SIGN_KIT line for src/app_template.html
Roadside signs are built from their shapes and sizes in the game (one shared atlas for every face), so only the
structures are converted: concrete footings, columns, trusses, cabinets and brackets, merged by material.
Bolts and the message-board vent slots are dropped (thousands of vertices nobody can see at 100 km/h).
Each vertex keeps a class: 0 = moves with the left column, 1 = stretches with the span, 2 = moves with the right column."""
import json,struct,sys,re,os
import numpy as np
D=sys.argv[1]
def load(f):
    b=open(f,'rb').read();n=struct.unpack('<I',b[12:16])[0];j=json.loads(b[20:20+n]);o=20+n;bl=struct.unpack('<I',b[o:o+4])[0];return j,b[o+8:o+8+bl]
def acc(j,B,i):
    a=j['accessors'][i];bv=j['bufferViews'][a['bufferView']];off=bv.get('byteOffset',0)+a.get('byteOffset',0)
    nc={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];dt={5126:'<f4',5123:'<u2',5125:'<u4',5121:'u1'}[a['componentType']]
    return np.frombuffer(B,dt,a['count']*nc,off).reshape(a['count'],nc) if nc>1 else np.frombuffer(B,dt,a['count'],off)
def M(nd):
    t=nd.get('translation',[0,0,0]);x,y,z,w=nd.get('rotation',[0,0,0,1]);s=nd.get('scale',[1,1,1])
    R=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
    return R*np.array(s),np.array(t)
MATCOL={'concrete':0,'metal':1,'dark':2}
def kit(fname,drop=r'^(Bolt|Vent slot)'):
    j,B=load(os.path.join(D,fname));parts={};faces=[]
    for nd in j['nodes']:
        if 'mesh' not in nd:continue
        nm=re.sub(r'\.\d+$','',nd.get('name',''))
        if re.match(drop,nm):continue
        R,t=M(nd)
        for p in j['meshes'][nd['mesh']]['primitives']:
            P=acc(j,B,p['attributes']['POSITION'])@R.T+t;N=acc(j,B,p['attributes']['NORMAL'])@R.T;I=acc(j,B,p['indices']).astype(int)
            mt=j['materials'][p.get('material',0)];mn=mt['name']
            if 'baseColorTexture' in mt.get('pbrMetallicRoughness',{}):   # a sign face or display: keep only its rectangle
                faces.append([round(float(P[:,0].min()),3),round(float(P[:,1].min()),3),round(float(P[:,0].max()),3),round(float(P[:,1].max()),3),round(float(P[:,2].max()),3)]);continue
            mc='concrete' if 'Concrete' in mn else ('dark' if re.search('cabinet|bracket|clamp|Mount|Bridge',nm,re.I) else 'metal')
            if nm=='DMS cabinet':mc='dark'
            cls=1 if not re.search('footing|column',nm,re.I) else (0 if P[:,0].mean()<0 else 2)
            L=parts.setdefault(mc,{'p':[],'n':[],'i':[],'c':[]});base=len(L['p'])//3
            L['p']+=[int(round(v*1000)) for v in P.reshape(-1)];L['n']+=[int(round(v*100)) for v in N.reshape(-1)];L['i']+=[int(v)+base for v in I];L['c']+=[cls]*len(P)
    return {'parts':parts,'faces':faces}
import base64
K={'gantry':kit('Overhead_Highway_Gantry.glb',r'^(Bolt|Vent slot|Concrete footing)'),'cant':kit('Cantilever_Exit_Gantry.glb',r'^(Bolt|Vent slot|Concrete footing)'),'dmsb':kit('Bridge_Mounted_Digital_Board_Blank.glb')}
# the gantry-mounted message board is the plain gantry with the bridge board's cabinet hung on it (same model in the pack)
K['dmsg']={'faces':kit('Digital_Board_Gantry_Blank.glb')['faces']}
def pack(L):   # int16 mm positions, int8 normals, uint16 indices, uint8 class: base64 so the kit stays small
    return {'p':base64.b64encode(np.array(L['p'],'<i2').tobytes()).decode(),'n':base64.b64encode(np.clip(np.array(L['n'])*127//100,-127,127).astype('i1').tobytes()).decode(),
            'i':base64.b64encode(np.array(L['i'],'<u2').tobytes()).decode(),'c':base64.b64encode(np.array(L['c'],'u1').tobytes()).decode()}
for k,v in K.items():
    if 'parts' in v:v['parts']={m:pack(L) for m,L in v['parts'].items()}
print('const SIGN_KIT='+json.dumps(K,separators=(',',':'))+';')
