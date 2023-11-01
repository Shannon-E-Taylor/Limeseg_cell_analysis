import pandas as pd
import numpy as np
import math

from skimage.io import imread, imsave
from skimage.measure import regionprops_table

from skimage.measure import marching_cubes, mesh_surface_area 

import matplotlib.pyplot as plt

import vedo 

import os 
import sys

# skeletonise tools 
from skan.csr import skeleton_to_csgraph
from skan import Skeleton, summarize
from skimage.morphology import skeletonize

import open3d as o3d


metrics_3d = [
     'area',
    'bbox',
  'bbox_area',
# # 'convex_area', # cause error
# #  'convex_image',
#  'coords',
# 'feret_diameter_max', # slow needs convex hull 
#  'filled_area',
#  'filled_image',
#  'image',
  'inertia_tensor',
 'inertia_tensor_eigvals',
# 'label',
 'major_axis_length',
 'minor_axis_length',
 'extent', 
#'moments',
#'moments_central',
 # 'slice',
 'solidity'
] 



##########################
# MORPHOMETRIC FUNCTIONS #
##########################

def get_measurements(masks, metrics, surf): 
    # measure our data 
    shapes_2 = regionprops_table(masks, properties = metrics)
    df = pd.DataFrame(shapes_2)

    df['surface area'] = surf

    df['cuboidness'] = df['area'] / df['bbox_area']
    df['sphericity'] = (math.pi**(1/3) * (6 * df['area'])**(2/3)) / df['surface area'] 
    df['flatness'] = df['major_axis_length'] / df['minor_axis_length'] 
    
    return(df)


def get_surface_area(tb_mask): 
    surface_areas = []

    for i in np.unique(tb_mask.flatten())[np.unique(tb_mask.flatten())>0]: 
        #print(i)
        mask = tb_mask.copy()
        mask[mask != i] = 0

        verts, faces, _, __ = marching_cubes(mask)

        surface_areas.append(mesh_surface_area(verts, faces))
    return(surface_areas) 

def calculate_metrics(df): 
    # calculate ap, dv, ml distances 

    # none of this is sensible if the embryo isn't aligned right which it aint 

    df['ap'] = (df['bbox-4'] - df['bbox-1']) 
    df['dv'] = (df['bbox-3'] - df['bbox-0'])
    df['ml'] = (df['bbox-5'] - df['bbox-2'])
    # calculate ratios 
    df['AP:DV'] = df['ap'] / df['dv']
    df['AP:ML'] = df['ap'] / df['ml']
    df['DV:ML'] = df['dv'] / df['ml'] 
    
    # transverse volume ratios - may need to remove this 
    df['transverse'] = (df['dv'] + df['ml']) / 2 #transverse cell diameter - why is this useful? 
    df['AP_anisotropy'] = df['ap'] / df['transverse'] 
    
    df['transverse_spread'] = df['dv'] * df['ml'] 
    df['transverse_xsection'] = df['area'] / df['ap'] 
    
    # shape metrics 
    df['cuboidness'] = df['area'] / (df['ap'] * df['dv'] * df['ml']) 
    df['sphericity'] = (math.pi**(1/3) * (6 * df['area'])**(2/3)) / df['surface area'] 
    df['flatness'] = df['major_axis_length'] / df['minor_axis_length'] 

    return(df)

def do_all_metrics(mask, metrics, surf):
    df = get_measurements(mask, metrics, surf)
    # surf = get_surface_area(mask)
    # read the surface area from LimeSeg as it's faster 
    df['surface area'] = surf 
    df = calculate_metrics(df)

    # df[
    #     ['n_skeleton_edges', 'sum_skel_edge_lengths', 
    #     'mean_skel_edge_lengths', 'internal_length']
    #     ] = get_skeleton_metrics(mask, df['major_axis_length'].values[0])

    return(df)


####
# skeletonization 
#### 


def apply_branch_stats(filt_branches): 
    filt_branches['branch-distance'].sum() 
    edges = filt_branches[filt_branches['branch-type']==1]
    n_edges = edges.shape[0]
    sum_edge_lengths = edges['branch-distance'].sum()
    #mean edge length nan makes no sense
    if n_edges > 0: 
        mean_edge_lengths = edges['branch-distance'].mean()
    else: 
        mean_edge_lengths = 0 

    internal_length = filt_branches[filt_branches['branch-type']==2]['branch-distance'].sum()
    
    return([n_edges, sum_edge_lengths, mean_edge_lengths, internal_length])


def get_skeleton_metrics(img, cell_len): 
    skeleton = skeletonize(img)
    # if np.sum(skeleton) < 255*5: 
    #     imsave('wrong_skel.tif', img)
    #     return ([0,0,0,0])
    branch_data = summarize(Skeleton(skeleton))
    filt_branches = branch_data[(branch_data['branch-type'] == 2) | (
     (branch_data['branch-type'] == 1) & (branch_data['branch-distance'] > cell_len/10)
     )]
    
    return(apply_branch_stats(filt_branches))


data = []

path_to_limeseg_folder = sys.argv[1]
path_to_morphometrics_output = sys.argv[2]

if True:   
    data = []
    if os.path.exists(f'{path_to_limeseg_folder}/Results.csv'): 
        results = pd.read_csv(f'{path_to_limeseg_folder}/Results.csv')
        print(results.shape)

        cell_list = results['Cell Name']
 
        for cell in cell_list: 
            path_ = f'{path_to_limeseg_folder}/{cell}/T_1.ply_.npy'
            if os.path.exists(path_): 
                cell_info = results[results['Cell Name'] == cell]
                surf = cell_info['Real Surface'].values[0]
                img = np.load(path_)
                d = do_all_metrics(img, metrics_3d, surf = surf) # oops forgot to save this 
                d[['X', 'Y', 'Z']] = cell_info[['Center X', 'Center Y', 'Center Z']]
                d['label'] = int(cell.split('_')[-1])

                data.append(d)
        data_df = pd.concat(data)
        data_df.to_csv(path_to_morphometrics_output)
    else: 
        print('Results file not found')
