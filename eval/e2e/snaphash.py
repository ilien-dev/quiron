#!/usr/bin/env python3
"""snaphash.py SNAP [SNAP ...] : the first 8 hex of a sha256 over a snapshot's files.

The hash covers every file's path under snaps/SNAP and its bytes, with CRLF read as LF, in sorted
order, the way the results files name a snapshot ("ship (df3f6914)"). Two snapshots with the same
hash hold the same skill, whatever their names.
"""
import hashlib, os, sys

H = os.environ.get("QUIRON_E2E", os.path.expanduser("~/.cache/quiron-e2e"))


def snaphash(name):
    top = os.path.join(H, "snaps", name)
    h = hashlib.sha256()
    for root, dirs, files in sorted(os.walk(top)):
        dirs.sort()
        for f in sorted(files):
            p = os.path.join(root, f)
            h.update(os.path.relpath(p, top).replace(os.sep, "/").encode())
            with open(p, "rb") as fh:
                h.update(fh.read().replace(b"\r\n", b"\n"))
    return h.hexdigest()[:8]


if __name__ == "__main__":
    for n in sys.argv[1:]:
        print(n, snaphash(n))
