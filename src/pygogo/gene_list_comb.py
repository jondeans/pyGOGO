#!/usr/bin/env python

import argparse
import os


def main(args):
    infile = args.infile
    outfile = args.outfile
    cluster = args.cluster

    cat = ["BPO", "CCO", "MFO"]

    for key in cat:
        sim = outfile + key + "sim"
        pre = outfile + key + "pre"
        cls = outfile + key + "cls"
        os.system(f"python gene_list.py {key} {infile} {sim} {pre}")
        if os.path.exists(pre):
            os.system(f"apcluster {sim} {pre} {cls}")

        lists = dict()
        names = dict()
        count = 0
        with open(infile, "r") as infile_fh:
            for line in infile_fh:
                line = line.rstrip()
                count += 1
                array = line.split(" ")
                lists[count] = line
                names[count] = array[0]

        simout = dict()
        for key in cat:
            count = 0
            sim = outfile + key + "sim"
            cls = outfile + key + "cls"
            with open(sim, "r") as sim_fh:
                for line in sim_fh:
                    line = line.rstrip()
                    count += 1
                    array = line.split(" ")
                    if key == "BPO":
                        simout[
                            count
                        ] = f"{names[array[0]]} {names[array[1]]} {key} {array[-1]}"
                    else:
                        simout[count] += f" {key} {array[-1]}"

        with open(outfile, "w") as outfile_fh:
            for key in sorted(simout):
                _ = outfile_fh.write(f"{simout[key]}\n")

        with open(cluster, "w") as cluster_fh:
            for key in cat:
                sim = outfile + key + "sim"
                pre = outfile + key + "pre"
                cls = outfile + key + "cls"
                count = 0
                _class = dict()

                if os.path.exists(pre):
                    _ = cluster_fh.write(f"{key}:\n")

                    with open(cls, "r") as fl_fh:
                        for line in fl_fh:
                            line = line.rstrip()
                            count += 1
                            if line == count:
                                if names[line] not in _class:
                                    _class[names[line]] = ""
                            else:
                                _class[names[line]] += f" {names[count]}"

                    for ele in _class.keys():
                        _ = cluster_fh.write(f"{ele}{_class[ele]}\n")

        for key in cat:
            sim = outfile + key + "sim"
            pre = outfile + key + "pre"
            cls = outfile + key + "cls"

            if os.path.exists(sim):
                os.remove(sim)
            if os.path.exists(pre):
                os.remove(pre)
            if os.path.exists(cls):
                os.remove(cls)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process an .obo file.")
    parser.add_argument("--category", help="The GO category to processed [BP, CC, MF].")
    parser.add_argument("--infile", help="Filename of .")
    parser.add_argument("--outfile", help="Filename to store descendants.")
    parser.add_argument("--cluster", help="Filename to store clusters.")
    args = parser.parse_args()
    main(args)
