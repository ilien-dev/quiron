#!/usr/bin/env python3
"""Rewrite detector: what still separates the skill's rewrites from human posts.

Logistic regression on topic-poor features: aimeter's rates, the explore.py rates, and
the frequency of words that occur in at least MIN_TITLES different titles on both
sides (so topic words cannot carry it). Cross-validated leaving one title out.

  rwdetect.py train   -> CV AUC, top features by weight, model saved to rw-model.pkl
  rwdetect.py score GLOB...  -> mean P(rewrite) per glob
"""
import glob, os, pickle, re, sys, statistics as st
from collections import Counter
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score

CODE = os.path.dirname(os.path.abspath(__file__))
H = os.environ.get("QUIRON_E2E", os.path.expanduser("~/.cache/quiron-e2e"))
sys.path.insert(0, CODE)
sys.path.insert(0, os.path.join(CODE, "..", "..", "scripts"))
import aimeter  # noqa
import explore  # noqa  (defines feats)

WORD = re.compile(r"[a-z][a-z']+")
E = os.path.join(CODE, "..", "ai", "blog")
MIN_TITLES = 8


def title_of(path):
    return os.path.basename(os.path.dirname(path)) if path.endswith("final.md") else os.path.basename(path)[:-3]


def dense(md):
    m = aimeter.measure(md)
    x = explore.feats(md)
    if not m or not x:
        return None
    d = {k: v for k, v in m.items() if not k.startswith("_")}
    d.update(x)
    return d


def load():
    hum = sorted(glob.glob(os.path.expanduser("~/corpus/blog/*.md")))
    rw = sorted(glob.glob(f"{H}/work/v110/r*/*/final.md")) + sorted(
        glob.glob(f"{E}/e2e-v[0-9]/*.md")) + sorted(glob.glob(f"{E}/final-fresh/*.md"))
    docs = []
    for y, fs in ((0, hum), (1, rw)):
        for f in fs:
            md = open(f).read()
            d = dense(md)
            if d:
                docs.append((f, y, title_of(f), md, d))
    return docs


def vocab(docs):
    titles = {0: {}, 1: {}}
    for f, y, t, md, d in docs:
        for w in set(WORD.findall(aimeter.prose(md).lower())):
            titles[y].setdefault(w, set()).add(t)
    return sorted(w for w in titles[0] if len(titles[0][w]) >= MIN_TITLES
                  and len(titles[1].get(w, ())) >= MIN_TITLES)


def matrix(docs, V, dkeys):
    X = []
    for f, y, t, md, d in docs:
        words = WORD.findall(aimeter.prose(md).lower())
        c = Counter(words)
        n = max(len(words), 1)
        X.append([d[k] for k in dkeys] + [c[w] / n * 1000 for w in V])
    return np.array(X, dtype=float)


def main():
    if sys.argv[1] == "train":
        docs = load()
        V = vocab(docs)
        dkeys = sorted(docs[0][4])
        X = matrix(docs, V, dkeys)
        y = np.array([d[1] for d in docs])
        titles = [d[2] for d in docs]
        names = dkeys + ["w:" + w for w in V]
        p = np.zeros(len(y))
        for t in sorted(set(titles)):
            te = np.array([tt == t for tt in titles])
            sc = StandardScaler().fit(X[~te])
            clf = LogisticRegression(C=0.05, max_iter=5000, class_weight="balanced")
            clf.fit(sc.transform(X[~te]), y[~te])
            p[te] = clf.predict_proba(sc.transform(X[te]))[:, 1]
        print(f"docs {len(y)} (human {sum(y == 0)}, rewrites {sum(y == 1)}), features {len(names)}")
        print(f"leave-one-title-out AUC {roc_auc_score(y, p):.3f}")
        for grp in ("v110", "e2e-v5", "final-fresh"):
            idx = [i for i, d in enumerate(docs) if grp in d[0]]
            print(f"  {grp}: mean P(rewrite) {p[idx].mean():.2f}")
        print(f"  human: mean P(rewrite) {p[y == 0].mean():.2f}, >0.5: {(p[y == 0] > .5).mean():.0%}")
        sc = StandardScaler().fit(X)
        clf = LogisticRegression(C=0.05, max_iter=5000, class_weight="balanced").fit(sc.transform(X), y)
        w = clf.coef_[0]
        order = np.argsort(w)
        hm, rm = X[y == 0].mean(0), X[y == 1].mean(0)
        print("\nmost rewrite-like (feature, weight, human mean, rewrite mean):")
        for i in order[::-1][:25]:
            print(f"  {names[i]:26} {w[i]:+.3f}  {hm[i]:8.2f} {rm[i]:8.2f}")
        print("\nmost human-like:")
        for i in order[:25]:
            print(f"  {names[i]:26} {w[i]:+.3f}  {hm[i]:8.2f} {rm[i]:8.2f}")
        pickle.dump((V, dkeys, sc, clf), open(f"{H}/rw-model.pkl", "wb"))
    else:
        V, dkeys, sc, clf = pickle.load(open(f"{H}/rw-model.pkl", "rb"))
        for g in sys.argv[2:]:
            docs = []
            for f in sorted(glob.glob(g)):
                md = open(f).read()
                d = dense(md)
                if d:
                    docs.append((f, 1, "", md, d))
            X = matrix(docs, V, dkeys)
            p = clf.predict_proba(sc.transform(X))[:, 1]
            print(f"{p.mean():.3f}  n={len(p)}  {g}")


if __name__ == "__main__":
    main()
