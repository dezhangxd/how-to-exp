# !/bin/bash
# run-para.sh @ V2.0 by Xindi Zhang 2026.02 dezhangxd@163.com MIT License


SEND_THREAD_NUM=16  # Set the number of concurrent threads
cutoff_time=10		# Set the cutoff time

# Function: solve tasks for the dataset
# Parameters:
#   $1: data path (all_data)
#   $2: sample file name (sample)
#   $3: output path (res_solver_ins)
#   $4: executable path (worker_dir)
#   $5: program name to run
#   $6: arguments for the program
#   $7: number of CPU cores
#   $8: output message
#   $9: RUB_FLAG
process_dataset() {
	local all_data="$1"
	local sample="$2"
	local res_solver_ins="$3"
	local work_dir="$4"
	local run_cmd="$5"
	local run_params="$6"
	local resources="$7"
	local output_msg="$8"
	local rub_flag="$9"
	
	kill_flag=false

	if [ ! -d "$res_solver_ins" ]; then
	 	mkdir -p $res_solver_ins
	fi
	
	for file in `cat $all_data/$sample | shuf`
	do

		if $kill_flag; then
			break
		fi

		if [ ! -d "$res_solver_ins" ]; then
	 		mkdir -p $res_solver_ins
		fi
		touch $res_solver_ins/$file

		for ((j=1; j<=resources; j++))
		do
			read -u 6
		done
		{

			cd $work_dir			
			if $rub_flag; then
				command="exec -a rubrub $run_cmd $all_data/$file $run_params | gnomon"
				eval "$command"
				RUB_THREAD_NUM=$(($(ps -ef | grep "rubrub" | grep -v grep | wc -l)))
				GOD_THREAD_NUM=$(($(ps -ef | grep "goodgood" | grep -v grep | wc -l)))
				if [ "${GOD_THREAD_NUM:-0}" -eq 0 ] && [ "${RUB_THREAD_NUM:-0}" -gt 0 ]; then
					# echo "c [kill] all processes are finished, killing rubbish threads" >&2
					pkill -f "rubrub"
					kill_flag=true
				fi
				

			else
				command="$run_cmd $all_data/$file $run_params | gnomon"
				echo "c [eval]" "$command" >&2
				eval "exec -a goodgood $command"
				echo "c [finish]" "$output_msg" "$file" >&2
			fi


			for ((j=1; j<=resources; j++))
			do
				echo >&6
			done
		} >$res_solver_ins/$file  &
	done
}
proc_cmd='process_dataset "$instance" "$sample" "$res_solver_ins" "$work_dir" "$solver_exec" "$solver_params" "$resources" "$output_msg" "$rub_flag"'


tmp_fifofile="/tmp/$$.fifo" # Use current process ID as the fifo filename
rub_flag=false
mkfifo "$tmp_fifofile" # Create a random fifo pipe file
exec 6<>"$tmp_fifofile" # Define file descriptor 6 pointing to this fifo pipe file
rm $tmp_fifofile # Remove the fifo file, keeping the fd
for i in $(seq 1 $SEND_THREAD_NUM)
do
    echo # Write $SEND_THREAD_NUM empty lines into the fifo pipe file
done >&6

#####################################################
base_path=$(pwd) # option: current path

ins_bench1="${base_path}/ins/bench1"
ins_bench2="${base_path}/ins/bench2"

base_res_dir="${base_path}/res"
res_seq_kis_inc="${base_res_dir}/kissat_inc"
res_seq_rlnt="${base_res_dir}/RLNT"
res_para_PRS="${base_res_dir}/PRS"
res_res_rub="${base_res_dir}/rubrub"

base_slv_path="${base_path}/slv"


#####################################################

all_datas=($ins_bench1   $ins_bench1  $ins_bench2)
all_samples=("part1.txt" "part2.txt"  "all.txt")


# parallel solvers first
for resources in 8 4 # using larger threads first
do

	for((i=0;i<${#all_datas[*]};i++))
	do
		instance=${all_datas[$i]}
		sample=${all_samples[$i]}

		res_solver_ins=$res_para_PRS"_"$resources
		work_dir="${base_slv_path}/ParKissat-RS"
		solver_exec="./parkissat -v=2 -t=$cutoff_time " # some parameters can be set here
		solver_params="-c=$resources -shr-sleep=500000 -shr-lit=1500 -initshuffle" # better to place all parameters here
		output_msg="ParKissat-RS finish solving with $resources threads"
		eval "$proc_cmd"
	done

done

# sequential solvers
for((i=0;i<${#all_datas[*]};i++))
do
	instance=${all_datas[$i]}
	sample=${all_samples[$i]}


	# RLNT
	res_solver_ins=$res_seq_rlnt
	resources=1
	work_dir="${base_slv_path}/Relaxed_LCMDCBDL_newTech/bin"
	solver_exec="timeout $cutoff_time ./Relaxed_LCMDCBDL_newTech"
	solver_params=""
	output_msg="RLNT finish solving with $resources threads"
	eval "$proc_cmd"
	


	# kissat_inc
	res_solver_ins=$res_seq_kis_inc
	resources=1
	work_dir="${base_slv_path}/kissat_inc/bin"
	solver_exec="timeout $cutoff_time ./kissat"
	solver_params=""
	output_msg="kissat_inc finish solving with $resources threads"
	eval "$proc_cmd"
	
done


#####################################################
# rub_threads for fairness
while true
do	

	instance=${all_datas[-1]}
	sample=${all_samples[-1]}
	res_solver_ins=$res_res_rub
	resources=1
	output_msg="[rub] kill"
	rub_flag=true

	# any seq solver can be used here
	(
		work_dir="${base_slv_path}/kissat_inc/bin"  
		solver_exec="timeout $cutoff_time ./kissat" 
		solver_params=""
	)
	eval "$proc_cmd"

	GOD_THREAD_NUM=$(($(ps -ef | grep "goodgood" | grep -v grep | wc -l)))
	if [ "${GOD_THREAD_NUM:-0}" -eq 0 ]; then
		sleep 2
		echo "c [run-para.sh] finish & exit" >&2
		rm -rf $res_solver_ins
		break
	fi

done

exit 0
