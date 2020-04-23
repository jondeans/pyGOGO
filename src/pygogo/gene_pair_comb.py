#!/usr/bin/env python

import argparse
import os


def main(args):
    infile = args.infile
    outfile = args.outfile

    outbpo = outfile + "bpo"
    outcco = outfile + "cco"
    outmfo = outfile + "mfo"

    os.system(f"python gene_pair.pl BPO {infile} {outbpo}")
    os.system(f"python gene_pair.pl CCO {infile} {outcco}")
    os.system(f"python gene_pair.pl MFO {infile} {outmfo}")

    pairs = dict()
    count = 0
    bpo = dict()
    with open(infile, "r") as infile_fh:
        for line in infile_fh:
            line = line.rstrip()
            count += 1
            pairs[count] = line

    count = 0
    with open(outbpo, "r") as outbpo_fh:
        for line in outbpo_fh:
            line = line.rstrip()
            count += 1
            array = line.split(" ")
            bpo[count] = f"{array[-2]} {array[-1]}"

    count = 0
    cco = dict()
    with open(outcco, "r") as outcco_fh:
        for line in outcco_fh:
            line = line.rstrip()
            count += 1
            array = line.split(" ")
            cco[count] = f"{array[-2]} {array[-1]}"

    count = 0
    mfo = dict()
    with open(outmfo, "r") as outmfo_fh:
        for line in outmfo_fh:
            line = line.rstrip()
            count += 1
            array = line.split(" ")
            mfo[count] = f"{array[-2]} {array[-1]}"

    count = 0
    out = outfile
    with open(out, "w") as out_fh:
        for key in sorted(pairs.keys()):
            _ = out_fh.write(f"{pairs[key]} {bpo[key]} {cco[key]} {mfo[key]}\n")

    # remove temporary files
    if os.path.exists(outbpo):
        os.remove(outbpo)
    if os.path.exists(outcco):
        os.remove(outcco)
    if os.path.exists(outmfo):
        os.remove(outmfo)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process an .obo file.")
    parser.add_argument("--category", help="The GO category to processed [BP, CC, MF].")
    parser.add_argument("--infile", help="Filename of .")
    parser.add_argument("--outfile", help="Filename to store descendants.")
    args = parser.parse_args()
    main(args)
