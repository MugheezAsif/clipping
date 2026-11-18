import json,sys
d=json.load(open(sys.argv[1],encoding='utf-8'))
out=[];words=[]
for e in d.get('events',[]):
    if 'segs' not in e: continue
    t0=e['tStartMs']
    for s in e['segs']:
        w=s.get('utf8','').strip()
        if not w: continue
        words.append((t0+s.get('tOffsetMs',0),w))
json.dump(words,open(sys.argv[2],'w',encoding='utf-8'))
# print lines grouped ~8s
cur=None;buf=[]
for t,w in words:
    b=t//8000
    if b!=cur:
        if buf: print(f"[{cur*8//60:02d}:{cur*8%60:02d}] "+" ".join(buf))
        cur=b;buf=[]
    buf.append(w)
if buf: print(f"[{cur*8//60:02d}:{cur*8%60:02d}] "+" ".join(buf))
