import os
import sys

import argparse
import numpy as np
import open3d as o3d
from PIL import Image
from trimesh.exchange.export import export_mesh
from trimesh.util import concatenate as stack_meshes

from roca.engine import Predictor
import torch


def main(args):
    predictor = Predictor(
        data_dir=args.data_dir,
        model_path=args.model_path,
        config_path=args.config_path,
        wild=True,
    )
    to_file = args.output_dir != 'none'

    for name, intrinsics in zip(
            ['3m', 'desk', 'lab', 'sofa'],
            [
                np.array([[435., 0., 240.], [0., 435., 180.], [0., 0., 1.]]),
                np.array([[435., 0., 240.], [0., 435., 180.], [0., 0., 1.]]),
                np.array([[435., 0., 240.], [0., 435., 180.], [0., 0., 1.]]),
                np.array([[435., 0., 240.], [0., 435., 180.], [0., 0., 1.]]),
            ]
    ):
        img = Image.open(os.path.join('assets', '{}.jpg'.format(name)))
        img = np.asarray(img)
        instances, cad_ids = predictor(img, intrinsics)

        # instances.pred_scales = torch.from_numpy(np.ones((len(instances), 3)))
        meshes = predictor.output_to_mesh(
            instances,
            cad_ids,
            as_open3d=not to_file
        )

        if to_file:
            os.makedirs(args.output_dir, exist_ok=True)

        if predictor.can_render:
            rendering, ids = predictor.render_meshes(meshes, img.shape[1], img.shape[0], intrinsics)
            mask = ids > 0
            overlay = img.copy()
            overlay[mask] = np.clip(
                0.8 * rendering[mask] * 255 + 0.2 * overlay[mask], 0, 255
            ).astype(np.uint8)
            if to_file:
                Image.fromarray(overlay).save(
                    os.path.join(args.output_dir, 'overlay_{}.jpg'.format(name))
                )
            else:
                img = o3d.geometry.Image(overlay)
                o3d.visualization.draw_geometries([img], height=480, width=640)

        if to_file:
            out_file = os.path.join(args.output_dir, 'mesh_{}.ply'.format(name))
            export_mesh(stack_meshes(meshes), out_file, file_type='ply')
        else:
            o3d.visualization.draw_geometries(meshes)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', required=True)
    parser.add_argument('--model_path', required=True)
    parser.add_argument('--config_path', required=True)
    parser.add_argument('--output_dir', default='none')
    args = parser.parse_args(sys.argv[1:])
    main(args)
