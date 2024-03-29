from glob import glob
from nilearn import image
from nipype.caching import Memory
from nipype.interfaces import fsl
import os 
from os import path, remove
import shutil
from utils.utils import get_flags

def create_group_mask(fmriprep_dir, threshold=.8, verbose=True):
    if verbose:
        print('Creating Group mask...')
    brainmasks = glob(path.join(fmriprep_dir,'sub-*',
                               'func','*MNI152NLin2009cAsym*brain_mask.nii.gz'))     
    mean_mask = image.mean_img(brainmasks)
    group_mask = image.math_img("a>=%s" % str(threshold), a=mean_mask)
    return group_mask
    if verbose:
        print('Finished creating group mask')

def load_contrast_maps(second_level_dir, task, regress_rt=False, beta=False):
    rt_flag, beta_flag = get_flags(regress_rt, beta)
    maps_dir = path.join(second_level_dir, task, 'secondlevel_RT-%s_beta-%s_N-*_maps' % (rt_flag, beta_flag))
    maps_dirs = glob(maps_dir)
    if len(maps_dirs) > 1:
        maps_dir = sorted(maps_dirs, key=lambda x: x.split('_')[-2])[-1]
    else:
        maps_dir = maps_dirs[0]
    map_files = glob(path.join(maps_dir, '*'))
    maps = {}
    for f in map_files:
        name = f.split(path.sep)[-1][9:].rstrip('.nii.gz')
        maps[name] = image.load_img(f)
    return maps

def randomise(maps, output_loc, mask_loc, n_perms=500, fwhm=6):
    contrast_name = maps[0][maps[0].index('contrast')+9:].rstrip('.nii.gz')
    # create 4d image
    concat_images = image.concat_imgs(maps)
    # smooth_concat_images
    concat_images = image.smooth_img(concat_images, fwhm)
    # save concat images temporarily
    concat_loc = path.join(output_loc, 'tmp_concat.nii.gz')
    concat_images.to_filename(concat_loc)
    # run randomise
    mem = Memory(base_dir=output_loc)
    randomise = mem.cache(fsl.Randomise)
    randomise_results = randomise(
        in_file=concat_loc,
        mask=mask_loc,
        one_sample_group_mean=True,
        tfce=True,
        vox_p_values=True,
        var_smooth=10,
        num_perm=n_perms)
    # save results
    tfile_loc = path.join(output_loc, "contrast-%s_raw_tfile.nii.gz" % contrast_name)
    tfile_corrected_loc = path.join(output_loc, "contrast-%s_corrected_tfile.nii.gz" % contrast_name)
    raw_tfile = randomise_results.outputs.tstat_files[0]
    corrected_tfile = randomise_results.outputs.t_corrected_p_files[0]
    shutil.move(raw_tfile, tfile_loc)
    shutil.move(corrected_tfile, tfile_corrected_loc)
    # remove temporary files
    remove(concat_loc)
    shutil.rmtree(path.join(output_loc, 'nipype_mem'))
