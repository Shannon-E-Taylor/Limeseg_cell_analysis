from importlib.resources import path
import numpy as np
import pandas as pd 

from skimage.io import imread
#import napari

from cellpose import metrics
from skimage.morphology import label

import pyclesperanto_prototype as cle 

import sys 


##########
# INPUTS # 
##########

path_to_2d_seg = sys.argv[1]
path_to_limeseg = sys.argv[2]
f = sys.argv[3]

print(path_to_2d_seg, path_to_limeseg, f)

seg_2d = np.load(path_to_2d_seg)

erode_radius = 5

# # the notocord and cells outside the PSM segment poorly, 
# # and I'm not interested in them 
# # so let's exclude them from analysis 
# tissue_annotation = imread('../data/tissue_segmentations/Experiment-347_s1.ome-1.labels.tif')
# tissue_annotation[tissue_annotation==2] = 0 #delete the notocord as this is poorly segmented 
# tissue_annotation[tissue_annotation>1] = 1 # and binarize

#############
# FUNCTIONS # 
#############

def count_masks(img): 
    maskcount = 0
    for img_slice in img: 
        slice_count = len(np.unique(img_slice[img_slice>0])) # remove the background so it isn't counted 
        maskcount += slice_count
    return(maskcount)

def get_iou(masks_true, masks_pred): 
    ious, labs, slices = np.array([]), np.array([]), np.array([])
    for i in range(masks_true.shape[0]): 
        iou, lab = metrics.mask_ious(masks_true[i], masks_pred[i])
        ious = np.append(ious, iou)
        labs = np.append(labs, lab)
        slices = np.append(slices, [i for i in range(len(iou))])
    
    cell_metrics = pd.DataFrame({'IOU': ious, 'slice': slices, 'label': labs})
    return(cell_metrics)

def get_average_precision(masks_true, masks_pred, threshold): 
    aps, tps, fps, fns, labs, slices = [np.array([]) for i in range(6)] 
    for i in range(masks_true.shape[0]): 
        # re-label cells so average_precision works correctly
        masks_pred[i] = label(masks_pred[i])
        masks_true[i] = label(masks_true[i]) 
        ap, tp, fp, fn = metrics.average_precision(masks_true[i], masks_pred[i], threshold)
        aps = np.append(aps, ap)
        tps = np.append(tps, tp)
        fps = np.append(fps, fp)
        fns = np.append(fns, fn)
        #labs = np.append(labs, np.unique(masks_pred[i]))
        slices = np.append(slices, i)
        
    cell_metrics = pd.DataFrame({'Average precision': aps, 
                                'False negatives': fns, 
                                'False positives': fps, 
                                'True positives': tps, 
                                #'label': labs, 
                                'slce': slices
                                })
    return(cell_metrics)


##########
# SCRIPT #
##########

##### 
# erode the cellpose masks 
# so that they look more like the limeseg ones 
masks_eroded = []



for slice in seg_2d: 
    eroded = cle.erode_labels(slice, radius=5)
    masks_eroded.append(eroded)

masks_eroded = np.array(masks_eroded)

# # get rid of all tissue outside PSM and spinal cord 
# masks_eroded = masks_eroded * tissue_annotation
# seg_2d = seg_2d * tissue_annotation
# seg_to_test = seg_to_test * tissue_annotation

seg_to_test = np.load(path_to_limeseg)['seg']

# print(list(seg_to_test.keys()))

# run the script 
eroded_metrics = get_iou(masks_eroded, seg_to_test)
uneroded_metrics = get_iou(seg_2d, seg_to_test)

eroded_metrics_by_cell = eroded_metrics[eroded_metrics['IOU']>0].groupby('label').mean()
uneroded_metrics_by_cell = uneroded_metrics[uneroded_metrics['IOU']>0].groupby('label').mean()

eroded_metrics.to_csv(f'../output/2d_segs/QC_eroded_masks_{f}.csv')
uneroded_metrics.to_csv(f'../output/2d_segs/QC_uneroded_masks_{f}.csv')

uneroded_metrics_by_cell.to_csv(f'../output/2d_segs/QC_eroded_masks_by_cell{f}.csv')
eroded_metrics_by_cell.to_csv(f'../output/2d_segs/QC_uneoded_masks_by_cell{f}.csv')