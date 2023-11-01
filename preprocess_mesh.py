import open3d as o3d 
import pymeshfix 
import numpy as np 
import os 
import vedo # to voxelise 

def to_voxels(path): 
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


import sys
path_to_dir = sys.argv[1]

print(path_to_dir)

print(os.listdir(path_to_dir))


cell_list = next(os.walk(path_to_dir))[1]  


for idx, cell in enumerate(cell_list): 
    path = path_to_dir + cell + '/T_1.ply'
    make_watertight(path)
    to_voxels(path)
    if idx%100==0: 
        print(idx)
