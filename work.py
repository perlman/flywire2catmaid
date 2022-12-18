import argparse

from neuron import CompressedNeurons

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--filename", default="/Users/eric/nobackup/fafb/526/l2_skeletons/m526_skeletons.zip")
    args = parser.parse_args()

    neurons = CompressedNeurons(args.filename)


    count = 5
    for neuron in neurons.neuron_iter():
        print(neuron)

        count -= 1
        if count < 0:
            break


if __name__ == "__main__":
    main()