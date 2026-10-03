import math, random, subprocess, os
from PIL import Image, ImageDraw, ImageFont
from multiprocessing import Pool
W,H,FPS,DUR=1080,1920,24,8
N=FPS*DUR
def font(s):
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf","/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]:
        if os.path.exists(p): return ImageFont.truetype(p,s)
    return ImageFont.load_default()
F1,F2=font(64),font(44)
X0,TW,GAP=85,140,14
TY0,TY1=800,1120
random.seed(4)
blobs=[[(random.uniform(.1,.9),random.uniform(.05,.95),random.uniform(14,30)) for _ in range(9)] for _ in range(6)]
def ease(x): x=max(0,min(1,x)); return x*x*(3-2*x)
def center(d,txt,y,f,fill):
    for j,line in enumerate(txt.split('\n')):
        w=d.textlength(line,font=f); d.text(((W-w)/2,y+j*80),line,font=f,fill=fill)
def frame(i):
    t=i/FPS
    im=Image.new("RGB",(W,H),(214,238,247)); d=ImageDraw.Draw(im)
    d.rectangle([0,0,W,H//2],fill=(200,230,245))
    # gum
    d.rounded_rectangle([40,700,1040,830],radius=40,fill=(236,120,140))
    grow=ease(t/2.4)
    brush_x=X0-120+ease((t-2.6)/2.2)*(910+240) if 2.6<=t<=4.9 else (-999 if t<2.6 else 9999)
    # teeth
    for k in range(6):
        x=X0+k*(TW+GAP)
        d.rounded_rectangle([x,TY0,x+TW,TY1],radius=45,fill=(252,252,250),outline=(205,210,215),width=3)
    # plaque on teeth fronts (cleared left of brush)
    for k in range(6):
        x=X0+k*(TW+GAP)
        for (bx,by,r) in blobs[k]:
            cx,cy=x+bx*TW,TY0+30+by*(TY1-TY0-60)
            if cx<brush_x-20: continue
            rr=r*grow*(1+0.05*math.sin(t*5+cx))
            if rr>1: d.ellipse([cx-rr,cy-rr,cx+rr,cy+rr],fill=(150,160,60))
    # gap plaque (cleared by floss)
    for g in range(5):
        gx=X0+(g+1)*(TW+GAP)-GAP/2
        clr=ease((t-(5.1+g*0.3))/0.3)
        if clr<1:
            h=(TY1-TY0-40)*grow
            d.rounded_rectangle([gx-9,TY0+20,gx+9,TY0+20+h],radius=8,fill=(110,120,40))
    # floss
    if 5.0<=t<=6.9:
        g=min(4,int((t-5.1)/0.3)) if t>=5.1 else 0
        gx=X0+(g+1)*(TW+GAP)-GAP/2
        sw=math.sin(t*40)*8
        # floss comes from top
        ty=TY0-60+ease((t-5.0)/0.15)*0 
        d.line([(gx-90,TY0-120),(gx+sw,TY0+10),(gx-sw,TY1-30),(gx+90,TY1+90)],fill=(60,120,230),width=6,joint="curve")
    # brush
    if 2.6<=t<=4.9:
        bx=brush_x; wob=math.sin(t*30)*14
        d.rounded_rectangle([bx-40,TY0-10+wob,bx+40,TY1+10+wob],radius=14,fill=(40,150,230))
        for q in range(8):
            yy=TY0+q*28+wob
            d.rectangle([bx-34,yy,bx+34,yy+14],fill=(255,255,255))
        d.rounded_rectangle([bx-14,TY1+10+wob,bx+14,TY1+190+wob],radius=12,fill=(30,110,190))
    # sparkles
    if t>=5.9:
        s=ease((t-5.9)/0.6)
        for k in range(6):
            x=X0+k*(TW+GAP)+TW/2+ (k%2)*20-10
            y=TY0+60+(k*37)%110
            r=(10+8*math.sin(t*8+k*1.3))*s
            if r>0:
                for a in (0,math.pi/2):
                    d.line([(x-r*2*math.cos(a),y-r*2*math.sin(a)),(x+r*2*math.cos(a),y+r*2*math.sin(a))],fill=(255,215,60),width=5)
    # captions
    if t<2.5: center(d,"Plaque builds up like\nmud on a fence...",260,F1,(70,60,30))
    elif t<5.0: center(d,"BRUSH sweeps\nthe fronts clean",260,F1,(20,90,160))
    elif t<6.9: center(d,"FLOSS cleans the gaps\nbrushes miss",260,F1,(40,90,200))
    else:
        center(d,"Brush + Floss =\nHealthy Teeth & Gums",260,F1,(20,110,80))
        center(d,"Brush 2x a day · Floss daily",1450,F2,(60,80,100))
    return im
def save(i): frame(i).save(f"frames/f{i:04d}.png")
if __name__=="__main__":
    os.makedirs("frames",exist_ok=True)
    with Pool(4) as p: p.map(save,range(N))
    subprocess.run(["ffmpeg","-y","-loglevel","error","-framerate",str(FPS),"-i","frames/f%04d.png","-i","audio.wav","-c:v","libx264","-preset","veryfast","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-shortest","dental_hygiene_vertical_1080x1920.mp4"],check=True)
