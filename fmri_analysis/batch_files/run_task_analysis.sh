for path in /scratch/PI/russpold/work/ieisenbe/uh2/fmriprep/fmriprep/sub-s591
do
    sid=${path: -4}
    echo ""
    echo ******************************${sid}***************************************
    echo ""
    tasks=""
    tasks_noRT=""
    # find tasks that haven't been run...
    for task in ANT CCTHot discountFix DPX motorSelectiveStop stopSignal stroop twoByTwo
    do
        # ...with RT as a regressor
        if [ -f /scratch/PI/russpold/work/ieisenbe/uh2/output/1stLevel/${sid}_task_${task}/cope1.nii.gz ]; 
        then
            echo task analysis already run on $sid $task
        else
            tasks="$tasks$task "
        fi
        # ...without RT as a regressor
        if [ -f /scratch/PI/russpold/work/ieisenbe/uh2/output_noRT/1stLevel/${sid}_task_${task}/cope1.nii.gz ]; 
        then
            echo task analysis noRT already run on $sid $task
        else
            tasks_noRT="$tasks_noRT$task "
        fi
    done
    if [ "$tasks" != "" ]; then
        echo Running $sid task analysis on $tasks
        sed -e "s/{sid}/$sid/g" -e "s/{tasks}/$tasks/g" task_analysis.batch | sbatch -p russpold
    fi

    if [ "$tasks_noRT" != "" ]; then
        echo Running $sid task analysis noRT on $tasks
        sed -e "s/{sid}/$sid/g" -e "s/{tasks}/$tasks/g" task_analysis_noRT.batch | sbatch -p russpold
    fi

done
