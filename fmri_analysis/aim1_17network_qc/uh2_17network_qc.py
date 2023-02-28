import sys 
import argparse
import nilearn
import pandas as pd
import numpy as np
import nibabel as nb
import matplotlib.pyplot as plt
from os import path
from glob import glob
from bids import BIDSLayout
from nilearn import image
from nilearn import datasets
from nilearn.input_data import NiftiLabelsMasker
from nilearn._utils import check_niimg

parser = argparse.ArgumentParser(description='aim1 timelocked responses')
parser.add_argument('--task', default="DPX", help="Choose from ANT, CCTHot, discountFix, DPX, motorSelectiveStop, stopSignal, stroop, surveyMedley, twoByTwo, WATT3")
args = parser.parse_args()

task = args.task


# CONSTANTS
num_nets = 17 #use yeo 17 network parcellation
num_trs = 20 #to average over

#getting the trial types for a given task
if task=='DPX':
    task_conditions = ['AX', 'AY', 'BX', 'BY']
elif task=='motorSelectiveStop':
    task_conditions = ['crit_go', 'crit_stop_failure', 'crit_stop_success',
     'noncrit_nosignal', 'noncrit_signal']
elif task=='stopSignal':
    task_conditions = ['go', 'stop_failure', 'stop_success']
elif task=='twoByTwo':
    task_conditions = ['cue_stay_100', 'cue_stay_900',
     'task_stay_cue_switch_100', 'task_stay_cue_switch_900',
     'task_switch_100', 'task_switch_100']
elif task=='WATT3':
    task_conditions = ['trial']
else:
    task_conditions = ['task']


#confounds, modified from:
# https://github.com/VU-Cog-Sci/nideconv/blob/d7f5c6a71e4cae4159c38b18b72e335a51437493/nideconv/utils/roi.py#L224
confounds_to_include = ['framewise_displacement', 'a_comp_cor_00',
                        'a_comp_cor_01', 'a_comp_cor_02', 'a_comp_cor_03',
                        'a_comp_cor_04', 'a_comp_cor_05', 'a_comp_cor_06',
                        'a_comp_cor_07', 'trans_x', 'trans_y', 'trans_z',
                        'rot_x', 'rot_y', 'rot_z']

# dictionary converting yeo number to network label
# done in this dumb way to check that ROIs agreed with each other
label_dict = {1.0: ['central visual', 'central visual', 'central visual', 'central visual'],
 2.0: ['peripheral visual',
  'peripheral visual',
  'peripheral visual',
  'peripheral visual',
  'peripheral visual',
  'peripheral visual'],
 3.0: ['somatomotor A', 'somatomotor A'],
 4.0: ['somatomotor B',
  'somatomotor B',
  'somatomotor B',
  'somatomotor B',
  'somatomotor B',
  'somatomotor B',
  'somatomotor B',
  'somatomotor B'],
 5.0: ['dorsal attention A',
  'dorsal attention A',
  'dorsal attention A',
  'dorsal attention A',
  'dorsal attention A',
  'dorsal attention A'],
 6.0: ['dorsal attention B',
  'dorsal attention B',
  'dorsal attention B',
  'dorsal attention B',
  'dorsal attention B',
  'dorsal attention B',
  'dorsal attention B',
  'dorsal attention B'],
 7.0: ['salience / ventral attention A',
  'salience / ventral attention A',
  'salience / ventral attention A',
  'salience / ventral attention A',
  'salience / ventral attention A',
  'salience / ventral attention A',
  'salience / ventral attention A',
  'salience / ventral attention A',
  'salience / ventral attention A',
  'salience / ventral attention A',
  'salience / ventral attention A'],
 8.0: ['salience / ventral attention B',
  'salience / ventral attention B',
  'salience / ventral attention B',
  'salience / ventral attention B',
  'salience / ventral attention B',
  'salience / ventral attention B',
  'salience / ventral attention B',
  'salience / ventral attention B',
  'salience / ventral attention B',
  'salience / ventral attention B',
  'salience / ventral attention B',
  'salience / ventral attention B'],
 9.0: ['limbic A', 'limbic A'],
 10.0: ['limbic B', 'limbic B'],
 12.0: ['control A',
  'control A',
  'control A',
  'control A',
  'control A',
  'control A',
  'control A',
  'control A',
  'control A',
  'control A',
  'control A'],
 13.0: ['control B',
  'control B',
  'control B',
  'control B',
  'control B',
  'control B',
  'control B',
  'control B',
  'control B',
  'control B',
  'control B'],
 11.0: ['control C', 'control C', 'control C', 'control C'],
 16.0: ['default A',
  'default A',
  'default A',
  'default A',
  'default A',
  'default A',
  'default A',
  'default A',
  'default A'],
 17.0: ['default B',
  'default B',
  'default B',
  'default B',
  'default B',
  'default B',
  'default B'],
 15.0: ['default C',
  'default C',
  'default C',
  'default C',
  'default C',
  'default C'],
 14.0: ['temporal parietal', 'temporal parietal']}

#paths - first line gets path to/downloads yeo parcellations
yeo = datasets.fetch_atlas_yeo_2011()

BIDS_dir = '/oak/stanford/groups/russpold/data/uh2/aim1/BIDS_scans'
deriv_base_path = '/oak/stanford/groups/russpold/data/uh2/aim1/BIDS_scans/derivatives/fmriprep/sub-*/ses-*/func/'
source_path = path.join(BIDS_dir, 'sub-*/ses-*/func/*%s*bold.nii.gz') #for oringal filepaths for metadata
prep_path = path.join(deriv_base_path, '*%s*space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz') #MNI-space preprocessed data
evs_path = path.join(BIDS_dir, 'derivatives/1stlevel/s*/%s/simplified_events_RT-False_beta-False.csv') #for timelocking
dsgn_path = path.join(BIDS_dir, 'derivatives/1stlevel/s*/%s/design_RT-False_beta-False.csv') #for confounds


# HELPERS
# taken from:
#https://github.com/VU-Cog-Sci/nideconv/blob/d7f5c6a71e4cae4159c38b18b72e335a51437493/nideconv/utils/roi.py#L261
def _make_psc(data):
    mean_img = image.mean_img(data)

    # Replace 0s for numerical reasons
    mean_data = mean_img.get_data()
    mean_data[mean_data == 0] = 1
    denom = image.new_img_like(mean_img, mean_data)

    return image.math_img('data / denom[..., np.newaxis] * 100 - 100',
                          data=data, denom=denom)

# modified from:
# https://github.com/VU-Cog-Sci/nideconv/blob/d7f5c6a71e4cae4159c38b18b72e335a51437493/nideconv/utils/roi.py#L8
def extract_timecourse_from_nii(atlas,
                                nii,
                                mask=None,
                                confounds=None,
                                atlas_type=None,
                                t_r=None,
                                low_pass=None,
                                high_pass=1./128,
                                *args,
                                **kwargs):
    """
    Extract time courses from a 4D `nii`, one for each label 
    or map in `atlas`,
    This method extracts a set of time series from a 4D nifti file
    (usually BOLD fMRI), corresponding to the ROIs in `atlas`.
    It also performs some minimal preprocessing using 
    `nilearn.signal.clean`.
    It is especially convenient when using atlases from the
    `nilearn.datasets`-module.
    Parameters
    ----------
    atlas: str  
        Path to 3D atlas image to be passed into NiftiLabelsMasker
    nii: 4D niimg-like object
        This NiftiImage contains the time series that need to
        be extracted using `atlas`
    mask: 3D niimg-like object
        Before time series are extracted, this mask is applied,
        can be useful if you want to exclude non-gray matter.
    confounds: CSV file or array-like, optional
        This parameter is passed to nilearn.signal.clean. Please 
        see the related documentation for details.
        shape: (number of scans, number of confounds)
    t_r, float, optional
        Repetition time of `nii`. Can be important for
        temporal filtering.
    low_pass: None or float, optional
        This parameter is passed to signal.clean. Please see the related
        documentation for details
    high_pass: None or float, optional
        This parameter is passed to signal.clean. Please see the related
        documentation for details
    Examples
    --------
    >>> from nilearn import datasets
    >>> data = '/data/ds001/derivatives/fmriprep/sub-01/func/sub-01_task-checkerboard_bold.nii.gz'
    >>> atlas = datasets.fetch_atlas_pauli_2017()
    >>> ts = extract_timecourse_from_nii(atlas,
                                         data,
                                         t_r=1.5)
    >>> ts.head()
    """

    standardize = kwargs.pop('standardize', False)
    detrend = kwargs.pop('detrend', False)

    masker = NiftiLabelsMasker(atlas,
                               mask_img=mask,
                               standardize=standardize,
                               detrend=detrend,
                               t_r=t_r,
                               low_pass=low_pass,
                               high_pass=high_pass,
                               *args, **kwargs)


    data = _make_psc(nii)

    results = masker.fit_transform(data,
                                   confounds=confounds)

    if t_r is None: #hold over from original
        t_r = 1

    #build up index with TR increments
    index = pd.Index(np.arange(0,
                               t_r*data.shape[-1],
                               t_r),
                     name='time')

    try: #occassionaly results has one less TR than original data
        out_df =  pd.DataFrame(results,
                            index=index)
    except ValueError:
        out_df =  pd.DataFrame(results,
                            index=index[:-1])        
    return(out_df)

def get_onsets(events, task_conditions=['task'], scanner_times=None):
    onsets = events.loc[events.conditions.isin(task_conditions), 'onsets'].values
    #round to nearest scanner time if available
    if scanner_times is not None: 
        onsets = [min(scanner_times, key=lambda x:abs(x-i)) for i in onsets] #takes closest value
#         onsets = [scanner_times[scanner_times > i].min() for i in onsets] #takes closest _larger_ value
        
    return(onsets)



# BODY
sourcedata_layout = BIDSLayout(BIDS_dir) #https://github.com/VU-Cog-Sci/nideconv/blob/master/nideconv/utils/bids.py#L173

task_sources = glob(source_path % task)
task_funcs = glob(prep_path % task)
task_evs = glob(evs_path % task)
task_dsgns = glob(dsgn_path % task)


task_funcs.sort()
task_dsgns.sort()
task_sources.sort()
task_evs.sort()

print('num raw funcs', len(task_sources))
print('num mni funcs', len(task_funcs))
print('num ev files', len(task_evs))
print('num dsgn files', len(task_dsgns))

#initial nan array for group
subject_network_responses = np.empty((num_trs, num_nets, len(task_funcs)))
subject_network_responses[:] = np.nan

#loop through all participants
for idx, func in enumerate(task_funcs):
    
    #set up nan array for subject
    meaned_responses = np.empty((num_trs,num_nets))
    meaned_responses[:] = np.nan
    
    #make sure sub has all required files
    sub_str = func.split('sub-')[1].split('/')[0]
    print(sub_str)
    #get relavent sub strs
    sub_dsgn = [i for i in task_dsgns if sub_str in i]
    sub_source = [i for i in task_sources if sub_str in i]
    sub_evs = [i for i in task_evs if sub_str in i]
    
    #if they are missing a file, skip them
    if (len(sub_dsgn)==0) | (len(sub_source)==0) | (len(sub_evs)==0):
        print('missing something for sub-'+sub_str)
        subject_network_responses[:,:,idx] = meaned_responses
        continue

    #grab sub files
    sub_dsgn = sub_dsgn[0]
    sub_source = sub_source[0]
    sub_evs = sub_evs[0]
    
    #get sub data
    meta = sourcedata_layout.get_metadata(sub_source)
    confounds= pd.read_csv(sub_dsgn) 
    evs = pd.read_csv(sub_evs)

    TR = meta['RepetitionTime'] #0.68s



    #extract timeseries for the task
    tc = extract_timecourse_from_nii(yeo['thick_17'],
                                     func,
                                     t_r=TR,
                                     atlas_type='labels',
                                     low_pass=None,
                                     high_pass=1./128,
                                     confounds=confounds[confounds_to_include].values)

    # get task onsets, shift to the nearest TR
    onsets = get_onsets(evs, task_conditions=task_conditions, scanner_times=tc.index)

    # take num_trs of signal for each network at each task onset
    timelocked_data = np.zeros((num_trs, num_nets, len(onsets)))
    for jdx, onset in enumerate(onsets):
        #initialize curr_resp
        curr_resp = np.empty((num_trs, num_nets))
        curr_resp[:] = np.nan
        #need to do in case curr_df is trial with less than 20TRs left
        curr_df = tc.loc[onset:onset+(num_trs*TR), :].head(num_trs)
        curr_resp[:len(curr_df), :len(curr_df.columns)] = curr_df.values 
        # add to timelocked_data 
        timelocked_data[:,:, jdx] = curr_resp
        
    # mean across onsets
    meaned_responses = np.mean(timelocked_data, axis=2)
    
    #append subj means to group
    subject_network_responses[:,:,idx] = meaned_responses

#save group data
np.save('%s_task_17network_responses_full' % task, subject_network_responses) 
#get and save group mean
group_resps = np.nanmean(subject_network_responses, axis=2)
np.save('%s_task_17network_responses_group' %task, group_resps) 
