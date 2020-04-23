#!/usr/bin/env python

import argparse


def main(args):
    cat = args.category  # category
    gene_file = args.infile
    sim_file = args.outfile
    pre_file = ""

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
            size = len(array)
            for i in range(2, size):
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

    gene = dict()
    lines = list()
    genes = list()
    genes2 = list()
    with open(gene_file, "r") as gene_file_fh:
        for line in gene_file_fh:
            line = line.rstrip()
            two = line.split(";")
            two[0] = two[0].strip()
            two[1] = two[1].strip()
            array = two[0].split(" ")
            brray = two[1].split(" ")
            genes.append(array[0])
            genes2.append(brray[0])

            for i, item in enumerate(array):
                array[i] = array[i][3:]
                if array[i] in father_dict:
                    if array[0] not in gene:
                        gene[array[0]] = dict()
                    gene[array[0]][array[i]] = 1  # unique GO terms
            if array[0] not in gene:
                lines.append(f"{line} {cat} NA")
                continue
            for j, item in enumerate(brray):
                brray[j] = brray[j][3:]
                if brray[j] in father_dict:
                    if brray[0] not in gene:
                        gene[brray[0]] = dict()
                    gene[brray[0]][brray[j]] = 1  # unique GO terms
            if brray[0] not in gene:
                lines.append(f"{line} {cat} NA")
                continue

            lines.append(line)

    simed = dict()
    simi = list()
    with open(sim_file, "w") as sim_file_fh:
        for i, item in enumerate(genes):
            gsim = ""
            up = 0
            down = 0
            max = dict()

            if lines[i].endswith(f"{cat} NA"):
                _ = sim_file_fh.write(f"{lines[i]}\n")
                continue
            for a in gene[genes[i]]:
                a = a[3:]
                Ta = own_set(a)
                for b in gene[genes2[i]]:
                    b = b[3:]
                    pair = f"{a}{b}"
                    riap = f"{b}{a}"
                    sim = 0
                    if pair in simed:
                        sim = simed[pair]
                    elif riap in simed:
                        sim = simed[riap]
                    else:
                        Tb = own_set(b)
                        sim = local_sesame(Ta, Tb)
                        simed[pair] = sim

                    if sim > max[a]:
                        max[a] = sim
                    if sim > max[b]:
                        max[b] = sim

            down = len(gene[genes[i]])  # was just "keys" in perl
            down += len(gene[genes2[i]])

            for key in gene[genes[i]]:
                key = key[3:]
                up += max[key]

            for key in gene[genes2[i]]:
                key = key[3:]
                up += max[key]

            if down == 0:
                gsim = 0
            else:
                gsim = up / down

            _ = sim_file_fh.write(f"{lines[i]} {cat} {gsim}\n")
            simi.append(gsim)

    with open(pre_file, "w") as pre_file_fh:
        sort = sorted(simi)
        index = len(simi) / 2
        t = 0
        if index == int(index):
            t = (sort[index - 1] + sort[index]) / 2
        else:
            t = sort[index]

        for i, term in enumerate(genes):
            _ = pre_file_fh.write(f"{t}\n")


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
