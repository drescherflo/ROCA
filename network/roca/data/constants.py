import numpy as np
import os
import json

SYMMETRY_CLASS_IDS = {
    '__SYM_NONE': 0,
    '__SYM_ROTATE_UP_2': 1,
    '__SYM_ROTATE_UP_4': 2,
    '__SYM_ROTATE_UP_INF': 3
}
SYMMETRY_ID_CLASSES = {v: k for k, v in SYMMETRY_CLASS_IDS.items()}

# IMAGE_SIZE = (480, 640)
IMAGE_SIZE = (360, 480)

VOXEL_RES = (32, 32, 32)

__taxonomy_cache = None


def __read_taxonomy(metadata_dir):
    global __taxonomy_cache
    with open(os.path.join(metadata_dir, "scan2cad_taxonomy_9.json"), "r") as f:
        __taxonomy_cache = json.load(f)


def load_constants(metadata_dir):
    __read_taxonomy(metadata_dir)


def get_all_classes():
    global __taxonomy_cache
    return tuple([taxonomy["name"] for taxonomy in __taxonomy_cache])


def get_benchmark_classes():
    return get_all_classes()


def get_cad_taxonomy():
    global __taxonomy_cache
    return dict((int(taxonomy["shapenet"]), taxonomy["name"]) for taxonomy in __taxonomy_cache)


def get_cad_taxonomy_reverse():
    global __taxonomy_cache
    return dict((taxonomy["name"], int(taxonomy["shapenet"])) for taxonomy in __taxonomy_cache)

