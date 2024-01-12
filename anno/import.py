# Import annotations
# Designed to import the data from "flywire_resource_data_files/630"
# https://drive.google.com/drive/folders/1jvYLNVbLBzccxUbDKFtKzgMdW53kiSOz

import argparse
import pandas
import os
import httpx

def post_annotation(session, entity, anno, dryrun=False):
    project_id = 1
    add_anno_url = f"https://m783.fafb-flywire.catmaid.org/{project_id}/annotations/add"

    postdata = {
        'entity_ids[0]': entity,
        'annotations[0]': anno
    }

    try:
        if dryrun:
            print("add: ", postdata)
        else:
            session.post(add_anno_url, data=postdata)
    except:
        raise


def delete_annotation(session, entity, anno, dryrun=False):
    project_id = 1
    add_anno_url = f"https://m783.fafb-flywire.catmaid.org/{project_id}/annotations/remove"

    postdata = {
        'entity_ids[0]': entity,
        'annotations[0]': anno
    }

    try:
        if dryrun:
            print("remove: ", postdata)
        else:
            session.post(add_anno_url, data=postdata)
    except:
        raise

def cell_sub_class_anno(rootmap, datapath):
    annos = []
    path = os.path.join(datapath, "cell_annotations", "cell_sub_class_anno_630.feather")
    data = pandas.read_feather(path)
    for index, row in data.iterrows():
        skel_id = rootmap.get(row["root_id"], None)
        if skel_id is None:
            continue
        anno = "cell_sub_class:%s" % row["cell_sub_class"]
        annos.append((skel_id, anno))
    return annos

def cell_type_anno(rootmap, datapath):
    annos = []
    path = os.path.join(datapath, "cell_annotations", "cell_type_anno_630.feather")
    data = pandas.read_feather(path)
    for index, row in data.iterrows():
        skel_id = rootmap.get(row["root_id"], None)
        if skel_id is None:
            continue
        anno = "cell_type:%s" % row["cell_type"]
        annos.append((skel_id, anno))
    return annos


def nerve_anno(rootmap, datapath):
    annos = []
    path = os.path.join(datapath, "cell_annotations", "nerve_anno_630.feather")
    data = pandas.read_feather(path)
    for index, row in data.iterrows():
        skel_id = rootmap.get(row["root_id"], None)
        if skel_id is None:
            continue
        anno = "nerve:%s" % row["nerve"]
        annos.append((skel_id, anno))
    return annos

def coarse_anno(rootmap, datapath):
    annos = []
    path = os.path.join(datapath, "cell_annotations", "coarse_anno_630.feather")
    data = pandas.read_feather(path)
    for index, row in data.iterrows():
        skel_id = rootmap.get(row["root_id"], None)
        if skel_id is None:
            continue
        skel_id = rootmap[row["root_id"]]
        flow = "coarse:flow:%s" % row["flow"]
        super_class = "coarse:super_class:%s" % row["super_class"]
        cell_class = "coarse:cell_class:%s" % row["cell_class"]
        for anno in [flow, super_class, cell_class]:
            annos.append((skel_id, anno))
    return annos

def side_anno_inverted(rootmap, datapath):
    annos = []
    path = os.path.join(datapath, "cell_annotations", "side_anno_inverted_630.feather")
    data = pandas.read_feather(path)
    for index, row in data.iterrows():
        skel_id = rootmap.get(row["root_id"], None)
        if skel_id is None:
            continue
        if row["side"] is None:
            continue
        anno = "side:%s" % (row["side"])
        annos.append((skel_id, anno))
    return annos

def hemibrain_anno(rootmap, datapath):
    annos = []
    path = os.path.join(datapath, "cell_annotations", "hemibrain_anno_630.feather")
    data = pandas.read_feather(path)
    for index, row in data.iterrows():
        skel_id = rootmap.get(row["root_id"], None)
        if skel_id is None:
            continue
        #if row["hemibrain_match"] is not None:
        #    anno = "hemibrain_match:%s" % row["hemibrain_match"]
        #    annos.append((skel_id, anno))
        if row["hemibrain_type"] is not None:
            for tag in row["hemibrain_type"].split(','):
                anno = "hemibrain_type:%s" % tag
                annos.append((skel_id, anno))
    return annos


def hemilineage(rootmap, datapath):
    # ito_lee_hemilineage hemilineages
    annos = []
    path = os.path.join(datapath, "cell_annotations", "hemilineage_anno_630.feather")
    data = pandas.read_feather(path)
    for index, row in data.iterrows():
        if row["ito_lee_hemilineage"] is not None:
            skel_id = rootmap.get(row["root_id"], None)
            if skel_id is None:
                continue
            for tag in row["ito_lee_hemilineage"].split('&'):
                anno = "ito_lee_hemilineage:%s" % tag
                annos.append((skel_id, anno))
    return annos


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
    
    raise Exception("TODO: Figure out format for these")
    return annos


def flywire_supplemental(rootmap, srcpath, datapath):
    # supervoxel_id   root_id pos_x   pos_y   pos_z   soma_x  soma_y  soma_z  nucleus_id
    # flow    super_class     cell_class      cell_sub_class
    # cell_type       hemibrain_type  ito_lee_hemilineage     hartenstein_hemilineage morphology_group
    # top_nt  top_nt_conf     side nerve    vfb_id  fbbt_id status

    x = set()
    annos = []
    for filename in ["Supplemental_file1_neuron_annotations.tsv", "Supplemental_file2_non_neuron_annotations.tsv"]:
        srcfile = os.path.join(srcpath, filename)
        annot = pandas.read_csv(srcfile, sep="\t", low_memory=False)


        for index, row in annot.iterrows():
            #print(row)
            skel_id = rootmap.get(row["root_id"], None)
            if skel_id is None:
                continue

            ito_lee_hemilineage = row["ito_lee_hemilineage"]
            if isinstance(ito_lee_hemilineage, str):  # instead of np.nan
                for tag in ito_lee_hemilineage.split('&'):
                    anno = "ito_lee_hemilineage:%s" % tag
                    annos.append((skel_id, anno))

            hemibrain_type = row["hemibrain_type"]
            if isinstance(hemibrain_type, str): # instead of np.nan
                for tag in hemibrain_type.split(','):
                    anno = "hemibrain_type:%s" % tag
                    annos.append((skel_id, anno))

            morphology_group = row["morphology_group"]
            if isinstance(morphology_group, str):  # instead of np.nan
                for tag in morphology_group.split('&'):
                    anno = "morphology_group:%s" % tag
                    annos.append((skel_id, anno))


            cell_type = row["cell_type"]
            if isinstance(cell_type, str):  # instead of np.nan
                for tag in cell_type.split('&'):
                    anno = "cell_type:%s" % tag
                    annos.append((skel_id, anno))



            for flat_field in ["flow", "cell_class", "cell_sub_class", "hartenstein_hemilineage",
                    "vfb_id", "fbbt_id", "side"]:
                field_value = row[flat_field]
                if isinstance(field_value, str):
                    anno = "%s:%s" % (flat_field, field_value)
                annos.append((skel_id, anno))

    return annos


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--datapath", default=".", type=str)
    parser.add_argument("--rootmap", type=str, required=True, help="TSV file mapping root_id to skeleton_id")
    parser.add_argument("--token", type=str, help="CATMAID API token")
    parser.add_argument("--dry-run", default=False, action="store_true")
    parser.add_argument("--delete", default=False, action="store_true", help="Delete annotations instead of create")
    parser.add_argument("--anno-src-dir", default=".", help="Path to flywire annotation TSV files")
    args = parser.parse_args()

    if args.token:
        if os.path.exists(args.token):
            # Token is a file
            with open(args.token) as f:
                token = f.read().strip()
        else:
            # Use passed token
            token = args.token
    else:
        raise Exception("Token not specified")


    rootmap = {}
    if args.rootmap:
        for line in open(args.rootmap, "r"):
            line = line.strip().split(',')
            rootmap[int(line[0])] = int(line[1]) + 1   # +1 to go from skeleton to neuron ID

    headers = {'X-Authorization' : 'Token ' + token}
    session = httpx.Client(headers=headers) 

    # new
    annos = flywire_supplemental(rootmap=rootmap, srcpath=args.anno_src_dir, datapath=args.datapath)


    # old
    #annos = hemilineage(rootmap=rootmap, datapath=args.datapath)
    #annos = side_anno_inverted(rootmap=rootmap, datapath=args.datapath)
    #annos = hemibrain_anno(rootmap=rootmap, datapath=args.datapath)  
    #annos = nerve_anno(rootmap=rootmap, datapath=args.datapath)  
    #annos = cell_type_anno(rootmap=rootmap, datapath=args.datapath)
    #annos = cell_sub_class_anno(rootmap=rootmap, datapath=args.datapath)
    #annos = coarse_anno(rootmap=rootmap, datapath=args.datapath)  
    #annos = coarse_anno(rootmap=rootmap, datapath=args.datapath)  
    #annos = hemilineage(rootmap=rootmap, datapath=args.datapath)
    #annos = cell_sub_class_anno(rootmap=rootmap, datapath=args.datapath)  
    #annos = hemibrain_anno(rootmap=rootmap, datapath=args.datapath)  
    #annos = cell_type_anno(rootmap=rootmap, datapath=args.datapath)
    # TODO
    #cell_identification(rootmap=rootmap, datapath=args.datapath)



    count = 0
    for (entity_id, anno) in annos:
        if args.delete:
            delete_annotation(session, entity_id, anno, dryrun=args.dry_run)
        else:
            post_annotation(session, entity_id, anno, dryrun=args.dry_run)

        count = count + 1
        if count % 5000 == 0:
            print(count)

if __name__ == "__main__":
    main()
