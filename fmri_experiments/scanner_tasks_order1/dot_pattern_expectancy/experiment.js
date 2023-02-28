/* ************************************ */
/* Define helper functions */
/* ************************************ */

var test_ITIs = [0.136,0.0,0.544,0.272,0.136,0.136,0.0,0.0,0.544,0.952,0.408,0.0,0.408,0.68,0.0,0.408,0.816,0.816,0.136,0.0,0.408,0.0,0.816,0.0,1.224,0.0,0.136,0.136,0.272,0.272,0.0,0.952,0.136,0.136,0.0,0.0,0.816,0.544,2.448,0.136,0.136,0.136,0.0,0.0,0.408,0.136,0.544,0.272,0.0,0.68,0.0,2.176,0.136,0.136,0.0,0.408,0.136,0.0,0.408,0.68,0.272,0.0,0.0,0.544,1.36,0.0,0.272,0.272,1.36,0.272,0.136,0.952,0.136,0.0,0.136,0.136,0.68,0.0,0.136,0.136,0.68,0.816,0.136,0.408,2.04,0.136,0.0,0.0,0.272,0.952,0.408,0.136,0.0,0.136,0.136,0.952,0.0,0.0,0.136,0.136,0.136,0.0,0.0,0.272,0.68,0.272,0.0,0.0,0.136,0.68,0.816,0.136,0.68,0.544,0.272,0.0,0.68,0.952,0.136,0.408,0.272,0.0,0.952,0.272,0.408,0.408,1.088,0.0,0.0,0.0,0.136,0.544,0.272,1.088,0.0,0.952,0.136,0.136,0.0,0.136,0.0,0.68,0.0,0.408,0.136,0.136,0.136,0.0,0.544,0.68,0.136,0.272,0.0,0.408,0.544,0.136,0.272,0.136,0.272,0.0]
var get_ITI = function() {
  return 1500 + ITIs.shift()*1000
 }


var randomDraw = function(lst) {
  var index = Math.floor(Math.random() * (lst.length))
  return lst[index]
}

var getValidProbe = function() {
  return prefix + path + valid_probe + postfix
}

var getValidCue = function() {
  return prefix + path + valid_cue + postfix
}

var getInvalidCue = function() {
  return prefix + path + randomDraw(cues) + postfix
}

var getInvalidProbe = function() {
  return prefix + path + randomDraw(probes) + postfix
}


var getFeedback = function() {
  var curr_trial = jsPsych.progress().current_trial_global
  var curr_data = jsPsych.data.getData()[curr_trial - 1]
  var condition = curr_data.condition
  var response = curr_data.key_press
  var feedback_text = ''
  var correct = false
  var correct_response = choices[1]
  if (condition == "AX") {
    correct_response = choices[0]
  }
  if (response == correct_response) {
    correct = true
    feedback_text =  '<div class = centerbox><div style="color:#4FE829"; class = center-text>Correct!</div></div>'
  } else if (response == -1) {
    feedback_text =  '<div class = centerbox><div class = center-text>Respond Faster!</p></div>'
  } else {
    feedback_text = '<div class = centerbox><div style="color:red"; class = center-text>Incorrect</div></div>'
  }
  jsPsych.data.addDataToLastTrial({'correct': correct, 'correct_response': correct_response})
  return feedback_text
}

var getInstructions = function() {
  var text = '<div class = centerbox><p style = "font-size:40px" class = center-block-text>Target Pair (press index finger):</p><p class = center-block-text><img src = "/static/experiments/dot_pattern_expectancy/images/' +
    valid_cue +
    '" ></img>&nbsp&nbsp&nbsp...followed by...&nbsp&nbsp&nbsp<img src = "/static/experiments/dot_pattern_expectancy/images/' +
    valid_probe + '" ></img><br></br></p><p style = "font-size:40px" class = center-block-text>Otherwise press middle finger</div>'
    return text
}

var getPracticeTrials = function() {
  ITIs = jsPsych.randomization.shuffle([0,1,.2,0,.6,0,0,.4,0,.8])
  var practice_proportions = ['AX','AX','AX','AX','AY','BX','BY','AY','BX','BY']
  var practice_block = jsPsych.randomization.repeat(practice_proportions, 1)
  var practice = []
  for (i = 0; i < practice_block.length; i++) {
    switch (practice_block[i]) {
      case "AX":
        cue = jQuery.extend(true, {}, A_cue)
        probe = jQuery.extend(true, {}, X_probe)
        cue.data.condition = "AX"
        probe.data.condition = "AX"
        break;
      case "BX":
        cue = jQuery.extend(true, {}, other_cue)
        probe = jQuery.extend(true, {}, X_probe)
        cue.data.condition = "BX"
        probe.data.condition = "BX"
        break;
      case "AY":
        cue = jQuery.extend(true, {}, A_cue)
        probe = jQuery.extend(true, {}, other_probe)
        cue.data.condition = "AY"
        probe.data.condition = "AY"
        break;
      case "BY":
        cue = jQuery.extend(true, {}, other_cue)
        probe = jQuery.extend(true, {}, other_probe)
        cue.data.condition = "BY"
        probe.data.condition = "BY"
        break;
    }
    practice.push(cue)
    practice.push(fixation_block)
    practice.push(probe)
    practice.push(feedback_block)
  }
  return practice
}


/* ************************************ */
/* Define experimental variables */
/* ************************************ */
var practice_repeats = 0
var ITIs = []
// task specific variables
var current_trial = 0
var choices = [89, 71]
var exp_stage = 'practice'
var path = '/static/experiments/dot_pattern_expectancy/images/'
var prefix = '<div class = centerbox><div class = img-container><img src = "'
var postfix = '"</img></div></div>'
var cues = ['cue1.png', 'cue2.png', 'cue3.png', 'cue4.png',
  'cue5.png', 'cue6.png'
]
var probes = ['probe1.png', 'probe2.png', 'probe3.png', 'probe4.png',
  'probe5.png', 'probe6.png'
]
var valid_cue = ''
var valid_probe = ''

//preload images
var images = []
for (var i = 0; i < cues.length; i++) {
  images.push(path + cues[i])
  images.push(path + probes[i])
}
jsPsych.pluginAPI.preloadImages(images)

// set up blocks
var num_blocks = 4
var block_length = 40

var stim_index = [3,1,0,3,2,0,0,0,1,0,0,0,0,2,0,3,2,1,2,1,3,0,1,0,1,0,0,0,0,3,0,3,0,0,2,2,0,1,0,0,1,0,0,0,0,2,0,0,0,0,0,2,3,3,2,0,0,2,0,3,0,0,0,0,0,2,3,0,0,0,2,2,0,2,0,0,3,0,1,0,0,1,1,2,0,2,3,0,0,3,0,2,0,0,0,3,0,3,0,0,1,0,0,0,0,2,3,0,0,1,1,2,2,1,0,0,0,1,0,0,0,0,1,1,0,0,0,1,3,3,0,2,0,2,1,0,3,0,0,3,0,1,0,0,3,3,0,0,3,1,1,1,3,2,0,0,0,0,2,0]

var trial_proportions = []
for (var i=0; i<stim_index.length;i++) {
  if (stim_index[i] == 0) {
    trial_proportions.push('AX')
  } else if (stim_index[i] == 1) {
    trial_proportions.push('AY')
  } else if (stim_index[i] == 2) {
    trial_proportions.push('BX')
  } else {
    trial_proportions.push('BY')
  }
}

var blocks = []
for (b = 0; b < num_blocks; b++) {
  blocks.push(trial_proportions.slice(b*block_length,(b+1)*block_length))
}


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
      "<p class = center-block-text>Experimenter P Setup</p>"
    ]
  ], on_finish: function(data) {
    cue_index = parseInt(data.responses.slice(7, 8))
    probe_index = parseInt(data.responses.slice(16, 17))
    valid_cue = cues.splice(cue_index-1,1)[0]
    valid_probe = probes.splice(probe_index-1,1)[0]
  }
}

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
      exp_stage = 'test'
      ITIs = test_ITIs
      current_trial = 0
  }
};

/* define static blocks */
 var end_block = {
  type: 'poldrack-single-stim',
  stimulus: '<div class = centerbox><div class = center-text><i>Fin</i></div></div>',
  is_html: true,
  choices: [32],
  timing_response: -1,
  response_ends_trial: true,
  data: {
    trial_id: "end",
    exp_id: 'dot_pattern_expectancy'
  },
  timing_post_trial: 0
};


 var instructions_block = {
  type: 'poldrack-single-stim',
  stimulus: getInstructions,
  is_html: true,
  timing_stim: -1, 
  timing_response: -1,
  response_ends_trial: true,
  choices: [32],
  data: {
    trial_id: "instructions",
  },
  timing_post_trial: 500
};

var rest_block = {
  type: 'poldrack-single-stim',
  stimulus: '<div class = centerbox><div class = center-text>Take a break!<br>Next run will start in a moment</div></div>',
  is_html: true,
  choices: 'none',
  timing_response: 7500,
  data: {
    trial_id: "rest_block"
  },
  timing_post_trial: 1000
};

var fixation_block = {
  type: 'poldrack-single-stim',
  stimulus: '<div class = centerbox><div class = fixation>+</div></div>',
  is_html: true,
  choices: 'none',
  data: {
    trial_id: "fixation",
  },
  timing_post_trial: 0,
  timing_stim: 2000,
  timing_response: 2000,
  on_finish: function() {
    jsPsych.data.addDataToLastTrial({exp_stage: exp_stage})
  }
}

var feedback_block = {
  type: 'poldrack-single-stim',
  stimulus: getFeedback,
  is_html: true,
  choices: 'none',
  data: {
    trial_id: "feedback",
  },
  timing_post_trial: 0,
  timing_stim: 500,
  timing_response: 500,
  on_finish: function() {
    jsPsych.data.addDataToLastTrial({
      exp_stage: exp_stage,
      trial_num: current_trial
    })
  }
}

/* define test block cues and probes*/
var A_cue = {
  type: 'poldrack-single-stim',
  stimulus: getValidCue,
  is_html: true,
  choices: 'none',
  data: {
    trial_id: "cue",
  },
  timing_stim: 500,
  timing_response: 500,
  timing_post_trial: 0,
  on_finish: function() {
    jsPsych.data.addDataToLastTrial({
    	exp_stage: exp_stage,
    	trial_num: current_trial
    })
  }
};

var other_cue = {
  type: 'poldrack-single-stim',
  stimulus: getInvalidCue,
  is_html: true,
  choices: 'none',
  data: {
    trial_id: "cue",
    exp_stage: "test"
  },
  timing_stim: 500,
  timing_response: 500,
  timing_post_trial: 0,
  on_finish: function() {
    jsPsych.data.addDataToLastTrial({
    	exp_stage: exp_stage,
    	trial_num: current_trial
    })
  }
};

var X_probe = {
  type: 'poldrack-single-stim',
  stimulus: getValidProbe,
  is_html: true,
  choices: choices,
  data: {
    trial_id: "probe",
    exp_stage: "test"
  },
  timing_stim: 500,
  timing_response: get_ITI,
  timing_post_trial: 0,
  on_finish: function(data) {
    var correct_response = choices[1]
    if (data.condition == "AX") {
      correct_response = choices[0]
    }
    var correct = false
    if (data.key_press == correct_response) {
      correct = true
    }
    jsPsych.data.addDataToLastTrial({
      correct_response: correct_response,
      correct: correct,
    	exp_stage: exp_stage,
    	trial_num: current_trial
	   })
     console.log('Trial: ' + current_trial +
              '\nCorrect Response? ' + correct + ', RT: ' + data.rt)
     current_trial += 1
  }
};

var other_probe = {
  type: 'poldrack-single-stim',
  stimulus: getInvalidProbe,
  is_html: true,
  choices: choices,
  data: {
    trial_id: "probe",
    exp_stage: "test"
  },
  timing_stim: 500,
  timing_response: get_ITI,
  timing_post_trial: 0,
  on_finish: function(data) {
    var correct_response = choices[1]
    if (data.condition == "AX") {
      correct_response = choices[0]
    }
    var correct = false
    if (data.key_press == correct_response) {
      correct = true
    }
    jsPsych.data.addDataToLastTrial({
      correct_response: correct_response,
      correct: correct,
      exp_stage: exp_stage,
      trial_num: current_trial
     })
     console.log('Trial: ' + current_trial +
              '\nCorrect Response? ' + correct + ', RT: ' + data.rt)
     current_trial += 1
  }
};

/* Set up practice trials */
var practice_trials = getPracticeTrials()
var practice_loop = {
  timeline: practice_trials,
  loop_function: function(data) {
    practice_repeats+=1
    total_trials = 0
    correct_trials = 0
    for (var i = 0; i < data.length; i++) {
      if (data[i].trial_id == 'probe') {
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

/* ************************************ */
/* Set up experiment */
/* ************************************ */

var dot_pattern_expectancy_experiment = []
test_keys(dot_pattern_expectancy_experiment,choices)
dot_pattern_expectancy_experiment.push(task_setup_block)
dot_pattern_expectancy_experiment.push(instructions_block);
dot_pattern_expectancy_experiment.push(practice_loop);
setup_fmri_intro(dot_pattern_expectancy_experiment)

for (b = 0; b < num_blocks; b++) {
  dot_pattern_expectancy_experiment.push(start_test_block);
  var block = blocks[b]
  for (i = 0; i < block_length; i++) {
    switch (block[i]) {
      case "AX":
        cue = jQuery.extend(true, {}, A_cue)
        probe = jQuery.extend(true, {}, X_probe)
        cue.data.condition = "AX"
        probe.data.condition = "AX"
        break;
      case "BX":
        cue = jQuery.extend(true, {}, other_cue)
        probe = jQuery.extend(true, {}, X_probe)
        cue.data.condition = "BX"
        probe.data.condition = "BX"
        break;
      case "AY":
        cue = jQuery.extend(true, {}, A_cue)
        probe = jQuery.extend(true, {}, other_probe)
        cue.data.condition = "AY"
        probe.data.condition = "AY"
        break;
      case "BY":
        cue = jQuery.extend(true, {}, other_cue)
        probe = jQuery.extend(true, {}, other_probe)
        cue.data.condition = "BY"
        probe.data.condition = "BY"
        break;
    }
    dot_pattern_expectancy_experiment.push(cue)
    dot_pattern_expectancy_experiment.push(fixation_block)
    dot_pattern_expectancy_experiment.push(probe)
  }
  if ((b+1)<num_blocks) {
    dot_pattern_expectancy_experiment.push(rest_block)
  }
}
dot_pattern_expectancy_experiment.push(end_block)