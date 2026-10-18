import math, struct, zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STOPS = [(0.0,(78,234,255)),(.34,(94,140,255)),(.68,(182,124,255)),(1.0,(255,120,223))]
BG=(7,16,24); FG=(244,251,255)

def gradient(t):
    for i in range(len(STOPS)-1):
        a,ca=STOPS[i]; b,cb=STOPS[i+1]
        if t <= b: 
            q=max(0,min(1,(t-a)/(b-a))); return tuple(round(ca[k]*(1-q)+cb[k]*q) for k in range(3))
    return STOPS[-1][1]

def blend(dst, src, alpha): return tuple(round(dst[k]*(1-alpha)+src[k]*alpha) for k in range(3))
def line_point(x,y, x1,y1,x2,y2,width, color, alpha, px):
    dx=x2-x1; dy=y2-y1; den=dx*dx+dy*dy
    q=max(0,min(1,((x-x1)*dx+(y-y1)*dy)/den)) if den else 0
    d=((x-(x1+q*dx))**2+(y-(y1+q*dy))**2)**.5
    if d <= width: px[0]=blend(px[0],color,alpha*(1-d/width if width else 1))
def render(path,w,h,portrait):
    data=bytearray(w*h*3)
    for y in range(h):
      for x in range(w):
        nx=x/w; ny=y/h
        t=(nx*.62+ny*.38)
        glow=math.exp(-(((nx-.5)/.7)**2+((ny-(.35 if portrait else .5))/.75)**2)*2.4)
        c=blend(BG,(94,140,255) if portrait else (182,124,255),.34*glow if portrait else .28*glow)
        p=[c]
        # crisp geometry corresponding to the SVG masters
        if portrait:
          lines=[(-120,1850,510,360,900,360,1410,1850),( -80,2140,390,990,680,700,1410,2140)]
          center=(645,1398); radius=255; axis=(645,480,645,2310,180,1398,1110,1398)
          border=(44,44,1246,2752,34)
        else:
          lines=[(130,1840,930,250,1790,250,2600,1840),(0,1660,690,960,1120,700,2732,1660)]
          center=(1366,1024); radius=330; axis=(1366,180,1366,1868,450,1024,2282,1024)
          border=(42,42,2690,2006,36)
        for l in lines:
          for a,b,c1,d,e,f,g,hh in [l]:
            # two connected segments, gradient sampled by x position
            line_point(x,y,a,b,c1,d,2.5,gradient((x/w+y/h)*.5),.9,p)
            line_point(x,y,c1,d,e,f,2.5,gradient((x/w+y/h)*.5+.2),.9,p)
            line_point(x,y,e,f,g,hh,2.5,gradient((x/w+y/h)*.5+.4),.9,p)
        line_point(x,y,*axis[:4],2.0,FG,.11,p); line_point(x,y,*axis[4:],2.0,FG,.11,p)
        bx,by,ex,ey,r=border; dist= min(abs(x-bx),abs(x-ex),abs(y-by),abs(y-ey));
        if dist<1.5: p[0]=blend(p[0],FG,.08)
        rr=((x-center[0])**2+(y-center[1])**2)**.5
        if abs(rr-radius)<2.0: p[0]=blend(p[0],gradient((x/w+y/h)*.5),.72)
        if rr<18: p[0]=blend(p[0],FG,1)
        i=(y*w+x)*3; data[i:i+3]=bytes(p[0])
    raw=b''.join(b'\x00'+data[y*w*3:(y+1)*w*3] for y in range(h))
    def chunk(t,d): return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
    png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw,6))+chunk(b'IEND',b'')
    path.write_bytes(png)
render(ROOT/'collections/efirio-signature/assets/wallpaper-portrait.png',1290,2796,True)
render(ROOT/'collections/efirio-signature/assets/wallpaper-landscape.png',2732,2048,False)
