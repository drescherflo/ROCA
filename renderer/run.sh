. ./env.sh

echo "####### resize_images"
python resize_images.py \
    --image_root $SCANNET25K_DIR \
    --output_root $IMAGE_DIR \
    --num_workers $NUM_WORKERS

echo "####### render"
python render.py \
    --s2c_root $S2C_ROOT \
    --cad_root $SHAPENET_DIR \
    --scan_root $IMAGE_DIR/tasks/scannet_frames_25k \
    --metadata_dir $METADATA_DIR \
    --output_json_dir $DATA_DIR \
    --output_image_dir $RENDERING_DIR \
    --num_workers $NUM_WORKERS

echo "####### rendering_to_coco"
python rendering_to_coco.py \
    --alignment_json $DATA_DIR/scan2cad_image_alignments.json \
    --output_dir $DATA_DIR \
    --center_filter 1 \
    --cat_repeat 1 \
    --rle 1 \
    --rendering_root $RENDERING_DIR \
    --metadata_dir $METADATA_DIR

echo "####### create_scenes"
python create_scenes.py \
    --s2c_dir $S2C_ROOT \
    --cad_root $SHAPENET_DIR \
    --data_dir $DATA_DIR \
    --metadata_dir $METADATA_DIR

echo "####### create_cad_db"
python create_cad_db.py \
    --cad_root $SHAPENET_DIR \
    --data_dir $DATA_DIR \
    --metadata_dir $METADATA_DIR

echo "####### voxelize_cads"
python voxelize_cads.py $DATA_DIR
