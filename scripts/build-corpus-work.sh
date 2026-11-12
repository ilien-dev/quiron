#!/usr/bin/env bash
# Rebuild a human corpus for one of the work registers, then calibrate its band file.
#
#   pr      descriptions of merged GitHub pull requests opened from 2019 to 2021
#   commit  commit messages with a long body, dated before 2022, from projects that write them
#   readme  READMEs of repositories last pushed before June 2021
#   email   workplace emails from the Enron corpus (AESLC, Zhang & Tetreault 2019), 1999-2002
#
# Every text predates ChatGPT. Only texts the meter can measure are kept (about 120 words
# and 8 sentences of prose), which leaves out the short ones: most commit messages and
# many emails. Texts are not redistributed; this script fetches them so the calibration
# is reproducible. Set GITHUB_TOKEN for pr, commit and readme: the anonymous API allows
# 60 requests an hour.
#
# Usage: build-corpus-work.sh REGISTER [OUTDIR]     MAX=160 NO_CALIBRATE=1 build-corpus-work.sh ...
set -euo pipefail
REG="${1:?register: pr, commit, readme or email}"
OUT="${2:-$HOME/.cache/quiron/$REG}"
HERE="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$OUT"
PYTHONUTF8=1 python3 - "$REG" "$OUT" "${MAX:-160}" "$HERE" <<'PY'
import io, json, os, re, sys, time, urllib.error, urllib.parse, urllib.request, zipfile
reg, out, cap_total, here = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
sys.path.insert(0, here)
import aimeter

TOKEN = os.environ.get("GITHUB_TOKEN", "")


def get(url, raw=False, accept=None):
    for wait in (2, 5, 15, 45, 90):
        try:
            h = {"User-Agent": "quiron-corpus/1.0"}
            if "api.github.com" in url:
                h["Accept"] = accept or "application/vnd.github+json"
                if TOKEN:
                    h["Authorization"] = "Bearer " + TOKEN
            with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=60) as r:
                data = r.read()
                return data if raw else json.loads(data)
        except urllib.error.HTTPError as e:
            if e.code not in (403, 429, 502, 503):
                return None
        except (urllib.error.URLError, TimeoutError, ValueError):
            pass
        time.sleep(wait)
    return None


EN = set("the and of to is in that it for with as on this you are be but not we".split())


def english(text):
    w = re.findall(r"[a-z]+", text.lower())
    return len(w) > 50 and sum(x in EN for x in w) > 0.12 * len(w)


def usable(text, lo, hi):
    n = len(aimeter.prose(text).split())
    return lo <= n <= hi and english(text) and aimeter.measure(text) is not None


kept, per = [], {}
quota = [0]  # texts one search query may still add, so no language or year fills the corpus


def keep(name, text, title, *keys_caps):
    """Save one text unless a cap (author, repository) is already full."""
    if len(kept) >= cap_total or quota[0] <= 0 or any(per.get(k, 0) >= c for k, c in keys_caps):
        return
    quota[0] -= 1
    name = re.sub(r"[^A-Za-z0-9_.-]+", "-", name)[:80]
    open(os.path.join(out, name + ".md"), "w", encoding="utf-8", newline="\n").write(text.strip() + "\n")
    kept.append((name, len(text.split()), " ".join(title.split())))
    for k, _ in keys_caps:
        per[k] = per.get(k, 0) + 1


BOT = re.compile(r"\[bot\]|bot$|dependabot|renovate|greenkeeper", re.I)

if reg == "pr":
    langs = ["python", "javascript", "typescript", "go", "rust", "java", "ruby", "c++", "php", "c#"]
    for year in (2019, 2020, 2021):
        for lang in langs:
            for page in (1, 2):
                q = f"is:pr is:merged created:{year}-01-01..{year}-12-31 comments:>3 language:{lang}"
                d = get("https://api.github.com/search/issues?per_page=100&page=%d&q=%s"
                        % (page, urllib.parse.quote(q)))
                time.sleep(2.5)
                quota[0] = cap_total // 40
                for it in (d or {}).get("items", []):
                    body = re.sub(r"<!--.*?-->", "", it.get("body") or "", flags=re.S).replace("\r\n", "\n")
                    user = it["user"]["login"]
                    repo = it["repository_url"].split("/repos/")[1]
                    boxes = len(re.findall(r"^\s*[-*] \[[ xX]\]", body, re.M))
                    if BOT.search(user) or boxes > 3 or not usable(body, 130, 900):
                        continue
                    keep(f"{repo.replace('/', '-')}-{it['number']}", body,
                         f'"{it["title"]}" in the {repo} repository', ("u:" + user, 2), ("r:" + repo, 4))
elif reg == "commit":
    repos = ["torvalds/linux", "git/git", "postgres/postgres", "golang/go", "python/cpython",
             "nodejs/node", "curl/curl", "systemd/systemd", "redis/redis", "qemu/qemu",
             "llvm/llvm-project", "freebsd/freebsd-src", "sqlite/sqlite", "neovim/neovim",
             "rust-lang/rust", "git-lfs/git-lfs", "mesonbuild/meson", "bitcoin/bitcoin"]
    trailer = re.compile(r"^(?:[A-Z][\w-]+-by|Cc|Link|Fixes|Reviewed-on|Change-Id|Closes|PR-URL|Refs?|"
                         r"Discussion|Backpatch\S*|Differential Revision|git-svn-id|Bug|Message-I[dD]):.*$", re.M)
    for year in (2021, 2020, 2019):
        for repo in repos:
            for page in (1, 2, 3):
                d = get(f"https://api.github.com/repos/{repo}/commits?until={year}-12-31T00:00:00Z"
                        f"&since={year}-01-01T00:00:00Z&per_page=100&page={page}")
                time.sleep(0.8)
                quota[0] = cap_total
                for c in d or []:
                    msg = c["commit"]["message"].replace("\r\n", "\n")
                    subject, _, body = msg.partition("\n")
                    body = trailer.sub("", body).strip()
                    author = c["commit"]["author"]["name"]
                    if subject.startswith(("Merge", "Revert", "Auto merge", "Rollup")) or BOT.search(author):
                        continue
                    if not usable(body, 130, 900):
                        continue
                    keep(f"{repo.replace('/', '-')}-{c['sha'][:10]}", subject + "\n\n" + body,
                         f'"{subject}" in the {repo} repository', ("u:" + author, 2), ("r:" + repo, 12))
elif reg == "readme":
    langs = ["python", "javascript", "go", "rust", "ruby", "java", "c", "typescript", "php", "shell"]
    for lang in langs:
        for page in (1, 2, 3):
            q = f"pushed:<2021-06-01 stars:200..3000 language:{lang} archived:false"
            d = get("https://api.github.com/search/repositories?per_page=100&page=%d&sort=stars&q=%s"
                    % (page, urllib.parse.quote(q)))
            time.sleep(2.5)
            quota[0] = cap_total // 20
            for it in (d or {}).get("items", []):
                if quota[0] <= 0:
                    break
                if it.get("fork") or per.get("u:" + it["owner"]["login"], 0) >= 1 or len(kept) >= cap_total:
                    continue
                raw = get(f"https://api.github.com/repos/{it['full_name']}/readme", raw=True,
                          accept="application/vnd.github.raw")
                time.sleep(0.5)
                if not raw:
                    continue
                text = raw.decode("utf-8", "replace").replace("\r\n", "\n")
                if "<table" in text.lower() or not usable(text, 300, 2500):
                    continue
                desc = (it.get("description") or "").strip()
                keep(it["full_name"].replace("/", "-"), text,
                     f'{it["name"]}' + (f', described as "{desc}"' if desc else ""),
                     ("u:" + it["owner"]["login"], 1))
elif reg == "email":
    z = get("https://codeload.github.com/ryanzhumich/AESLC/zip/refs/heads/master", raw=True)
    if not z:
        sys.exit("could not download the AESLC corpus")
    zf = zipfile.ZipFile(io.BytesIO(z))
    names = sorted(n for n in zf.namelist() if n.endswith(".subject"))
    # spread over the corpus instead of taking one mailbox
    names.sort(key=lambda n: os.path.basename(n)[::-1])
    seen = set()
    quota[0] = cap_total
    for n in names:
        txt = zf.read(n).decode("utf-8", "replace").replace("\r\n", "\n")
        body, _, rest = txt.partition("@subject")
        subject = rest.strip().split("\n")[0].strip()
        body = body.strip()
        key = body[:80]
        if not subject or key in seen or "-----Original Message" in body or "Forwarded by" in body:
            continue
        if not usable(body, 130, 700):
            continue
        seen.add(key)
        keep("enron-" + os.path.basename(n).replace(".subject", ""), body, f'"{subject}"')
else:
    sys.exit("register must be pr, commit, readme or email")

with open(os.path.join(out, "titles.tsv"), "w", encoding="utf-8", newline="\n") as idx:
    for name, words, title in sorted(kept):
        idx.write(f"{name}\t{words}\t{title}\n")
print(f"{reg} corpus: {len(kept)} texts in {out}", file=sys.stderr)
PY
AI="$HERE/../eval/ai/$REG/train-2026-11"
[ -n "${NO_CALIBRATE:-}" ] || python3 "$HERE/aimeter.py" --calibrate "$OUT" \
  $([ -d "$AI" ] && echo --ai "$AI") --out "$HERE/bands-$REG.json"
