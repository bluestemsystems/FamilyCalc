#!/usr/bin/env python3
"""Pack a set of PNGs into a Windows .ico. Pure stdlib.
Usage: build_ico.py out.ico 16.png 32.png 48.png 64.png 128.png 256.png"""
import struct
import sys


def build_ico(out_path, png_paths):
    images = []
    for p in png_paths:
        with open(p, "rb") as f:
            data = f.read()
        # size derived from filename stem (e.g. 256.png -> 256)
        size = int(p.rsplit("/", 1)[-1].split(".")[0])
        images.append((size, data))
    n = len(images)
    out = struct.pack("<HHH", 0, 1, n)          # reserved, type=icon, count
    offset = 6 + 16 * n
    body = b""
    for size, data in images:
        dim = 0 if size >= 256 else size        # 0 means 256 in ICO
        out += struct.pack("<BBBBHHII", dim, dim, 0, 0, 1, 32, len(data), offset)
        offset += len(data)
        body += data
    with open(out_path, "wb") as f:
        f.write(out + body)


if __name__ == "__main__":
    build_ico(sys.argv[1], sys.argv[2:])
    print("wrote", sys.argv[1])
