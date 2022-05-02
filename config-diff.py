#!/usr/bin/env python3

import argparse
from typing import Tuple


def isSimple(value: str) -> bool:
    return (value == 'y' or value == 'm')


def parseFile(filename: str, freeform: bool) -> Tuple[dict, dict]:
    simple = {}
    comp = {}
    with open(filename, mode="r") as f:
        for line in f:
            line = line.strip()

            if line and not line.startswith("#"):
                kv = line.split('=')
                if isSimple(kv[1]):
                    simple[kv[0]] = kv[1]
                elif freeform:
                    comp[kv[0]] = kv[1]

    return simple, comp


parser = argparse.ArgumentParser(description="""\
    Compare downstream Linux kernel config with one or two upstream configs, \
    pointing out differences.""")
parser.add_argument("downstream", help="Downstream config to compare")
parser.add_argument("upstream", help="Upstream config to compare")
parser.add_argument("upstream2", nargs='?', default="", help="""\
    Additional upstream config to compare.  Shows differences between \
    downstream and the intersection of the two upstream configurations.""")
parser.add_argument("--freeform", action="store_true", help="""\
    Include options with values other than y or m.  Shows keys that downstream\
    is missing that exist in either upstream config as well as keys that exist\
    but have a different value than at least one of the upstream configs.""")
args = parser.parse_args()


downstream, dcomp = parseFile(args.downstream, args.freeform)
upstream1, u1comp = parseFile(args.upstream, args.freeform)

if (args.upstream2):
    upstream2, u2comp = parseFile(args.upstream2, args.freeform)
    upstreams = (upstream1.keys() | set()).intersection(upstream2.keys())
else:
    upstreams = upstream1.keys() | set()

diff = upstreams - downstream.keys()

print("Missing simple keys:")
for option in sorted(diff):
    print(f"{option: <45} {upstream1[option]: <5} {upstream2[option]: <5}")

if args.freeform:
    uscomp = (u1comp.keys() | set()).intersection(u2comp.keys())
    diffcomp = uscomp - dcomp.keys()

    print("\nMissing freeform keys:")
    for option in sorted(diffcomp):
        print(f"{option: <45} {u1comp[option]: <5} {u2comp[option]: <5}")

    print("\nDiffering freeform keys:")
    for option in sorted(dcomp.keys()):
        u1val = ""
        if option in u1comp:
            u1val = u1comp[option]
        u2val = ""
        if option in u2comp:
            u2val = u2comp[option]
        dval = dcomp[option]
        if dval != u1val or dval != u2val:
            print(f"{option: <45} {dval: <5}: {u1val: <5} , {u2val: <5}")
