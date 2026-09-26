"""Poll the official AFL stats API for the Grand Final and write data/live.json.

Prints one line to stdout whenever the snapshot changes (at most every MIN_GAP
seconds) so a watcher can relay it to the tracker page's database.
"""
import json, os, sys, time, urllib.request

MATCH = os.environ.get("MATCH_ID", "CD_M20260142901")
OUT = os.environ.get("OUT", "data/live.json")
MIN_GAP = int(os.environ.get("MIN_GAP", "60"))
IDS = {("Hugh", "McCluggage"): "mccluggage", ("Lachie", "Neale"): "neale", ("Dayne", "Zorko"): "zorko",
       ("Will", "Ashcroft"): "ashcroft", ("Zac", "Bailey"): "bailey", ("Harris", "Andrews"): "andrews",
       ("Charlie", "Cameron"): "cameron", ("Eric", "Hipwood"): "hipwood", ("Andrew", "Brayshaw"): "brayshaw",
       ("Shai", "Bolton"): "bolton", ("Jordan", "Clark"): "clark", ("Patrick", "Voss"): "voss"}
tok, tok_at = None, 0


def req(url, auth=True, method="GET"):
    h = {"User-Agent": "Mozilla/5.0"}
    if auth:
        h["x-media-mis-token"] = tok
    r = urllib.request.Request(url, headers=h, method=method, data=b"" if method == "POST" else None)
    return json.load(urllib.request.urlopen(r, timeout=20))


def token():
    global tok, tok_at
    if not tok or time.time() - tok_at > 1200:
        tok = req("https://api.afl.com.au/cfs/afl/WMCTok", auth=False, method="POST")["token"]
        tok_at = time.time()


def snap():
    token()
    mi = req(f"https://api.afl.com.au/cfs/afl/matchItem/{MATCH}")
    ps = req(f"https://api.afl.com.au/cfs/afl/playerStats/match/{MATCH}")
    sc = mi.get("score") or {}
    status = sc.get("status") or mi["match"].get("status")
    periods = ((sc.get("matchClock") or {}).get("periods")) or []
    cur = {"periodNumber": 1, "periodSeconds": 0, "periodCompleted": False}
    for p in periods:
        if p.get("periodSeconds") or p.get("periodCompleted"):
            cur = p
    # Fremantle are the home side
    def ts(side):
        m = ((sc.get(side) or {}).get("matchScore")) or {}
        return {"g": int(m.get("goals") or 0), "b": int(m.get("behinds") or 0)}
    players = {}
    for side in ("homeTeamPlayerStats", "awayTeamPlayerStats"):
        for x in ps.get(side) or []:
            n = x["player"]["player"]["player"]["playerName"]
            k = IDS.get((n["givenName"], n["surname"]))
            if k:
                s = x["playerStats"]["stats"]
                players[k] = {"d": int(s.get("disposals") or 0), "g": int(s.get("goals") or 0),
                              "tog": x["playerStats"].get("timeOnGroundPercentage")}
    return {"status": status, "period": int(cur.get("periodNumber") or 1),
            "periodSeconds": int(cur.get("periodSeconds") or 0), "periodCompleted": bool(cur.get("periodCompleted")),
            "fre": ts("homeTeamScore"), "bri": ts("awayTeamScore"), "players": players}


last_key, last_emit = None, 0
while True:
    try:
        s = snap()
        key = json.dumps({k: v for k, v in s.items() if k != "periodSeconds"}, sort_keys=True)
        now = time.time()
        if key != last_key and now - last_emit >= MIN_GAP:
            s["updatedAt"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            json.dump(s, open(OUT, "w"))
            if os.environ.get("GIT_PUSH"):
                os.makedirs("live", exist_ok=True)
                json.dump(s, open("live/gf.json", "w"))
                os.system("git add live/gf.json >/dev/null && git commit -qm 'Live update: %s Q%s' -m 'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>' -m 'Claude-Session: https://claude.ai/code/session_01HBaQKpGcWcRebHmAcNETxX' >/dev/null 2>&1; git push -q origin HEAD >/dev/null 2>&1 || (sleep 3; git push -q origin HEAD >/dev/null 2>&1)" % (s["status"], s["period"]))
            last_key, last_emit = key, now
            print(f"UPDATE {s['status']} Q{s['period']} {s['periodSeconds']//60}m "
                  f"BRI {s['bri']['g']}.{s['bri']['b']} FRE {s['fre']['g']}.{s['fre']['b']}", flush=True)
            if s["status"] == "CONCLUDED":
                print("FINAL", flush=True)
                break
    except Exception as e:  # keep polling through transient failures
        tok = None if "401" in str(e) or "403" in str(e) else tok
        print(f"ERROR {e}", file=sys.stderr, flush=True)
    time.sleep(20)
