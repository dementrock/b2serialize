import argparse
from framework import (Framework, main)
from xml_box2d import world_from_xml


class Liveload(Framework):

    name = "Liveload"

    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("file", type=str, help="path to the xml file")
        args = parser.parse_args()
        with open(args.file, "r") as f:
            s = f.read()
        world = world_from_xml(s)
        super(Liveload, self).__init__(world)

if __name__ == "__main__":
    main(Liveload)
