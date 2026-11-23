import json,os,random,urllib.request
U=os.environ["MAKEFUN_ENV_URL"]
def req(path,body):
    r=urllib.request.Request(U+path,json.dumps(body).encode(),{"content-type":"application/json"})
    with urllib.request.urlopen(r) as f:
        return json.load(f)

PAWN,KNIGHT,BISHOP,ROOK,QUEEN,KING=1,2,3,4,5,6
VAL=[0,100,320,330,500,900,0]
PST=[None,
(0,0,0,0,0,0,0,0,5,10,10,15,15,10,10,5,5,5,10,15,15,10,5,5,0,0,5,20,20,5,0,0,5,5,10,25,25,10,5,5,10,10,20,30,30,20,10,10,50,50,50,50,50,50,50,50,0,0,0,0,0,0,0,0),
(-50,-40,-30,-30,-30,-30,-40,-50,-40,-20,0,5,5,0,-20,-40,-30,5,15,20,20,15,5,-30,-30,0,20,25,25,20,0,-30,-30,5,20,25,25,20,5,-30,-30,0,15,20,20,15,0,-30,-40,-20,0,5,5,0,-20,-40,-50,-40,-30,-30,-30,-30,-40,-50),
(-20,-10,-10,-10,-10,-10,-10,-20,-10,0,0,0,0,0,0,-10,-10,0,5,10,10,5,0,-10,-10,5,5,10,10,5,5,-10,-10,0,10,10,10,10,0,-10,-10,10,10,10,10,10,10,-10,-10,5,0,0,0,0,5,-10,-20,-10,-10,-10,-10,-10,-10,-20),
(0,0,0,5,5,0,0,0,5,10,10,10,10,10,10,5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,5,10,10,10,10,10,10,5,0,0,0,5,5,0,0,0),
(-20,-10,-10,-5,-5,-10,-10,-20,-10,0,0,0,0,0,0,-10,-10,0,5,5,5,5,0,-10,-5,0,5,5,5,5,0,-5,0,0,5,5,5,5,0,-5,-10,5,5,5,5,5,0,-10,-10,0,5,0,0,0,0,-10,-20,-10,-10,-5,-5,-10,-10,-20),
(-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-20,-30,-30,-40,-40,-30,-30,-20,-10,-20,-20,-20,-20,-20,-20,-10,20,20,0,0,0,0,20,20,20,30,10,0,0,10,30,20),
(-50,-30,-30,-30,-30,-30,-30,-50,-30,-30,0,0,0,0,-30,-30,-30,-30,0,10,10,0,-30,-30,-30,-30,0,20,20,0,-30,-30,-30,-30,0,20,20,0,-30,-30,-30,-30,0,0,0,0,-30,-30,-30,-40,-30,-30,-30,-30,-40,-30,-50,-40,-30,-30,-30,-30,-40,-50)]
R=random.Random(20261123)
Z=[[R.getrandbits(64) for _ in range(128)] for _ in range(16)]
ZS=R.getrandbits(64)
ZC=[R.getrandbits(64) for _ in range(16)]
ZE=[R.getrandbits(64) for _ in range(128)]
B=[0]*128
SIDE=0
EP=-1
CAS=0
HALF=0
KS=[0,0]
HH=0
ST=[]
TT={}
NODES=0
LIMIT=100000
KILL=[[0,0] for _ in range(64)]
HIST={}

def attacked(sq,by):
    p=PAWN+8*by
    for d in ((-15,-17) if by==0 else (15,17)):
        x=sq+d
        if not(x&0x88) and B[x]==p: return True
    p=KNIGHT+8*by
    for d in (-33,-31,-18,-14,14,18,31,33):
        x=sq+d
        if not(x&0x88) and B[x]==p: return True
    p=KING+8*by
    for d in (-17,-16,-15,-1,1,15,16,17):
        x=sq+d
        if not(x&0x88) and B[x]==p: return True
    p=BISHOP+8*by; q=QUEEN+8*by
    for d in (-17,-15,15,17):
        x=sq+d
        while not(x&0x88):
            z=B[x]
            if z:
                if z==p or z==q: return True
                break
            x+=d
    p=ROOK+8*by; q=QUEEN+8*by
    for d in (-16,-1,1,16):
        x=sq+d
        while not(x&0x88):
            z=B[x]
            if z:
                if z==p or z==q: return True
                break
            x+=d
    return False

def setfen(f):
    global B,SIDE,EP,CAS,HALF,KS,HH,TT,ST
    B=[0]*128
    ST=[]
    a=f.split()
    row=0; file=0
    for c in a[0]:
        if c=='/': row+=1; file=0
        elif c.isdigit(): file+=int(c)
        else:
            p="pnbrqk".find(c.lower())+1
            if c.isupper(): p+=0
            else: p+=8
            B[(7-row)*16+file]=p
            if p&7==KING: KS[p>>3]=(7-row)*16+file
            file+=1
    SIDE=0 if a[1]=='w' else 1
    CAS=0
    if 'K' in a[2]: CAS|=1
    if 'Q' in a[2]: CAS|=2
    if 'k' in a[2]: CAS|=4
    if 'q' in a[2]: CAS|=8
    EP=-1
    if a[3]!='-':
        EP=(int(a[3][1])-1)*16+"abcdefgh".find(a[3][0])
    HALF=int(a[4]) if len(a)>4 else 0
    HH=0
    for x,p in enumerate(B):
        if p: HH^=Z[p][x]
    if SIDE: HH^=ZS
    HH^=ZC[CAS]
    if EP>=0: HH^=ZE[EP]
    TT={}

def gen(caps=False):
    ms=[]
    s=SIDE
    side=s
    for f in range(128):
        p=B[f]
        if not p or (p>>3)!=side: continue
        t=p&7
        if t==PAWN:
            d=16 if side==0 else -16
            last=7 if side==0 else 0
            to=f+d
            if not(to&0x88):
                if not B[to]:
                    if (to>>4)==last:
                        for q in (5,4,3,2): ms.append(f|(to<<7)|(q<<14))
                    else:
                        if not caps:
                            ms.append(f|(to<<7))
                            if (f>>4)==(1 if side==0 else 6) and not B[to+d]:
                                ms.append(f|((to+d)<<7)|(1<<17))
                for dd in (d-1,d+1):
                    to=f+dd
                    if not(to&0x88):
                        if B[to] and (B[to]>>3)!=side:
                            if (to>>4)==last:
                                for q in (5,4,3,2): ms.append(f|(to<<7)|(q<<14))
                            else:
                                ms.append(f|(to<<7))
                        elif to==EP:
                            ms.append(f|(to<<7)|(2<<17))
        elif t==KNIGHT or t==KING:
            ds=(-33,-31,-18,-14,14,18,31,33) if t==KNIGHT else (-17,-16,-15,-1,1,15,16,17)
            for d in ds:
                to=f+d
                if not(to&0x88):
                    q=B[to]
                    if not q or (q>>3)!=side:
                        if not caps or q: ms.append(f|(to<<7))
        else:
            ds=(-17,-15,15,17) if t==BISHOP else ((-16,-1,1,16) if t==ROOK else (-17,-16,-15,-1,1,15,16,17))
            for d in ds:
                to=f+d
                while not(to&0x88):
                    q=B[to]
                    if not q:
                        if not caps: ms.append(f|(to<<7))
                    else:
                        if (q>>3)!=side: ms.append(f|(to<<7))
                        break
                    to+=d
    if not caps and side==0:
        if CAS&1 and not B[5] and not B[6] and not attacked(4,1) and not attacked(5,1) and not attacked(6,1):
            ms.append(4|(6<<7)|(3<<17))
        if CAS&2 and not B[1] and not B[2] and not B[3] and not attacked(4,1) and not attacked(3,1) and not attacked(2,1):
            ms.append(4|(2<<7)|(3<<17))
    if not caps and side==1:
        if CAS&4 and not B[117] and not B[118] and not attacked(116,0) and not attacked(117,0) and not attacked(118,0):
            ms.append(116|(118<<7)|(3<<17))
        if CAS&8 and not B[113] and not B[114] and not B[115] and not attacked(116,0) and not attacked(115,0) and not attacked(114,0):
            ms.append(116|(114<<7)|(3<<17))
    return ms

def do(m):
    global SIDE,EP,CAS,HALF,KS,HH
    f=m&127; t=(m>>7)&127; pr=(m>>14)&7; fl=(m>>17)&3
    p=B[f]; cap=B[t]; cs=-1
    if fl==2:
        cs=t-(16 if SIDE==0 else -16)
        cap=B[cs]
    ST.append((m,p,cap,cs,CAS,EP,HALF,KS[0],KS[1],HH))
    B[f]=0
    if fl==3:
        B[t]=p
        if t>f: rf=f+3; rt=f+1
        else: rf=f-4; rt=f-1
        rook=B[rf]
        B[rt]=rook; B[rf]=0
        HH^=Z[p][f]^Z[p][t]^Z[rook][rf]^Z[rook][rt]
    elif fl==2:
        B[t]=p; B[cs]=0
        HH^=Z[p][f]^Z[p][t]^Z[cap][cs]
    else:
        np=pr+8*SIDE if pr else p
        B[t]=np
        HH^=Z[p][f]^Z[np][t]
        if cap: HH^=Z[cap][t]
    if (p&7)==KING:
        KS[SIDE]=t
        CAS&=~(3 if SIDE==0 else 12)
    if (p&7)==ROOK:
        if f==0: CAS&=~2
        elif f==7: CAS&=~1
        elif f==112: CAS&=~8
        elif f==119: CAS&=~4
    if cap and (cap&7)==ROOK:
        if t==0: CAS&=~2
        elif t==7: CAS&=~1
        elif t==112: CAS&=~8
        elif t==119: CAS&=~4
    HH^=ZC[ST[-1][4]]^ZC[CAS]^ZS
    if EP>=0: HH^=ZE[EP]
    EP=(f+t)//2 if fl==1 else -1
    if EP>=0: HH^=ZE[EP]
    HALF=0 if (p&7)==PAWN or cap else HALF+1
    SIDE^=1

def undo():
    global SIDE,EP,CAS,HALF,KS,HH
    m,p,cap,cs,c0,e0,h0,k0,k1,hh=ST.pop()
    f=m&127; t=(m>>7)&127; pr=(m>>14)&7; fl=(m>>17)&3
    SIDE^=1
    B[f]=p
    B[t]=0
    if fl==3:
        if t>f: rf=f+3; rt=f+1
        else: rf=f-4; rt=f-1
        B[rf]=B[rt]; B[rt]=0
    elif fl==2:
        B[cs]=cap
    else:
        B[t]=cap
    CAS=c0; EP=e0; HALF=h0; KS[0]=k0; KS[1]=k1; HH=hh

def ev():
    s=0
    npm=0
    pb=[0,0]
    for f in range(128):
        p=B[f]
        if not p: continue
        c=p>>3; t=p&7
        idx=(f>>4)*8+(f&7) if c==0 else (7-(f>>4))*8+(f&7)
        v=VAL[t]+PST[t][idx]
        if c==0: s+=v
        else: s-=v
        if t in (KNIGHT,BISHOP,ROOK,QUEEN): npm+=VAL[t]
        if t==BISHOP: pb[c]+=1
    if pb[0]>=2: s+=25
    if pb[1]>=2: s-=25
    # pawn structure
    for f in range(128):
        p=B[f]
        if p and (p&7)==PAWN:
            c=p>>3; r=f>>4; file=f&7; d=1 if c==0 else -1
            passed=True
            for ff in (file-1,file,file+1):
                if 0<=ff<8:
                    for rr in range(r+d,8 if c==0 else -1,d):
                        q=B[rr*16+ff]
                        if q==PAWN+8*(1-c): passed=False; break
                    if not passed: break
            if passed:
                s+= (8,15,25,40,60,90,0,0)[r] if c==0 else -(8,15,25,40,60,90,0,0)[7-r]
    return s if SIDE==0 else -s

def order(ms,ttm=0,ply=0):
    def key(m):
        if m==ttm: return 10000000
        f=m&127; t=(m>>7)&127; pr=(m>>14)&7; fl=(m>>17)&3
        cap=B[t]
        if fl==2: cap=PAWN+8*(1-SIDE)
        if cap:
            return 1000000+10*VAL[cap&7]-VAL[B[f]&7]+(800000 if pr else 0)
        if pr: return 900000+VAL[pr]
        if m==KILL[ply][0]: return 800000
        if m==KILL[ply][1]: return 790000
        return HIST.get(m,0)
    ms.sort(key=key,reverse=True)

MATE=100000
INF=1000000

def qsearch(a,b,ply,qd):
    global NODES
    NODES+=1
    if NODES>LIMIT: raise RuntimeError
    chk=attacked(KS[SIDE],SIDE^1)
    if chk:
        if qd<=0: return ev()
        ms=gen()
        if not ms: return -MATE+ply
        order(ms,0,ply)
        best=-INF
        for m in ms:
            do(m)
            sc=-qsearch(-b,-a,ply+1,qd-1)
            undo()
            if sc>best: best=sc
            if sc>a: a=sc
            if a>=b: break
        return best
    stand=ev()
    if stand>=b: return b
    if stand>a: a=stand
    ms=gen(True)
    order(ms,0,ply)
    for m in ms:
        do(m)
        sc=-qsearch(-b,-a,ply+1,qd-1)
        undo()
        if sc>a:
            a=sc
            if a>=b: break
    return a

def ab(depth,a,b,ply):
    global NODES
    NODES+=1
    if NODES>LIMIT: raise RuntimeError
    if HALF>=100: return 0
    chk=attacked(KS[SIDE],SIDE^1)
    if depth<=0: return qsearch(a,b,ply,4)
    ttm=0
    e=TT.get(HH)
    if e:
        d,sc,fl,ttm=e
        if d>=depth:
            if fl==0: return sc
            if fl==1 and sc>=b: return sc
            if fl==2 and sc<=a: return sc
    ms=gen()
    if not ms: return -MATE+ply if chk else 0
    order(ms,ttm,ply)
    best=-INF; bm=0; olda=a
    for m in ms:
        do(m)
        sc=-ab(depth-1,-b,-a,ply+1)
        undo()
        if sc>best: best=sc; bm=m
        if sc>a:
            a=sc
            if a>=b:
                if (m>>17)&3==0:
                    KILL[ply][1]=KILL[ply][0]; KILL[ply][0]=m
                    HIST[m]=HIST.get(m,0)+depth*depth
                break
    fl=0
    if best<=olda: fl=2
    elif best>=b: fl=1
    TT[HH]=(depth,best,fl,bm)
    return best

def uci_move(u):
    f=("abcdefgh".find(u[0]))+(int(u[1])-1)*16
    t=("abcdefgh".find(u[2]))+(int(u[3])-1)*16
    pr=0
    if len(u)>4: pr=" pnbrqk".find(u[4])
    fl=0
    p=B[f]
    if (p&7)==KING and abs((t&7)-(f&7))==2: fl=3
    elif (p&7)==PAWN:
        if t==EP and (f&7)!=(t&7): fl=2
        elif abs(t-f)==32: fl=1
    return f|(t<<7)|(pr<<14)|(fl<<17)

def think(fen,legal):
    global NODES,TT,KILL,HIST
    setfen(fen)
    moves=[uci_move(u) for u in legal]
    if not moves: return legal[0]
    NODES=0; KILL=[[0,0] for _ in range(64)]; HIST={}
    best=moves[0]
    for depth in range(1,7):
        base=len(ST)
        try:
            a=-INF; bm=best; first=True
            for m in moves:
                do(m)
                sc=-ab(depth-1,-INF,-a,1)
                undo()
                if sc>a or first:
                    a=sc; bm=m; first=False
            best=bm
        except RuntimeError:
            while len(ST)>base: undo()
            break
    return next(u for u in legal if uci_move(u)==best)

def main():
    while True:
        g=req("/game",{})
        if g["status"]=="done": break
        while g["status"]=="your_move":
            m=think(g["fen"],g["legal_moves"])
            g=req("/move",{"game":g["game"],"move":m})
        print("game",g["game"],g.get("outcome"),g.get("reason"),file=__import__("sys").stderr)

if __name__=="__main__": main()
