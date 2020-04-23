fsl_dir="/home/groups/russpold/uh2_analysis/Self_Regulation_Ontology_fMRI/fmri_analysis/fsl"
template_dir=$fsl_dir/"templates"
tmp_dir=$fsl_dir/"tmp_batch"


OLDIFS=$IFS; IFS=',';
for i in /sub-s061/ses-1/func/sub-s061_ses-1_task-stopSignal_run-1_bold,s061,brain1,524,335360000 /sub-s130/ses-2/func/sub-s130_ses-2_task-stopSignal_run-1_bold,s130,brain2,524,335360000 /sub-s144/ses-1/func/sub-s144_ses-1_task-stopSignal_run-1_bold,s144,brain1,508,325120000 /sub-s172/ses-2/func/sub-s172_ses-2_task-stopSignal_run-1_bold,s172,brain2,508,325120000 /sub-s192/ses-2/func/sub-s192_ses-2_task-stopSignal_run-1_bold,s192,brain2,517,330880000 /sub-s234/ses-1/func/sub-s234_ses-1_task-stopSignal_run-1_bold,s234,brain1,502,321280000 /sub-s251/ses-1/func/sub-s251_ses-1_task-stopSignal_run-1_bold,s251,brain1,524,335360000 /sub-s358/ses-1/func/sub-s358_ses-1_task-stopSignal_run-1_bold,s358,brain1,524,335360000 /sub-s373/ses-1/func/sub-s373_ses-1_task-stopSignal_run-1_bold,s373,brain1,505,323200000 /sub-s445/ses-2/func/sub-s445_ses-2_task-stopSignal_run-1_bold,s445,brain1,524,335360000 /sub-s465/ses-1/func/sub-s465_ses-1_task-stopSignal_run-1_bold,s465,brain1,524,335360000 /sub-s471/ses-1/func/sub-s471_ses-1_task-stopSignal_run-1_bold,s471,brain1,524,335360000 /sub-s483/ses-2/func/sub-s483_ses-2_task-stopSignal_run-1_bold,s483,brain2,510,326400000 /sub-s491/ses-1/func/sub-s491_ses-1_task-stopSignal_run-1_bold,s491,brain1,524,335360000 /sub-s495/ses-1/func/sub-s495_ses-1_task-stopSignal_run-1_bold,s495,brain1,515,329600000 /sub-s497/ses-2/func/sub-s497_ses-2_task-stopSignal_run-1_bold,s497,brain2,514,328960000 /sub-s499/ses-1/func/sub-s499_ses-1_task-stopSignal_run-1_bold,s499,brain1,514,328960000 /sub-s512/ses-2/func/sub-s512_ses-2_task-stopSignal_run-1_bold,s512,brain1,512,327680000 /sub-s518/ses-2/func/sub-s518_ses-2_task-stopSignal_run-1_bold,s518,brain2,509,325760000 /sub-s519/ses-1/func/sub-s519_ses-1_task-stopSignal_run-1_bold,s519,brain1,506,323840000 /sub-s524/ses-2/func/sub-s524_ses-2_task-stopSignal_run-1_bold,s524,brain2,524,335360000 /sub-s525/ses-2/func/sub-s525_ses-2_task-stopSignal_run-1_bold,s525,brain2,509,325760000 /sub-s526/ses-2/func/sub-s526_ses-2_task-stopSignal_run-1_bold,s526,brain1,524,335360000 /sub-s533/ses-1/func/sub-s533_ses-1_task-stopSignal_run-1_bold,s533,brain1,524,335360000 /sub-s541/ses-1/func/sub-s541_ses-1_task-stopSignal_run-1_bold,s541,brain1,515,329600000 /sub-s546/ses-1/func/sub-s546_ses-1_task-stopSignal_run-1_bold,s546,brain1,525,336000000 /sub-s548/ses-2/func/sub-s548_ses-2_task-stopSignal_run-1_bold,s548,brain2,510,326400000 /sub-s549/ses-2/func/sub-s549_ses-2_task-stopSignal_run-1_bold,s549,brain1,524,335360000 /sub-s553/ses-2/func/sub-s553_ses-2_task-stopSignal_run-1_bold,s553,brain2,513,328320000 /sub-s554/ses-1/func/sub-s554_ses-1_task-stopSignal_run-1_bold,s554,brain1,508,325120000 /sub-s555/ses-1/func/sub-s555_ses-1_task-stopSignal_run-1_bold,s555,brain1,487,311680000 /sub-s556/ses-1/func/sub-s556_ses-1_task-stopSignal_run-1_bold,s556,brain1,510,326400000 /sub-s557/ses-2/func/sub-s557_ses-2_task-stopSignal_run-1_bold,s557,brain1,506,323840000 /sub-s558/ses-2/func/sub-s558_ses-2_task-stopSignal_run-1_bold,s558,brain1,509,325760000 /sub-s561/ses-2/func/sub-s561_ses-2_task-stopSignal_run-1_bold,s561,brain2,509,325760000 /sub-s567/ses-1/func/sub-s567_ses-1_task-stopSignal_run-1_bold,s567,brain1,524,335360000 /sub-s568/ses-1/func/sub-s568_ses-1_task-stopSignal_run-1_bold,s568,brain1,519,332160000 /sub-s570/ses-1/func/sub-s570_ses-1_task-stopSignal_run-1_bold,s570,brain2,524,335360000 /sub-s572/ses-2/func/sub-s572_ses-2_task-stopSignal_run-1_bold,s572,brain1,516,330240000 /sub-s573/ses-2/func/sub-s573_ses-2_task-stopSignal_run-1_bold,s573,brain2,509,325760000 /sub-s574/ses-2/func/sub-s574_ses-2_task-stopSignal_run-1_bold,s574,brain2,509,325760000 /sub-s577/ses-1/func/sub-s577_ses-1_task-stopSignal_run-1_bold,s577,brain1,513,328320000 /sub-s579/ses-1/func/sub-s579_ses-1_task-stopSignal_run-1_bold,s579,brain1,502,321280000 /sub-s581/ses-2/func/sub-s581_ses-2_task-stopSignal_run-1_bold,s581,brain2,524,335360000 /sub-s582/ses-2/func/sub-s582_ses-2_task-stopSignal_run-1_bold,s582,brain2,509,325760000 /sub-s583/ses-2/func/sub-s583_ses-2_task-stopSignal_run-1_bold,s583,brain1,524,335360000 /sub-s584/ses-2/func/sub-s584_ses-2_task-stopSignal_run-1_bold,s584,brain2,502,321280000 /sub-s585/ses-2/func/sub-s585_ses-2_task-stopSignal_run-1_bold,s585,brain1,509,325760000 /sub-s586/ses-2/func/sub-s586_ses-2_task-stopSignal_run-1_bold,s586,brain1,524,335360000 /sub-s587/ses-1/func/sub-s587_ses-1_task-stopSignal_run-1_bold,s587,brain1,509,325760000 /sub-s588/ses-1/func/sub-s588_ses-1_task-stopSignal_run-1_bold,s588,brain1,524,335360000 /sub-s589/ses-1/func/sub-s589_ses-1_task-stopSignal_run-1_bold,s589,brain1,510,326400000 /sub-s590/ses-1/func/sub-s590_ses-1_task-stopSignal_run-1_bold,s590,brain1,509,325760000 /sub-s591/ses-2/func/sub-s591_ses-2_task-stopSignal_run-1_bold,s591,brain1,516,330240000 /sub-s592/ses-2/func/sub-s592_ses-2_task-stopSignal_run-1_bold,s592,brain2,509,325760000 /sub-s593/ses-2/func/sub-s593_ses-2_task-stopSignal_run-1_bold,s593,brain1,524,335360000 /sub-s594/ses-2/func/sub-s594_ses-2_task-stopSignal_run-1_bold,s594,brain2,502,321280000 /sub-s595/ses-2/func/sub-s595_ses-2_task-stopSignal_run-1_bold,s595,brain2,524,335360000 /sub-s596/ses-1/func/sub-s596_ses-1_task-stopSignal_run-1_bold,s596,brain1,494,316160000 /sub-s597/ses-1/func/sub-s597_ses-1_task-stopSignal_run-1_bold,s597,brain1,510,326400000 /sub-s598/ses-1/func/sub-s598_ses-1_task-stopSignal_run-1_bold,s598,brain1,509,325760000 /sub-s601/ses-2/func/sub-s601_ses-2_task-stopSignal_run-1_bold,s601,brain1,512,327680000 /sub-s602/ses-2/func/sub-s602_ses-2_task-stopSignal_run-1_bold,s602,brain2,505,323200000 /sub-s603/ses-1/func/sub-s603_ses-1_task-stopSignal_run-1_bold,s603,brain1,495,316800000 /sub-s605/ses-1/func/sub-s605_ses-1_task-stopSignal_run-1_bold,s605,brain1,509,325760000 /sub-s606/ses-1/func/sub-s606_ses-1_task-stopSignal_run-1_bold,s606,brain1,504,322560000 /sub-s607/ses-2/func/sub-s607_ses-2_task-stopSignal_run-1_bold,s607,brain2,510,326400000 /sub-s608/ses-2/func/sub-s608_ses-2_task-stopSignal_run-1_bold,s608,brain2,509,325760000 /sub-s609/ses-2/func/sub-s609_ses-2_task-stopSignal_run-1_bold,s609,brain2,517,330880000 /sub-s610/ses-2/func/sub-s610_ses-2_task-stopSignal_run-1_bold,s610,brain2,517,330880000 /sub-s611/ses-1/func/sub-s611_ses-1_task-stopSignal_run-1_bold,s611,brain1,513,328320000 /sub-s612/ses-1/func/sub-s612_ses-1_task-stopSignal_run-1_bold,s612,brain1,513,328320000 /sub-s613/ses-1/func/sub-s613_ses-1_task-stopSignal_run-1_bold,s613,brain3,524,335360000 /sub-s614/ses-1/func/sub-s614_ses-1_task-stopSignal_run-1_bold,s614,brain1,515,329600000 /sub-s615/ses-3/func/sub-s615_ses-3_task-stopSignal_run-1_bold,s615,brain3,502,321280000 /sub-s616/ses-2/func/sub-s616_ses-2_task-stopSignal_run-1_bold,s616,brain2,514,328960000 /sub-s617/ses-2/func/sub-s617_ses-2_task-stopSignal_run-1_bold,s617,brain2,511,327040000 /sub-s618/ses-2/func/sub-s618_ses-2_task-stopSignal_run-1_bold,s618,brain2,524,335360000 /sub-s619/ses-1/func/sub-s619_ses-1_task-stopSignal_run-1_bold,s619,brain1,524,335360000 /sub-s621/ses-1/func/sub-s621_ses-1_task-stopSignal_run-1_bold,s621,brain1,509,325760000 /sub-s622/ses-2/func/sub-s622_ses-2_task-stopSignal_run-1_bold,s622,brain2,508,325120000 /sub-s623/ses-4/func/sub-s623_ses-4_task-stopSignal_run-1_bold,s623,brain3,332,212480000 /sub-s624/ses-2/func/sub-s624_ses-2_task-stopSignal_run-1_bold,s624,brain2,509,325760000 /sub-s626/ses-1/func/sub-s626_ses-1_task-stopSignal_run-1_bold,s626,brain1,502,321280000 /sub-s627/ses-1/func/sub-s627_ses-1_task-stopSignal_run-1_bold,s627,brain1,501,320640000 /sub-s628/ses-1/func/sub-s628_ses-1_task-stopSignal_run-1_bold,s628,brain1,509,325760000 /sub-s629/ses-1/func/sub-s629_ses-1_task-stopSignal_run-1_bold,s629,brain1,513,328320000 /sub-s631/ses-2/func/sub-s631_ses-2_task-stopSignal_run-1_bold,s631,brain1,516,330240000 /sub-s633/ses-2/func/sub-s633_ses-2_task-stopSignal_run-1_bold,s633,brain2,513,328320000 /sub-s634/ses-2/func/sub-s634_ses-2_task-stopSignal_run-1_bold,s634,brain1,524,335360000 /sub-s635/ses-2/func/sub-s635_ses-2_task-stopSignal_run-1_bold,s635,brain2,498,318720000 /sub-s636/ses-1/func/sub-s636_ses-1_task-stopSignal_run-1_bold,s636,brain1,509,325760000 /sub-s638/ses-1/func/sub-s638_ses-1_task-stopSignal_run-1_bold,s638,brain1,509,325760000 /sub-s639/ses-1/func/sub-s639_ses-1_task-stopSignal_run-1_bold,s639,brain1,516,330240000 /sub-s640/ses-1/func/sub-s640_ses-1_task-stopSignal_run-1_bold,s640,brain1,515,329600000 /sub-s641/ses-3/func/sub-s641_ses-3_task-stopSignal_run-1_bold,s641,brain3,524,335360000 /sub-s642/ses-2/func/sub-s642_ses-2_task-stopSignal_run-1_bold,s642,brain2,510,326400000 /sub-s643/ses-2/func/sub-s643_ses-2_task-stopSignal_run-1_bold,s643,brain2,502,321280000 /sub-s644/ses-2/func/sub-s644_ses-2_task-stopSignal_run-1_bold,s644,brain2,498,318720000 /sub-s645/ses-1/func/sub-s645_ses-1_task-stopSignal_run-1_bold,s645,brain1,518,331520000 /sub-s646/ses-1/func/sub-s646_ses-1_task-stopSignal_run-1_bold,s646,brain1,501,320640000 /sub-s647/ses-1/func/sub-s647_ses-1_task-stopSignal_run-1_bold,s647,brain1,506,323840000 /sub-s648/ses-2/func/sub-s648_ses-2_task-stopSignal_run-1_bold,s648,brain2,524,335360000 /sub-s649/ses-3/func/sub-s649_ses-3_task-stopSignal_run-1_bold,s649,brain3,524,335360000 /sub-s650/ses-2/func/sub-s650_ses-2_task-stopSignal_run-1_bold,s650,brain2,524,335360000; do set -- $i;
	sed -e "s|{RELATIVE_BOLD}|$1|g" -e "s|{SUBJECT}|$2|g" -e "s|{SES_BRAIN}|$3|g" -e "s|{NTP}|$4|g" -e "s|{TOT_VOX}|$5|g" $template_dir/template_stopSignal_fsl.fsf > $tmp_dir/stopSignal_$2_fsl.fsf;
    sed -e "s|{SUBJECT}|$2|g" -e "s|{TASK}|stopSignal|g" $template_dir/template_1stlevel_FEAT.batch > $tmp_dir/stopSignal_$2_FEAT.batch;
    sbatch $tmp_dir/stopSignal_$2_FEAT.batch;
done;
IFS=$OLDIFS;
    