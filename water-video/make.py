import math, os, subprocess
from PIL import Image, ImageDraw, ImageFont
from multiprocessing import Pool
W,H,FPS,DUR=1080,1920,24,8
N=FPS*DUR
def font(s):
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf","/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]:
        if os.path.exists(p): return ImageFont.truetype(p,s)
    return ImageFont.load_default()
F1,F2=font(66),font(44)
def ease(x): x=max(0,min(1,x)); return x*x*(3-2*x)
def lerp(a,b,u): return a+(b-a)*u
def lc(c1,c2,u): return tuple(int(lerp(a,b,u)) for a,b in zip(c1,c2))
def center(d,txt,y,f,fill):
    for j,line in enumerate(txt.split('\n')):
        w=d.textlength(line,font=f); d.text(((W-w)/2,y+j*84),line,font=f,fill=fill)
def drop(d,x,y,r,col):
    d.polygon([(x,y-r*2),(x-r,y),(x+r,y)],fill=col); d.ellipse([x-r,y-r,x+r,y+r],fill=col)
SKIN=(240,190,160); HAIR=(70,40,30); DRESS=(80,170,200)
STX,STY=540,1230   # stomach center
def frame(i):
    t=i/FPS
    base=Image.new("RGBA",(W,H),(205,235,250,255)); d=ImageDraw.Draw(base)
    d.rectangle([0,1500,W,H],fill=(185,225,245))
    # timeline values
    lift=ease((t-2.0)/0.6)-ease((t-5.2)/0.6)        # glass raised 0..1
    drinking=2.7<=t<=5.1
    L=0.85*ease((t-2.9)/2.4)                          # stomach level
    h=ease((t-3.3)/2.2)                               # plant health
    glass_level=1-0.75*ease((t-2.7)/2.4)
    smile=ease((t-4.8)/0.5)
    # hair back
    d.ellipse([410,490,670,790],fill=HAIR); d.ellipse([480,430,600,520],fill=HAIR)
    # neck & torso
    d.rectangle([505,720,575,830],fill=SKIN)
    d.polygon([(310,830),(770,830),(800,1500),(280,1500)],fill=DRESS)
    d.ellipse([310,780,770,900],fill=DRESS)
    # head
    d.ellipse([430,500,650,740],fill=SKIN)
    d.pieslice([420,480,660,700],180,360,fill=HAIR)
    tired=1-ease((t-2.0)/0.6)          # droopy lids at start
    for ex in (500,580):
        if lift>0.55 and drinking:     # eyes gently closed while sipping
            d.arc([ex-20,606,ex+20,636],200,340,fill=(60,40,30),width=5)
        else:
            ew,eh=22,15
            d.ellipse([ex-ew,620-eh,ex+ew,620+eh],fill=(255,255,255),outline=(90,60,50),width=2)
            lx=-2 if t<2.0 else 3*math.sin(t*2)
            d.ellipse([ex-11+lx,620-11,ex+11+lx,620+11],fill=(90,140,90))
            d.ellipse([ex-11+lx,620-11,ex+11+lx,620+11],outline=(50,90,50),width=2)
            d.ellipse([ex-5+lx,620-5,ex+5+lx,620+5],fill=(15,15,20))
            d.ellipse([ex-8+lx,620-9,ex-3+lx,620-4],fill=(255,255,255))
            d.arc([ex-ew-2,620-eh-4,ex+ew+2,620+eh],195,345,fill=(40,25,20),width=4)  # upper lash line
            for a in (215,250,290,325):
                x=ex+(ew+2)*math.cos(math.radians(a)); y=620+(eh+1)*math.sin(math.radians(a))
                d.line([(x,y),(x+7*math.cos(math.radians(a)),y+7*math.sin(math.radians(a)))],fill=(40,25,20),width=3)
            if tired>0.01:  # heavy eyelid
                d.rectangle([ex-ew-3,620-eh-4,ex+ew+3,620-eh+int(18*tired)],fill=SKIN)
                d.line([ex-ew,620-eh+int(18*tired),ex+ew,620-eh+int(18*tired)],fill=(40,25,20),width=4)
        d.line([(ex-24,602-(0 if lift>0.3 else -4)),(ex+22,597-(0 if lift>0.3 else -4))],fill=HAIR,width=6)  # brow
    d.ellipse([455,650,485,670],fill=(245,150,150)); d.ellipse([595,650,625,670],fill=(245,150,150))
    if lift>0.5: d.ellipse([524,678,556,700],fill=(170,70,80))          # open mouth
    elif smile>0.1: d.arc([510,660,570,700],20,160,fill=(170,70,80),width=6)
    else: d.line([515,690,565,690],fill=(170,70,80),width=6)
    # x-ray panel
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); o=ImageDraw.Draw(ov)
    o.rounded_rectangle([370,880,710,1420],radius=60,fill=(255,255,255,110),outline=(255,255,255,200),width=5)
    base=Image.alpha_composite(base,ov); d=ImageDraw.Draw(base)
    # esophagus
    d.rounded_rectangle([505,800,545,1100],radius=18,fill=(235,150,160),outline=(200,100,120),width=3)
    # water drops down the tube
    if drinking:
        for k in range(4):
            y=800+((t*1.1+k/4)%1)*280
            drop(d,525,y,10,(60,150,240))
    # stomach (mask fill)
    sx0,sy0,sx1,sy1=STX-130,STY-150,STX+130,STY+130
    d.ellipse([sx0,sy0,sx1,sy1],fill=(250,215,215),outline=(200,100,120),width=6)
    wl=Image.new("RGBA",(W,H),(0,0,0,0)); wd=ImageDraw.Draw(wl)
    top=sy1-(sy1-sy0)*L
    pts=[(x,top+6*math.sin(x/25+t*8)) for x in range(sx0,sx1+1,6)]
    wd.polygon(pts+[(sx1,sy1+5),(sx0,sy1+5)],fill=(60,150,240,235))
    mk=Image.new("L",(W,H),0); ImageDraw.Draw(mk).ellipse([sx0+4,sy0+4,sx1-4,sy1-4],fill=255)
    base.paste(wl,(0,0),Image.composite(wl.split()[3],Image.new("L",(W,H),0),mk))
    d=ImageDraw.Draw(base)
    # plant (grows from stomach top-right through chest)
    bx,by=630,STY-120; tx=bx+(1-h)*110; ty=by-180*(0.55+0.45*h)+(1-h)*70
    stem=(lc((150,130,70),(60,170,80),h))
    pts=[]
    for k in range(21):
        u=k/20; x=(1-u)**2*bx+2*(1-u)*u*(bx)+u*u*tx; y=(1-u)**2*by+2*(1-u)*u*(by-120*(0.6+0.4*h))+u*u*ty; pts.append((x,y))
    d.line(pts,fill=stem,width=12)
    for sgn in (-1,1):
        mx,my=pts[8]; ang=lerp(0.9,-0.5,h)
        ex=mx+sgn*70*math.cos(ang); ey=my-sgn*0*0+70*math.sin(ang)*sgn*-1+ (1-h)*30
        d.line([(mx,my),(ex,ey)],fill=stem,width=9); d.ellipse([ex-22,ey-12,ex+22,ey+12],fill=stem)
    pc=lc((170,150,120),(255,110,160),h); pr=lerp(22,40,h)
    for k in range(6):
        a=k*math.pi/3
        d.ellipse([tx+math.cos(a)*pr*1.1-pr*0.75,ty+math.sin(a)*pr*1.1-pr*0.75,tx+math.cos(a)*pr*1.1+pr*0.75,ty+math.sin(a)*pr*1.1+pr*0.75],fill=pc)
    d.ellipse([tx-pr*0.5,ty-pr*0.5,tx+pr*0.5,ty+pr*0.5],fill=lc((130,110,70),(255,210,60),h))
    # arm + glass
    hx,hy=lerp(330,455,lift),lerp(1120,720,lift)
    d.line([(350,880),(lerp(250,300,lift),lerp(1020,880,lift)),(hx,hy)],fill=SKIN,width=44,joint="curve")
    gw=lerp(110,100,0); gh=190
    gx,gy=hx-10,hy
    d.polygon([(gx-60,gy-gh/2),(gx+60,gy-gh/2),(gx+46,gy+gh/2),(gx-46,gy+gh/2)],fill=(235,248,255),outline=(120,170,200))
    wy=gy+gh/2-(gh-14)*glass_level
    if glass_level>0.02:
        wd2=lerp(60,46,(wy-(gy-gh/2))/gh)
        d.polygon([(gx-wd2+2,wy),(gx+wd2-2,wy),(gx+44,gy+gh/2-5),(gx-44,gy+gh/2-5)],fill=(90,170,245))
    d.ellipse([hx-24,hy-14,hx+24,hy+34],fill=SKIN)
    # sparkles at bloom
    if t>=5.3:
        s=ease((t-5.3)/0.6)
        for k in range(5):
            x=tx+math.cos(k*1.7)*95; y=ty+math.sin(k*2.3)*80
            r=(10+7*math.sin(t*8+k))*s
            for a in (0,math.pi/2):
                d.line([(x-r*2*math.cos(a),y-r*2*math.sin(a)),(x+r*2*math.cos(a),y+r*2*math.sin(a))],fill=(255,215,60),width=5)
    # captions
    if t<2.5: center(d,"A thirsty body is\na wilting plant...",190,F1,(70,60,40))
    elif t<5.2: center(d,"Sip water and\nwatch it bloom",190,F1,(20,90,170))
    else:
        center(d,"Stay hydrated for\nenergy, focus & digestion",170,F1,(20,110,150))
        center(d,"Drink water through the day",1620,F2,(40,70,100))
        drop(d,W/2,1760,22,(60,150,240))
    return base.convert("RGB")
def save(i): frame(i).save(f"frames/f{i:04d}.png")
if __name__=="__main__":
    os.makedirs("frames",exist_ok=True)
    with Pool(4) as p: p.map(save,range(N))
    subprocess.run(["ffmpeg","-y","-loglevel","error","-framerate",str(FPS),"-i","frames/f%04d.png","-i","audio.wav","-c:v","libx264","-preset","veryfast","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-shortest","water_hydration_vertical_1080x1920.mp4"],check=True)
