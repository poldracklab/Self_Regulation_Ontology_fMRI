/* ************************************ */
/* Define helper functions */
/* ************************************ */

var ITIs = [1.224,0.408,0.816,0.408,0.136,0.136,0.0,0.0,0.272,0.408,0.0,0.136,0.0,0.408,0.272,0.0,0.272,0.0,0.0,0.272,0.136,0.0,0.0,0.0,0.0,0.0,0.136,0.0,0.0,0.136,0.0,0.136,0.68,0.272,0.136,0.0,0.136,0.68,0.272,0.0,0.0,0.136,0.0,0.0,0.0,0.272,0.408,0.0,0.0,0.0,0.272,0.136,0.0,0.544,0.272,0.272,0.0,0.0,0.136,0.0,0.136,0.272,0.136,0.272,0.0,0.816,0.408,0.0,0.544,0.136,0.0,0.0,0.136,0.136,0.272,1.224,0.0,0.0,0.272,0.136,0.0,0.0,0.0,0.68,0.0,0.272,0.0,0.272,0.952,0.0,0.0,0.0,0.0,0.136,0.0,0.0,0.0,0.272,0.136,0.0,0.136,0.816,0.408,0.0,0.136,0.136,0.136,0.544,0.136,0.0,0.0,0.0,0.0,0.136,0.0,0.0,0.0,0.136,0.136,0.136,0.136,0.68,0.544,0.272,0.272,0.408,0.136,0.272,0.0,0.136,0.272,0.0,0.68,0.0,0.0,0.0,0.272,0.0,0.0,0.0,0.68,0.0,0.136,0.408,0.136,0.0,0.0,0.544,0.136,0.544,0.68,0.0,0.272,1.088,0.0,0.136,0.136,0.0,0.272,0.0,0.136,0.136,0.544,0.0,0.136,0.136,0.136,0.0,0.136,0.0,0.136,0.816,0.136,0.0,0.0,0.272,0.0,0.0,0.0,0.408,0.272,0.136,0.0,0.0,0.136,0.0,0.136,0.408,0.136,0.0,0.136,0.272,0.0,0.408,0.0,0.136,0.408,0.136,0.408,0.136,0.0,0.272,0.0,0.272,0.272,0.952,0.68,0.136,0.272,0.272,0.136,0.408,0.136,0.136,0.0,0.0,0.0,0.0,0.0,0.272,0.408,0.0,0.136,0.0,0.136,0.544,0.68,1.088,0.136,0.544,0.0,0.136,0.0,0.408,0.0,0.0,0.0,0.68,0.272,0.408]
var get_ITI = function() {
  return 2000 + ITIs.shift()*1000
}

var randomDraw = function(lst) {
  var index = Math.floor(Math.random() * (lst.length))
  return lst[index]
}

var getInstructFeedback = function() {
  return '<div class = centerbox><p class = center-block-text>' + feedback_instruct_text +
    '</p></div>'
}

// Task Specific Functions
var getKeys = function(obj) {
  var keys = [];
  for (var key in obj) {
    keys.push(key);
  }
  return keys
}

var genStims = function(n) {
  stims = []
  for (var i = 0; i < n; i++) {
    var number = randomDraw('12346789')
    var color = randomDraw(['orange', '#1F45FC'])
    var stim = {
      number: parseInt(number),
      color: color
    }
    stims.push(stim)
  }
  return stims
}

var getCTI = function() {
  return CTI
}

/* Index into task_switches using the global var current_trial. Using the task_switch and cue_switch
change the task. If "stay", keep the same task but change the cue based on "cue switch". 
If "switch", switch to the other task and randomly draw a cue_i
*/
var setStims = function() {
  switch (task_switches[current_trial].task_switch) {
    case "stay":
      if (task_switches[current_trial].cue_switch == "switch") {
        cue_i = 1 - cue_i
      }
      break
    case "switch":
      cue_i = randomDraw([0, 1])
      if (curr_task == "color") {
        curr_task = "magnitude"
      } else {
        curr_task = "color"
      }
      break
  }
  curr_cue = tasks[curr_task].cues[cue_i]
  curr_stim = stims[current_trial]
  CTI = task_switches[current_trial].CTI
}

var getCue = function() {
  var cue_html = '<div class = upperbox><div class = "center-text" >' + curr_cue +
    '</div></div><div class = lowerbox><div class = fixation>+</div></div>'
  return cue_html
}

var getStim = function() {
  var stim_html = '<div class = upperbox><div class = "center-text" >' + curr_cue +
    '</div></div><div class = lowerbox><div class = "stim-text" style=color:' + curr_stim.color +
    ';>' + curr_stim.number + '</div>'
  return stim_html
}

get_instructions = function() {
  return '<div class = centerbox><div class = center-text style="font-size:40px">' + prompt_task_list + '</div></div>'
}

get_prompt = function() {
  return '<div class = promptbox>' + prompt_task_list + '</div>'
}

getResponses = function(order) {
  var response_keys = {key: [89,71], key_name: ["Index Finger", "Middle Finger"]}
  if (order == 2) {
    response_keys= {key: [71,89], key_name: ["Middle Finger", "Index Finger"]}
  }
  return response_keys
}



//Returns the key corresponding to the correct response for the current
// task and stim
var getResponse = function() {
  switch (curr_task) {
    case 'color':
      if (curr_stim.color == 'orange') {
        return response_keys_color.key[0]
      } else {
        return response_keys_color.key[1]
      }
      break;
    case 'magnitude':
      if (curr_stim.number > 5) {
        return response_keys_mag.key[0]
      } else {
        return response_keys_mag.key[1]
      }
      break;
  }
}


/* Append gap and current trial to data and then recalculate for next trial*/
var appendData = function() {
  var trial_num = current_trial //current_trial has already been updated with setStims, so subtract one to record data
  var task_switch = task_switches[trial_num]
  jsPsych.data.addDataToLastTrial({
    cue: curr_cue,
    stim_color: curr_stim.color,
    stim_number: curr_stim.number,
    task: curr_task,
    task_switch: task_switch.task_switch,
    cue_switch: task_switch.cue_switch,
    trial_num: trial_num
  })
}

var getPracticeTrials = function() {
  var practice = []
  current_trial = 0
  task_switches = jsPsych.randomization.repeat(base_task_switches, practice_length/8)
  for (var i = 0; i < practice_length; i++) {
    practice.push(setStims_block)
    practice.push(prompt_fixation_block)
    practice.push(prompt_cue_block);
    practice.push(practice_block);
    practice.push(gap_block);
  }
  return practice
}

/* ************************************ */
/* Define experimental variables */
/* ************************************ */
var practice_repeats = 0
// task specific variables
var response_keys_color = {}
var response_keys_mag = {}

var choices = [89,71]
var practice_length = 16
var num_blocks = 3
var block_length = 80
var test_length = num_blocks * block_length

//set up block stim. correct_responses indexed by [block][stim][type]
var tasks = {
  color: {
    task: 'color',
    cues: ['Color', 'Orange-Blue']
  },
  magnitude: {
    task: 'magnitude',
    cues: ['Magnitude', 'High-Low']
  }
}

var task_switches = []
var base_task_switches = []
var task_switch_types = ["stay", "switch"]
var cue_switch_types = ["stay", "switch"]
var CTIs = [100, 900]
for (var t = 0; t < task_switch_types.length; t++) {
  for (var c = 0; c < cue_switch_types.length; c++) {
    for (var j = 0; j < CTIs.length; j++) {
      base_task_switches.push({
        task_switch: task_switch_types[t],
        cue_switch: cue_switch_types[c],
        CTI: CTIs[j]
      })
    }
  }
}

var task_switch_trials = jsPsych.randomization.repeat(base_task_switches.slice(4), test_length/2)
var cue_stay_trials = jsPsych.randomization.repeat(base_task_switches.slice(0,2), test_length/4)
var cue_switch_trials = jsPsych.randomization.repeat(base_task_switches.slice(2,4), test_length/4)

// set up stim order based on optimized trial sequence
var stim_index = [1,0,0,0,0,1,2,2,0,0,0,2,0,0,2,0,2,0,0,1,0,0,1,0,2,1,0,1,0,2,2,0,0,1,1,0,0,0,0,2,0,1,1,1,2,0,0,1,1,0,0,1,0,2,0,1,2,1,0,0,2,0,0,1,0,1,2,1,1,0,0,1,2,1,0,2,2,0,0,0,2,1,1,1,0,0,0,2,2,0,2,0,1,2,0,0,2,0,0,0,0,0,2,0,0,1,2,0,0,0,0,1,0,0,2,2,1,0,0,1,0,1,2,2,2,0,1,0,2,2,1,0,0,2,0,1,0,0,0,0,1,1,0,2,1,1,0,0,1,1,0,2,0,0,0,1,0,1,2,0,0,0,1,0,1,0,0,0,0,1,2,0,1,1,0,1,0,0,0,0,1,0,2,0,0,0,0,1,0,0,0,1,0,0,2,0,0,0,0,0,2,1,0,0,2,2,1,1,1,2,0,2,2,2,2,1,2,2,2,2,2,1,0,2,0,0,0,2,2,2,2,0,0,0,2,1,0,1,2,1]
var test_task_switches = []
for (var i=0; i<test_length; i++) {
  if (stim_index[i] == 0) {
    test_task_switches.push(task_switch_trials.shift())
  } else if (stim_index[i] == 1) {
    test_task_switches.push(cue_stay_trials.shift())
  } else {
    test_task_switches.push(cue_switch_trials.shift())
  }
  //refill if necessary
  if (task_switch_trials.length == 0) {
  	task_switch_trials = jsPsych.randomization.repeat(base_task_switches.slice(4), test_length/2)
  }
  if (cue_stay_trials.length == 0) {
	cue_stay_trials = jsPsych.randomization.repeat(base_task_switches.slice(0,2), test_length/4)
  }
  if (cue_switch_trials.length == 0) {
	cue_switch_trials = jsPsych.randomization.repeat(base_task_switches.slice(2,4), test_length/4)
  }
}


var testStims = genStims(test_length)
var stims = testStims
var curr_task = randomDraw(getKeys(tasks))
var cue_i = randomDraw([0, 1]) //index for one of two cues of the current task
var curr_cue = tasks[curr_task].cues[cue_i] //object that holds the current cue, set by setStims()
var curr_stim = 'na' //object that holds the current stim, set by setStims()
var current_trial = 0
var CTI = 0 //cue-target-interval
var exp_stage = 'practice' // defines the exp_stage, switched by start_test_block
var prompt_task_list = ''






/* ************************************ */
/* Set up jsPsych blocks */
/* ************************************ */
var task_setup_block = {
  type: 'survey-text',
  data: {
    trial_id: "task_setup"
  },
  questions: [
    [
      "<p class = center-block-text>Experimenter C Setup</p>"
    ],
    [
      "<p class = center-block-text>Experimenter M Setup</p>"
    ]
  ], on_finish: function(data) {
    color_order = parseInt(data.responses.slice(7, 8))
    mag_order = parseInt(data.responses.slice(16, 17))
    response_keys_color = getResponses(color_order)
    response_keys_mag = getResponses(mag_order)


    prompt_task_list = '<strong>Color</strong> or <strong>Orange-Blue</strong>: ' +
    response_keys_color.key_name[0] + ' if orange and ' + 
    response_keys_color.key_name[1] + ' if blue.' +
    '<br><br><strong>Magnitude</strong> or <strong>High-Low</strong>: ' + 
    response_keys_mag.key_name[0] + ' if >5 and ' + 
    response_keys_mag.key_name[1] + ' if <5.'
  }
}

var instructions_block = {
  type: 'poldrack-single-stim',
  stimulus: get_instructions,
  is_html: true,
  timing_stim: -1, 
  timing_response: -1,
  response_ends_trial: true,
  choices: [32],
  data: {
    trial_id: "instructions",
  },
  timing_post_trial: 0
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
    exp_id: 'twobytwo'
  },
  timing_post_trial: 0
};


var start_test_block = {
  type: 'poldrack-single-stim',
  stimulus: '<div class = centerbox><div class = center-text>Get ready!</p></div>',
  is_html: true,
  choices: 'none',
  timing_stim: 1500, 
  timing_response: 1500,
  data: {
    trial_id: "test_start_block"
  },
  timing_post_trial: 500,
  on_finish: function() {
    current_trial = 0
    exp_stage = 'test'
    task_switches = test_task_switches
    curr_task = randomDraw(getKeys(tasks))
    curr_stim = 'na' //object that holds the current stim, set by setStims()
    curr_cue = tasks[curr_task].cues[cue_i] //object that holds the current cue, set by setStims()
  }
};

var rest_block = {
  type: 'poldrack-single-stim',
  stimulus: '<div class = centerbox><div class = center-text>Take a break!<br>Next run will start in a moment</div></div>',
  is_html: true,
  choices: 'none',
  timing_response: 10000,
  data: {
    trial_id: "rest_block"
  },
  timing_post_trial: 1000
};

/* define test blocks */
var setStims_block = {
  type: 'call-function',
  data: {
    trial_id: "set_stims"
  },
  func: setStims,
  timing_post_trial: 0
}

var fixation_block = {
  type: 'poldrack-single-stim',
  stimulus: '<div class = upperbox><div class = fixation>+</div></div><div class = lowerbox><div class = fixation>+</div></div>',
  is_html: true,
  choices: 'none',
  data: {
    trial_id: "fixation"
  },
  timing_post_trial: 0,
  timing_response: 500,
  on_finish: function() {
    jsPsych.data.addDataToLastTrial({
      exp_stage: exp_stage
    })
  }
}

var cue_block = {
  type: 'poldrack-single-stim',
  stimulus: getCue,
  is_html: true,
  choices: 'none',
  data: {
    trial_id: 'cue'
  },
  timing_response: getCTI,
  timing_stim: getCTI,
  timing_post_trial: 0,
  on_finish: function() {
    jsPsych.data.addDataToLastTrial({
      exp_stage: exp_stage
    })
    appendData()
  }
};


var test_block = {
  type: 'poldrack-single-stim',
  stimulus: getStim,
  is_html: true,
  key_answer: getResponse,
  choices: choices,
  data: {
    trial_id: 'stim',
    exp_stage: 'test'
  },
  timing_post_trial: 0,
  timing_response: get_ITI,
  timing_stim: 1000,
  on_finish: function(data) {
    appendData()
    correct_response = getResponse()
    correct = false
    if (data.key_press === correct_response) {
      correct = true
    }
    jsPsych.data.addDataToLastTrial({
      'correct_response': correct_response,
      'correct': correct
    })
    console.log('Trial: ' + current_trial +
              '\nCorrect Response? ' + correct + ', RT: ' + data.rt)
    current_trial += 1
  }
}

/* Set up practice trials */
var prompt_fixation_block = {
  type: 'poldrack-single-stim',
  stimulus: '<div class = upperbox><div class = fixation>+</div></div><div class = lowerbox><div class = fixation>+</div></div>',
  is_html: true,
  choices: 'none',
  data: {
    trial_id: "fixation",
    exp_stage: "practice"
  },
  timing_post_trial: 0,
  timing_response: 500,
  prompt: get_prompt
}

var gap_block = {
  type: 'poldrack-single-stim',
  stimulus: ' ',
  is_html: true,
  choices: 'none',
  data: {
    trial_id: 'gap',
    exp_stage: 'practice'
  },
  timing_response: 500,
  timing_stim: 0,
  timing_post_trial: 0,
  prompt: get_prompt
};

var prompt_cue_block = {
  type: 'poldrack-single-stim',
  stimulus: getCue,
  is_html: true,
  choices: 'none',
  data: {
    trial_id: 'cue',
    exp_stage: 'practice'
  },
  timing_response: getCTI,
  timing_stim: getCTI,
  timing_post_trial: 0,
  prompt: get_prompt,
  on_finish: function() {
    appendData()
  }
};

var practice_block = {
  type: 'poldrack-categorize',
  stimulus: getStim,
  is_html: true,
  key_answer: getResponse,
  correct_text: '<div class = centerbox><div style="color:#4FE829"; class = center-text>Correct!</p></div>',
  incorrect_text: '<div class = centerbox><div style="color:red"; class = center-text>Incorrect</p></div>',
  timeout_message: '<div class = centerbox><div class = center-text>Too Slow</div></div>',
  choices: choices,
  data: {
    trial_id: 'stim',
    exp_stage: "practice"
  },
  timing_feedback_duration: 500,
  show_stim_with_feedback: false,
  timing_response: 2000,
  timing_stim: 1000,
  timing_post_trial: 0,
  prompt: get_prompt,
  on_finish: function(data) {
    appendData()
    console.log('Trial: ' + current_trial +
                  '\nCorrect Response? ' + data.correct + ', RT: ' + data.rt)
    current_trial += 1
  }
}

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
      return false
    } else {
      practice_trials = getPracticeTrials()
      return true
    }
  }
};

/* create experiment definition array */
var twobytwo_experiment = [];
test_keys(twobytwo_experiment, choices)
twobytwo_experiment.push(task_setup_block)
twobytwo_experiment.push(instructions_block);
twobytwo_experiment.push(practice_loop);
setup_fmri_intro(twobytwo_experiment)
for (var b = 0; b < num_blocks; b++) {
	twobytwo_experiment.push(start_test_block)
  twobytwo_experiment.push(fixation_block)
	for (var i = 0; i < block_length; i++) {
	  twobytwo_experiment.push(setStims_block)
	  twobytwo_experiment.push(cue_block);
	  twobytwo_experiment.push(test_block);
	}
	if ((b+1)<num_blocks) {
		twobytwo_experiment.push(rest_block)
	}
}
twobytwo_experiment.push(end_block)
