import vedo 
import os
import open3d as o3d
import numpy as np
import sys
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

for cell in cell_list: 
    path = path_to_limeseg_folder + '/' + cell + '/T_1.ply'
    make_watertight(path)
    to_voxels(path)

print("Finished voxelising images") 

