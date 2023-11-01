import vedo 
import os
import open3d as o3d
import numpy as np
import sys
from skimage.io import imread 

# f_in = sys.argv[0]

f_out = sys.argv[1]
path_to_image = sys.argv[2]
f_in = sys.argv[3]

cell_list = os.listdir(f_in)

img_zeros = imread(path_to_image).astype(np.int) * 0 

# img_zeros = img_zeros

print('inputs ok')

img_zeros = img_zeros * 0 

cell_list = os.listdir(f_in)

for cell in cell_list: 
    path = f_in + '/' + cell + '/T_1.ply'
    if os.path.exists(path + '_.npy'): 
        print(cell)
        cell_mask = np.load(path + '_.npy')
        x, y, z = np.nonzero(cell_mask)
        pointcloud = o3d.io.read_point_cloud(path)
        x_shift, y_shift, z_shift = pointcloud.get_min_bound()
        x_put, y_put = x + round(x_shift), y + round(y_shift)
        z_put = (z + z_shift)
        img_zeros[
            z_put.astype(int), y_put, x_put 
            ] = int(cell.split('_')[-1])

print(np.max(img_zeros))

np.savez_compressed(f_out, seg=img_zeros)



