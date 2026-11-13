#!/usr/bin/env python3
"""Compare skill snapshots end to end.

  report.py [--set dev] [--k 3] [--det] SNAP_A [SNAP_B ...]

The snapshot name "draft" stands for the set's own drafts, untouched (for scrh, the human
captions). On a video-script set (scr*) every text is also measured against the script band
file of its language, and the table adds the mean number of features per text that come out
overshot and on the AI side.

For each snapshot: every work/SNAP/r*/NAME/final.md is judged by K fresh Opus judges
(cached), measured with aimeter/audit, and (with --det) scored by the local detectors.
Per title, the judge P(AI) is averaged over reps and judges. The first snapshot is the
baseline; every other is compared per title (paired) with a Wilcoxon signed-rank test.
"""
import argparse, glob, json, math, os, subprocess, sys, statistics as st
from collections import Counter

CODE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CODE)
import harness  # noqa
H = harness.H
REPO = harness.REPO
sys.path.insert(0, os.path.join(REPO, "scripts"))
import aimeter  # noqa
import audit  # noqa


def wilcoxon(diffs):
    d = [x for x in diffs if x != 0]
    n = len(d)
    if n == 0:
        return 1.0
    ranks = sorted(range(n), key=lambda i: abs(d[i]))
    r = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j + 1 < n and abs(d[ranks[j + 1]]) == abs(d[ranks[i]]):
            j += 1
        for k in range(i, j + 1):
            r[ranks[k]] = (i + j) / 2 + 1
        i = j + 1
    wp = sum(r[i] for i in range(n) if d[i] > 0)
    mu = n * (n + 1) / 4
    sd = math.sqrt(n * (n + 1) * (2 * n + 1) / 24)
    z = (wp - mu) / sd if sd else 0
    return math.erfc(abs(z) / math.sqrt(2))


def finals(snap, names, reps="r*", rows=()):
    if snap == "draft":
        return {r[0]: [r[1]] for r in rows if r[0] in names}
    out = {}
    for n in names:
        fs = sorted(glob.glob(os.path.join(H, "work", snap, reps, n, "final.md")))
        if fs:
            out[n] = fs
    return out


def meter(f):
    text = open(f).read()
    m = aimeter.measure(text)
    if not m:
        return None
    sc = aimeter.score(m) if hasattr(aimeter, "score") else None
    return m, sc


def script_bands(set_name):
    return os.path.join(REPO, "scripts", "bands-script-es.json" if set_name.endswith("-es") else "bands-script.json")


def band_counts(files, bands):
    """Per file, how many of the meter's features are overshot and how many on the AI side,
    measured on the spoken words (the script band files say "_spoken")."""
    env = dict(os.environ, QUIRON_BANDS=bands, PYTHONUTF8="1")
    out = {}
    for f in files:
        r = subprocess.run([sys.executable, os.path.join(REPO, "scripts", "aimeter.py"), "--json", f],
                           capture_output=True, text=True, encoding="utf-8", env=env)
        try:
            v = json.loads(r.stdout)["verdicts"].values()
        except ValueError:  # too short to measure
            continue
        out[f] = (sum(x.endswith("overshot") for x in v), sum(x.endswith("AI side") for x in v))
    return out


def det_scores(files):
    py = os.environ.get("QUIRON_DETECTOR_PY", os.path.expanduser("~/.cache/quiron-detector/venv/bin/python"))
    r = subprocess.run([py, os.path.join(CODE, "detector.py"), *files], capture_output=True, text=True)
    out = {}
    for l in r.stdout.splitlines():
        f, b, d = l.split("\t")
        out[f] = (float(b), float(d))
    return out


def noise(snaps, per, allrec):
    """How far the same version moves by itself: rep against rep, judge against judge.
    A difference between versions smaller than these is not a result."""
    print()
    for s in snaps:
        byrep, jd = {}, []
        for n, v in per[s].items():
            for f in v["files"]:
                ps = [r["p_ai"] for r in allrec[s][f] if r["p_ai"] is not None and not str(r["k"]).startswith("g")]
                if ps:
                    byrep.setdefault(os.path.basename(os.path.dirname(os.path.dirname(f))), {})[n] = st.mean(ps)
                if len(ps) >= 2:
                    jd.append(ps[0] - ps[1])
        reps = sorted(byrep)
        line = f"{s:14} noise: judge-judge sd {st.pstdev(jd):4.1f}" if len(jd) > 1 else f"{s:14} noise:"
        for x, y in zip(reps, reps[1:]):
            d = [byrep[x][n] - byrep[y][n] for n in byrep[x] if n in byrep[y]]
            if len(d) > 1:
                line += f"   {x}-{y}: set mean {st.mean(d):+5.1f}, per-title sd {st.pstdev(d):4.1f}"
        print(line)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("snaps", nargs="+")
    ap.add_argument("--set", default="dev")
    ap.add_argument("--k", type=int, default=2)
    ap.add_argument("--g", type=int, default=0)
    ap.add_argument("--det", action="store_true")
    ap.add_argument("--reps", default="r[0-9]")
    ap.add_argument("--reasons", action="store_true")
    ap.add_argument("--noise", action="store_true")
    a = ap.parse_args()
    rows_ = harness.sets()[a.set]
    names = [r[0] for r in rows_]
    scr = a.set.startswith("scr")
    per = {}
    allrec = {}
    for s in a.snaps:
        fm = finals(s, names, a.reps, rows_)
        files = [f for fs in fm.values() for f in fs]
        res = harness.judge_files(files, a.k, 10, a.g, harness.JPROMPT_FIC if a.set.startswith("fic") else
                                   harness.script_prompt(a.set) if a.set.startswith("scr") else None)
        dets = det_scores(files) if a.det else {}
        bc = band_counts(files, script_bands(a.set)) if scr else {}
        per[s] = {}
        allrec[s] = res
        for n, fs in fm.items():
            ps = [r["p_ai"] for f in fs for r in res[f] if r["p_ai"] is not None and not str(r["k"]).startswith("g")]
            pg = [r["p_ai"] for f in fs for r in res[f] if r["p_ai"] is not None and str(r["k"]).startswith("g")]
            per[s][n] = {"p": st.mean(ps), "g": st.mean(pg) if pg else float("nan"), "files": fs,
                         "bino": st.mean(dets[f][0] for f in fs) if dets else None,
                         "desk": st.mean(dets[f][1] for f in fs) if dets else None,
                         "over": st.mean(bc[f][0] for f in fs if f in bc) if any(f in bc for f in fs) else None,
                         "aiside": st.mean(bc[f][1] for f in fs if f in bc) if any(f in bc for f in fs) else None}
    base = a.snaps[0]
    print(f"{'snap':14} {'n':>3} {'files':>5} {'Opus':>6} {'>50%':>6} {'GPT':>6} {'bino':>6} {'desk':>6}"
          + (f" {'over':>5} {'aiside':>6}" if scr else "") + f"  vs {base}")
    for s in a.snaps:
        rows = per[s]
        files = [f for v in rows.values() for f in v["files"]]
        fp = [st.mean(r["p_ai"] for r in allrec[s][f] if r["p_ai"] is not None and not str(r["k"]).startswith("g")) for f in files]
        line = f"{s:14} {len(rows):3} {len(files):5} {st.mean(fp):6.1f} {sum(p > 50 for p in fp) / len(fp):6.0%} {st.mean(v['g'] for v in rows.values()):6.1f}"
        if a.det:
            line += f" {st.mean(v['bino'] for v in rows.values()):6.3f} {st.mean(v['desk'] for v in rows.values()):6.2f}"
        if scr:
            ov = [v["over"] for v in rows.values() if v["over"] is not None]
            ai = [v["aiside"] for v in rows.values() if v["aiside"] is not None]
            line += (" " * (14 if not a.det else 0)) + f" {st.mean(ov) if ov else float('nan'):5.2f} {st.mean(ai) if ai else float('nan'):6.2f}"
        if s != base:
            common = [n for n in rows if n in per[base]]
            d = [rows[n]["p"] - per[base][n]["p"] for n in common]
            worse = sum(x > 0 for x in d)
            dg = [rows[n]["g"] - per[base][n]["g"] for n in common]
            line += (f"   Opus {st.mean(d):+5.1f} (worse {worse}/{len(d)}, p={wilcoxon(d):.3f})"
                     f"  GPT {st.mean(dg):+5.1f} (p={wilcoxon(dg):.3f})")
            if scr:
                do = [rows[n]["over"] - per[base][n]["over"] for n in common
                      if rows[n]["over"] is not None and per[base][n]["over"] is not None]
                if do:
                    line += f"  over {st.mean(do):+5.2f} (higher {sum(x > 0 for x in do)}, lower {sum(x < 0 for x in do)}, p={wilcoxon(do):.3f})"
        print(line)
    if a.noise:
        noise(a.snaps, per, allrec)
    if a.reasons:
        for s in a.snaps:
            c = Counter()
            for f, recs in allrec[s].items():
                for r in recs:
                    if r["p_ai"] and r["p_ai"] > 50:
                        for x in r["reasons"]:
                            c[x.split(":")[0].split("(")[0].strip().lower()[:60]] += 1
            print(f"\n{s} top reasons (judged AI):")
            for k, v in c.most_common(15):
                print(f"  {v:3} {k}")


if __name__ == "__main__":
    main()
