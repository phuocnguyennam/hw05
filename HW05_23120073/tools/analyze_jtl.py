"""Task 2 helper: compute metrics straight from raw .jtl files (no AI involved).
Splits a .jtl into runs (a new run begins at each SETUP_preflight_login sample), then prints
per-run, per-label and (for Stress/Spike) per-time-window statistics.
"""
import csv, sys, glob, os, statistics, json
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results")


def pct(v, p):
    v = sorted(v)
    # JMeter Aggregate Report method: element at index ceil(p*n)-1
    k = max(0, int(-(-len(v) * p // 1)) - 1)
    return v[k]


DEFAULT_FIELDS = [
    "timeStamp", "elapsed", "label", "responseCode", "responseMessage",
    "threadName", "dataType", "success", "failureMessage", "bytes",
    "sentBytes", "grpThreads", "allThreads", "URL", "Latency", "IdleTime", "Connect"
]


def load(path):
    if os.path.getsize(path) == 0:
        return []
    with open(path, newline="", encoding="utf-8") as f:
        first = f.readline()
        f.seek(0)
        if first.startswith("timeStamp,"):
            return list(csv.DictReader(f))
        return list(csv.DictReader(f, fieldnames=DEFAULT_FIELDS))


def split_runs(rows):
    runs, cur = [], []
    for r in rows:
        if r["label"] == "SETUP_preflight_login" and cur:
            runs.append(cur)
            cur = []
        cur.append(r)
    if cur:
        runs.append(cur)
    return runs


def summarize(rows):
    main = [r for r in rows if not r["label"].startswith(("SETUP", "TEARDOWN"))]
    if not main:
        return None
    ts = [int(r["timeStamp"]) for r in main]
    el = [int(r["elapsed"]) for r in main]
    start, end = min(ts), max(int(r["timeStamp"]) + int(r["elapsed"]) for r in main)
    dur = (end - start) / 1000
    err = sum(r["success"] != "true" for r in main)
    return dict(n=len(main), dur_s=round(dur, 1), rps=round(len(main) / dur, 2), avg=round(statistics.mean(el), 1),
                p50=pct(el, .5), p90=pct(el, .9), p95=pct(el, .95), p99=pct(el, .99), max=max(el),
                err=err, err_pct=round(100 * err / len(main), 2), maxvu=max(int(r["allThreads"]) for r in main),
                start=start)


def by_label(rows):
    g = defaultdict(list)
    for r in rows:
        if not r["label"].startswith(("SETUP", "TEARDOWN")):
            g[r["label"]].append(r)
    out = {}
    for k, v in sorted(g.items()):
        el = [int(r["elapsed"]) for r in v]
        out[k] = dict(n=len(v), avg=round(statistics.mean(el), 1), p50=pct(el, .5), p95=pct(el, .95), p99=pct(el, .99),
                      max=max(el), err=sum(r["success"] != "true" for r in v),
                      kb=round(statistics.mean(int(r["bytes"]) for r in v) / 1024, 1))
    return out


def windows(rows, width_s):
    main = [r for r in rows if not r["label"].startswith(("SETUP", "TEARDOWN"))]
    t0 = min(int(r["timeStamp"]) for r in main)
    g = defaultdict(list)
    for r in main:
        g[(int(r["timeStamp"]) - t0) // (width_s * 1000)].append(r)
    out = []
    for k in sorted(g):
        v = g[k]
        el = [int(r["elapsed"]) for r in v]
        codes = defaultdict(int)
        for r in v:
            if r["success"] != "true":
                codes[r["responseCode"][:40]] += 1
        out.append(dict(t=f"{k*width_s}-{(k+1)*width_s}s", n=len(v), rps=round(len(v) / width_s, 1), avg=round(statistics.mean(el), 1),
                        p95=pct(el, .95), p99=pct(el, .99), max=max(el), vu=max(int(r["allThreads"]) for r in v),
                        err_pct=round(100 * sum(r["success"] != "true" for r in v) / len(v), 2), codes=dict(codes)))
    return out


if __name__ == "__main__":
    width = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    for path in sorted(glob.glob(os.path.join(RES, "*.jtl"))):
        rows = load(path)
        print("=" * 100)
        print(os.path.basename(path), "rows:", len(rows))
        for i, run in enumerate(split_runs(rows), 1):
            s = summarize(run)
            print(f"-- run #{i}: rows={len(run)}", json.dumps(s) if s else "(no main samples: aborted at preflight)")
            if s and "-v" in sys.argv:
                for k, v in by_label(run).items():
                    print("   ", k, v)
                for w in windows(run, width):
                    print("   ", w)
