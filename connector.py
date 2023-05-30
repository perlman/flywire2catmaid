import argparse
import os

import navis
import pymaid
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

    data = pandas.read_csv(filename, header=None,
                           names=colnames,
                           usecols=usecols
                           )
    
    return data




def main():
    parser = argparse.ArgumentParser()
    # parser.add_argument("--token")
    parser.add_argument("--project_id", type=int, required=True)
    parser.add_argument("connectorfile", help="CSV file with synapses")
    parser.add_argument("--rootmap", help="TSV file mapping root_id to skeleton_id")
    args = parser.parse_args()

    if args.rootmap:
        for line in open(args.rootmap, "r"):
            line = line.strip().split()
            # print(line)
            rootmap[int(line[0])] = int(line[1])

    #data = get_connectors(args.connectorfile)
    data = get_clean_connectors(args.connectorfile)
    for index, row in data.iterrows():
        # print(row)
        pre_skel = rootmap.get(row["pre_pt_root_id"], None)
        post_skel = rootmap.get(row["post_pt_root_id"], None)

        if pre_skel is None or post_skel is None:
            # TODO: Lookup and cache missing skeletons 
            print("Skipping %s->%s (id %d)" % (row["pre_pt_root_id"], row["post_pt_root_id"], row["id"]))
        else:
            print("NOT skipping %s->%s (id %d)" % (row["pre_pt_root_id"], row["post_pt_root_id"], row["id"]))

        # print(pre_skel, post_skel)

        pre_node = pymaid.get_nearest_node(x=row["pre_pt_position_x"], y=row["pre_pt_position_y"], z=row["pre_pt_position_z"],
                                           skeleton_id=pre_skel)
        post_node = pymaid.get_nearest_node(x=row["post_pt_position_x"], y=row["post_pt_position_y"], z=row["post_pt_position_z"],
                                           skeleton_id=post_skel)
        if "treenode_id" in pre_node and "treenode_id" in post_node:
            pre_node = pre_node["treenode_id"]
            post_node = post_node["treenode_id"]
        else:
            print("Skipping %s->%s (id %d): no treenode_ids found" % (row["pre_pt_root_id"], row["post_pt_root_id"], row["id"]))
            continue

        # Use the center point for the connector
        connector_x = (row["pre_pt_position_x"] + row["post_pt_position_x"]) / 2.0
        connector_y = (row["pre_pt_position_y"] + row["post_pt_position_y"]) / 2.0
        connector_z = (row["pre_pt_position_z"] + row["post_pt_position_z"]) / 2.0

        connector_id = pymaid.add_connector(coords=[connector_x, connector_y, connector_z], check_existing=True)[0]["connector_id"]

        try:
            new_connectors = pymaid.link_connector(
                [(pre_node, connector_id, 'presynaptic_to'),
                (post_node, connector_id, 'postsynaptic_to')]
            )
        except requests.exceptions.RequestException as err:
            print("Could not link connector %d [%s]" % (row["id"], type(err)))

        if index % 500 == 0:
            print(f'Processing connector {index}...')

if __name__ == "__main__":
    main()
