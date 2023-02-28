import numpy as np
import pandas as pd
from expanalysis.experiments.jspsych_processing import calc_discount_fixed_DV
from utils import get_survey_items_order
# *********************************
# helper functions
# *********************************
def get_drop_columns(df, columns=None, use_default=True):
    """
    defines columns to drop when converting from _clean to _event
    files each event file. Generates a list of columns to drop,
    constrains it to columns already in the dataframe.
    """
    default_cols = ['correct_response', 'exp_stage',
                    'feedback_duration', 'possible_responses',
                    'stim_duration', 'text', 'time_elapsed',
                   'timing_post_trial', 'trial_num']
    drop_columns = []
    if columns is not None:
        drop_columns = columns
    if use_default == True:
        #if true, drop columns come from argument and from default (inclusive or)
        drop_columns = set(default_cols) | set(drop_columns)
     #drop columns only included if they appear in the dataframe   
    drop_columns = set(df.columns) & set(drop_columns)
    return drop_columns

def get_junk_trials(df):
    """
    junk trials are defined here as trials with responses faster than
    50 ms, or incorrect trials
    """
    junk = pd.Series(False, df.index)
    if 'correct' in df.columns:
             junk = np.logical_or(junk,np.logical_not(df.correct))
    if 'rt' in df.columns:
            junk = np.logical_or(junk,df.rt < 50)
    return junk

def get_movement_times(df):
    """
    time elapsed is evaluated at the end of a trial, so we have to subtract
    timing post trial and the entire block duration to get the time when
    the trial started. Then add the reaction time to get the time of movement
    """
    trial_time = df.time_elapsed - df.block_duration + \
                 df.rt
    return trial_time
    
def get_trial_times(df):
    """
    time elapsed is evaluated at the end of a trial, so we have to subtract
    timing post trial and the entire block duration to get the time when
    the trial started
    """
    trial_time = df.time_elapsed - df.block_duration
    return trial_time

def process_rt(events_df):
    """changes -1 rts (javascript no response) to nan, changes column from rt -> response_time """
    events_df.rt.replace({-1: np.nan}, inplace=True) #replaces no response rts with nan
    events_df.rename(columns={'rt': 'response_time'}, inplace=True) 
    
def row_match(df,row_list):
    bool_list = pd.Series(True,index=df.index)
    for i in range(len(row_list)):
        bool_list = bool_list & (df.iloc[:,i] == row_list[i])
    return bool_list[bool_list].index    


def create_events(df, exp_id, aim, duration=None):
    """
    defines what function to reference to create each task-specific event file 
    takes in a dataframe from processed data, and exp_id and a duration
    """ 
    events_df = None
    lookup = {'attention_network_task': create_ANT_event,
              'columbia_card_task_fmri': create_CCT_event,
              'discount_fixed': create_discountFix_event,
              'dot_pattern_expectancy': create_DPX_event,
              'motor_selective_stop_signal': create_motorSelectiveStop_event,
              'stop_signal': create_stopSignal_event,
              'stroop': create_stroop_event,
              'survey_medley': create_survey_event,
              'twobytwo': create_twobytwo_event,
              'ward_and_allport': create_WATT_event,
              'manipulation_task': create_manipulation_event}
    fun = lookup.get(exp_id)
    if fun is not None:
        if exp_id != 'columbia_card_task_fmri':
            events_df = fun(df, aim, duration=duration)
        else:
            events_df = fun(df, aim)
    return events_df



# *********************************
# Functions to create event files
# *********************************

def create_ANT_event(df, aim, duration=None):
    columns_to_drop = get_drop_columns(df)
    events_df = df[df['time_elapsed']>0]
    # add junk regressor
    events_df.loc[:,'junk'] = get_junk_trials(df)
    # reorganize and rename columns in line with BIDs specifications

    if duration is None:
        events_df.insert(0,'duration',events_df.stim_duration)
    else:
        events_df.insert(0,'duration',duration)
    # time elapsed is at the end of the trial, so have to remove the block
    # duration
    events_df.insert(0,'onset',get_trial_times(df))
    # process RT
    process_rt(events_df)
    # convert milliseconds to seconds
    events_df.loc[:,['response_time','onset','duration']]/=1000
    # drop unnecessary columns
    events_df = events_df.drop(columns_to_drop, axis=1)
    
    mean_rts = pd.read_csv('../behavioral_data/%s/processed/group_data/task_mean_rts.csv' % aim)
    if 'attention_network_task' in mean_rts.columns:
        group_RT = np.mean(mean_rts['attention_network_task'])/1000
        events_df.insert(0,'group_RT', group_RT)
    
    return events_df

def create_CCT_event(df, aim):
    columns_to_drop = get_drop_columns(df, columns = ['cards_left',
                                                      'clicked_on_loss_card',
                                                      'round_points',
                                                      'which_round'])

    events_df = df[df['time_elapsed']>0]
    # add junk regressor
    events_df.loc[:,'junk'] = get_junk_trials(df)
    # reorganize and rename columns in line with BIDs specifications
    events_df.insert(0, 'duration', events_df.block_duration)
    # time elapsed is at the end of the trial, so have to remove the block
    # duration
    events_df.insert(0,'onset',get_trial_times(df))
    # change onset of ITI columns to reflect the fact that the stimulus changes 750 ms after blcok starts
    ITI_trials = events_df.query('trial_id == "ITI"').index
    events_df.loc[ITI_trials, 'onset'] += 750
    events_df.loc[ITI_trials, 'duration'] = events_df.loc[ITI_trials, 'stim_duration']-750
    # add motor onsets
    events_df.insert(2,'movement_onset',get_movement_times(df))
    # process RT
    process_rt(events_df)
    # convert milliseconds to seconds
    events_df.loc[:,['response_time','onset','block_duration',
                     'duration','movement_onset']]/=1000
    # add feedback columns
    events_df.loc[:,'feedback'] = events_df.clicked_on_loss_card \
                                    .apply(lambda x: int(not x))
    # drop unnecessary columns
    events_df = events_df.drop(columns_to_drop, axis=1)
    
    mean_rts = pd.read_csv('../behavioral_data/%s/processed/group_data/task_mean_rts.csv' % aim)
    if 'columbia_card_task_fmri' in mean_rts.columns:
        group_RT = np.mean(mean_rts['columbia_card_task_fmri'])/1000
        events_df.insert(0,'group_RT', group_RT)
    return events_df

def create_discountFix_event(df, aim, duration=None):
    columns_to_drop = get_drop_columns(df)
    events_df = df[df['time_elapsed']>0]
    # add junk regressor
    events_df.loc[:,'junk'] = get_junk_trials(df)



    # reorganize and rename columns in line with BIDs specifications
    events_df.loc[:,'trial_type'] = events_df.choice
    if duration is None:
        events_df.insert(0,'duration',events_df.stim_duration)
    else:
        events_df.insert(0,'duration',duration)
    # time elapsed is at the end of the trial, so have to remove the block
    # duration
    events_df.insert(0,'onset',get_trial_times(df))
    # process RT
    process_rt(events_df)
    # convert milliseconds to seconds
    events_df.loc[:,['response_time','onset','duration']]/=1000
    
    
    #additional parametric regressors:
    #subjective value
    worker_id = df.worker_id.unique()[0]
    discount_rate = calc_discount_fixed_DV(df)[0].get(worker_id).get('hyp_discount_rate_glm').get('value')
    larger_value =  events_df.large_amount/(1+discount_rate*events_df.later_delay)
    subjective_choice_value = [larger_value[i] if events_df['trial_type'][i]=='larger_later' else 20 for i in events_df.index]
    events_df.insert(0, 'subjective_choice_value', subjective_choice_value - np.mean(subjective_choice_value)) #insert demeaned subjective choice value
    
    #inverse_delay
    inverse_delay = 1/events_df.later_delay
    events_df.insert(0, 'inverse_delay', inverse_delay - np.mean(inverse_delay)) #insert demeaned inverse delay

    # drop unnecessary columns
    events_df = events_df.drop(columns_to_drop, axis=1)
    
    mean_rts = pd.read_csv('../behavioral_data/%s/processed/group_data/task_mean_rts.csv' % aim)
    if 'discount_fixed' in mean_rts.columns:
        group_RT = np.mean(mean_rts['discount_fixed'])/1000
        events_df.insert(0,'group_RT', group_RT)
    
    return events_df

def create_DPX_event(df, aim, duration=None):
    columns_to_drop = get_drop_columns(df)
    events_df = df[df['time_elapsed']>0]
    # add junk regressor
    events_df.loc[:,'junk'] = get_junk_trials(df)
    # reorganize and rename columns in line with BIDs specifications
    events_df.loc[:,'trial_type'] = events_df.condition
    # Cue-to-Probe time
    CPI=1000
    if duration is None:
        events_df.insert(0,'duration',events_df.stim_duration+CPI)
    else:
        events_df.insert(0,'duration',duration+CPI)
    # time elapsed is at the end of the trial, so have to remove the block
    # duration. We also want the trial
    onsets = get_trial_times(df)-CPI
    events_df.insert(0,'onset',onsets)
    # add motor onsets
    events_df.insert(2,'movement_onset',get_movement_times(df))
    # process RT
    process_rt(events_df)
    # convert milliseconds to seconds
    events_df.loc[:,['response_time','onset',
                     'duration','movement_onset']]/=1000
    # drop unnecessary columns
    events_df = events_df.drop(columns_to_drop, axis=1)
    
    mean_rts = pd.read_csv('../behavioral_data/%s/processed/group_data/task_mean_rts.csv' % aim)
    if 'dot_pattern_expectancy' in mean_rts.columns:
        group_RT = np.mean(mean_rts['dot_pattern_expectancy'])/1000
        events_df.insert(0,'group_RT', group_RT)
        
    return events_df

def create_manipulation_event(df, aim, duration=None):
    #this events file is different than the others and requires more processing to line information up 
   
    columns_to_drop = get_drop_columns(df, columns =['possible_responses', 'text', 'key_press', 'junk_tmp'])
    #cut off end trials at end of scan response & trials before scan starts
    #finds last instance of response == nan
    end_time = df[~np.isnan(df['response'])].iloc[-1] 
    end_time = end_time['time_elapsed']
    events_df = df[df['time_elapsed']>0]
    #sets events_df to only when time_elapsed 
    events_df = events_df[events_df['time_elapsed'] <= end_time]
                                             
    events_df = events_df.drop('trial_type', axis = 1)
    events_df.insert(0, 'duration', events_df.block_duration)
    
    #transform key press from JS key numbers to actual ratings
    events_df.loc[(events_df['key_press'] == 66), 'response'] = 1
    events_df.loc[(events_df['key_press'] == 89), 'response'] = 2
    events_df.loc[(events_df['key_press'] == 71), 'response'] = 3
    events_df.loc[(events_df['key_press'] == 82), 'response'] = 4
    events_df.loc[(events_df['key_press'] == 77), 'response'] = 5
    
    #fixes stim_type to be condition agnostic 
    events_df.stim_type = events_df.stim_type.replace('smoking', 'valence') 
    events_df.stim_type = events_df.stim_type.replace('food', 'valence')
    
    events_df['trial_type'] = events_df['stim_type']
    #creates response trials of interest 
    events_df.loc[(events_df['trial_type']=='valence') & (events_df['which_cue'] == 'NOW'), 'trial_type'] = 'present_valence'
    events_df.loc[(events_df['trial_type']=='valence') & (events_df['which_cue'] == 'LATER'), 'trial_type'] = 'future_valence'
    events_df.loc[(events_df['trial_type']=='neutral') & (events_df['which_cue'] == 'LATER'), 'trial_type'] = 'future_neutral'
    events_df.loc[(events_df['trial_type']=='neutral') & (events_df['which_cue'] == 'NOW'), 'trial_type'] = 'present_neutral'
  
    #shifts to match stim with onset time column
    events_df['which_cue'] = events_df['which_cue'].shift(-2)
    events_df['stim_type'] = events_df['stim_type'].shift(-1)
    
    #populate cue events in 'trial_type'
    events_df.loc[(events_df['trial_id']=='cue') & (events_df['which_cue'] == 'NOW'), 'trial_type'] = 'cue_present'
    events_df.loc[(events_df['trial_id']=='cue') & (events_df['which_cue'] == 'LATER'), 'trial_type'] = 'cue_future'
    
    #ceate probe events for 'trial_type'
    events_df.loc[(events_df['trial_id'] == 'probe') & (events_df['stim_type'] == 'neutral'), 'trial_type'] = 'neutral_probe'
    events_df.loc[(events_df['trial_id'] == 'probe') & (events_df['stim_type'] == 'valence'), 'trial_type'] = 'valence_probe'

    #and change null trial events to no_stim
    events_df.loc[(pd.isnull(events_df['trial_type'])), 'trial_type'] = 'no_stim'

    #make junk trials specific to manip 
    events_df.loc[:,'junk'] = np.logical_and(df.rt < 50, df.rt > 1)
    #creates junk for no response trials 
    events_df.loc[:, 'junk'] = np.logical_and(pd.isnull(events_df['response']), np.logical_and(events_df['trial_id'] == 'current_rating', events_df['trial_type'] != 'no_stim' ))
    #creates junk for cue and probe corresponding to no-response trials 
    events_df['junk_tmp'] = events_df['response'].shift(-1)
    events_df.loc[np.logical_and(pd.isnull(events_df['junk_tmp']), np.logical_and(events_df['trial_id'] == 'probe', events_df['trial_type'] != 'no_stim' )), 'junk'] = 'True'
    events_df['junk_tmp'] = events_df['response'].shift(-2)
    events_df.loc[np.logical_and(pd.isnull(events_df['junk_tmp']), np.logical_and(events_df['trial_id'] == 'cue', events_df['trial_type'] != 'no_stim' )), 'junk'] = 'True'

    # time elapsed is at the end of the trial, so have to remove the block
    # duration
    events_df.insert(0,'onset',get_trial_times(df))
    # process RT - drops no response RTs 
    process_rt(events_df)
    # convert milliseconds to seconsds
    events_df.loc[:,['response_time','onset','block_duration', 'duration']]/=1000
    # drop unnecessary columns defined at top of function
    events_df = events_df.drop(columns_to_drop, axis=1)
    
    mean_rts = pd.read_csv('../behavioral_data/%s/processed/group_data/task_mean_rts.csv' % aim)
    if 'manipulation_task' in mean_rts.columns:
        group_RT = np.mean(mean_rts['manipulation_task'])/1000
        events_df.insert(0,'group_RT', group_RT)
        
    return events_df

def create_motorSelectiveStop_event(df, aim, duration=None):
    columns_to_drop = get_drop_columns(df, columns = ['condition',
                                                      'SS_duration',
                                                      'SS_stimulus',
                                                      'SS_trial_type'])
    events_df = df[df['time_elapsed']>0]
    # add junk regressor
    events_df.loc[:,'junk'] = get_junk_trials(df)
    stops = events_df.query("stopped == True and condition == 'stop'").index
    events_df.loc[stops,'junk'] = False
    # create condition column
    crit_key = events_df.query('condition=="stop"') \
                .correct_response.unique()[0]
    noncrit_key = events_df.query('condition=="ignore"') \
                    .correct_response.unique()[0]
    condition_df = events_df.loc[:,['correct_response',
                                    'SS_trial_type','stopped']]
    condition = pd.Series(index=events_df.index)
    condition[row_match(condition_df, [crit_key,'go',False])] = 'crit_go'
    condition[row_match(condition_df,
                        [crit_key,'stop',True])] = 'crit_stop_success'
    condition[row_match(condition_df,
                        [crit_key,'stop',False])] = 'crit_stop_failure'
    condition[row_match(condition_df,
                        [noncrit_key,'stop',False])] = 'noncrit_signal'
    condition[row_match(condition_df,
                        [noncrit_key,'go',False])] = 'noncrit_nosignal'
    
    events_df.loc[:,'trial_type'] = condition
    
     #fix stop success correctness 
    events_df.loc[events_df['trial_type'] == 'crit_stop_success', ['correct']] = 1
    
    if duration is None:
        events_df.insert(0,'duration',events_df.stim_duration)
    else:
        events_df.insert(0,'duration',duration)
    # time elapsed is at the end of the trial, so have to remove the block
    # duration
    events_df.insert(0,'onset',get_trial_times(df))
    # process RT
    process_rt(events_df)
    # convert milliseconds to seconds
    events_df.loc[:,['response_time','onset','duration']]/=1000
    # drop unnecessary columns
    events_df = events_df.drop(columns_to_drop, axis=1)
    
    mean_rts = pd.read_csv('../behavioral_data/%s/processed/group_data/task_mean_rts.csv' %aim)
    if 'motor_selective_stop_signal' in mean_rts.columns:
        group_RT = np.mean(mean_rts['motor_selective_stop_signal'])/1000
        events_df.insert(0,'group_RT', group_RT)
        
    return events_df

def create_stopSignal_event(df, aim, duration=None):

    events_df = df[df['time_elapsed']>0]
    # add junk regressor
    events_df.loc[:,'junk'] = get_junk_trials(df)
    stops = events_df.query("stopped == True and SS_trial_type == 'stop'").index
    events_df.loc[stops,'junk'] = False
    # reorganize and rename columns in line with BIDs specifications
    # create condition label
    SS_success_trials = events_df.query('SS_trial_type == "stop" \
                                        and stopped == True').index
    SS_fail_trials = events_df.query('SS_trial_type == "stop" \
                                        and stopped == False').index
    events_df.loc[:,'condition'] = 'go'
    events_df.loc[SS_success_trials,'condition'] = 'stop_success'
    events_df.loc[SS_fail_trials,'condition'] = 'stop_failure'
    events_df.loc[:,'trial_type'] = events_df.condition
    
    events_df.loc[events_df['trial_type'] == 'stop_success', ['correct']] = 1
    # duration    
    if duration is None:
        events_df.insert(0,'duration',events_df.stim_duration)
    else:
        events_df.insert(0,'duration',duration)
    # time elapsed is at the end of the trial, so have to remove the block

    events_df.insert(0,'onset',get_trial_times(df))
    # process RT
    process_rt(events_df)
    # convert milliseconds to seconds
    events_df.loc[:,['response_time','onset','duration']]/=1000
    # get and drop unnecessary columns
    columns_to_drop = get_drop_columns(events_df, columns = ['condition',
                                                      'SS_duration',
                                                      'SS_stimulus',
                                                      'SS_trial_type'])    
    events_df = events_df.drop(columns_to_drop, axis=1)
    
    mean_rts = pd.read_csv('../behavioral_data/%s/processed/group_data/task_mean_rts.csv' % aim)
    if 'stop_signal' in mean_rts.columns:
        group_RT = np.mean(mean_rts['stop_signal'])/1000
        events_df.insert(0,'group_RT', group_RT)
    return events_df

def create_stroop_event(df, aim, duration=None):
    columns_to_drop = get_drop_columns(df)
    events_df = df[df['time_elapsed']>0]
    # add junk regressor
    events_df.loc[:,'junk'] = get_junk_trials(df)
    # reorganize and rename columns in line with BIDs specifications
    events_df.loc[:,'trial_type'] = events_df.condition
    if duration is None:
        events_df.insert(0,'duration',events_df.stim_duration)
    else:
        events_df.insert(0,'duration',duration)
    # time elapsed is at the end of the trial, so have to remove the block
    # duration
    events_df.insert(0,'onset',get_trial_times(df))
    # process RT
    process_rt(events_df)
    # convert milliseconds to seconds
    events_df.loc[:,['response_time','onset','duration']]/=1000
    # drop unnecessary columns
    events_df = events_df.drop(columns_to_drop, axis=1)
    
    mean_rts = pd.read_csv('../behavioral_data/%s/processed/group_data/task_mean_rts.csv' % aim)
    if 'stroop' in mean_rts.columns:
        group_RT = np.mean(mean_rts['stroop'])/1000
        events_df.insert(0,'group_RT', group_RT)
        
    return events_df

def create_survey_event(df, aim, duration=None):
    columns_to_drop = get_drop_columns(df,
                                       use_default=False,
                                       columns = ['block_duration',
                                                  'key_press',
                                                  'options',
                                                  'response',
                                                  'stim_duration',
                                                  'text',
                                                  'time_elapsed',
                                                  'timing_post_trial',
                                                  'trial_id'])
    events_df = df[df['time_elapsed']>0]
    # add junk regressor
    junk = get_junk_trials(df)
    # response with a key outside of item responses
    if 'item_responses'  in df.columns:
        wrong_response = df.apply(lambda x: str(x['key_press']) not in x['item_responses'], axis=1)
        events_df.loc[:, 'junk'] = np.logical_or(junk, wrong_response)
    else:
        events_df.loc[:, 'junk'] = junk
    # add signifiers for each question
    events_df['trial_type'] = df['item_text'].map(get_survey_items_order())
    # add duration and response regressor
    if duration is None:
        events_df.insert(0,'duration',events_df.stim_duration)
    else:#
        events_df.insert(0,'duration',duration)
    # time elapsed is at the end of the trial, so have to remove the block
    # duration
    events_df.insert(0,'onset',get_trial_times(df))
    # add motor onsets
    events_df.insert(2,'movement_onset',get_movement_times(df))
    # process RT
    process_rt(events_df)
    # convert milliseconds to seconds
    events_df.loc[:,['response_time','onset','duration',
                     'movement_onset']]/=1000
    # drop unnecessary columns
    events_df = events_df.drop(columns_to_drop, axis=1)
    
    mean_rts = pd.read_csv('../behavioral_data/%s/processed/group_data/task_mean_rts.csv' % aim)
    if 'survey_medley' in mean_rts.columns:
        group_RT = np.mean(mean_rts['survey_medley'])/1000
        events_df.insert(0,'group_RT', group_RT)
        
    return events_df

def create_twobytwo_event(df,aim, duration=None):
    columns_to_drop = get_drop_columns(df)
    events_df = df[df['time_elapsed']>0]
    # add junk regressor
    events_df.loc[:,'junk'] = get_junk_trials(df)
    # reorganize and rename columns in line with BIDs specifications
    # add CTI to RT
    df.loc[:, 'rt'] = [rt+CTI if rt > -1 else -1 for rt,CTI in zip(df.rt, df.CTI)]
    if duration is None:
        events_df.insert(0,'duration',events_df.stim_duration)
    else:
        events_df.insert(0,'duration',duration)
    # time elapsed is at the end of the trial, so have to remove the block
    # duration
    events_df.insert(0,'onset',get_trial_times(df)-df.CTI)
    # add motor onsets
    events_df.insert(2,'movement_onset',get_movement_times(df))
    # process RT
    process_rt(events_df)
    # convert milliseconds to seconds
    events_df.loc[:,['response_time','onset',
                     'duration','movement_onset']]/=1000
    # drop unnecessary columns
    events_df = events_df.drop(columns_to_drop, axis=1)
    
    mean_rts = pd.read_csv('../behavioral_data/%s/processed/group_data/task_mean_rts.csv' % aim)
    if 'twobytwo' in mean_rts.columns:
        group_RT = np.mean(mean_rts['twobytwo'])/1000
        events_df.insert(0,'group_RT', group_RT)
        
    return events_df

def create_WATT_event(df,aim, duration):
    columns_to_drop = get_drop_columns(df, columns = ['correct',
                                                      'current_position',
                                                      'goal_state',
                                                      'min_moves',
                                                      'num_moves_made',
                                                      'problem_time',
                                                      'start_state'])

    events_df = df[df['exp_stage']=='test']
    # add junk regressor
    events_df.loc[:,'junk'] = False
    # get planning, movement, and feedback index
    planning_moves = events_df.query('trial_id == "to_hand"' +
                                  'and num_moves_made==1').index
    other_moves = events_df.query('not (trial_id == "to_hand"' +
                                  'and num_moves_made==1)' +
                                  ' and trial_id != "feedback"').index
    feedback = events_df.query('trial_id == "feedback"').index
    # add planning indicator
    events_df.insert(1,'planning',0)
    events_df.loc[planning_moves,'planning'] = 1
    # ** Durations **
    events_df.insert(0, 'duration', 0)
    # add durations for planning
    events_df.loc[planning_moves,'duration'] = duration['planning_time']
    # add durations for planning
    events_df.loc[other_moves,'duration'] = duration['move_time']

    # add durations for feedback
    events_df.loc[feedback, 'duration'] = events_df.loc[feedback, 'block_duration']

    # ** Onsets **
    # time elapsed is at the end of the trial, so have to remove the block
    # duration
    events_df.insert(0,'onset',get_trial_times(df))
    # add motor onsets
    events_df.insert(2,'movement_onset',get_movement_times(df))
    # process RT
    process_rt(events_df)
    # convert milliseconds to seconds
    events_df.loc[:,['onset','duration',
                     'response_time','movement_onset']]/=1000
    # drop unnecessary columns
    events_df = events_df.drop(columns_to_drop, axis=1)
    
    mean_rts = pd.read_csv('../behavioral_data/%s/processed/group_data/task_mean_rts.csv' % aim)
    if 'ward_and_allport' in mean_rts.columns:
        group_RT = np.mean(mean_rts['ward_and_allport'])/1000
        events_df.insert(0,'group_RT', group_RT)
        
    return events_df
