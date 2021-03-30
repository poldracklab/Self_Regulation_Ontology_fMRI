import shutil
import json
import nibabel as nb
import numpy as np
from glob import glob
from os import path, remove, makedirs
from nilearn import image
from nipype.caching import Memory
from nipype.interfaces import fsl

from utils.utils import get_flags


def mean_masks(masks):
    mask = nb.load(masks[0])
    hdr, aff = mask.header, mask.affine
    data = np.zeros(mask.shape)
    for mask in masks:
        data += nb.load(mask).get_data()
    data /= len(masks)
    return nb.Nifti1Image(data, aff, hdr)


def create_group_mask(fmriprep_dir, threshold=.8, verbose=True):
    if verbose:
        print('Creating Group mask...')
    # check if there's a session folder
    if len(glob(path.join(fmriprep_dir, 'sub-*', 'func',
                          '*MNI152NLin2009cAsym*brain_mask.nii.gz'))):
        brainmasks = glob(path.join(fmriprep_dir,
                                    'sub-*',
                                    'func',
                                    '*MNI152NLin2009cAsym*brain_mask.nii.gz'))
    else:
        brainmasks = glob(path.join(fmriprep_dir, 'sub-*', '*', 'func',
                                    '*MNI152NLin2009cAsym*brain_mask.nii.gz'))
    if verbose:
        print("%s maps found at %s" % (len(brainmasks), fmriprep_dir))
        print('threshold info:')
        print(threshold)
        print(type(threshold))
    mean_mask = mean_masks(brainmasks)
    if verbose:
        print('Thresholding, finishing creating group mask')
    return image.math_img("a>=%s" % str(threshold), a=mean_mask)


def load_contrast_maps(second_level_dir, task, regress_rt=False, beta=False):
    rt_flag, beta_flag = get_flags(regress_rt, beta)
    maps_dir = path.join(
        second_level_dir, task,
        'secondlevel_RT-%s_beta-%s_N-*_maps' % (rt_flag, beta_flag)
        )
    maps_dirs = glob(maps_dir)
    if len(maps_dirs) > 1:
        maps_dir = sorted(maps_dirs, key=lambda x: x.split('_')[-2])[-1]
    else:
        maps_dir = maps_dirs[0]
    map_files = glob(path.join(maps_dir, '*'))
    maps = {}
    for f in map_files:
        name = f.split(path.sep)[-1][9:].replace('.nii.gz', '')
        maps[name] = image.load_img(f)
    return maps


def randomise(maps, maps_dir, mask_loc, des_mat,
              n_perms=1000, fwhm=6, c_thresh=None):
    contrast_name = maps[0][maps[0].index('contrast')+9:].replace('.nii.gz', '')
    # create 4d image
    concat_images = image.concat_imgs(maps)
    # smooth_concat_images
    concat_images = image.smooth_img(concat_images, fwhm)
    # save concat images temporarily
    concat_loc = path.join(maps_dir, 'tmp_concat.nii.gz')
    concat_images.to_filename(concat_loc)

    mem = Memory(base_dir=maps_dir)
    #build up randomise design files
    des_contrasts = [
            ('group_mean_pos', 'T',['intercept'], [1]),
            ('group_mean_neg', 'T',['intercept'], [-1]),
            ('group_mean_F', 'F', [('group_mean_pos', 'T', ['intercept'],[1])])
        ]
    t_name_map = {
        1: 'groupMeanPos',
        2: 'groupMeanNeg',
    }
    f_name_map = {
        1: 'groupMean',
    }
    t_counter = 3
    f_counter = 2
    for rt_col in des_mat.filter(regex='RT').columns:
        des_contrasts += [
            ('%s_pos' % rt_col, 'T', [rt_col],[1]),
            ('%s_neg' % rt_col, 'T', [rt_col],[-1]),
            ('%s_F' % rt_col, 'F', [('%s_pos' % rt_col, 'T', [rt_col],[1])])
        ]
        t_name_map[t_counter] = '%sPos' % rt_col
        t_counter += 1
        t_name_map[t_counter] = '%sNeg' % rt_col
        t_counter += 1
        f_name_map[f_counter] = '%s' % rt_col
        f_counter += 1
    mult_regress_design = mem.cache(fsl.MultipleRegressDesign)
    mult_res_model_results = mult_regress_design(
        contrasts=des_contrasts,
        regressors=des_mat.reset_index(drop=True).to_dict('l')
    )
    # assume TFCE unless a cluster size is given
    kwargs={'c_thresh': c_thresh} if c_thresh is not None else {'tfce':True}

    # run randomise    
    fsl_randomise = mem.cache(fsl.Randomise)
    randomise_results = fsl_randomise(
        in_file=concat_loc,
        mask=mask_loc,
        design_mat=mult_res_model_results.outputs.design_mat,
        fcon=mult_res_model_results.outputs.design_fts,
        tcon=mult_res_model_results.outputs.design_con,
        num_perm=n_perms,
        var_smooth=fwhm,
        vox_p_values=False,
        demean=False,
        one_sample_group_mean=False,
        **kwargs
        )
    # save results
    output_dir = path.join(maps_dir, 'contrast-%s_Randomise' % contrast_name)
    makedirs(output_dir, exist_ok=True)
    mrd_out_dir = path.dirname(mult_res_model_results.outputs.design_con)
    mrd_files = glob(path.join(mrd_out_dir, 'design*')) + glob(path.join(mrd_out_dir, '*.json')) + glob(path.join(mrd_out_dir, '*.txt'))
    rand_out_dir = path.dirname(randomise_results.outputs.f_corrected_p_files[0])
    rand_files = glob(path.join(rand_out_dir, '*.nii.gz'))
    for filey in mrd_files + rand_files:
        filename = filey.split('/')[-1]
        shutil.move(filey, path.join(output_dir, filename)) 

    with open(path.join(output_dir, 'f_name_map.json'), 'w') as f:
        json.dump(f_name_map, f)
    with open(path.join(output_dir, 't_name_map.json'), 'w') as f:
        json.dump(t_name_map, f)

    # remove temporary files
    remove(concat_loc)
    shutil.rmtree(path.join(maps_dir, 'nipype_mem'))


    # def move_outputs_w_map(output_list, name_map, filetype):
    #     for filey in output_list:
    #         name_idxs = re.findall(r'[0-9$,%]+\d*', test_str)
    #         assert len(name_idxs)==1  # want to make sure there was only 1 num in the str, the idx
    #         name_idx = int(name_idxs[0])
    #         mapped_name = name_map[name_idx]
    #         new_file_loc = path.join(
    #             maps_dir,
    #             "contrast-%s_2ndlevel-%s_%s.nii.gz" % (contrast_name, mapped_name, filetype)
    #         )
    #         shutil.move(filey, new_file_loc) 
    # move_outputs_w_map(randomise_results.outputs.fstat_files, f_name_map, filetype='raw_fstatfile')
    # move_outputs_w_map(randomise_results.outputs.f_corrected_p_files, f_name_map, filetype='fcorrected_pfile')
    # move_outputs_w_map(randomise_results.outputs.tstat_files, t_name_map, filetype='raw_tstatfile')
    # move_outputs_w_map(randomise_results.outputs.t_corrected_p_files, t_name_map, filetype='tcorrected_pfile')                             

    # # remove temporary files
    # remove(concat_loc)
    # shutil.rmtree(path.join(maps_dir, 'nipype_mem'))
