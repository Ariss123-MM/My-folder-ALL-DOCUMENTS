import numpy as np, wave
SR=44100; DUR=8.0; n=int(SR*DUR); rng=np.random.default_rng(5)
mix=np.zeros(n); T=np.arange(n)/SR
mt=lambda m:440*2**((m-69)/12)
def add(t0,sig,g=1.0):
    i=int(t0*SR)
    if i>=n: return
    s=sig[:n-i]; mix[i:i+len(s)]+=s*g
def lowpass(x,fc):
    X=np.fft.rfft(x); f=np.fft.rfftfreq(len(x),1/SR); X*=1/(1+(f/fc)**4); return np.fft.irfft(X,len(x))
def bandpass(x,lo,hi):
    X=np.fft.rfft(x); f=np.fft.rfftfreq(len(x),1/SR); X*=((f>lo)&(f<hi)); return np.fft.irfft(X,len(x))
# airy pads: soft chords Cmaj7 - Am7 - Fmaj7 - G, ~3.4s each (70 BPM ≈ 6 beats)
chords=[[48,55,60,64,71],[45,52,57,60,67],[41,48,57,60,64],[43,50,59,62,67]]
seg=DUR/4
for ci,ch in enumerate(chords):
    t=np.arange(int(SR*(seg+1.2)))/SR
    env=np.minimum(t/1.0,1)*np.exp(-np.clip(t-seg,0,None)*3)
    pad=sum(np.sin(2*np.pi*mt(m)*(1+d)*t+k)*(0.6 if m<50 else 0.35) for k,m in enumerate(ch) for d in (-0.003,0.003))
    pad+=0.15*sum(np.sin(4*np.pi*mt(m)*t) for m in ch)
    add(ci*seg,pad*env*0.07)
# flowing swell (rising filtered sweep)
sw=lowpass(rng.standard_normal(n),1500)*(0.5+0.5*np.sin(2*np.pi*T/4-1.2))*0.08
mix+=sw
# waves: low-passed noise with slow swell envelope
wav=lowpass(rng.standard_normal(n),900)
lfo=(0.5+0.5*np.sin(2*np.pi*T/3.2-1.57))**2
mix+=wav*lfo*0.35
foam=bandpass(rng.standard_normal(n),3000,8000)*lfo*0.9*0.1
mix+=foam
# gentle bell melody, pentatonic
for tt,m in zip([0.5,1.4,2.1,3.0,3.9,4.7,5.6,6.3],[79,76,81,79,84,81,88,84]):
    t=np.arange(int(SR*1.4))/SR; f=mt(m)
    add(tt,(np.sin(2*np.pi*f*t)+.3*np.sin(2*np.pi*f*2.76*t))*np.exp(-t*3)*0.07)
# water sfx: soft gulps / bubbles / bloom chime
def gulp(d=0.22):
    t=np.arange(int(SR*d))/SR; ph=2*np.pi*np.cumsum(380-700*t)/SR; return np.sin(ph)*np.exp(-t*14)*0.35
def bloop(f0,d=0.1):
    t=np.arange(int(SR*d))/SR; ph=2*np.pi*np.cumsum(f0+3000*t)/SR; return np.sin(ph)*np.exp(-t*35)*0.15
for tt in (2.9,3.5,4.1,4.7): add(tt,gulp()); add(tt+.12,bloop(900))
for k in range(8): add(2.9+k*.3,bloop(700+40*k),.7)
for i,m in enumerate([76,81,85,88,93]):
    t=np.arange(int(SR*1.2))/SR; add(5.3+i*.12,(np.sin(2*np.pi*mt(m)*t)+.4*np.sin(2*np.pi*mt(m)*2.01*t))*np.exp(-t*3.5)*0.1)
mix=np.tanh(mix*1.6); mix=mix/np.max(np.abs(mix))*0.8
f=int(SR*.8); mix[-f:]*=np.linspace(1,0,f); mix[:int(SR*.1)]*=np.linspace(0,1,int(SR*.1))
with wave.open("audio_ocean.wav","wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix*32767).astype(np.int16).tobytes())
