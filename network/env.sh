# System config
export OMP_NUM_THREADS=1
export NUM_WORKERS=4
export SEED=2021

BASE_DIR=$HOME/custom_roca_data
export METADATA_DIR=$BASE_DIR/metadata
# NOTE: Change the data config based on your detup!
# JSON files
export DATA_DIR=$BASE_DIR/Dataset
# Resized images with intrinsics and poses
export IMAGE_ROOT=$BASE_DIR/Images
# Depths and instances rendered over images
export RENDERING_ROOT=$BASE_DIR/Rendering
# Scan2CAD Full Annotations
export FULL_ANNOT=$BASE_DIR/Scan2CAD/full_annotations.json

# Model configurations
export RETRIEVAL_MODE=resnet_resnet+image+comp
export E2E=1
export NOC_WEIGHTS=1

# Train and test behavior
export EVAL_ONLY=0
export CHECKPOINT="none" #$BASE_DIR/model_best.pth  # "none"
export RESUME=0  # This means from last checkpoint
export OUTPUT_DIR=output
