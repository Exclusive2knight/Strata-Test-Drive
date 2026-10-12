import sys,collections,numpy as np,json,base64
sys.path.insert(0,"/home/claude/strata")
import import_model as M
M.NODES={}
parts,_=M.load_gltf("x/Models/Two_Bay_Dual_Helix_Garage.glb")
names=sorted(set(p["node"] for p in parts));print([n for n in names if "Gate" in n or "Ticket" in n or "ped" in n.lower()])
skip=lambda n:any(k in n for k in ["Entry_Gate","Exit_Gate","Entry_Ticket","Exit_Ticket","Ticket_pedestal"])
G=collections.OrderedDict()
for p in parts:
  if skip(p["node"]):continue
  m=p["mat"];mk=m["name"]
  T=p["V"][p["F"]]  # (n,3,3)
  if p["node"]=="Labels":
    # the game world is the model mirrored front-to-back (its z runs the other way), which would show every sign's text backwards:
    # mirror each sign's text back across its own centre, along the direction the text runs
    C=T.mean(1);key=np.round(C/2.0).astype(int);T=T.copy()
    groups={}
    for i,k in enumerate(map(tuple,key)):groups.setdefault(k,[]).append(i)
    # merge neighbouring cells into whole signs
    lab={};nid=0
    for k in groups:
      if k in lab:continue
      stack=[k];lab[k]=nid
      while stack:
        c=stack.pop()
        for dx in(-1,0,1):
          for dy in(-1,0,1):
            for dz in(-1,0,1):
              n=(c[0]+dx,c[1]+dy,c[2]+dz)
              if n in groups and n not in lab:lab[n]=nid;stack.append(n)
      nid+=1
    sig={}
    for k,ids in groups.items():sig.setdefault(lab[k],[]).extend(ids)
    for ids in sig.values():
      V=T[ids].reshape(-1,3);mn=V.min(0);mx=V.max(0);ax=0 if (mx[0]-mn[0])>=(mx[2]-mn[2]) else 2;c=(mn[ax]+mx[ax])/2
      T[ids,:,ax]=2*c-T[ids,:,ax]
    print("labels",len(sig))
  G.setdefault(mk,{"m":m,"t":[]})["t"].append(T)
out=[];tot=0
for k,g in G.items():
  T=np.concatenate(g["t"]);tot+=len(T)
  q=np.round(T.reshape(-1,3)*100).astype("<i2")
  m=g["m"];c=[round(float(x),3) for x in m["color"]];e=[round(float(x),3) for x in m["emissive"]]
  out.append({"n":k,"c":c,"e":e,"mt":round(float(m["metal"]),2),"r":round(float(m["rough"]),2),"p":base64.b64encode(q.tobytes()).decode()})
  print(k,len(T),c,e)
json.dump({"v":2,"tris":tot,"g":out},open("/home/claude/strata-test-drive/models/garage_helix.json","w"),separators=(",",":"))
print("total",tot)
