#!/usr/bin/env python

import argparse
import os


def main(args):
    infile = args.infile
    outfile = args.outfile

    outbpo = outfile + "bpo"
    outcco = outfile + "cco"
    outmfo = outfile + "mfo"

    os.system(f"python go.pl BPO {infile} {outbpo}")
    os.system(f"python go.pl CCO {infile} {outcco}")
    os.system(f"python go.pl MFO {infile} {outmfo}")

    pairs = dict()
    count = 0
    bpo = dict()
    with open(outbpo, "r") as outbpo_fh:
        for line in outbpo_fh:
            line = line.rstrip()
            count += 1
            array = line.split(" ")
            bpo[f"{array[0]} {array[1]}"] = array[3]
            pairs[f"{array[0]} {array[1]}"] = count

    cco = dict()
    with open(outcco, "r") as outcco_fh:
        for line in outcco_fh:
            line = line.rstrip()
            array = line.split(" ")
            cco[f"{array[0]} {array[1]}"] = array[3]

    mfo = dict()
    with open(outmfo, "r") as outmfo_fh:
        for line in outmfo_fh:
            line = line.rstrip()
            array = line.split(" ")
            mfo[f"{array[0]} {array[1]}"] = array[3]

    out = outfile
    with open(out, "w") as out_fh:
        for key in sorted(pairs.keys()):
            if bpo[key] != "NA":
                _ = out_fh.write(f"{key} BPO {bpo[key]}\n")
            elif cco[key] != "NA":
                _ = out_fh.write(f"{key} CCO {cco[key]}\n")
            elif mfo[key] != "NA":
                _ = out_fh.write(f"{key} MFO {mfo[key]}\n")
            else:
                _ = out_fh.write(f"{key} Error:not_in_the_same_ontology\n")

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
