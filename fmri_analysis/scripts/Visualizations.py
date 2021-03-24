
# coding: utf-8

# In[ ]:

import argparse
from glob import glob
import os
from os import makedirs, path
import pickle
import nibabel as nib
import numpy as np
from nilearn import plotting
from nistats.thresholding import map_threshold
from nilearn.image import math_img
import matplotlib.pyplot as plt
from matplotlib import rcParams
import sys

from utils.firstlevel_utils import get_first_level_objs
from utils.plot_utils import (plot_design, plot_design_timeseries,
                              plot_design_heatmap, plot_contrast,
                              plot_map, plot_task_maps,
                              get_contrast_title,
                              plot_vif)


# In[ ]:

parser = argparse.ArgumentParser(description='2nd level Entrypoint Script.')
parser.add_argument('-derivatives_dir', default=None)
parser.add_argument('--skip_designs', action='store_true')
parser.add_argument('--skip_first', action='store_true')
parser.add_argument('--skip_second', action='store_true')
parser.add_argument('--save', action='store_true')
parser.add_argument('--tasks', nargs="+", default='ANT, CCTHot, discountFix, DPX, motorSelectiveStop, stopSignal, stroop, surveyMedley, twoByTwo, WATT3'.split(', '), help="Choose from ANT, CCTHot, discountFix, DPX, motorSelectiveStop, stopSignal, stroop, surveyMedley, twoByTwo, WATT3")
parser.add_argument('-group', default='NONE')

if '-derivatives_dir' in sys.argv or '-h' in sys.argv:
    args = parser.parse_args()
else:
    args = parser.parse_args([])
    args.derivatives_dir = '/mnt/OAK/data/uh2/BIDS_data/derivatives/'
    args.data_dir = '/mnt/OAK/data/uh2/BIDS_data/'
    args.tasks = ['ANT', 'CCTHot', 'discountFix',
        'DPX', 'motorSelectiveStop',
        'stopSignal', 'stroop',
        'twoByTwo', 'WATT3']
    # args.rt=True
    args.save=True
    get_ipython().magic(u'matplotlib inline')


# In[ ]:

# set paths
all_tasks = ['ANT', 'CCTHot', 'discountFix', 'DPX', 'motorSelectiveStop', 'stopSignal', 'stopSignal', 'twoByTwo', 'WATT3']
first_level_dir = path.join(args.derivatives_dir, '1stlevel')
print(first_level_dir)
second_level_dir = path.join(args.derivatives_dir,'2ndlevel')
fmriprep_dir = path.join(args.derivatives_dir, 'fmriprep', 'fmriprep')
tasks = all_tasks if 'all' in args.tasks else args.tasks
# tasks = ['ANT', 'CCTHot', 'discountFix',
#         'DPX', 'motorSelectiveStop',
#         'stopSignal', 'stroop',
#         'twoByTwo', 'WATT3']
save = args.save
plot_designs = not args.skip_designs
run_first_level = not args.skip_first
run_second_level = not args.skip_second
group = args.group



# # Design Visualization

# In[ ]:

# load design
# subject_id, task = 's592', 'stroop'
# files = get_first_level_objs(subject_id, task, first_level_dir, regress_rt=False)
# subjinfo = pickle.load(open(files[0], 'rb'))


# In[ ]:



# display the glm to make sure its not wonky - useful for doublechecking, not necessary #
#    from nistats.reporting import plot_design_matrix
#    import matplotlib.pyplot as plt
#    fig, (ax1) = plt.subplots(figsize=(20, 10), nrows=1, ncols=1)
#    ax1.set_title(subjinfo)
#    plot_design_matrix(design_matrix, ax=ax1)
####


# In[ ]:
if plot_designs:
    rcParams.update({'figure.autolayout': True})
    fig_dir = os.path.join(first_level_dir, 'figs')
    makedirs(fig_dir, exist_ok=True)
    subjects = sorted([i.split("/")[-1] for i in glob(os.path.join(first_level_dir, '*')) if 'fig' not in i])
    print(subjects)
    for sub in subjects: 
        for task in tasks:
            print(sub, task)
            try:
                files = get_first_level_objs(sub, task, first_level_dir, regress_rt=True, beta = False)[0]
                print(files)
                f = open(files, 'rb')
                subjinfo = pickle.load(f)
                f.close()

                plot_design(subjinfo)
                plt.gcf()
                plt.savefig(os.path.join(fig_dir, '%s_%s_design_fig' % (sub, task)))
                plt.close()

                plot_design_timeseries(subjinfo)
                plt.gcf()
                plt.savefig(os.path.join(fig_dir, '%s_%s__design_timeseries' % (sub, task)))
                plt.close()

                if task=='WATT3':
                    plot_design_timeseries(subjinfo, 0, 200)
                else:
                    plot_design_timeseries(subjinfo, 0, 100)
                plt.gcf()
                plt.savefig(os.path.join(fig_dir, '%s_%s__design_timeseries_trunc' % (sub, task)))
                plt.close()                
        
                plot_design_heatmap(subjinfo)
                plt.gcf()
                plt.savefig(os.path.join(fig_dir, '%s_%s_heatmap' % (sub, task)), bbox_inches="tight")
                plt.close()

                plot_vif(subjinfo)
                plt.gcf()
                plt.savefig(os.path.join(fig_dir, '%s_%s__design_vif' % (sub, task)))
                plt.close()
            except:
                print('task not found')

        


# # First Level Visualization

# In[ ]:

if run_first_level:
    for task in tasks:
        contrast_maps = glob(path.join(first_level_dir, '*', task, '*maps*', '*.nii.gz'))
        for map_file in contrast_maps:
            contrast_name = map_file[map_file.index('contrast')+9:].replace('.nii.gz', '')
            f = plot_map(map_file, title=contrast_name)
            if save:
                output = map_file.replace('.nii.gz', '_plots.pdf')
                f.savefig(output)


# # Second Level Visualization

# In[ ]:

# if run_second_level:
#     for task in tasks:
#         contrast_maps = sorted(glob(path.join(second_level_dir, task, '*maps', '*.nii.gz')))
#         for map_file in contrast_maps:
#             contrast_name = map_file[map_file.index('contrast')+9:].rstrip('.nii.gz')
#             # plot
#             f = plot_map(map_file, title=contrast_name)
#             if save:
#                 output = map_file.replace('.nii.gz', '_plots.pdf')
#                 f.savefig(output)
def transform_p_val_map(map_path):
    img = nib.load(map_path)
    p_vals = img.get_fdata()
    p_vals[p_vals==0.0] = np.nan
    p_vals = 1 - p_vals
    neg_log_pvals = -np.log10(p_vals)
    return nib.Nifti1Image(neg_log_pvals, img.affine, img.header)


def make_mask(img_path):
    return math_img('img > .95',
                    img=nib.load(img_path))


def mask_img(img_path, mask):
    img = nib.load(img_path)
    data = img.get_fdata()
    data[~mask.get_fdata().astype(bool)] = np.nan
    return nib.Nifti1Image(data, img.affine, img.header)


if run_second_level:
    print('running!')
    for task in tasks:
        print(task)
        contrast_dirs = sorted(glob(path.join(second_level_dir, task, '*maps')))
        for contrast_dir in contrast_dirs:
            RT_flag = 'RT-True' in contrast_dir
            contrast_title = task+'_RT-'+str(RT_flag)
            out_dir = contrast_dir if group == 'NONE' else path.join(contrast_dir, group)
            print(out_dir)
            all_maps = sorted(glob(path.join(out_dir, 'contrast-*.nii.gz')))
            beta_maps = [mapi for mapi in all_maps if all(reg not in mapi for reg in ['statfile', 'corrected_pfile'])]
            scnd_lvl_contrasts = list(
                {
                    s.split('2ndlevel-')[-1].replace('.nii.gz', '')
                    for s in beta_maps
                }
            )
            for scnd_lvl in scnd_lvl_contrasts:
                curr_title = contrast_title + '_2ndlevel-'+scnd_lvl
                curr_beta_maps = sorted(mapi for mapi in beta_maps if ('2ndlevel-'+scnd_lvl in mapi))
                curr_fp_maps = sorted(mapi for mapi in all_maps if (('2ndlevel-'+scnd_lvl in mapi) and ('fcorrected_pfile' in mapi)))
                curr_fstat_maps = sorted(mapi for mapi in all_maps if (('2ndlevel-'+scnd_lvl in mapi) and ('fstatfile' in mapi)))
                curr_tp_maps = sorted(mapi for mapi in all_maps if (('2ndlevel-'+scnd_lvl in mapi) and ('Pos_tcorrected_pfile' in mapi)))
                curr_tstat_maps = sorted(mapi for mapi in all_maps if (('2ndlevel-'+scnd_lvl in mapi) and ('Pos_raw_tstatfile' in mapi)))
                curr_masked_beta_images = [mask_img(beta_path, make_mask(mask_path)) for beta_path, mask_path in zip(curr_beta_maps, curr_fp_maps)]
                curr_transformed_p_maps = [transform_p_val_map(path) for path in curr_fp_maps]
                contrast_titles = [get_contrast_title(path) for path in curr_beta_maps]
                # plot and save
                plot_task_maps(curr_beta_maps, curr_title, threshold=0, contrast_titles=contrast_titles).savefig(path.join(out_dir, '%s_2ndlevel-%s_rawBeta_plots.pdf'%(task, scnd_lvl)))
                plot_task_maps(curr_beta_maps, curr_title, contrast_titles=contrast_titles).savefig(path.join(out_dir, '%s_2ndlevel-%s_thresh3Beta_plots.pdf' %(task, scnd_lvl)))
                plot_task_maps(curr_masked_beta_images, curr_title, threshold=0, contrast_titles=contrast_titles).savefig(path.join(out_dir, '%s_2ndlevel-%s_fpMaskedBeta_plots.pdf' %(task, scnd_lvl)))
                plot_task_maps(curr_transformed_p_maps, curr_title, threshold=0, contrast_titles=contrast_titles).savefig(path.join(out_dir, '%s_2ndlevel-%s_transformedFP_plots.pdf' %(task, scnd_lvl)))
                plot_task_maps(curr_fp_maps, curr_title, threshold=.9, contrast_titles=contrast_titles).savefig(path.join(out_dir, '%s_2ndlevel-%s_thresh9FP_plots.pdf' %(task, scnd_lvl)))
                plot_task_maps(curr_fstat_maps, curr_title, threshold=0, contrast_titles=contrast_titles).savefig(path.join(out_dir, '%s_2ndlevel-%s_rawFstat_plots.pdf' %(task, scnd_lvl)))
                plot_task_maps(curr_tp_maps, curr_title, threshold=.9, contrast_titles=contrast_titles).savefig(path.join(out_dir, '%s_2ndlevel-%s_PosThresh9TP_plots.pdf' %(task, scnd_lvl)))
                plot_task_maps(curr_tstat_maps, curr_title, threshold=0, contrast_titles=contrast_titles).savefig(path.join(out_dir, '%s_2ndlevel-%s_PosRawTstat_plots.pdf' %(task, scnd_lvl)))

# if run_second_level:
#     print('running!')
#     for task in tasks:
#         print(task)
#         contrast_dirs = sorted(glob(path.join(second_level_dir, task, '*maps')))
#         for contrast_dir in contrast_dirs:
#             out_dir = contrast_dir if group == 'NONE' else path.join(contrast_dir, group)
#             print(out_dir)
#             contrast_maps = sorted(glob(path.join(out_dir, '*.nii.gz')))
#             beta_maps = [mapi for mapi in contrast_maps if 'tfile' not in mapi]
#             t_maps = [mapi for mapi in contrast_maps if 'raw_tfile' in mapi]
#             corrected_t_maps = [mapi for mapi in contrast_maps if 'corrected_tfile' in mapi]
#             RT_flag = 'RT-True' in contrast_dir
#             curr_title = task+'_RT-'+str(RT_flag)

#             f_beta = plot_task_maps(beta_maps, curr_title)
#             f_raw_t = plot_task_maps(t_maps, curr_title, threshold=0)
#             f_raw_t_wThresh = plot_task_maps(t_maps, curr_title)

#             transformed_p_maps = [transform_p_val_map(path) for path in corrected_t_maps]
#             contrast_titles = [get_contrast_title(path) for path in corrected_t_maps]
#             f_transformed_p = plot_task_maps(transformed_p_maps, curr_title, threshold=-np.log10(.05), contrast_titles=contrast_titles)

#             # mask and plot
#             masks = [make_mask(path) for path in corrected_t_maps]
#             masked_beta_images = [mask_img(path, mask) for path, mask in zip(beta_maps, masks)]
#             masked_t_images = [mask_img(path, mask) for path, mask in zip(t_maps, masks)]

#             f_beta_wMask = plot_task_maps(masked_beta_images, curr_title, threshold=0, contrast_titles=contrast_titles)
#             f_raw_t_wMask = plot_task_maps(masked_t_images, curr_title, threshold=0, contrast_titles=contrast_titles)

#             if save:
#                 output_beta = path.join(out_dir, task+'_beta_plots.pdf')
#                 f_beta.savefig(output_beta)

#                 output_beta_mask = path.join(out_dir, task+'_beta_wMask_plots.pdf')
#                 f_beta_wMask.savefig(output_beta_mask)

#                 output_raw_t = path.join(out_dir, task+'_raw_tfile_plots.pdf')
#                 f_raw_t.savefig(output_raw_t)

#                 output_raw_t_wThresh = path.join(out_dir, task+'_raw_tfile_wThresh_plots.pdf')
#                 f_raw_t_wThresh.savefig(output_raw_t_wThresh)

#                 output_raw_t_wMask = path.join(out_dir, task+'_raw_tfile_wMask_plots.pdf')
#                 f_raw_t_wMask.savefig(output_raw_t_wMask)

#                 output_corr_p = path.join(out_dir, task+'_FWE_corrected_negLog10Transformed_pfile_wThresh_plots.pdf')
#                 f_transformed_p.savefig(output_corr_p)
