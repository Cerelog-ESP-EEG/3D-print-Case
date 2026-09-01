"""Z-buffer preview render of the case. Plain Python, no FreeCAD.

    python3 export_board_mesh.py   (via freecadcmd, first)
    python3 render_preview.py

Writes design/preview.png.

This uses a real z-buffer rasteriser. An earlier version used painter's
algorithm, which has no true occlusion and drew the engraved text through
the solid lid - it looked like the engraving cut all the way through when
it never did. Do not replace this with depth sorting.
"""
import os, sys, struct, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _paths
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

P = _paths.params()
S = _paths.TOOLS + os.sep
D = _paths.DESIGN_DIR + os.sep
W, H = 920, 660


def load(p,dz=0.0):
    b=open(p,'rb').read(); n=struct.unpack('<I',b[80:84])[0]
    a=np.frombuffer(b[84:84+n*50],dtype=np.uint8).reshape(n,50)
    tri=a[:,12:48].copy().view('<f4').reshape(n,3,3).astype(np.float64)
    if dz: tri=tri+np.array([0,0,dz])
    e1=tri[:,1]-tri[:,0]; e2=tri[:,2]-tri[:,0]
    nr=np.cross(e1,e2); ln=np.linalg.norm(nr,axis=1,keepdims=True); ln[ln==0]=1
    return tri, nr/ln

def cam(elev,azim):
    e,a=np.radians(elev),np.radians(azim)
    f=np.array([np.cos(e)*np.cos(a),np.cos(e)*np.sin(a),np.sin(e)])
    up=np.array([0,0,1.0])
    if abs(f@up)>0.999: up=np.array([0,1.0,0])
    r=np.cross(up,f); r/=np.linalg.norm(r); u=np.cross(f,r)
    return np.stack([r,u,f])

def render(items,elev,azim,bg=(1.0,1.0,1.0)):
    R=cam(elev,azim); fwd=R[2]
    key=fwd+np.array([0.30,-0.45,0.55]); key/=np.linalg.norm(key)
    fill=np.array([-0.4,0.3,0.2]); fill/=np.linalg.norm(fill)
    P=[];C=[]
    for tri,nrm,col in items:
        keep=(nrm@fwd)>-0.03
        tri,nrm=tri[keep],nrm[keep]
        if not len(tri): continue
        v=tri@R.T
        inten=0.34+0.60*np.clip(nrm@key,0,1)+0.16*np.clip(nrm@fill,0,1)
        P.append(v); C.append(np.clip(np.array(col)[None,:]*inten[:,None],0,1))
    V=np.concatenate(P); C=np.concatenate(C)
    xy=V[:,:,:2].reshape(-1,2)
    mn,mx=xy.min(0),xy.max(0); ctr=(mn+mx)/2; half=(mx-mn).max()/2*1.06
    sc=min(W,H)/(2*half)
    px=(V[:,:,0]-ctr[0])*sc+W/2
    py=H/2-(V[:,:,1]-ctr[1])*sc
    pz=V[:,:,2]
    img=np.ones((H,W,3))*np.array(bg); zb=np.full((H,W),-1e18)
    x0=np.clip(np.floor(px.min(1)).astype(int),0,W-1); x1=np.clip(np.ceil(px.max(1)).astype(int),0,W-1)
    y0=np.clip(np.floor(py.min(1)).astype(int),0,H-1); y1=np.clip(np.ceil(py.max(1)).astype(int),0,H-1)
    ax,ay=px[:,0],py[:,0]; bx,by=px[:,1],py[:,1]; cx,cy=px[:,2],py[:,2]
    den=(by-cy)*(ax-cx)+(cx-bx)*(ay-cy)
    ok=np.abs(den)>1e-12
    for i in np.nonzero(ok)[0]:
        X0,X1,Y0,Y1=x0[i],x1[i],y0[i],y1[i]
        if X1<X0 or Y1<Y0: continue
        xs=np.arange(X0,X1+1)+0.5; ys=np.arange(Y0,Y1+1)+0.5
        gx,gy=np.meshgrid(xs,ys)
        d=den[i]
        l1=((by[i]-cy[i])*(gx-cx[i])+(cx[i]-bx[i])*(gy-cy[i]))/d
        l2=((cy[i]-ay[i])*(gx-cx[i])+(ax[i]-cx[i])*(gy-cy[i]))/d
        l3=1.0-l1-l2
        m=(l1>=-1e-9)&(l2>=-1e-9)&(l3>=-1e-9)
        if not m.any(): continue
        z=l1*pz[i,0]+l2*pz[i,1]+l3*pz[i,2]
        sub=zb[Y0:Y1+1,X0:X1+1]
        upd=m&(z>sub)
        if not upd.any(): continue
        sub[upd]=z[upd]
        img[Y0:Y1+1,X0:X1+1][upd]=C[i]
    return img

def roll_long_axis(item):
    """Roll the part over about its LONG (X) axis: (x,y,z) -> (x,-y,-z).

    This is how you physically turn a 120 mm case over to reach the DIP
    switches, and it is the frame the bottom legend is mirrored for. Winding
    is reversed by the flip, so two vertices are swapped to keep normals out.
    """
    tri, _ = item
    t = tri * np.array([1.0, -1.0, -1.0])
    t = t[:, [0, 2, 1], :]
    e1 = t[:,1]-t[:,0]; e2 = t[:,2]-t[:,0]
    n = np.cross(e1,e2); ln = np.linalg.norm(n,axis=1,keepdims=True); ln[ln==0]=1
    return t, n/ln

base=load(_paths.BASE_STL); lid=load(_paths.LID_STL)
base_rolled=roll_long_axis(base)
pcb=load(S+"_pv_pcb.stl"); comp=load(S+"_pv_comp.stl")
lidup=load(_paths.LID_STL,dz=22.0)
CB=(0.62,0.66,0.72); CL=(0.74,0.78,0.84); CP=(0.10,0.48,0.30); CC=(0.80,0.78,0.73)
B=(*base,CB); BR=(*base_rolled,CB); L=(*lid,CL); LU=(*lidup,CL); PB=(*pcb,CP); CM=(*comp,CC)

specs=[
 ("Base, populated",                [B,PB,CM], 32,-128),
 ("Base, empty - pegs + DIP switch holes", [B], 36,-128),
 ("Lid top - engraving + LED holes",[L],       62,-96),
 ("Lid underside - sleeves + snaps",[L],     -52,-84),
 ("Exploded assembly",              [B,PB,CM,LU],26,-128),
 ("Case rolled over - DIP switch mode legend", [BR], 68,-90),
]
fig=plt.figure(figsize=(17,10.5),facecolor='white')
for i,(t,items,el,az) in enumerate(specs,1):
    t0=time.time(); im=render(items,el,az)
    ax=fig.add_subplot(2,3,i); ax.imshow(im); ax.axis('off')
    ax.set_title(t,fontsize=11.5,color='#111',pad=6)
    print("  %-36s %5.1fs"%(t,time.time()-t0))
fig.suptitle("Cerelog ESP-EEG 16CH enclosure   %.2f x %.2f x %.2f mm"%(P["OUT_L"],P["OUT_W"],P["TOTAL_H"])+"",fontsize=15,y=0.97)
fig.tight_layout(rect=(0,0,1,0.945))
fig.savefig(D+"preview.png",dpi=115,facecolor='white')
print("ok")
