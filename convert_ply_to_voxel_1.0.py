import vedo 
import os
import open3d as o3d
import numpy as np
import sys
from skimage.io import imread 

# get the file paths from the command line 
path_to_output_image = sys.argv[1] # path to save the new label image to 
path_to_input_image = sys.argv[2] # path to the original image you segmented, to read image dimensions from  
path_to_limeseg_folder = sys.argv[3] # path to the folder where you saved your limeseg data 

# Limeseg automatically saves each cell in its own folder
# So to read all the cells we want a list of all of these folders 
cell_list = os.listdir(path_to_limeseg_folder)

# generate a template image of the same dimensions as the original image 
img_zeros = imread(path_to_input_image).astype(np.int) * 0 

for cell in cell_list: 
    path = f_in + '/' + cell + '/T_1.ply'
    # only try to load the cell if we've successfully generated a label image in the previous script 
    if os.path.exists(path + '_.npy'): 
        cell_mask = np.load(path + '_.npy')
        x, y, z = np.nonzero(cell_mask)
        pointcloud = o3d.io.read_point_cloud(path)
        x_shift, y_shift, z_shift = pointcloud.get_min_bound()
        x_put, y_put = x + round(x_shift), y + round(y_shift)
        z_put = (z + z_shift)
        img_zeros[
            z_put.astype(int), y_put, x_put 
            ] = int(cell.split('_')[-1])


print("Got up to cell number {np.max(img_zeros)}")

np.savez_compressed(f_out, seg=img_zeros)

print("Saved and finished!") 

