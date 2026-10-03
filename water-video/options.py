import math
from PIL import Image, ImageDraw, ImageFont
SKIN=(150,100,68); HAIR=(70,40,30); DARK=(40,25,18); LIP=(120,50,55); LIPH=(165,85,85)
SHIRT=(225,140,60); DRESS=(80,170,200)
def font(s): return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",s)
def lc(a,b,u): return tuple(int(x+(y-x)*u) for x,y in zip(a,b))
def lerp(a,b,u): return a+(b-a)*u
def face(d,male,lipy=690):
    d.rectangle([505,720,575,830],fill=SKIN)
    d.polygon([(310,830),(770,830),(800,1100),(280,1100)],fill=SHIRT if male else DRESS)
    d.ellipse([310,780,770,900],fill=SHIRT if male else DRESS)
    if male:
        for ex in (428,652): d.ellipse([ex-16,615,ex+16,670],fill=(138,90,60))
    d.ellipse([430,500,650,740],fill=SKIN)
def features(d,male,lipy=692):
    for ex in (500,580):
        d.ellipse([ex-22,605,ex+22,635],fill=(255,255,255),outline=(90,60,50),width=2)
        d.ellipse([ex-11,609,ex+11,631],fill=(90,140,90)); d.ellipse([ex-5,615,ex+5,625],fill=(15,15,20)); d.ellipse([ex-8,611,ex-3,616],fill=(255,255,255))
        d.arc([ex-24,602,ex+24,632],195,345,fill=DARK,width=4)
        d.line([(ex-24,598),(ex+22,593)],fill=HAIR,width=6)
    d.ellipse([455,650,485,670],fill=(190,105,95)); d.ellipse([595,650,625,670],fill=(190,105,95))
    d.arc([532,650,548,672],60,120,fill=(110,70,50),width=3)
    d.arc([508,lipy-32,572,lipy+12],20,160,fill=LIP,width=14); d.arc([514,lipy-26,566,lipy+6],40,140,fill=LIPH,width=3)
def fade(d,top=488,steps=4,h=212,x0=430,x1=650):
    d.pieslice([x0,top,x1,top+h],200,340,fill=HAIR)
    for k in range(steps):
        col=lc(HAIR,SKIN,(k+1)/(steps+1))
        d.pieslice([x0,top,x1,top+h],200-9*(k+1),200-9*k,fill=col); d.pieslice([x0,top,x1,top+h],340+9*k,340+9*(k+1),fill=col)
def braid(d,sx,ex,ey,side,y0=590,bead=True,r=11):
    for u in range(0,41):
        p=u/40; x=lerp(sx,ex,p)+3*math.sin(p*12); y=lerp(y0,ey,p)
        X=540+(540-x) if side==1 else x
        d.ellipse([X-r,y-r*0.82,X+r,y+r*0.82],fill=(75,48,36) if u%2 else (48,30,22))
    X=540+(540-ex) if side==1 else ex
    if bead: d.ellipse([X-9,ey-6,X+9,ey+12],fill=(225,180,60))
# ---------- men
def m1(d):  # flat-top fade (current)
    face(d,True); fade(d); d.line([(452,572),(628,572)],fill=DARK,width=3); features(d,True)
def m2(d):  # high fade + full beard
    face(d,True); fade(d,top=470,steps=5,h=225,x0=432,x1=648)
    d.polygon([(436,630),(446,700),(488,742),(540,756),(592,742),(634,700),(644,630),(622,690),(590,708),(540,716),(490,708),(458,690)],fill=DARK)
    features(d,True,lipy=700)
    d.ellipse([505,672,575,690],fill=DARK)   # mustache
    d.arc([512,684,568,706],20,160,fill=LIP,width=10)
def m3(d):  # low taper + goatee
    face(d,True); fade(d,top=492,steps=3,h=205); d.line([(455,575),(625,575)],fill=DARK,width=3); features(d,True)
    d.ellipse([514,714,566,748],fill=DARK); d.line([(500,684),(580,684)],fill=DARK,width=5)
    d.arc([512,664,568,708],20,160,fill=LIP,width=12)
def m4(d):  # high-top fade (big curly top) + light stubble
    face(d,True); d.ellipse([438,420,642,590],fill=HAIR)
    for k in range(18):
        a=k*0.35; d.ellipse([540+math.cos(a)*85-8,505+math.sin(a)*60-8,540+math.cos(a)*85+8,505+math.sin(a)*60+8],fill=(55,32,24))
    d.pieslice([430,500,650,700],195,345,fill=lc(HAIR,SKIN,0.0))
    for k in range(3):
        col=lc(HAIR,SKIN,(k+1)/4)
        d.pieslice([430,500,650,700],195-10*(k+1),195-10*k,fill=col); d.pieslice([430,500,650,700],345+10*k,345+10*(k+1),fill=col)
    d.polygon([(445,650),(470,730),(540,742),(610,730),(635,650),(600,720),(540,728),(480,720)],fill=(95,62,46))
    features(d,True)
# ---------- women
def w1(d):  # long box braids (current)
    face(d,False); d.ellipse([415,492,665,760],fill=HAIR); d.pieslice([420,480,660,700],180,360,fill=HAIR)
    d.ellipse([430,500,650,740],fill=SKIN); d.pieslice([420,480,660,700],180,360,fill=HAIR)
    for x in range(485,600,28): d.line([(540+(x-540)*0.35,498),(x,586)],fill=DARK,width=3)
    for side in (-1,1):
        for sx,ex,ey in [(432,380,1020),(424,350,1090),(442,408,970)]: braid(d,sx,ex,ey,1 if side==1 else -1)
    features(d,False)
def w2(d):  # braided high bun with face-framing braids
    face(d,False); d.ellipse([485,395,595,500],fill=HAIR)
    for k in range(5): d.arc([490+k*4,400+k*3,590-k*4,495-k*3],0,360,fill=(95,62,46),width=2)
    d.pieslice([425,484,655,700],180,360,fill=HAIR)
    d.ellipse([430,500,650,740],fill=SKIN); d.pieslice([425,484,655,700],180,360,fill=HAIR)
    for x in range(480,610,26): d.line([(540+(x-540)*0.3,495),(x,580)],fill=DARK,width=3)
    d.ellipse([495,480,585,500],fill=(225,180,60),outline=(190,140,40))   # gold band
    for side in (-1,1):
        for sx,ex,ey in [(436,418,830),(426,396,860)]: braid(d,sx,ex,ey,1 if side==1 else -1,r=9)
    features(d,False)
def w3(d):  # cornrows to the back + one long braid over shoulder
    face(d,False); d.pieslice([425,484,655,700],180,360,fill=HAIR)
    d.ellipse([430,500,650,740],fill=SKIN); d.pieslice([425,484,655,700],180,360,fill=HAIR)
    for x in range(480,610,26): d.line([(540+(x-540)*0.3,495),(x,580)],fill=(110,75,55),width=3)
    braid(d,622,690,1060,-1,y0=600,r=15); 
    features(d,False)
def w4(d):  # short bob braids (chin length)
    face(d,False); d.ellipse([420,492,660,730],fill=HAIR)
    d.ellipse([430,500,650,740],fill=SKIN); d.pieslice([420,480,660,700],180,360,fill=HAIR)
    d.polygon([(430,560),(540,500),(650,560),(630,600),(540,560),(450,600)],fill=HAIR)   # curtain bangs
    d.line([(540,500),(540,552)],fill=(110,75,55),width=3)
    for side in (-1,1):
        for sx,ex,ey in [(432,418,800),(424,402,820),(442,430,780)]: braid(d,sx,ex,ey,1 if side==1 else -1,r=10)
    features(d,False)
opts=[("1  Flat-top fade (now)",m1,True),("2  High fade + full beard",m2,True),("3  Low taper + goatee",m3,True),("4  High-top fade + stubble",m4,True),
      ("1  Long box braids (now)",w1,False),("2  Braided high bun",w2,False),("3  Cornrows + long braid",w3,False),("4  Short bob braids",w4,False)]
CW=420; sheet=Image.new("RGB",(CW*4,2*(CW+70)+130),(250,250,252)); sd=ImageDraw.Draw(sheet)
sd.text((20,18),"HAIR / BEARD OPTIONS - tell me the numbers",font=font(40),fill=(40,60,90))
for i,(name,fn,male) in enumerate(opts):
    im=Image.new("RGBA",(1080,1100),(232,218,196,255) if male else (205,235,250,255)); d=ImageDraw.Draw(im); fn(d)
    im=im.convert("RGB").crop((240,380,840,980)).resize((CW,CW),Image.LANCZOS)
    r,c=divmod(i,4); x,y=c*CW,100+r*(CW+70)
    sheet.paste(im,(x,y+40)); sd.text((x+14,y+6),("M" if male else "W")+name,font=font(20),fill=(30,50,80))
sheet.save("hair_options.png")
