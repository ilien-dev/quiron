#!/usr/bin/env bash
# One iteration of the im-human loop: measure, audit, record, say whether it converged.
#
# Convergence is deliberately not "one clean run". A single pass can be clean
# because a check silently failed to fire, or because the last edit happened to
# land well. Two consecutive clean passes, with the judgement items ruled on in
# both, is the bar. Any FAIL resets the counter to zero.
#
#   check.sh FILE                       run an iteration
#   check.sh FILE --ruled "note"        same, and record that you read and ruled
#                                       on every READ item this pass
#   check.sh FILE --status              print the state without running
#   check.sh FILE --reset               start the count again
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
FILE="${1:?usage: check.sh FILE [--ruled \"note\"] [--status] [--reset]}"; shift || true
[ -f "$FILE" ] || { echo "no such file: $FILE"; exit 2; }
STATE="$(dirname "$FILE")/.$(basename "$FILE").im-human.json"

case "${1:-}" in
  --status) [ -f "$STATE" ] && cat "$STATE" || echo "no state yet"; exit 0 ;;
  --reset)  rm -f "$STATE"; echo "count reset"; exit 0 ;;
esac
RULED=""; [ "${1:-}" = "--ruled" ] && RULED="${2:-yes}"

echo "=== rates"
python3 "$HERE/aimeter.py" "$FILE" | sed -n '3,25p'
echo
echo "=== checklist"
python3 "$HERE/audit.py" --brief "$FILE"
FAILS=$?

python3 - "$STATE" "$FILE" "$FAILS" "$RULED" <<'PY'
import hashlib, json, os, sys
state_path, file_path, fails, ruled = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
digest = hashlib.sha256(open(file_path, "rb").read()).hexdigest()[:12]
st = json.load(open(state_path)) if os.path.exists(state_path) else {"clean_streak": 0, "runs": []}
clean = fails == 0
st["clean_streak"] = st["clean_streak"] + 1 if clean else 0
st["runs"].append({"sha": digest, "fails": fails, "ruled": ruled or None})
st["runs"] = st["runs"][-12:]
json.dump(st, open(state_path, "w"), indent=1)

recent = st["runs"][-2:]
ruled_twice = len(recent) == 2 and all(r["ruled"] for r in recent)
changed = len({r["sha"] for r in recent}) > 1 if len(recent) == 2 else True

print()
if not clean:
    print(f"NOT CONVERGED: {fails} fail(s) above. Fix them and run again. Streak reset to 0.")
elif st["clean_streak"] < 2:
    print(f"CLEAN PASS {st['clean_streak']} of 2. Rule on every READ item, then run again"
          f"{' with --ruled' if not ruled else ''}. One clean pass is not convergence.")
elif not ruled_twice:
    print(f"CLEAN PASS {st['clean_streak']}, but the READ items were not recorded as ruled on "
          f"in both passes. Re-run with --ruled \"what you decided\".")
else:
    print(f"CONVERGED after {len(st['runs'])} run(s): {st['clean_streak']} consecutive clean "
          f"passes, judgement items ruled on in both"
          f"{', text unchanged between them' if not changed else ''}.")
print(f"state: {state_path}")
PY
