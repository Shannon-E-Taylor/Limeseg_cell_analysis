import os
import open3d as o3d
import numpy as np
import sys
from skimage.io import imread 

# get the file paths from the command line 
path_to_output_image = sys.argv[1] # path to save the new label image to 
path_to_input_image = sys.argv[2] # path to the original image you segmented, to read image dimensions from  
path_to_limeseg_folder = sys.argv[3] # path to the folder where you saved your limeseg data 

# generate a template image of the same dimensions as the original image 
segmented_image = imread(path_to_input_image).astype(np.int) * 0 


# loop through every subfolder 
list_of_folders = os.listdir(path_to_limeseg_folder)

for folder in list_of_folders: 
    cell_list = os.listdir(f'{path_to_limeseg_folder}/{folder}/')

    for cell in cell_list: 
        path = path_to_limeseg_folder + '/' + cell + '/T_1.ply'
        # only try to load the cell if we've successfully generated a label image
        if os.path.exists(path + '_.npy'): 
            cell_mask = np.load(path + '_.npy')
            x, y, z = np.nonzero(cell_mask)
            pointcloud = o3d.io.read_point_cloud(path)
            x_shift, y_shift, z_shift = pointcloud.get_min_bound()
            x_put, y_put = x + round(x_shift), y + round(y_shift)
            z_put = (z + z_shift)
            segmented_image[
                z_put.astype(int), y_put, x_put 
                ] = int(cell.split('_')[-1])


print(f"Got up to cell number {np.max(segmented_image)}")

np.savez_compressed(path_to_output_image, seg=segmented_image)

print("Saved and finished!") 

