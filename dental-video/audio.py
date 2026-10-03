import numpy as np, wave
SR=44100; DUR=8.0; BPM=105; B=60/BPM
n=int(SR*DUR); mix=np.zeros(n); rng=np.random.default_rng(1)
def add(t0,sig,g=1.0):
    i=int(t0*SR)
    if i>=n: return
    s=sig[:n-i]; mix[i:i+len(s)]+=s*g
def mtof(m): return 440*2**((m-69)/12)
def pluck(m,d=0.35):
    t=np.arange(int(SR*d))/SR; f=mtof(m)
    s=sum(np.sin(2*np.pi*f*k*t)*a for k,a in ((1,1),(2,.4),(3,.2)))+0.3*np.sign(np.sin(2*np.pi*f*t))
    return s*np.exp(-t*9)*0.25
def bass(m,d=0.5):
    t=np.arange(int(SR*d))/SR; return np.sin(2*np.pi*mtof(m)*t)*np.exp(-t*4)*0.5
def clap():
    d=0.18; t=np.arange(int(SR*d))/SR; x=rng.standard_normal(len(t))
    x=np.convolve(x,np.ones(4)/4,'same')  # soften
    env=np.exp(-t*30)+0.6*np.exp(-np.clip(t-0.012,0,None)*30)*(t>0.012)
    return x*env*0.25
def noise_sweep(d,f0,f1,g=0.15):
    t=np.arange(int(SR*d))/SR; x=rng.standard_normal(len(t))
    k=np.ones(int(SR/ (f0+ (f1-f0)*0.5) )+1); y=x-np.convolve(x,np.ones(8)/8,'same')  # highpass-ish
    return y*np.sin(np.pi*t/d)*g
def chime(m,d=0.8):
    t=np.arange(int(SR*d))/SR; f=mtof(m)
    return (np.sin(2*np.pi*f*t)+.5*np.sin(2*np.pi*f*2.01*t))*np.exp(-t*4)*0.18
chords=[([60,64,67,72],36),([55,59,62,67],31),([57,60,64,69],33),([53,57,60,65],29)]
step=B/2
for s in range(int(DUR/step)):
    t0=s*step; ci=(s//4)%4; notes,root=chords[ci]
    pat=[0,1,2,3,2,1,2,3][s%8]
    add(t0,pluck(notes[pat]+(12 if s%8 in(6,7) else 0)),1)
    if s%4==0: add(t0,bass(root),1)
    if s%4==2: add(t0,bass(root+(7 if ci!=1 else 5),0.3),0.6)
    if s%4==0 and s%8==4: pass
for b in range(int(DUR/B)):
    if b%2==1: add(b*B,clap())
    # soft hat on offbeats
    h=np.diff(rng.standard_normal(int(SR*.05)),prepend=0)*np.exp(-np.arange(int(SR*.05))/SR*80)*0.12
    add(b*B+B/2,h)
# sfx synced to video
for k in range(8): add(2.6+k*0.28,noise_sweep(0.25,3000,6000,0.12))   # brush swishes 2.6-4.9
for g in range(5): add(5.1+g*0.3,noise_sweep(0.12,5000,8000,0.2))     # floss zips
for i,m in enumerate([84,88,91,96]): add(6.9+i*0.12,chime(m))          # sparkle finale
add(6.9,chime(72,1.1),1.2)
mix=np.tanh(mix*1.3); mix=mix/np.max(np.abs(mix))*0.8
fade=int(SR*.4); mix[-fade:]*=np.linspace(1,0,fade)
with wave.open("audio.wav","wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix*32767).astype(np.int16).tobytes())
