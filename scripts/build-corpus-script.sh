#!/usr/bin/env bash
# Build a human corpus of video scripts from the manual captions of pre-2022 YouTube videos.
#
#   en  narrated explainer channels, English captions
#   es  narrated explainer channels, Spanish captions (manual tracks are rarer: many rows
#       end as no-manual)
#
# Every text predates ChatGPT: the upload date comes from each video's own metadata and is
# tested against 2021-12-31, and only manual caption tracks are read (the "subtitles" of
# yt-dlp, never "automatic_captions"; --write-auto-subs is never passed). A video whose
# audio is not in the language is skipped as translated. Every video examined is recorded in
# eval/titles/script[-es]-manifest.tsv with its status, so the corpus can be audited. The
# texts are not redistributed and never enter the repository; this script fetches them.
#
# This is the one script that needs more than the standard library: plain urllib gets an
# empty body from the caption endpoint, so it calls yt-dlp (tested with 2026.10.26, install
# with: python3 -m pip install --user yt-dlp). It stops with an error if yt-dlp is missing.
# yt-dlp uses node for its JavaScript challenges when node is on PATH; manual subtitles
# download without it.
# Every kept text is cleaned and judged by the same function, also the ones saved by an earlier run, so
# manifest, files and titles.tsv always agree; one that no longer passes loses its row's kept status and its file.
# The only files it deletes are <channel>-<video id>.md ones whose manifest row is not kept; any other file in
# OUTDIR is left alone. A kept row whose file is missing is fetched again, and keeps its row until that fetch has
# been attempted, so a run that fetches nothing leaves the manifest as it was.
# Resumable: a video already in the manifest is not fetched again (error rows are retried).
# A channel listing that fails is reported on stderr and is not a manifest row. The exit status is not zero when
# no channel matches, when every listing failed, or when every fetch failed.
# Requests are spaced 1 to 2 seconds apart, and a channel stops at 12 kept videos or 60 examined.
#
# Usage: build-corpus-script.sh en|es [OUTDIR]     OUTDIR defaults to ~/corpus/script[-es]
#        CHANNELS="Kurzgesagt,Tom Scott" limits the run to those channels; RESERVE=1 adds
#        the reserve channels. It only builds the corpus; calibration is a separate step.
set -euo pipefail
LANG_CODE="${1:?language: en or es}"
case "$LANG_CODE" in en) SUF="" ;; es) SUF="-es" ;; *) echo "language must be en or es" >&2; exit 2 ;; esac
if ! python3 -m yt_dlp --version >/dev/null 2>&1; then
  echo "yt-dlp is not installed for python3: python3 -m pip install --user yt-dlp" >&2
  exit 3
fi
OUT="${2:-$HOME/corpus/script$SUF}"
HERE="$(cd "$(dirname "$0")" && pwd)"
MANIFEST="$HERE/../eval/titles/script$SUF-manifest.tsv"
mkdir -p "$OUT" "$(dirname "$MANIFEST")"
PYTHONUTF8=1 python3 - "$LANG_CODE" "$OUT" "$MANIFEST" "$HERE" "${CHANNELS:-}" "${RESERVE:-}" <<'PY'
import html, json, os, random, re, shutil, subprocess, sys, time, unicodedata
lang, out, manifest, here, only, reserve = sys.argv[1:7]
if lang == "es":
    os.environ.setdefault("QUIRON_BANDS", os.path.join(here, "bands-es.json"))
sys.path.insert(0, here)
import aimeter

CUTOFF = "20211231"      # upload_date must not be later
PER_CHANNEL = 12         # kept videos per channel
MAX_EXAMINED = 60        # candidates examined per channel
LO, HI = 300, 3000       # spoken words

# name -> handle. The handle only finds candidates; the date and the track come from the video.
CHANNELS = {
    "en": {
        "Kurzgesagt": "kurzgesagt", "CGP Grey": "CGPGrey", "Vox": "Vox", "Vsauce": "Vsauce",
        "Veritasium": "veritasium", "Every Frame a Painting": "everyframeapainting",
        "Nerdwriter1": "Nerdwriter1", "LEMMiNO": "LEMMiNO",
        "Wendover Productions": "Wendoverproductions", "Tom Scott": "TomScottGo",
        "Johnny Harris": "johnnyharris", "TED-Ed": "TEDEd", "3Blue1Brown": "3blue1brown",
        "Real Engineering": "RealEngineering", "PBS Space Time": "pbsspacetime",
        "exurb1a": "exurb1a", "Oversimplified": "OverSimplified",
    },
    # Antroporama and Magic Markers were dropped: their handles returned no listing, and the right ones
    # could not be established without contacting YouTube.
    "es": {
        "QuantumFracture": "QuantumFracture", "Jaime Altozano": "JaimeAltozano",
        "CuriosaMente": "CuriosaMente", "Academia Play": "AcademiaPlay",
        "Memorias de Pez": "MemoriasdePez", "El Robot de Platón": "ElRobotdePlaton",
        "Date un Vlog": "DateunVlog",
        "VisualPolitik": "VisualPolitik", "Derivando": "Derivando",
        "La Hiperactina": "LaHiperactina", "Pero eso es otra historia": "Peroesoesotrahistoria",
        "C de Ciencia": "CdeCiencia", "Un Mundo Inmenso": "UnMundoInmenso",
    },
}[lang]
RESERVE = {
    "en": {"Polyphonic": "Polyphonic", "Sam ONella Academy": "SamONellaAcademy",
           "Kaptainkristian": "KaptainKristian", "Captain Disillusion": "CaptainDisillusion",
           "Primer": "PrimerLearning"},
    "es": {},
}[lang]
if reserve:
    CHANNELS = {**CHANNELS, **RESERVE}
if only:
    CHANNELS = {k: v for k, v in {**CHANNELS, **RESERVE}.items() if k in only.split(",")}

# "este" is also the demonstrative ("este modelo"), so it counts only as a hesitation: "este..." or "este,"
FILLER = re.compile(r"\b(?:uh+|um+|uhm)\b" if lang == "en"
                    else r"\b(?:eh+|em+|o sea)\b|\beste(?=\s*(?:\.\.\.|…|,|--))", re.I)
# a cue that opens a turn of dialogue: ">>", a dash ("-", "--", "—"), or "NAME: " (accented names too)
SWITCH = re.compile(r"^(?:>>|-\s|--|—|[A-ZÁÉÍÓÚÑÜ][\w.' ]{0,24}:\s)")
# the same turns in running text, where the cue lines are gone: " --What?" or " —¿Qué?"
SWITCH_TEXT = re.compile(r"(?:^|\s)(?:--|—)(?=[\w¿¡\"'])")
# an error that says something lasting about the video; anything that mentions a retry is transient
GONE = re.compile(r"not available|members|Join this channel|Private video|has been removed|terminated|copyright|"
                  r"age-restricted|confirm your age|Video unavailable", re.I)
TRANSIENT = re.compile(r"try again|temporar|timed out|HTTP Error 5|429|Unable to download|not a bot|rate.limit", re.I)
# punctuation floors and ceilings, chosen on the kept texts
MIN_TERMINATORS = 0.02   # sentence ends per word: 1 in 50 words at most without one
MIN_CAPITALS = 0.03      # share of capitalised words: below it the caption is lower-case
MAX_FW_CAPITALS = 0.12   # share of "the/and/los/que..." capitalised mid-sentence: cues each started with a capital
FUNCTION = set(("the and of to in is that it for with as on this are be but not we you they was have has at by from or "
                "an so if then when what which who how there their" if lang == "en" else
                "el la los las y de que en un una es son se por con para como pero no lo del al su sus más muy ya si "
                "cuando donde qué cómo hay fue ha han").split())
COLS = "id channel upload_date track words status title".split()
YT = [sys.executable, "-m", "yt_dlp", "--no-warnings", "--ignore-config"]
if shutil.which("node"):
    YT[3:3] = ["--js-runtimes", "node"]
VIDEO_FILE = re.compile(r"[a-z0-9]+-[A-Za-z0-9_-]{11}\.md")


def slug(name):
    plain = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "", plain.lower())


def pause():
    time.sleep(random.uniform(1, 2))


def why(text):
    """The first ERROR line of yt-dlp's stderr, else its last line."""
    lines = [l for l in text.strip().splitlines() if l]
    return next((l for l in lines if l.startswith("ERROR")), lines[-1] if lines else "no output")[:200]


def run(args, timeout=180):
    return subprocess.run(YT + args, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=timeout)


def load():
    rows = {}
    if os.path.exists(manifest):
        for l in open(manifest, encoding="utf-8").read().splitlines()[1:]:
            r = dict(zip(COLS, l.split("\t")))
            if len(r) == len(COLS):
                rows[(r["channel"], r["id"])] = r
    return rows


def save(rows):
    with open(manifest, "w", encoding="utf-8", newline="\n") as f:
        f.write("\t".join(COLS) + "\n")
        for k in sorted(rows):
            f.write("\t".join(rows[k][c] for c in COLS) + "\n")


def record(rows, channel, vid, date="", track="", words=0, status="", title=""):
    rows[(channel, vid)] = dict(id=vid, channel=channel, upload_date=date, track=track,
                                words=str(words), status=status,
                                title=" ".join(title.split()))
    save(rows)


def candidates(channel, handle):
    """Video ids of a channel, roughly dated, spread round-robin over its years."""
    cache = os.path.join(out, ".candidates", slug(channel) + ".txt")
    if not os.path.exists(cache):
        r = run(["--flat-playlist", "--extractor-args", "youtubetab:approximate_date", "--print",
                 "%(upload_date)s\t%(id)s\t%(duration)s\t%(title)s",
                 f"https://www.youtube.com/@{handle}/videos"], timeout=1800)
        if not r.stdout.strip():
            raise RuntimeError("no listing: " + why(r.stderr))
        os.makedirs(os.path.dirname(cache), exist_ok=True)
        open(cache, "w", encoding="utf-8", newline="\n").write(r.stdout)
    years = {}
    for l in open(cache, encoding="utf-8").read().splitlines():
        p = l.split("\t", 3)
        if len(p) < 4:
            continue
        date, vid, dur, title = p
        # the listing rounds to "N years ago" (down), so its dates are approximate. Skipping those later than
        # 20220630 can also skip an eligible video from mid-November to December 2021 (the latest kept upload
        # is 2021-11-11). Whatever passes is still tested per video against CUTOFF.
        if date not in ("NA", "") and date > "20220630":
            continue
        try:
            if not 120 <= float(dur) <= 1800:
                continue
        except ValueError:
            pass
        years.setdefault(date[:4] if date[:1].isdigit() else "????", []).append((vid, title))
    rng = random.Random(channel)
    for v in years.values():
        rng.shuffle(v)
    order = []
    while any(years.values()):
        for y in sorted(years):
            if years[y]:
                order.append(years[y].pop())
    return order


CUE = re.compile(r"\[[^\[\]\d]{1,40}\]|\((?=[^()]{0,40}\))[^()\d]*(?:music|laugh|applause|sound|noise|rustl|bang|beep|chime|"
                 r"cheer|gasp|clap|whoosh|sigh|m[uú]sica|risas?|aplausos?|sonido)[^()\d]*\)", re.I)


def unescape(l):
    """Captions are sometimes escaped twice ("&amp;lt;i&amp;gt;"): decode until stable, then drop tags."""
    for _ in range(3):
        u = html.unescape(l)
        if u == l:
            break
        l = u
    return re.sub(r"</?[A-Za-z][^>]*>|<\d[\d:.]*>", "", l).replace("\u00a0", " ")


def tidy(text):
    """Caption cues such as [Music] or (upbeat music), markup and a leading dash are not speech."""
    t = re.sub(r"\s{2,}", " ", CUE.sub("", unescape(text.strip()))).strip()
    return re.sub(r"^- ", "", t)


def vtt_text(path):
    """Caption cues as running text, plus the number of speaker changes. No timestamps,
    no tags, no line repeated from the cue before."""
    lines, last, switches = [], "", 0
    for l in open(path, encoding="utf-8", errors="replace").read().splitlines():
        l = l.strip()
        if (not l or l.startswith(("WEBVTT", "Kind:", "Language:", "NOTE", "STYLE")) or "-->" in l
                or re.fullmatch(r"\d+", l)):
            continue
        l = unescape(l).strip()
        if l and l != last:
            switches += bool(SWITCH.match(l))
            lines.append(l)
        last = l
    return tidy(" ".join(lines)), switches


def judge(text, switches):
    """(words, status) of a cleaned text: kept, or the reason it is not a script."""
    w = text.split()
    n = len(w)
    if n < LO:
        return n, "short"
    if n > HI:
        return n, "long"
    if switches > 5 or len(FILLER.findall(text)) > 2 * n / 1000:
        return n, "unscripted"
    letters = [c for c in text if c.isalpha()]
    ends = len(re.findall(r"[.!?…]+(?=[\"')\]”’»]*(?:\s|$))", text))
    caps = sum(x.lstrip("\"'(“¿¡")[:1].isupper() for x in w)
    fw = [b.strip("\"'(“¿¡)") for a, b in zip(w, w[1:]) if not re.search(r"[.!?…:][\"')”’»]*$", a)]
    fw = [x for x in fw if x.lower() in FUNCTION]
    fwcap = sum(x[:1].isupper() and x != "I" for x in fw) / len(fw) if len(fw) >= 30 else 0
    if (r"\rtf" in text or aimeter.measure(text) is None or sum(c.isupper() for c in letters) > 0.6 * len(letters)
            or ends < MIN_TERMINATORS * n or caps < MIN_CAPITALS * n or fwcap > MAX_FW_CAPITALS):
        return n, "unpunctuated"
    return n, "kept"


def examine(channel, vid, title, work):
    """(date, track, words, status, text, title) for one video."""
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work)
    r = run(["--skip-download", "--write-info-json", "--write-subs", "--sub-langs", lang + ".*",
             "--sub-format", "vtt", "-o", os.path.join(work, "%(id)s"),
             "https://www.youtube.com/watch?v=" + vid])
    info_path = os.path.join(work, vid + ".info.json")
    if not os.path.exists(info_path):
        raise RuntimeError(why(r.stderr) if r.stderr.strip() else "no metadata")
    info = json.load(open(info_path, encoding="utf-8"))
    d = info.get("upload_date") or ""
    date = f"{d[:4]}-{d[4:6]}-{d[6:]}" if len(d) == 8 else ""
    title = info.get("title") or title
    if not d or d > CUTOFF:
        return date, "", 0, "late" if d else "error", "", title
    manual = sorted(k for k in (info.get("subtitles") or {}) if re.match(lang + r"(?:[-_]|$)", k))
    auto = [k for k in (info.get("automatic_captions") or {}) if re.match(lang + r"(?:[-_]|$)", k)]
    if not manual:
        return date, "auto" if auto else "none", 0, "no-manual", "", title
    orig = (info.get("language") or lang).lower()
    if not orig.startswith(lang):
        return date, "manual", 0, "translated", "", title
    track = sorted(manual, key=lambda k: (k != lang, len(k)))[0]
    path = os.path.join(work, f"{vid}.{track}.vtt")
    if not os.path.exists(path):
        raise RuntimeError("manual track listed but not downloaded: " + why(r.stderr))
    text, switches = vtt_text(path)
    spoken = aimeter.spoken(text)  # an RTF caption is not text: judge() sends it to unpunctuated
    n, status = judge(spoken, switches)
    return date, "manual", n, status, spoken, title


def path_of(r):
    return os.path.join(out, f"{slug(r['channel'])}-{r['id']}.md")


def rejudge(rows):
    """Clean and judge again every kept text with the current rules, from the saved file: the manifest
    words come from the file, a text that no longer passes loses its kept status and its file. A kept row whose
    file is missing is left as it is (the loop fetches it again). Only a file named <channel>-<video id>.md
    whose row is not kept is deleted (calibration reads every .md in the folder); nothing else is touched."""
    before = repr(sorted(rows.items()))
    for r in rows.values():
        if r["status"] != "kept" or not os.path.exists(path_of(r)):
            continue
        t = tidy(open(path_of(r), encoding="utf-8").read())
        n, status = judge(t, len(SWITCH_TEXT.findall(t)))
        r["words"], r["status"] = str(n), status
        if status == "kept":
            open(path_of(r), "w", encoding="utf-8", newline="\n").write(t + "\n")
    for r in rows.values():
        f = path_of(r)
        if r["status"] != "kept" and VIDEO_FILE.fullmatch(os.path.basename(f)) and os.path.isfile(f):
            os.remove(f)
    if repr(sorted(rows.items())) != before:
        save(rows)


def fetch(channel, vid, title, state):
    """Examine one video and record it. True when the video was kept."""
    pause()
    work = os.path.join(out, ".work")
    state["tried"] += 1
    try:
        date, track, n, status, text, title = examine(channel, vid, title, work)
        state["streak"] = 0
        state["fetched"] += 1
    except Exception as e:
        print(f"  {channel} {vid}: {e}", file=sys.stderr)
        if GONE.search(str(e)) and not TRANSIENT.search(str(e)):  # members-only, private or removed: a fact about the video, not a refusal
            record(rows, channel, vid, status="unavailable", title=title)
            return False
        record(rows, channel, vid, status="error", title=title)
        state["streak"] += 1
        if state["streak"] >= 6:
            # YouTube answers "sign in to confirm you're not a bot" for a while: wait it out
            if "not a bot" in str(e) and state["pauses"] < 6:
                state["pauses"] += 1
                print(f"  blocked; waiting 20 minutes ({state['pauses']}/6)", file=sys.stderr)
                time.sleep(1200)
                state["streak"] = 0
            else:
                sys.exit("6 errors in a row: YouTube is refusing requests; run again later (resumable)")
        return False
    if status == "kept":
        open(os.path.join(out, f"{slug(channel)}-{vid}.md"), "w", encoding="utf-8",
             newline="\n").write(text + "\n")
    record(rows, channel, vid, date, track, n, status, title)
    return status == "kept"


if not CHANNELS:
    sys.exit("no channel matches CHANNELS=" + repr(only))
rows = load()
rejudge(rows)
state = dict(streak=0, pauses=0, tried=0, fetched=0)
listed = failed = 0
for channel, handle in CHANNELS.items():
    mine = lambda: [r for k, r in rows.items() if k[0] == channel and r["id"] != "-"]
    for r in [r for r in mine() if r["status"] == "kept" and not os.path.exists(path_of(r))]:
        fetch(channel, r["id"], r["title"], state)  # a kept row without its file: fetch it again
    try:
        todo = candidates(channel, handle)
        listed += 1
    except Exception as e:
        print(f"{channel}: listing failed ({e})", file=sys.stderr)
        failed += 1
        continue
    done = {r["id"] for r in mine() if r["status"] != "error"}
    kept = sum(r["status"] == "kept" for r in mine())
    examined = len(done)
    for vid, title in todo:
        if kept >= PER_CHANNEL or examined >= MAX_EXAMINED:
            break
        if vid in done:
            continue
        before = state["fetched"]
        kept += fetch(channel, vid, title, state)
        examined += state["fetched"] > before
    shutil.rmtree(os.path.join(out, ".work"), ignore_errors=True)
    print(f"{channel}: {kept} kept, {examined} examined", file=sys.stderr)

rejudge(rows)  # the same cleaning and judging for every text, so manifest, files and titles.tsv agree

with open(os.path.join(out, "titles.tsv"), "w", encoding="utf-8", newline="\n") as idx:
    for r in sorted(rows.values(), key=lambda r: slug(r["channel"]) + "-" + r["id"]):
        if r["status"] == "kept" and os.path.exists(path_of(r)):
            idx.write(f"{slug(r['channel'])}-{r['id']}\t{r['words']}\t{r['title']}\n")
n = sum(r["status"] == "kept" and os.path.exists(path_of(r)) for r in rows.values())
print(f"{lang} script corpus: {n} texts in {out}", file=sys.stderr)
if listed == 0 or (state["tried"] and not state["fetched"]):
    sys.exit(f"nothing built: {failed} listing(s) failed, {state['tried']} fetch(es) tried, none succeeded")
PY
