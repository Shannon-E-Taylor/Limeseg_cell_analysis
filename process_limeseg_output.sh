#!/bin/bash

# activate environment 
# conda init bash
source activate napari-env

# path_to_limeseg_folder="../output/cell_segs_limeseg/isotropic_embryo_1_v2/"
path_to_limeseg_folder="../output/cell_segs_limeseg/image_25/"
# img_path="../output/Experiment-347_s1.ome-1_8bit_gauss2simga_isotropic.tif"
img_path="../data/Image25.tif"
path_out="../output/cell_segs_as_tiff/isotropic_embryo_1.npz"
path_out="../output/Image_25.npz"
twod_seg="../output/2d_segs/isotropic_image_1a.npy"

echo 'its running'

# close meshes, and convert to voxels 
# python preprocess_mesh.py $path_to_limeseg_folder

# # get all segmentations in one file 

# python convert_ply_to_voxel_1.0.py $path_out $img_path $path_to_limeseg_folder

# get agreement scores for each cell 
# python assess_accuracy_2.py $twod_seg $path_out "isotropic_embryo1"

# run SPHARM 
# calculate_spherical_harmonics.py 

# run morphometrics pipeline 
# let's leave this until I have fixed skeletonization 
# python run_morphometrics_v2.py "image_25"
# python run_morphometrics_v2.py "image_25_core_cells"

# now we should have 
# 1. agreement scores for each cell 
# 2. spherical harmonics for each cell 
# 3. morhometric measurements for each cell 
# and can proceed to analysis! 

python calculate_aligned_spherical_harmonics.py "image_25"
