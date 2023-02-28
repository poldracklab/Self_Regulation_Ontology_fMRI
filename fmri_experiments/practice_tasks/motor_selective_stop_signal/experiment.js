/* ************************************ */
/* Define helper functions */
/* ************************************ */

var ITIs = [0.0,0.0,0.1,0.3,0.7,0.0,0.1,0.3,0.0,0.1,0.3,0.2,0.1,0.4,0.3,0.5,0.3,0.2,0.5,0.3,0.1,0.0,0.4,0.0,0.1,0.0,0.1,0.1,0.0,0.6,0.0,0.0,0.1,0.3,0.7,0.0,0.1,0.3,0.0,0.1,0.3,0.2,0.1,0.4,0.3,0.5,0.3,0.2,0.5,0.3,0.1,0.0,0.4,0.0,0.1,0.0,0.1,0.1,0.0,0.6]

var get_ITI = function() {
  return 2250 + ITIs.shift()*1000
 }

var randomDraw = function(lst) {
	var index = Math.floor(Math.random() * (lst.length))
	return lst[index]
}

var permute = function(input) {
    var permArr = [],
        usedChars = [];
    return (function main() {
        for (var i = 0; i < input.length; i++) {
            var ch = input.splice(i, 1)[0];
            usedChars.push(ch);
            if (input.length == 0) {
                permArr.push(usedChars.slice());
            }
            main();
            input.splice(i, 0, ch);
            usedChars.pop();
        }
        return permArr;
    })();
}


/* Staircase procedure. After each successful stop, make the stop signal delay longer (making stopping harder) */
var updateSSD = function(data) {
	if (data.condition == 'stop') {
		if (data.rt == -1 && SSD < 1000) {
			SSD = SSD + 50
		} else if (data.rt != -1 && SSD > 0) {
			SSD = SSD - 50
		}
	}
}

var getSSD = function() {
	return SSD
}

var getPracticeTrials = function() {
	var practice = []
	var trials = jsPsych.randomization.repeat(stimuli, practice_len/4)
	for (i=0; i<trials.length; i++) {
		trials[i]['key_answer'] = trials[i].data.correct_response
	}
	var practice_block = {
		type: 'poldrack-categorize',
		timeline: trials, 
		is_html: true,
		choices: choices,
		timing_stim: 850,
		timing_response: 1850,
		correct_text: '<div class = feedbackbox><div style="color:#4FE829"; class = center-text>Correct!</p></div>',
		incorrect_text: '<div class = feedbackbox><div style="color:red"; class = center-text>Incorrect</p></div>',
		timeout_message: '<div class = feedbackbox><div class = center-text>Too Slow</div></div>',
		show_stim_with_feedback: false,
		timing_feedback_duration: 500,
		timing_post_trial: 250,
		on_finish: function(data) {
			jsPsych.data.addDataToLastTrial({
				exp_stage: 'practice',
				trial_num: current_trial,
			})
			current_trial += 1
			console.log('Trial: ' + current_trial +
              '\nCorrect Response? ' + data.correct + ', RT: ' + data.rt)
		}
	}
	practice.push(practice_block)
	return practice
}

/* ************************************ */
/* Define experimental variables */
/* ************************************ */
var practice_repeats = 0
// task specific variables
// Define and load images
var prefix = '/static/experiments/motor_selective_stop_signal/images/'
var images = [prefix + 'circle.png', prefix + 'Lshape.png', prefix + 'rhombus.png', prefix +
	'triangle.png'
]
var permutations = permute([0,1,2,3])
var permutation_index = randomDraw([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24])
var permutation = permutations[permutation_index]
// permutation = 0 // Change value if you have to restart the task


images = [images[permutation[0]], images[permutation[1]], 
		images[permutation[2]], images[permutation[3]]]
jsPsych.pluginAPI.preloadImages(images);

/* Stop signal delay in ms */
var SSD = 250
var stop_signal =
	'<div class = coverbox></div><div class = stopbox><div class = centered-shape id = stop-signal></div><div class = centered-shape id = stop-signal-inner></div></div>'

/* Instruction Prompt */
var choice_order = randomDraw([0,1])
// choice_order = 0 // Change value if you have to restart the task
var possible_responses = [
	["index finger", 37],
	["middle finger", 40]
]
if (choice_order == 1) {
	possible_responses = [
		["middle finger", 40],
		["index finger", 37]
	]
}
var choices = [possible_responses[0][1], possible_responses[1][1]]

var prompt_text = '<ul list-text>' + 
					'<li><div class = prompt_container><img class = prompt_stim src = ' + 
					images[0] + '></img>' + possible_responses[0][0] + '</div></li>' +
					'</li><li><div class = prompt_container><img class = prompt_stim src = ' +
					images[1] + '></img>'  + possible_responses[0][0] + '</div></li>' +
					' </li><li><div class = prompt_container><img class = prompt_stim src = ' 
					+ images[2] + '></img>' + possible_responses[1][0] + '</div></li>' +
					' </li><li><div class = prompt_container><img class = prompt_stim src = ' +
					images[3] + '></img>' + possible_responses[1][0] + '</div></li></ul>'
	
/* Global task variables */
var current_trial = 0
var rtMedians = []
var stopAccMeans =[]
var RT_thresh = 1000
var rt_diff_thresh = 75
var missed_response_thresh = 0.1
var accuracy_thresh = 0.8
var stop_thresh = 0.2
var motor_thresh = 0.6
var stop_response = possible_responses[0]
var ignore_response = possible_responses[1]
var practice_len = 20
var test_block_data = [] // records the data in the current block to calculate feedback
var test_block_len = 30
var num_blocks = 2
var test_len = test_block_len*num_blocks

/* Define Stims */
var stimuli = [{
	stimulus: '<div class = coverbox></div><div class = shapebox><img class = stim src = ' + images[0] + '></img></div>',
	data: {
		correct_response: possible_responses[0][1],
		trial_id: 'stim',
	}
}, {
	stimulus: '<div class = coverbox></div><div class = shapebox><img class = stim src = ' + images[1] + '></img></div>',
	data: {
		correct_response: possible_responses[0][1],
		trial_id: 'stim',
	}
}, {
	stimulus: '<div class = coverbox></div><div class = shapebox><img class = stim src = ' + images[2] + '></img></div>',
	data: {
		correct_response: possible_responses[1][1],
		trial_id: 'stim',
	}
}, {
	stimulus: '<div class = coverbox></div><div class = shapebox><img class = stim src = ' + images[3] + '></img></div>',
	data: {
		correct_response: possible_responses[1][1],
		trial_id: 'stim',
	}
}]

// set up stim order based on optimized trial sequence
var stim_index = [0,0,2,1,0,1,0,0,2,2,2,2,0,0,0,1,1,2,0,0,1,0,0,1,0,0,0,0,0,2,
				1,0,2,1,0,1,0,0,2,0,2,2,0,2,0,0,1,2,0,0,1,0,0,1,0,0,0,0,0,2]
var test_stims = []
var go_stims = jsPsych.randomization.repeat(stimuli, test_len*0.6 / 4)
var stop_stims = jsPsych.randomization.repeat(stimuli.slice(0,2), test_len*0.2 / 2)
var ignore_stims = jsPsych.randomization.repeat(stimuli.slice(2,4), test_len*0.2 / 2)
for (var i=0; i<stim_index.length; i++) {
	var stim = {}
	if (stim_index[i] == 0) {
		stim.stim = jQuery.extend({}, go_stims.shift())
		stim.type = 'go'
	} else if (stim_index[i] == 1) {
		stim.stim = jQuery.extend({},stop_stims.shift())
		stim.type = 'stop'
	} else {
		stim.stim = jQuery.extend({},ignore_stims.shift())
		stim.type = 'ignore'
	}
	test_stims.push(stim)
	// refill if necessary
	if (go_stims.length == 0) {
		go_stims = jsPsych.randomization.repeat(stimuli, test_len*0.6 / 4)
	} 
	if (stop_stims.length == 0) {
		stop_stims = jsPsych.randomization.repeat(stimuli.slice(0,2), test_len*0.2 / 2)
	} 
	if (ignore_stims.length == 0) {
		ignore_stims = jsPsych.randomization.repeat(stimuli.slice(2,4), test_len*0.2 / 2)
	} 
}
/* ************************************ */
/* Set up jsPsych blocks */
/* ************************************ */
/* define static blocks */
var start_test_block = {
  type: 'poldrack-single-stim',
  stimulus: '<div class = centerbox><div class = center-text>Get ready!</p></div>',
  is_html: true,
  choices: [32],
  timing_stim: -1, 
  timing_response: -1,
  response_ends_trial: true,
  data: {
    trial_id: "test_start_block"
  },
  timing_post_trial: 500,
  on_finish: function() {
  	exp_stage = 'test'
  }
};

 var end_block = {
	type: 'poldrack-single-stim',
	stimulus: '<div class = centerbox><div class = center-text><i>Fin</i></div></div>',
	is_html: true,
	choices: [32],
	timing_response: -1,
	response_ends_trial: true,
	data: {
		trial_id: "end",
		exp_id: 'motor_selective_stop_signal'
	},
	timing_post_trial: 0,
	on_finish: function() {
		console.log('Permutation Index: ' + permutation_index)
		console.log('Choice Order: ' + choice_order)
	}
};

 var instructions_block = {
  type: 'poldrack-single-stim',
  stimulus: '<div class = instructbox><p class = instruct-text>Only one key is correct for each shape. The correct keys are as follows:' + prompt_text +
		'</p><p class = instruct-text><strong>Do not respond if you see the red star if your response was going to be your ' + stop_response[0] + '!</strong></p><p class = instruct-text>We will start with practice</p></div>',
  is_html: true,
  timing_stim: -1, 
  timing_response: -1,
  response_ends_trial: true,
  choices: [32],
  data: {
    trial_id: "instructions",
  },
  timing_post_trial: 0,
	on_finish: function() {
		console.log('Permutation Index: ' + permutation_index)
		console.log('Choice Order: ' + choice_order)
	}
};

// set up practice trials
var practice_trials = getPracticeTrials()
var practice_loop = {
  timeline: practice_trials,
  loop_function: function(data) {
    practice_repeats+=1
    total_trials = 0
    correct_trials = 0
    for (var i = 0; i < data.length; i++) {
      if (data[i].trial_id == 'stim') {
        total_trials+=1
        if (data[i].correct == true) {
          correct_trials+=1
        }
      }
    }
    console.log('Practice Block Accuracy: ', correct_trials/total_trials)
    if (correct_trials/total_trials > .75 || practice_repeats == 3) {
    	current_trial = 0
      return false
    } else {
      practice_trials = getPracticeTrials()
      return true
    }
  }
};

/* ************************************ */
/* Set up experiment */
/* ************************************ */

var motor_selective_stop_signal_experiment = []
motor_selective_stop_signal_experiment.push(instructions_block);
motor_selective_stop_signal_experiment.push(practice_loop);


/* Test blocks */
// Loop through the multiple blocks within each condition
for (b = 0; b < num_blocks; b++) {
	stop_signal_exp_block = []

	// Loop through each trial within the block
	stop_signal_exp_block.push(start_test_block)
	for (i = 0; i < test_block_len; i++) {
		var current_stim = test_stims.shift()
		var trial_stim = current_stim.stim.stimulus
		var trial_data = current_stim.stim.data
	    trial_data = $.extend({}, trial_data)
	    trial_data.condition = current_stim.type
	    var stop_trial = 'stop'
	    if (current_stim.type == 'go') {
	    	stop_trial = 'go'
	    }
		var stop_signal_block = {
			type: 'stop-signal',
			stimulus: trial_stim,
			SS_stimulus: stop_signal,
			SS_trial_type: stop_trial,
			data: trial_data,
			is_html: true,
			choices: choices,
			timing_stim: 850,
			timing_response: get_ITI,
			SSD: getSSD,
			timing_SS: 500,
			timing_post_trial: 0,
			on_finish: function(data) {
				correct = false
				if (data.key_press == data.correct_response) {
					correct = true
				}
				updateSSD(data)
				jsPsych.data.addDataToLastTrial({
					exp_stage: "test",
					stop_response: stop_response[1],
					trial_num: current_trial
				})
				current_trial += 1
				test_block_data.push(data)
				console.log('Trial: ' + current_trial +
              '\nCorrect Response? ' + correct + ', RT: ' + data.rt + ', SSD: ' + data.SS_delay)
			}
		}
		stop_signal_exp_block.push(stop_signal_block)
	}

	motor_selective_stop_signal_experiment = motor_selective_stop_signal_experiment.concat(
		stop_signal_exp_block)

}

motor_selective_stop_signal_experiment.push(end_block)