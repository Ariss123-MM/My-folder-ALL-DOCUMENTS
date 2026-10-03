import os, subprocess
from multiprocessing import Pool
from PIL import Image
import fig
def save(i): fig.frame(i,False).save(f"wframes/f{i:04d}.png")
if __name__=="__main__":
    os.makedirs("wframes",exist_ok=True)
    with Pool(4) as p: p.map(save,range(fig.N))
    subprocess.run(["ffmpeg","-y","-loglevel","error","-framerate","24","-i","wframes/f%04d.png","-i","audio_ocean.wav","-c:v","libx264","-preset","veryfast","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-shortest","water_hydration_v2_ocean.mp4"],check=True)
