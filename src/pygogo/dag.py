#!/usr/bin/env python

import argparse


def main(args):
    # go.obo /*download from http://purl.obolibrary.org/obo/go.obo*/ generate files of direct ancestor and children based on three categories
    obo = args.obo
    # for one category, the file containing each GO term and it's direct ancestor
    father = args.ancestor
    # for one category, the file containing each GO term and it's direct descendant
    son = args.descendant
    # the category of go ontology. Choosing from BPO, CCO and MFO
    go_ontology = args.category

    (body, cat, anc, son_dict, nspace) = ("", dict(), dict(), dict(), dict())

    nspace["BPO"] = "biological_process"
    nspace["CCO"] = "cellular_component"
    nspace["MFO"] = "molecular_function"

    with open(obo, "r") as obo_fh:
        for line in obo_fh:
            line = line.rstrip()
            items = line.split(" ")
            if items[0] == "id:":
                if items[1][0:3] == "GO:":
                    body = items[1]
            elif items[0] == "namespace:":
                if items[1] == nspace[go_ontology]:
                    cat[body] = ""
            elif items[0] == "is_obsolete:":
                if body in anc:
                    del anc[body]
                if body in cat:
                    del cat[body]
            elif items[0] == "is_a:":
                if items[1][0:3] == "GO:":
                    if body not in anc:
                        anc[body] = ""
                    anc[body] += f"{items[1]}:isa "
            elif items[0] == "relationship:":
                if items[1] == "part_of":
                    if body not in anc:
                        anc[body] = ""
                    anc[body] += f"{items[2]}:partof "

    i = 0
    with open(father, "w") as father_fh:
        for key in sorted(cat.keys()):
            if key not in anc:
                _ = father_fh.write(f"{key} {i} \n")
                i += 1
                ele = key[3:]
                if ele not in anc:
                    anc[ele] = ""
                continue

            _ = father_fh.write(f"{key} {i} {anc[key]}\n")
            i += 1
            items = anc[key].rstrip().split(" ")
            ele = key[3:]
            if ele not in anc:
                anc[ele] = ""
            for j, term in enumerate(items):
                combo = items[j].split(":")
                if "GO:" + combo[1] not in son_dict:
                    son_dict["GO:" + combo[1]] = ""
                son_dict["GO:" + combo[1]] += f"{key} "

    i = 0
    with open(son, "w") as son_fh:
        for key in sorted(cat.keys()):
            _ = son_fh.write(f"{key} {i} {son_dict.get(key, '')}\n")
            i += 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process an .obo file.")
    parser.add_argument("--obo", help="The obo file to be processed.")
    parser.add_argument("--ancestor", help="Filename to store ancestors.")
    parser.add_argument("--descendant", help="Filename to store descendants.")
    parser.add_argument("--category", help="The GO category to consider [BP, CC, MF].")
    args = parser.parse_args()
    main(args)
