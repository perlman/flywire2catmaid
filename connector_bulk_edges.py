# Script to do create the connectors in bulk -- but don't link them in
# Each connector has a base unique ID

import argparse
import os

import navis
import pandas
import requests


def get_connectors(filename):
    # Use pandas to read connectors file
    colnames = ["id", "pre_pt_supervoxel_id", "pre_pt_root_id", "post_pt_supervoxel_id", "post_pt_root_id", "connection_score", "cleft_score",
                "gaba", "ach", "glut", "oct", "ser", "da",
                "compartment",
                "pre_pt_position_x", "pre_pt_position_y", "pre_pt_position_z",
                "post_pt_position_x", "post_pt_position_y", "post_pt_position_z"
                ]
    usecols = ["id", "pre_pt_supervoxel_id", "pre_pt_root_id", "post_pt_supervoxel_id", "post_pt_root_id",
                                    "pre_pt_position_x", "pre_pt_position_y", "pre_pt_position_z",
                                     "post_pt_position_x", "post_pt_position_y", "post_pt_position_z"]
    data = pandas.read_csv(filename, header=None,
                           names=colnames,
                           usecols=usecols
                           )
    
    return data

def get_clean_connectors(filename):
    # Use the cleaned up table
    colnames = ["id", "pre_pt_root_id", "post_pt_root_id", "pre_pt_position_x", "pre_pt_position_y", "pre_pt_position_z", "post_pt_position_x", "post_pt_position_y", "post_pt_position_z"]
    usecols = colnames
    data = pandas.read_csv(filename, header=None, names=colnames, usecols=usecols, sep='\t')

    return data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--user_id", type=int, required=True)
    parser.add_argument("--project_id", type=int, required=True)
    parser.add_argument("connectorfile", help="CSV file with synapses")
    parser.add_argument("--rootmap", help="TSV file mapping root_id to skeleton_id")
    parser.add_argument("--connector_edge_query_csv", default=None, help="Table to load into SQL for finding treenodes")
    #parser.add_argument("--base_id", default=400000000, type=int)
    parser.add_argument("--base_id", default=0, type=int)
    parser.add_argument("--temp_table_name", default="connector_treenode_lookup")
    args = parser.parse_args()

    # 

    rootmap = {}
    if args.rootmap:
        for line in open(args.rootmap, "r"):
            line = line.strip().split(',')
            rootmap[int(line[0])] = int(line[1])

    connector_file = open(args.connector_edge_query_csv, "w")

    #data = get_connectors(args.connectorfile)
    data = get_clean_connectors(args.connectorfile)
    for index, row in data.iterrows():
        # presynaptic_to has ID 20 and postsynaptic_to has ID 21. I just looked at the table relation: SELECT * FROM relation;
        pre_skel = rootmap.get(row["pre_pt_root_id"], None)
        post_skel = rootmap.get(row["post_pt_root_id"], None)
        # Check pre
        if pre_skel:
            query1 = (row["id"] + args.base_id, 20, pre_skel, row["post_pt_position_x"], row["pre_pt_position_y"], row["pre_pt_position_z"])
        else:
            # Not in set of imported skeletons
            query1 = None

        # Check post
        if post_skel:
            query2 = (row["id"] + args.base_id, 21, post_skel, row["post_pt_position_x"], row["post_pt_position_y"], row["post_pt_position_z"])
        else:
            # Not in set of imported skeletons
            query2 = None
        
        for data in [query1, query2]:
            if data is not None:
                connector_file.write(','.join(map(str, data)) + '\n')

    connector_file.close()
    print("SQL Command:")
    print(f"""
    CREATE TEMPORARY TABLE {args.temp_table_name} (
        id INT NOT NULL,
        relation INT NOT NULL,
        skeleton_id INT  NOT NULL,
        x real NOT NULL,
        y real NOT NULL,
        z real NOT NULL
);
    
        COPY {args.temp_table_name} (id, relation, skeleton_id, x, y, z) FROM '{args.connector_edge_query_csv}' WITH (FORMAT csv);

        """)
if __name__ == "__main__":
    main()
