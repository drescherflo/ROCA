# System config
export OMP_NUM_THREADS=1
export NUM_WORKERS=4
export SEED=2021

# NOTE: Change the data config based on your detup!
CUSTOM_DATASET_DIR=$HOME/custom_dataset
BASE_DIR=$CUSTOM_DATASET_DIR/converted/6_dof/ReplicatorToRoca
export METADATA_DIR=$BASE_DIR/metadata
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
export AUGMENT=1  # Run augmentation provided by ROCA during training

# Set output dir
if [ "$AUGMENT" -eq "1" ]; then
  export OUTPUT_DIR=$CUSTOM_DATASET_DIR/ROCA_Outputs/Augmentation
else
  export OUTPUT_DIR=$CUSTOM_DATASET_DIR/ROCA_Outputs/No_Augmentation
fi
