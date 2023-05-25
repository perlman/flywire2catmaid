# Import annotations
# Designed to import the data from "flywire_resource_data_files/630"
# https://drive.google.com/drive/folders/1jvYLNVbLBzccxUbDKFtKzgMdW53kiSOz

import argparse
import pandas
import os

def cell_sub_class_anno(rootmap, datapath):
    path = os.path.join(datapath, "cell_annotations", "cell_sub_class_anno_630.feather")
    data = pandas.read_feather(path)
    for index, row in data.iterrows():
        skel_id = rootmap[row["root_id"]]
        anno = "cell_sub_class:%s" % row["cell_sub_class"]
        print(anno)

def cell_type_anno(rootmap, datapath):
    path = os.path.join(datapath, "cell_annotations", "cell_type_anno_630.feather")
    data = pandas.read_feather(path)
    for index, row in data.iterrows():
        skel_id = rootmap[row["root_id"]]
        anno = "cell_type:%s" % row["cell_type"]
        print(anno)


def nerve_anno(rootmap, datapath):
    path = os.path.join(datapath, "cell_annotations", "nerve_anno_630.feather")
    data = pandas.read_feather(path)
    for index, row in data.iterrows():
        skel_id = rootmap[row["root_id"]]
        anno = "nerve:%s" % row["nerve"]

def coarse_anno(rootmap, datapath):
    path = os.path.join(datapath, "cell_annotations", "coarse_anno_630.feather")
    data = pandas.read_feather(path)
    for index, row in data.iterrows():
        skel_id = rootmap[row["root_id"]]
        flow = row["flow"]
        super_class = row["super_class"]
        cell_class = row["cell_class"]

def side_anno_inverted(rootmap, datapath):
    path = os.path.join(datapath, "cell_annotations", "side_anno_inverted_630.feather")
    data = pandas.read_feather(path)
    for index, row in data.iterrows():
        skel_id = rootmap[row["root_id"]]
        anno = "side:%s" % (row["side"])
        print(anno)


def hemibrain_anno(rootmap, datapath):
    path = os.path.join(datapath, "cell_annotations", "hemibrain_anno_630.feather")
    data = pandas.read_feather(path)
    for index, row in data.iterrows():
        skel_id = rootmap[row["root_id"]]
        if row["hemibrain_match"] is not None:
            anno = "hemibrain_match:%s" % row["hemibrain_match"]
            print(anno)
        if row["hemibrain_type"] is not None:
            anno = "hemibrain_type:%s" % row["hemibrain_type"]
            print(anno)


def hemilineage(rootmap, datapath):
    # ito_lee_hemilineage hemilineages
    path = os.path.join(datapath, "cell_annotations", "hemilineage_anno_630.feather")
    data = pandas.read_feather(path)
    for index, row in data.iterrows():
        if row["ito_lee_hemilineage"] is not None:
            skel_id = rootmap[row["root_id"]]
            for tag in row["ito_lee_hemilineage"].split('&'):
                anno = "ito_lee_hemilineage:%s" % tag
                print(skel_id, anno)


def cell_identification(rootmap, datapath):
    # Cell identification table
    # `tag` are freeform...
    # TODO: Actually figure this out
    path = os.path.join(datapath, "cell_identification", "neuron_information_v2_630.feather")
    data = pandas.read_feather(path)
    print(data)
    for index, row in data.iterrows():
        # row["pt_root_id"]
        print(row["tag"])
        pass

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--datapath", default=".", type=str)
    parser.add_argument("--rootmap", type=str, required=True, help="TSV file mapping root_id to skeleton_id")
    args = parser.parse_args()

    rootmap = {}
    if args.rootmap:
        for line in open(args.rootmap, "r"):
            line = line.strip().split(',')
            rootmap[int(line[0])] = int(line[1])

    #cell_type_anno(rootmap=rootmap, datapath=args.datapath)
    #cell_sub_class_anno(rootmap=rootmap, datapath=args.datapath)  
    #nerve_anno(rootmap=rootmap, datapath=args.datapath)  
    #hemibrain_anno(rootmap=rootmap, datapath=args.datapath)  
    #coarse_anno(rootmap=rootmap, datapath=args.datapath)  
    #side_anno_inverted(rootmap=rootmap, datapath=args.datapath)
    #hemilineage(rootmap=rootmap, datapath=args.datapath)
    #cell_identification(rootmap=rootmap, datapath=args.datapath)

if __name__ == "__main__":
    main()