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




def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--user_id", type=int, required=True)
    parser.add_argument("--project_id", type=int, required=True)
    parser.add_argument("connectorfile", help="CSV file with synapses")
    parser.add_argument("--rootmap", help="TSV file mapping root_id to skeleton_id")
    parser.add_argument("--connector_csv", default=None, help="CSV file with connectors for incertion into catmaid")
    parser.add_argument("--base_id", default=400000000, type=int)
    args = parser.parse_args()


    rootmap = {}
    if args.rootmap:
        for line in open(args.rootmap, "r"):
            line = line.strip().split()
            rootmap[int(line[0])] = int(line[1])

    connector_file = open(args.connector_csv, "w")

    data = get_connectors(args.connectorfile)
    for index, row in data.iterrows():
        # Use the center point for the connector

        connector_id = args.base_id + row["id"]
        connector_x = (row["pre_pt_position_x"] + row["post_pt_position_x"]) / 2.0
        connector_y = (row["pre_pt_position_y"] + row["post_pt_position_y"]) / 2.0
        connector_z = (row["pre_pt_position_z"] + row["post_pt_position_z"]) / 2.0

        connector_file.write("%d,%d,%d,%d,%d,%d\n" % (
                             connector_id, args.project_id, connector_x, connector_y, connector_z,
                             args.user_id,
                             ))

    connector_file.close()

    print("SQL Command:")
    print("COPY connector (id, project_id, location_x, location_y, location_z, user_id) FROM '%s WITH (FORMAT csv);" % args.connector_csv)


if __name__ == "__main__":
    main()
