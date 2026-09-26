import json, urllib.request, statistics as st, concurrent.futures as cf
TOK=open(__import__('os').environ.get('AFL_TOK_FILE','tok')).read().strip()
def get(u, auth=False):
    h={"User-Agent":"Mozilla/5.0"}
    if auth: h["x-media-mis-token"]=TOK
    return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=h),timeout=30))
ms=[]
for page in range(0,4):
    d=get(f"https://aflapi.afl.com.au/afl/v2/matches?competitionId=1&compSeasonId=85&pageSize=100&page={page}")
    ms+=d["matches"]
    if len(d["matches"])<100: break
ms=[m for m in ms if m["status"]=="CONCLUDED" and ({m["home"]["team"]["name"],m["away"]["team"]["name"]} & {"Fremantle","Brisbane Lions"})]
ms.sort(key=lambda m:m["utcStartTime"])
print("matches",len(ms))
WANT={("Hugh","McCluggage"):"mccluggage",("Lachie","Neale"):"neale",("Dayne","Zorko"):"zorko",("Will","Ashcroft"):"ashcroft",("Zac","Bailey"):"bailey",("Harris","Andrews"):"andrews",("Charlie","Cameron"):"cameron",("Eric","Hipwood"):"hipwood",("Andrew","Brayshaw"):"brayshaw",("Shai","Bolton"):"bolton",("Jordan","Clark"):"clark",("Patrick","Voss"):"voss"}
rows={v:[] for v in WANT.values()}
def fetch(m):
    return m, get(f"https://api.afl.com.au/cfs/afl/playerStats/match/{m['providerId']}",True)
with cf.ThreadPoolExecutor(8) as ex:
    res=list(ex.map(fetch,ms))
for m,d in res:
    for side in ("homeTeamPlayerStats","awayTeamPlayerStats"):
        for x in d.get(side) or []:
            pn=x["player"]["player"]["player"]["playerName"]; k=WANT.get((pn["givenName"],pn["surname"]))
            if not k: continue
            s=x["playerStats"]["stats"]
            rows[k].append({"t":m["utcStartTime"][:10],"rd":m["round"]["name"] if m.get("round") else "","opp":m["away"]["team"]["name"] if side=="homeTeamPlayerStats" else m["home"]["team"]["name"],"d":s["disposals"],"g":s["goals"],"tog":x["playerStats"].get("timeOnGroundPercentage")})
out={}
for k,r in rows.items():
    r.sort(key=lambda z:z["t"])
    D=[z["d"] for z in r]; G=[z["g"] for z in r]
    if not D: print(k,"NO DATA"); continue
    l5=r[-5:]
    vs=[z for z in r if z["opp"] in ("Fremantle","Brisbane Lions")]
    out[k]={"n":len(D),"dAvg":round(st.mean(D),2),"dSd":round(st.pstdev(D),2),"gAvg":round(st.mean(G),2),"gSd":round(st.pstdev(G),2),
      "d5":round(st.mean(z["d"] for z in l5),2),"g5":round(st.mean(z["g"] for z in l5),2),
      "last":[[z["rd"],z["opp"],int(z["d"]),int(z["g"])] for z in r[-6:]],
      "vs":[[z["rd"],int(z["d"]),int(z["g"])] for z in vs]}
    o=out[k]; print(f'{k:11} n={o["n"]:2} disp {o["dAvg"]:5} sd {o["dSd"]:4} L5 {o["d5"]:5} | goals {o["gAvg"]:4} sd {o["gSd"]:4} L5 {o["g5"]} | vs {o["vs"]} | last {[(a[1][:4],a[2],a[3]) for a in o["last"]]}')
json.dump(out,open("data/research.json","w"))
