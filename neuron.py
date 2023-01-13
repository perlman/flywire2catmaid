
import re
import io
from zipfile import ZipFile
import h5py
from dataclasses import dataclass
import json
import navis
import networkx as nx
import numpy as np

@dataclass
class FlywireNeuron:
    neuron_id: int
    tree_neuron: navis.TreeNeuron

class CompressedNeurons:
    """Read the hdf5+zip neuron skeletons from Sven."""
    def __init__(self, filename):
        self.filename = filename
    
    def neuron_iter(self):
        with ZipFile(self.filename, 'r') as myzip:
            for zipinfo in myzip.infolist():
                # m526_skeletons/720575940618769345.h5 -> 720575940618769345
                neuron_file_match = re.match('.*/([0-9]+)\.h5', zipinfo.filename)
                if not neuron_file_match:
                    continue
                neuron_id = int(neuron_file_match.group(1))
                
                h5stream = io.BytesIO(myzip.read(zipinfo))
                h5 = h5py.File(h5stream, 'r')

                # <HDF5 dataset "edges": shape (47, 2), type "<i8">
                # <HDF5 dataset "mesh_to_skel_map": shape (96,), type "<i8">
                # <HDF5 dataset "vertices": shape (48, 3), type "<f8">

                h5_metadata = json.loads(h5["meta"][()].decode("utf-8"))
                assert(neuron_id == h5_metadata["root_id"])

                h5_root = h5["root"][()]
                h5_edges = h5["edges"]
                h5_verts = h5["vertices"]

                # Turn into a TreeNeuron...
                # Currently slow cruddy using networkx.
                # TODO: Ask Philipp for a better route?

                G = nx.Graph()

                for node_id in np.unique(h5_edges):
                    G.add_node(node_id, x=h5_verts[node_id,0], y=h5_verts[node_id,1], z=h5_verts[node_id,2], radius=1.0)
                for edge in range(h5_edges.shape[0]):
                    G.add_edge(h5_edges[edge][0], h5_edges[edge][1])

                #tree_neuron = navis.TreeNeuron(G, units='1 nm')
                tree_neuron = navis.graph.nx2neuron(G, root=h5_root, break_cycles=True, units='1 nm', name=neuron_id)
                flywire_neuron = FlywireNeuron(neuron_id=neuron_id, tree_neuron=tree_neuron)

                yield flywire_neuron
