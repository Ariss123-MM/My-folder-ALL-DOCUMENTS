import os, subprocess
from PIL import Image, ImageDraw
from multiprocessing import Pool
import fig
from fig import F1,F2,W,H,FPS,N,ease,center
def build(i):
    t=i/FPS
    man=fig.frame(i,True).crop((240,420,840,1520)).resize((540,990),Image.LANCZOS)
    wom=fig.frame(i,False).crop((240,420,840,1520)).resize((540,990),Image.LANCZOS)
    im=Image.new("RGB",(W,H),(245,245,245)); d=ImageDraw.Draw(im)
    im.paste(man,(0,430)); im.paste(wom,(540,430))
    d.rectangle([537,430,543,1420],fill=(255,255,255))
    d.rectangle([0,0,W,430],fill=(250,250,252)); d.rectangle([0,1420,W,H],fill=(250,250,252))
    if t<2.4: center(d,"Same body.\nDifferent water habit.",130,F1,(50,60,80))
    elif t<5.2: center(d,"One sips...\nthe other doesn't",130,F1,(20,90,170))
    else: center(d,"Which one feels\nlike you today?",130,F1,(20,110,150))
    d.rectangle([0,1425,540,1520],fill=(200,70,60)); d.rectangle([540,1425,W,1520],fill=(40,150,110))
    for txt,x0 in (("NOT ENOUGH\nWATER",0),("ENOUGH\nWATER",540)):
        for j,line in enumerate(txt.split("\n")):
            w=d.textlength(line,font=F2); d.text((x0+(540-w)/2,1432+j*44),line,font=F2,fill=(255,255,255))
    center(d,"Stay hydrated for energy,\nfocus & digestion",1600,F2,(40,70,100))
    im.save(f"cframes/f{i:04d}.png")
if __name__=="__main__":
    os.makedirs("cframes",exist_ok=True)
    with Pool(4) as p: p.map(build,range(N))
    subprocess.run(["ffmpeg","-y","-loglevel","error","-framerate",str(FPS),"-i","cframes/f%04d.png","-i","audio_ocean.wav","-c:v","libx264","-preset","veryfast","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-shortest","water_compare_v2_ocean.mp4"],check=True)
