#!/usr/bin/env python3
"""Score the skill itself: human texts vs AI texts vs AI texts after the skill.

A change to the meter, the checklist or the lexicons is only an improvement if it
separates AI text from human text better AND keeps flagging human text no more
often than before. This measures both on held-out data, so the bands are never
scored against the texts they were built from.

The human corpus is split deterministically: every Kth file (sorted by name,
counting from the first) is held out, the rest calibrate a temporary band file. Every group, the held-out
humans included, is then scored against that band file.

Reported per group:
  score        features inside the band, of 23 (median, and share at 14+)
  AI side      mean number of features outside the band on the AI side
  overshot     mean number outside on the overshoot side
  audit FAILs  mean FAIL items from audit.py, and share of texts with none
Per feature: AUC of each AI group against the held-out humans, i.e. the chance
a random AI text sits further toward the AI side than a random human text.
0.5 is no signal. Per check: the share of texts in each group it FAILs, so a
check that fires on humans is visible at once.

With --ai-train DIR, a second and independent judge is trained: a naive Bayes
classifier over word frequencies, fitted on the calibration humans against those
AI texts, and never shown the held-out humans or any scored group. Its mean
P(AI) per group is reported. It is independent of the bands and the checklist,
so a rewrite that games the 17 rates without changing the underlying word
distribution shows up here. Keep the AI training texts on topics disjoint from
the scored groups, or the judge learns topics instead of style.

Usage:
  evaluate.py --human DIR [--holdout K] [--ai-train DIR] NAME=DIR [NAME=DIR ...] [--json]
"""
import json, math, os, re, statistics as st, sys, tempfile
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import aimeter  # noqa: E402


def texts(directory):
    return sorted(os.path.join(directory, n) for n in os.listdir(directory)
                  if n.endswith((".md", ".txt")))


def measured(paths):
    out = []
    for p in paths:
        m = aimeter.measure(open(p, encoding="utf-8").read())
        if m:
            out.append((p, m))
    return out


def auc(ai, human, push):
    """P(AI value is further toward the AI side than a human value)."""
    if not ai or not human:
        return None
    sign = -1 if push == "lo" else 1
    wins = sum((sign * a > sign * h) + 0.5 * (a == h) for a in ai for h in human)
    return round(wins / (len(ai) * len(human)), 3)


def tokens(path):
    return re.findall(r"[a-z']+", aimeter.prose(open(path, encoding="utf-8").read()).lower())


class Judge:
    """Multinomial naive Bayes, human vs AI, Laplace smoothing, equal priors."""

    def __init__(self, human_paths, ai_paths):
        self.counts = [Counter(), Counter()]
        for label, paths in ((0, human_paths), (1, ai_paths)):
            for p in paths:
                self.counts[label].update(tokens(p))
        vocab = set(self.counts[0]) | set(self.counts[1])
        self.v = len(vocab)
        self.tot = [sum(c.values()) for c in self.counts]

    def p_ai(self, path):
        ll = [0.0, 0.0]
        for w in tokens(path):
            for c in (0, 1):
                ll[c] += math.log((self.counts[c][w] + 1) / (self.tot[c] + self.v))
        d = max(min(ll[0] - ll[1], 700), -700)
        return 1 / (1 + math.exp(d))


def main():
    args = sys.argv[1:]
    as_json = "--json" in args
    args = [a for a in args if a != "--json"]
    if "--human" not in args:
        sys.exit(__doc__)
    k = int(args[args.index("--holdout") + 1]) if "--holdout" in args else 4
    human_dir = args[args.index("--human") + 1]
    groups = [a.split("=", 1) for a in args if "=" in a]

    # split on the file list, not on what measured, so the split is stable
    all_h = texts(human_dir)
    train_paths = [p for i, p in enumerate(all_h) if i % k != 0]
    train = [m for _, m in measured(train_paths)]
    test = measured([p for i, p in enumerate(all_h) if i % k == 0])
    ai_train = args[args.index("--ai-train") + 1] if "--ai-train" in args else None
    # directions are learned from the AI training texts too, never from a scored group
    bands = aimeter.bands_from(train, [m for _, m in measured(texts(ai_train))]
                               if ai_train else None)
    bands.update(aimeter.band_meta())  # keep the register's language, lexicon, thresholds
    bands.pop("_corpus", None)
    tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
    json.dump(bands, tmp)
    tmp.close()
    os.environ["IM_HUMAN_BANDS"] = tmp.name
    import audit  # reads the band file through aimeter, so import after the override

    rows = {"human-heldout": test}
    rows.update({name: measured(texts(d)) for name, d in groups})
    judge = None
    if ai_train:
        judge = Judge(train_paths, texts(ai_train))

    report = {"bands_from": len(train), "groups": {}, "auc": {}, "checks": {}}
    for name, items in rows.items():
        scores, ai_side, over, fails, zero = [], [], [], [], 0
        check_fail = {}
        for path, m in items:
            v = {key: aimeter.verdict(key, m[key], bands[key]) for key in aimeter.AI_REF}
            scores.append(sum(1 for x in v.values() if x == "ok"))
            ai_side.append(sum(1 for x in v.values() if x.endswith("AI side")))
            over.append(sum(1 for x in v.values() if x.endswith("overshot")))
            res = audit.run(path)
            nf = [r[0] for r in res if r[2] == "FAIL"]
            fails.append(len(nf))
            zero += not nf
            for cid in nf:
                check_fail[cid] = check_fail.get(cid, 0) + 1
        n = len(items)
        pj = [judge.p_ai(p) for p, _ in items] if judge else []
        report["groups"][name] = {
            "n": n,
            "judge_p_ai": round(st.mean(pj), 2) if pj else None,
            "judge_as_ai": round(sum(x > 0.5 for x in pj) / n, 2) if pj else None,
            "score_median": st.median(scores) if n else None,
            "score_14plus": round(sum(s >= 14 for s in scores) / n, 2) if n else None,
            "ai_side_mean": round(st.mean(ai_side), 2) if n else None,
            "overshot_mean": round(st.mean(over), 2) if n else None,
            "audit_fails_mean": round(st.mean(fails), 2) if n else None,
            "audit_clean_share": round(zero / n, 2) if n else None,
        }
        report["checks"][name] = {c: round(x / n, 2) for c, x in sorted(check_fail.items())}
    for key in aimeter.AI_REF:
        push = bands[key].get("push", aimeter.AI_REF[key][0])
        if not push:
            continue
        hv = [m[key] for _, m in test]
        report["auc"][key] = {name: auc([m[key] for _, m in items], hv, push)
                              for name, items in rows.items() if name != "human-heldout"}
    os.unlink(tmp.name)

    if as_json:
        print(json.dumps(report, indent=1))
        return
    print(f"bands from {len(train)} human texts, {len(test)} held out\n")
    cols = ["n", "judge_p_ai", "judge_as_ai", "score_median", "score_14plus", "ai_side_mean", "overshot_mean",
            "audit_fails_mean", "audit_clean_share"]
    print(f"{'group':18}" + "".join(f"{c:>18}" for c in cols))
    for name, g in report["groups"].items():
        print(f"{name:18}" + "".join(f"{str(g[c]):>18}" for c in cols))
    names = [n for n in rows if n != "human-heldout"]
    print(f"\n{'AUC vs held-out humans':30}" + "".join(f"{n:>16}" for n in names))
    for key, byg in report["auc"].items():
        print(f"{aimeter.LABELS[key]:30}" + "".join(f"{str(byg[n]):>16}" for n in names))
    print(f"\n{'FAIL rate per check':18}" + "".join(f"{n:>16}" for n in rows))
    cids = sorted({c for g in report["checks"].values() for c in g})
    for c in cids:
        print(f"{c:18}" + "".join(f"{report['checks'][n].get(c, 0):>16}" for n in rows))


if __name__ == "__main__":
    main()
