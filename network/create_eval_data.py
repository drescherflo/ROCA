import glob
import os
import argparse
import sys
import time
import json
from typing import List, Tuple

import numpy as np
import torch
from PIL import Image
from detectron2.structures import Instances

from roca.engine.predictor import Predictor


def __quit_on_error(message: str) -> None:
    if not message.endswith(".") or not message.endswith(". "):
        message += "."
    print(message, "Exiting...")
    exit(-1)


def __yes_no_question(prompt: str) -> bool:
    while True:
        answer = input(prompt + " (Yes/No) [Yes]: ").strip().lower()

        # Check for yes
        if answer in ['ja', 'j', 'yes', 'y', '']:
            return True

        # Check for no
        elif answer in ['nein', 'n', 'no']:
            return False

        # Invalid answer, ask again
        else:
            print("Invalid answer. Please answer with yes or no.")


def get_image_files(input_dir: str) -> List[str]:
    return glob.glob(os.path.join(input_dir, "image_*.jpg"))


def read_intrinsics_file(file_path: str) -> np.ndarray:
    with open(file_path, "r") as f:
        lines = f.readlines()
        intrinsics = [line.strip().split(' ') for line in lines]
        intrinsics = np.array(intrinsics, dtype=float)
    return intrinsics


def save_image_with_object_masks(image: np.ndarray, intrinsics: np.ndarray, image_file_name, predictor: Predictor, instances: Instances, cad_ids: List[Tuple[str, str]], out_dir: str, force_scale_1: bool = False) -> None:
    out_file_name = image_file_name.replace(".jpg", "_object_mask_forced_scale.jpg") if force_scale_1 else image_file_name.replace(".jpg", "_object_mask.jpg")
    if force_scale_1:
        instances.pred_scales = torch.from_numpy(np.ones((len(instances), 3)))
    meshes = predictor.output_to_mesh(instances, cad_ids)
    rendering, ids = predictor.render_meshes(meshes, image.shape[1], image.shape[0], intrinsics)
    mask = ids > 0
    overlay = image.copy()
    overlay[mask] = np.clip(0.8 * rendering[mask] * 255 + 0.2 * overlay[mask], 0, 255).astype(np.uint8)
    Image.fromarray(overlay).save(os.path.join(out_dir, out_file_name))


def main(argv) -> None:
    # Parse Args
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", help="Directory with test images and corresponding camera intrinsics", required=True)
    parser.add_argument("--model", help="Path to trained model", required=True)
    parser.add_argument("--model_config", help="Path to the model's config file", required=True)
    parser.add_argument("--data_dir", "Path to the directory with cad database files, etc. created by the ROCA renderer during training preprocessing", required=True)
    parser.add_argument("--out_file", help="Path to the output file", required=True)
    parser.add_argument("--confidence_threshold", help="Confidence threshold for determining whether a detected object is returned or not", default=0.5, type=float)
    parser.add_argument("--image_out_dir", help="Specifies the directory where the input images with rendered object masks will be saved", required=True)
    args = parser.parse_args(argv)

    # Test if relevant directories and files exist
    if not os.path.exists(args.input_dir):
        __quit_on_error("Input directory '{}' does not exist".format(args.input_dir))
    if not os.path.exists(args.model):
        __quit_on_error("Model file '{}' does not exist".format(args.model))
    if not os.path.exists(args.model_config):
        __quit_on_error("Model config file '{}' does not exist".format(args.model_config))
    if not os.path.exists(args.data_dir):
        __quit_on_error("Data directory '{}' does not exist".format(args.data_dir))

    # Validate threshold
    confidence_threshold = args.confidence_threshold
    confidence_threshold = confidence_threshold if confidence_threshold <= 1 else 1
    confidence_threshold = confidence_threshold if confidence_threshold >= 0 else 0

    # Test for out_file existence and ask for overwriting
    if os.path.exists(args.out_file):
        if not __yes_no_question("Output file '{}' already exists. Overwrite?".format(args)):
            __quit_on_error("")

    # Load semantic labels
    with open(os.path.join(args.data_dir, "scan2cad_alignment_classes.json")) as f:
        labels = json.load(f)

    # Create ROCA predictor
    predictor = Predictor(args.data_dir, args.model, args.model_config, confidence_threshold)

    # Load image files
    image_paths = get_image_files(args.input_dir)

    # Create image out dir
    os.makedirs(args.image_out_dir, exist_ok=True)

    # Run per frame evaluation
    per_frame_results = []
    for image_path in image_paths:
        # Load image
        image = np.asarray(Image.open(image_path))

        # Load intrinsics
        intrinsics = read_intrinsics_file(image_path.replace(".jpg", ".txt"))

        # Run ROCA
        start_time = time.time()
        instances, cad_ids = predictor(image, intrinsics)
        end_time = time.time()

        # Store results
        per_object_instances = []
        for i in range(len(instances)):
            per_object_instances.append({
                "scale": instances.pred_scales[i],
                "translation": instances.pred_translations[i],
                "rotation": instances.pred_rotations[i],
                "semantic_label": labels[instances.pred_classes[i]]
            })

        image_file_name = os.path.basename(image_path)
        frame_results = {
            "image": image_file_name,
            "instances": per_object_instances,
            "inference_start_time": start_time,
            "inference_end_time": end_time
        }

        per_frame_results.append(frame_results)

        # Create images with object masks
        if predictor.can_render:
            save_image_with_object_masks(image, intrinsics, image_file_name, predictor, instances, cad_ids, args.image_out_dir)
            save_image_with_object_masks(image, intrinsics, image_file_name, predictor, instances, cad_ids, args.image_out_dir, force_scale_1=True)

    # Save results
    os.makedirs(os.path.dirname(args.out_file), exist_ok=True)
    with open(args.out_file, "w") as f:
        json.dump(per_frame_results, f, indent=4)


if __name__ == '__main__':
    main(sys.argv[1:])
