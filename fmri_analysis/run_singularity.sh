#singularity run -B `pwd`/output:/output -B `pwd`/Data:/Data singularity_images/nipype_image-2017-06-07-4b577eb8576b.img --participant_label $1 

singularity run -B /home/ieisenbe/Self_Regulation_Ontology_fMRI/fmri_analysis/output:/output -B /scratch/PI/russpold/work/ieisenbe/uh2/fmriprep/fmriprep/:/Data singularity_images/nipype_image-2017-06-07-4b577eb8576b.img --participant_label s358
