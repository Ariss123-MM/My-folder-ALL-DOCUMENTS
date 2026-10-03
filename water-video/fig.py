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
SKIN=(150,100,68); HAIR=(70,40,30); DRESS=(80,170,200)
SHIRT=(225,140,60)
STX,STY=540,1230   # stomach center
def frame(i,male=False):
    t=i/FPS
    base=Image.new("RGBA",(W,H),(232,218,196,255) if male else (205,235,250,255)); d=ImageDraw.Draw(base)
    d.rectangle([0,1500,W,H],fill=(215,198,170) if male else (185,225,245))
    # timeline values
    lift=ease((t-2.0)/0.6)-ease((t-5.2)/0.6)        # glass raised 0..1
    drinking=2.7<=t<=5.1
    L=0.85*ease((t-2.9)/2.4)                          # stomach level
    h=ease((t-3.3)/2.2)                               # plant health
    glass_level=1-0.75*ease((t-2.7)/2.4)
    smile=ease((t-4.8)/0.5)
    if male: lift=0; drinking=False; L=0.04; h=0; glass_level=0; smile=0
    # hair back
    if not male: d.ellipse([415,492,665,760],fill=HAIR)
    # neck & torso
    d.rectangle([505,720,575,830],fill=SKIN)
    DR=SHIRT if male else DRESS
    d.polygon([(310,830),(770,830),(800,1500),(280,1500)],fill=DR)
    d.ellipse([310,780,770,900],fill=DR)
    # head
    if male:
        for ex in (428,652): d.ellipse([ex-16,615,ex+16,670],fill=(138,90,60))
    d.ellipse([430,500,650,740],fill=SKIN)
    if male:   # neat fade: dense flat-top, stepped taper at the temples
        d.pieslice([430,488,650,700],200,340,fill=HAIR)
        for k in range(4):
            col=lc(HAIR,SKIN,(k+1)/5)
            d.pieslice([430,488,650,700],200-9*(k+1),200-9*k,fill=col)
            d.pieslice([430,488,650,700],340+9*k,340+9*(k+1),fill=col)
        d.line([(452,572),(628,572)],fill=(35,20,15),width=3)   # crisp hairline
    else:      # braided style: hair cap with cornrow lines, braids hang to both sides
        d.pieslice([420,480,660,700],180,360,fill=HAIR)
        for x in range(485,600,28): d.line([(540+(x-540)*0.35,498),(x,586)],fill=(40,25,18),width=3)
        for side in (-1,1):
            for j,(sx,ex2,ey) in enumerate([(432,380,1020),(424,350,1090),(442,408,970)]):
                for u in range(0,41):
                    p=u/40; x=lerp(sx,ex2,p)+3*math.sin(p*12); y=lerp(590,ey,p)
                    X=540+side*(540-x) if side==1 else x
                    cc=(75,48,36) if u%2 else (48,30,22)
                    d.ellipse([X-11,y-9,X+11,y+9],fill=cc)
                X=540+side*(540-ex2) if side==1 else ex2
                d.ellipse([X-9,ey-6,X+9,ey+12],fill=(225,180,60))   # gold bead
    tired=1.0 if male else 1-ease((t-2.0)/0.6)          # droopy lids at start
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
    d.ellipse([455,650,485,670],fill=(190,105,95)); d.ellipse([595,650,625,670],fill=(190,105,95))
    LIP=(120,50,55); LIPH=(165,85,85)
    if lift>0.5: d.ellipse([520,676,560,704],fill=(70,25,30),outline=LIP,width=8)          # open mouth, moderate lips
    elif smile>0.1:
        d.arc([508,658,572,702],20,160,fill=LIP,width=14); d.arc([514,664,566,696],40,140,fill=LIPH,width=3)
    elif male: d.arc([508,690,572,724],200,340,fill=LIP,width=14)
    else:
        d.rounded_rectangle([512,684,568,704],radius=9,fill=LIP); d.line([514,693,566,693],fill=(60,20,25),width=3); d.line([524,688,556,688],fill=LIPH,width=2)
    if male:
        for ex in (500,580): d.arc([ex-22,628,ex+22,652],20,160,fill=(105,68,55),width=4)   # eye bags
        for k in range(120): 
            x=470+(k*37)%140; y=665+(k*53)%75
            if (x-540)**2/70**2+(y-680)**2/40**2>0.2 and y>690: d.point((x,y),fill=(90,58,44))
        for k in range(3):
            u=(t*0.6+k/3)%1; drop(d,452+k*5,540+u*130,7,(110,180,240))
        for k in range(3):
            u=(t*0.5+k/3+0.2)%1; drop(d,632-k*4,540+u*130,7,(110,180,240))
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
    if t>=5.3 and not male:
        s=ease((t-5.3)/0.6)
        for k in range(5):
            x=tx+math.cos(k*1.7)*95; y=ty+math.sin(k*2.3)*80
            r=(10+7*math.sin(t*8+k))*s
            for a in (0,math.pi/2):
                d.line([(x-r*2*math.cos(a),y-r*2*math.sin(a)),(x+r*2*math.cos(a),y+r*2*math.sin(a))],fill=(255,215,60),width=5)
    # captions
    if male: return base.convert('RGB')
    if t<2.5: center(d,"A thirsty body is\na wilting plant...",190,F1,(70,60,40))
    elif t<5.2: center(d,"Sip water and\nwatch it bloom",190,F1,(20,90,170))
    else:
        center(d,"Stay hydrated for\nenergy, focus & digestion",170,F1,(20,110,150))
        center(d,"Drink water through the day",1620,F2,(40,70,100))
        drop(d,W/2,1760,22,(60,150,240))
    return base.convert("RGB")
