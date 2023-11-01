#!/bin/bash

# activate environment 
# conda init bash
source activate napari-env


# File paths  
path_to_output_image="demo_data/demo_label_image.tif" # path to save the new label image to 
path_to_input_image="demo_data/microscopy_data.tif" # path to the original image you segmented, to read image dimensions from  
path_to_limeseg_folder="demo_data/limeseg_output/" # path to the folder where you saved your limeseg data 
path_to_morphometrics_output="demo_data/demo_morphometrics.csv"

# Unused files (for now)
# two_d_segmentation=""
# path_to_spharm_output=""

echo 'its running'

# Run script to preprocess the cell meshes, 
# voxelize each cell 
# and create a label image containing each cell for further analysis 
python scripts/voxelize_cell.py $path_to_output_image $path_to_input_image $path_to_limeseg_folder

# Now run the morphometrics script 
python scripts/run_morphometrics.py $path_to_limeseg_folder $path_to_morphometrics_output

# TODO 
# generate agreement scores for each cell 

# and do SPHARM 

