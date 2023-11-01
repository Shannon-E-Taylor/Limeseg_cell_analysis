import vedo 
import os
import open3d as o3d
import numpy as np
import sys
from skimage.io import imread 
import pymeshfix 

def to_voxels(path): 
    '''
    This code takes the input .ply file, converts it to voxels using vedo, and saves the output 
    To the same folder as the cell originated from 
    '''
    if not os.path.exists(path + '_npy'): # dont overwrite 
        pointcloud = o3d.io.read_point_cloud(path)
        if pointcloud.has_points(): 
            mesh = vedo.load(path)
            vol = mesh.binarize()
            np.save(path + '_.npy', vol.tonumpy())


def make_watertight(path): 
    '''
    This code reads and cleans the existing mesh using the pymeshfix library
    There is a simpler command to achieve this : 
    pymeshfix.clean_from_file(infile, outfile)      
    But this crashes for me so I'm using the longer method from the docs 
    '''
    bpa_mesh = o3d.io.read_triangle_mesh(path)
    faces = np.asarray(bpa_mesh.triangles) 
    vertices = np.asarray(bpa_mesh.vertices) 

    # Create object from vertex and face arrays
    meshfix = pymeshfix.MeshFix(vertices, faces)
    # Repair input mesh
    meshfix.repair()
    # Save the mesh
    meshfix.save(path)

# get the file paths from the command line 
path_to_output_image = sys.argv[1] # path to save the new label image to 
path_to_input_image = sys.argv[2] # path to the original image you segmented, to read image dimensions from  
path_to_limeseg_folder = sys.argv[3] # path to the folder where you saved your limeseg data 

# Limeseg automatically saves each cell in its own folder
# So to read all the cells we want a list of all of these folders 
cell_list = os.listdir(path_to_limeseg_folder)

# generate a template image of the same dimensions as the original image 
segmented_image = imread(path_to_input_image).astype(np.int) * 0 

for cell in cell_list: 
    path = path_to_limeseg_folder + '/' + cell + '/T_1.ply'
    make_watertight(path)
    to_voxels(path)
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

