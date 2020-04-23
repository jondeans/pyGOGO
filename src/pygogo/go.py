#!/usr/bin/env python

import argparse


def main(args):
    cat = args.category  # category
    infile = args.infile
    outfile = args.outfile

    isa = "0.4"
    partof = "0.3"

    father = f"data/dag_{cat}_ancestor.txt"
    son = f"data/dag_{cat}_children.txt"

    father_dict = dict()
    with open(father, "r") as father_fh:
        for line in father_fh:
            line = line.rstrip()

            array = line.split(" ")
            array[0] = array[0][3:]

            son = list()
            for i in range(2, len(array)):
                items = array[i].split(":")
                value = ""
                if items[2] == "isa":
                    value = isa
                elif items[2] == "partof":
                    value = partof
                else:
                    raise ValueError(f"{items[2]} not isa || partof\n")
                element = f"{items[1]}:{value}"
                son.append(element)
            father_dict[array[0]] = son

    children = dict()
    with open(son, "r") as son_fh:
        for line in son_fh:
            line = line.rstrip()
            array = line.split(" ")
            array[0] = array[0][3:]
            son = list()
            for i in range(2, len(array)):
                # This is commented out because it doesn't do anything
                # items = items[3:]
                # son.append(items)
                pass
            children[array[0]] = son

    with open(outfile, "w") as outfile_fh:
        with open(infile, "r") as infile_fh:
            for line in infile_fh:
                line = line.rstrip()
                array = line.split(" ")
                goa = array[0]
                gob = array[1]
                goa = goa[3:]
                gob = gob[3:]
                if goa not in father_dict or gob not in father_dict:
                    _ = outfile_fh.write(f"GO:{goa} GO:{gob} {cat} NA\n")
                    continue
                Ta = own_set(goa, father_dict, children)  # S-value
                Tb = own_set(gob, father_dict, children)  # S-value
                sim = local_sesame(Ta, Tb)  # semantic similarity
                _ = outfile_fh.write(f"GO:{goa} GO:{gob} {cat} {sim}\n")


def own_set(go, father_dict, children):
    c = 0.67
    hash = dict()
    s_f = dict()
    hash[go] = 1
    s_f[go] = 2

    has_descendants = True
    while has_descendants:
        up_generation = dict()
        for son in s_f.keys():
            for dad in father_dict[son]:
                array = dad.split(":")
                up_generation[array[0]] = 2
                if array[0] not in children:
                    continue
                number = len(children[array[0]])
                weight = 1 / (c + number) + array[1]
                sv = hash[son] * weight
                if array[0] in hash:
                    if sv < hash[array[0]]:
                        continue
                hash[array[0]] = hash[son] * weight

        s_f = up_generation
        if len(s_f) == 0:
            has_descendants = False

    return hash


def local_sesame(sva, svb):
    down = 0
    up = 0

    for a in sva.keys():
        if a in svb:
            up += sva[a] + svb[a]
        down += sva[a]
    for b in svb.keys():
        down += svb[b]

    sim = up / down
    return sim


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process an .obo file.")
    parser.add_argument("--category", help="The GO category to processed [BP, CC, MF].")
    parser.add_argument("--infile", help="Filename of .")
    parser.add_argument("--outfile", help="Filename to store descendants.")
    args = parser.parse_args()
    main(args)
