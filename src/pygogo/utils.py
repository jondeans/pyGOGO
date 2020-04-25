"""Generic utils for reading and handling GO datasets."""

import networkx as nx
import pandas as pd


def read_obo(obo_file, category_filter=["BP", "MF", "CC"]):
    single_value_keys = ["name", "namespace", "is_obsolete", "replaced_by"]
    multi_value_keys = ["alt_id", "is_a", "consider", "relationship", "intersection_of"]
    namespace_dict = {
        "biological_process": "BP",
        "molecular_function": "MF",
        "cellular_component": "CC",
    }

    if isinstance(category_filter, str):
        category_filter = [category_filter]

    with open(obo_file, "r") as f:
        goterm = dict()
        goterm_list = list()

        curr_typedef = None
        for line in f:
            line = line.rstrip("\n\r")

            key, value = (None, None)
            if ":" in line:
                key, value = line.split(": ", 1)

            # Get the current typedef
            if line.startswith("["):
                curr_typedef = line.strip("[]").lower()

            # Grab relevant data for any typedef.
            elif key == "id":
                goterm["go_id"] = value
            elif key in single_value_keys:
                goterm[key] = value
            elif key in multi_value_keys:
                if key not in goterm:
                    goterm[key] = list()
                goterm[key].append(value)
            # Blank lines signify end of record. If record is [Term], then keep it.
            elif line == "":
                if goterm and curr_typedef == "term" and not goterm.get("is_obsolete"):
                    goterm_list.append(goterm)
                goterm = dict()
                curr_typedef = None

        df = pd.DataFrame(goterm_list)
        df["namespace"] = df["namespace"].replace(namespace_dict)
        df = df.query("namespace.isin(@category_filter)")
        return df


def dataframe_to_dag(df):

    # Get all "is_a" edges
    is_a_df = df.copy()
    is_a_df = is_a_df[["go_id", "is_a"]]

    is_a_df = is_a_df.explode("is_a")
    is_a_df["is_a"] = is_a_df["is_a"].str.replace(r" \! .*?$", r"")
    is_a_df.columns = ["head", "tail"]
    is_a_df["edge_type"] = "is_a"
    is_a_df["weight"] = 0.4
    is_a_df = is_a_df.reset_index(drop=True)

    # Get all "part_of" edges
    relationship_df = df.copy()
    relationship_df = relationship_df[["go_id", "relationship"]]

    relationship_df = relationship_df.dropna()
    relationship_df = relationship_df.explode("relationship")
    relationship_df["relationship"] = relationship_df["relationship"].str.replace(
        r" \! .*?$", r""
    )
    relationship_df[["edge_type", "tail"]] = relationship_df["relationship"].str.split(
        expand=True
    )
    relationship_df = relationship_df.drop(columns=["relationship"])
    relationship_df = relationship_df.rename(columns={"go_id": "head"})
    relationship_df["weight"] = 0.3
    relationship_df = relationship_df.query("edge_type == 'part_of'")
    relationship_df = relationship_df.reset_index(drop=True)

    edgelist_df = is_a_df.copy()
    edgelist_df = edgelist_df.append(relationship_df, ignore_index=True)

    # Drop top-level edges with no tail. (this is a parsing error).
    edgelist_df = edgelist_df.dropna(subset=["tail"])

    dag = nx.from_pandas_edgelist(
        edgelist_df, "head", "tail", edge_attr=True, create_using=nx.DiGraph
    )
    return dag


def get_primary_ancestors(graph, node):
    return [f"{n}:{graph[node][n]['edge_type'].replace('_', '')}" for n in graph[node]]


def save_primary_ancestors(graph, output_file):
    with open(output_file, "w") as output_fh:
        for i, node in enumerate(sorted(list(graph.nodes()))):
            primary_ancestors = " ".join(
                [
                    f"{n}:{graph[node][n]['edge_type'].replace('_', '')}"
                    for n in graph[node]
                ]
            )
            _ = output_fh.write(f"{node} {i} {primary_ancestors}\n")


def get_primary_descendants(graph, node):
    return [d for d in sorted(graph.predecessors(node))]


def save_primary_descendants(graph, output_file):
    with open(output_file, "w") as output_fh:
        for i, node in enumerate(sorted(list(graph.nodes()))):
            primary_descendants = graph.predecessors(node)
            _ = output_fh.write(
                f"{node} {i} {' '.join([d for d in sorted(primary_descendants)])}\n"
            )
