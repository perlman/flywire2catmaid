import argparse

import navis
import pymaid
import os

from neuron import CompressedNeurons

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--token")
    parser.add_argument("--filename", default="/Users/eric/nobackup/fafb/526/l2_skeletons/m526_skeletons.zip")
    parser.add_argument("--import-session", default="import")
    parser.add_argument("--workfile", default="work.txt")
    parser.add_argument("--project_id", type=int, required=True)
    parser.add_argument("--rootid_meta_annotation", type=str, required=False, default=None, help="Meta annotation to use for root_id annotations")
    args = parser.parse_args()

    if args.token:
        token = args.token
    else:
        token = open("token.txt").read().strip()
    
    itanna = pymaid.CatmaidInstance(server='https://spaces.itanna.io', project_id=args.project_id, api_token=token, caching=False)


    # itanna = pymaid.CatmaidInstance(server='http://localhost:8080', project_id=64, api_token=token, caching=False)

    neurons = CompressedNeurons(args.filename)

    # Read workfile for list of processed neurons
    # Quick & dirty kludge
    processed = set()
    if os.path.exists(args.workfile):
        with open(args.workfile, 'r') as f:
            for line in f.readlines():
                line = line.split('\t')
                neuron_id = int(line[0])
                processed.add(neuron_id)

    # Now open again to append
    work_fd = open(args.workfile, 'a')


    for neuron in neurons.neuron_iter():
        # Skip if needed?
        if neuron.neuron_id in processed:
            print(f"Skipping {neuron.neuron_id}")
            continue


        # Add basic import annotations
        neuron.tree_neuron.annotations = []
        skel_id_anno = f'{neuron.neuron_id}'
        neuron.tree_neuron.annotations.append(skel_id_anno)




        r = pymaid.upload_neuron(neuron.tree_neuron, import_annotations=True, remote_instance=itanna)
        # print(neuron)

        if args.rootid_meta_annotation:
            # Add the meta annotation to this new annotation
            pymaid.add_meta_annotations(to_annotate=skel_id_anno, to_add=args.rootid_meta_annotation, remote_instance=itanna)

        work_fd.write("%d\t%s\n" % (neuron.neuron_id, r['skeleton_id']))
        work_fd.flush()

    work_fd.close()

if __name__ == "__main__":
    main()
