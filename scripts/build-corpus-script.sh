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
# with: python3 -m pip install --user yt-dlp) and node for its JavaScript challenges.
# Resumable: a video already in the manifest is not fetched again (error rows are retried).
# Requests are spaced 1 to 2 seconds apart, and a channel stops at 12 kept videos or 60 examined.
#
# Usage: build-corpus-script.sh en|es [OUTDIR]     OUTDIR defaults to ~/corpus/script[-es]
#        CHANNELS="Kurzgesagt,Tom Scott" limits the run to those channels; RESERVE=1 adds
#        the reserve channels. It only builds the corpus; calibration is a separate step.
set -euo pipefail
LANG_CODE="${1:?language: en or es}"
case "$LANG_CODE" in en) SUF="" ;; es) SUF="-es" ;; *) echo "language must be en or es" >&2; exit 2 ;; esac
OUT="${2:-$HOME/corpus/script$SUF}"
HERE="$(cd "$(dirname "$0")" && pwd)"
MANIFEST="$HERE/../eval/titles/script$SUF-manifest.tsv"
mkdir -p "$OUT" "$(dirname "$MANIFEST")"
PYTHONUTF8=1 python3 - "$LANG_CODE" "$OUT" "$MANIFEST" "$HERE" "${CHANNELS:-}" "${RESERVE:-}" <<'PY'
import glob, json, os, random, re, shutil, subprocess, sys, time
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
    "es": {
        "QuantumFracture": "QuantumFracture", "Jaime Altozano": "JaimeAltozano",
        "CuriosaMente": "CuriosaMente", "Academia Play": "AcademiaPlay",
        "Memorias de Pez": "MemoriasdePez", "El Robot de Platon": "ElRobotdePlaton",
        "Date un Vlog": "DateunVlog", "Magic Markers": "MagicMarkers",
        "VisualPolitik": "VisualPolitik", "Derivando": "Derivando",
        "La Hiperactina": "LaHiperactina", "Pero eso es otra historia": "Peroesoesotrahistoria",
        "Antroporama": "Antroporama", "C de Ciencia": "CdeCiencia", "Un Mundo Inmenso": "UnMundoInmenso",
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
SWITCH = re.compile(r"^(?:>>|-\s|[A-Z][A-Za-z.' ]{0,24}:\s)")
GONE = re.compile(r"not available|members|Join this channel|Private video|has been removed|terminated|copyright|age-restricted|confirm your age|unavailable", re.I)
COLS = "id channel upload_date track words status title".split()
YT = [sys.executable, "-m", "yt_dlp", "--js-runtimes", "node", "--no-warnings", "--ignore-config"]
node = "C:/Program Files/nodejs"
if os.path.isdir(node):
    os.environ["PATH"] += os.pathsep + node


def slug(name):
    return re.sub(r"[^a-z0-9]+", "", name.lower())


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
        # the listing rounds to "N years ago": keep a margin, the real date is tested later
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


def tidy(text):
    """Caption cues such as [Music] or (upbeat music) and a leading dash are not speech."""
    return re.sub(r"\s{2,}", " ", CUE.sub("", re.sub(r"^- ", "", text.strip()))).strip()


def vtt_text(path):
    """Caption cues as running text, plus the number of speaker changes. No timestamps,
    no tags, no line repeated from the cue before."""
    lines, last, switches = [], "", 0
    for l in open(path, encoding="utf-8", errors="replace").read().splitlines():
        l = l.strip()
        if (not l or l.startswith(("WEBVTT", "Kind:", "Language:", "NOTE", "STYLE")) or "-->" in l
                or re.fullmatch(r"\d+", l)):
            continue
        l = re.sub(r"<[^>]+>", "", l).replace("&nbsp;", " ").replace("&amp;", "&")
        l = l.replace("&gt;", ">").replace("&lt;", "<").strip()
        if l and l != last:
            switches += bool(SWITCH.match(l))
            lines.append(l)
        last = l
    return tidy(" ".join(lines)), switches


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
    spoken = aimeter.spoken(text)  # a caption uploaded as an RTF file is not text: it ends as unpunctuated
    n = len(aimeter.PROFILES[aimeter.LANG]["word"].findall(aimeter.prose(spoken)))
    letters = [c for c in spoken if c.isalpha()]
    if n < LO:
        status = "short"
    elif n > HI:
        status = "long"
    elif switches > 5 or len(FILLER.findall(spoken)) > 2 * n / 1000:
        status = "unscripted"
    elif r"\rtf" in text or aimeter.measure(spoken) is None or sum(c.isupper() for c in letters) > 0.6 * len(letters):
        status = "unpunctuated"
    else:
        status = "kept"
    return date, "manual", n, status, spoken, title


rows = load()
streak = pauses = 0
for channel, handle in CHANNELS.items():
    mine = lambda: [r for k, r in rows.items() if k[0] == channel and r["id"] != "-"]
    try:
        todo = candidates(channel, handle)
    except Exception as e:
        print(f"{channel}: listing failed ({e})", file=sys.stderr)
        record(rows, channel, "-", status="error", title="channel listing failed")
        continue
    done = {r["id"] for r in mine() if r["status"] != "error"}
    kept = sum(r["status"] == "kept" for r in mine())
    examined = len(done)
    for vid, title in todo:
        if kept >= PER_CHANNEL or examined >= MAX_EXAMINED:
            break
        if vid in done:
            continue
        pause()
        work = os.path.join(out, ".work")
        try:
            date, track, n, status, text, title = examine(channel, vid, title, work)
            streak = 0
        except Exception as e:
            print(f"  {channel} {vid}: {e}", file=sys.stderr)
            if GONE.search(str(e)):  # members-only, private or removed: a fact about the video, not a refusal
                record(rows, channel, vid, status="unavailable", title=title)
                continue
            record(rows, channel, vid, status="error", title=title)
            streak += 1
            if streak >= 6:
                # YouTube answers "sign in to confirm you're not a bot" for a while: wait it out
                if "not a bot" in str(e) and pauses < 6:
                    pauses += 1
                    print(f"  blocked; waiting 20 minutes ({pauses}/6)", file=sys.stderr)
                    time.sleep(1200)
                    streak = 0
                else:
                    sys.exit("6 errors in a row: YouTube is refusing requests; run again later (resumable)")
            continue
        examined += 1
        if status == "kept":
            kept += 1
            open(os.path.join(out, f"{slug(channel)}-{vid}.md"), "w", encoding="utf-8",
                 newline="\n").write(text.strip() + "\n")
        record(rows, channel, vid, date, track, n, status, title)
    shutil.rmtree(os.path.join(out, ".work"), ignore_errors=True)
    print(f"{channel}: {kept} kept, {examined} examined", file=sys.stderr)

for f in glob.glob(os.path.join(out, "*.md")):  # texts kept by an earlier run get the same cleaning
    t = open(f, encoding="utf-8").read()
    clean = tidy(t) + "\n"
    if clean != t:
        open(f, "w", encoding="utf-8", newline="\n").write(clean)

with open(os.path.join(out, "titles.tsv"), "w", encoding="utf-8", newline="\n") as idx:
    for r in sorted(rows.values(), key=lambda r: slug(r["channel"]) + "-" + r["id"]):
        if r["status"] == "kept" and os.path.exists(os.path.join(out, f"{slug(r['channel'])}-{r['id']}.md")):
            idx.write(f"{slug(r['channel'])}-{r['id']}\t{r['words']}\t{r['title']}\n")
n = sum(r["status"] == "kept" for r in rows.values())
print(f"{lang} script corpus: {n} texts in {out}", file=sys.stderr)
PY
