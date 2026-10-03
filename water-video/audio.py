import numpy as np, wave
SR=44100; DUR=8.0; BPM=100; B=60/BPM
n=int(SR*DUR); mix=np.zeros(n); rng=np.random.default_rng(2)
def add(t0,sig,g=1.0):
    i=int(t0*SR)
    if i>=n: return
    s=sig[:n-i]; mix[i:i+len(s)]+=s*g
mt=lambda m:440*2**((m-69)/12)
def pluck(m,d=0.35):
    t=np.arange(int(SR*d))/SR; f=mt(m)
    return (np.sin(2*np.pi*f*t)+.4*np.sin(4*np.pi*f*t)+.2*np.sin(6*np.pi*f*t)+.3*np.sign(np.sin(2*np.pi*f*t)))*np.exp(-t*9)*0.22
def bass(m,d=0.5):
    t=np.arange(int(SR*d))/SR; return np.sin(2*np.pi*mt(m)*t)*np.exp(-t*4)*0.5
def clap():
    d=0.18; t=np.arange(int(SR*d))/SR; x=np.convolve(rng.standard_normal(len(t)),np.ones(4)/4,'same')
    return x*(np.exp(-t*30)+0.6*np.exp(-np.clip(t-0.012,0,None)*30)*(t>0.012))*0.25
def gulp(d=0.22):
    t=np.arange(int(SR*d))/SR; f=380-700*t; ph=2*np.pi*np.cumsum(f)/SR
    return (np.sin(ph)*np.exp(-t*14)+0.3*np.sin(ph*1.5)*np.exp(-t*25))*0.7
def bloop(f0=900,d=0.1):
    t=np.arange(int(SR*d))/SR; ph=2*np.pi*np.cumsum(f0+3000*t)/SR; return np.sin(ph)*np.exp(-t*35)*0.3
def slide(f0,f1,d):
    t=np.arange(int(SR*d))/SR; ph=2*np.pi*np.cumsum(np.linspace(f0,f1,len(t)))/SR; return np.sin(ph)*np.exp(-t*2.5)*0.22
def chime(m,d=0.9):
    t=np.arange(int(SR*d))/SR; f=mt(m); return (np.sin(2*np.pi*f*t)+.5*np.sin(2*np.pi*f*2.01*t))*np.exp(-t*4)*0.2
chords=[([67,71,74,79],43),([64,67,71,76],40),([60,64,67,72],36),([62,66,69,74],38)]
step=B/2
for s in range(int(DUR/step)):
    t0=s*step; ci=(s//4)%4; notes,root=chords[ci]
    add(t0,pluck(notes[[0,1,2,3,2,1,2,3][s%8]]))
    if s%4==0: add(t0,bass(root))
for b in range(int(DUR/B)):
    if b%2==1 and b*B>2.3: add(b*B,clap())
add(0.6,slide(500,300,1.0))                      # sad droop
for k,tt in enumerate([2.9,3.5,4.1,4.7]): add(tt,gulp()); add(tt+0.12,bloop())   # gulps
for k in range(8): add(2.9+k*0.3,bloop(700+k*40),0.7)
for i,m in enumerate([76,81,85,88,93]): add(5.3+i*0.12,chime(m))   # bloom
mix=np.tanh(mix*1.3); mix=mix/np.max(np.abs(mix))*0.8
f=int(SR*.4); mix[-f:]*=np.linspace(1,0,f)
with wave.open("audio.wav","wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix*32767).astype(np.int16).tobytes())
