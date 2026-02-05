#!/usr/bin/python
# -*- coding: UTF-8 -*-
# cal.py @ V2.0 by Xindi Zhang 2026.02 dezhangxd@163.com MIT License
import os, re

# global limit
CUTOFF = 10
PUNISH = 2 #PAR2
MEMS_MAX = 61440 # 60G

class states(object):
    res = "unknown"
    time = CUTOFF*PUNISH
    mems = MEMS_MAX
    mono = False        # only this one can solve
    best = False        # show the best performance

class solver(object):
    def __init__(self, res_dir, name):
        self.res_dir    = res_dir  # save the results files
        self.print_name = name     # names want to show
        self.datas      = dict()   # datas[ins] save the instances
    def reset(self):
        # SAT-ins UNSAT-ins solved-ins all-ins
        self.sat_num = self.unsat_num = self.solved_num = self.all_num = 0
        self.avg_sat_time = self.avg_unsat_time = self.avg_solved_time = self.avg_all_time = 0.0
        self.PAR_sat_time = self.PAR_unsat_time = self.PAR_solved_time = self.PAR_all_time = 0.0
        self.mono_num = 0
        self.best_num = 0
    def cal_soln(self, ins_name):
        self.all_num += 1
        state = self.datas[ins_name]
        if(self.datas[ins_name].time > CUTOFF):
            self.datas[ins_name] = states()
        if(state.res=="sat"):
            self.sat_num            += 1
            self.solved_num         += 1
            self.avg_sat_time       += state.time
            self.avg_solved_time    += state.time
            self.avg_all_time       += state.time
            self.PAR_sat_time       += state.time
            self.PAR_solved_time    += state.time
            self.PAR_all_time       += state.time
        elif(state.res=="unsat"):
            self.unsat_num          += 1
            self.solved_num         += 1
            self.avg_unsat_time     += state.time
            self.avg_solved_time    += state.time
            self.avg_all_time       += state.time
            self.PAR_unsat_time     += state.time
            self.PAR_solved_time    += state.time
            self.PAR_all_time       += state.time
        else:
            self.avg_all_time       += CUTOFF
            self.PAR_all_time       += CUTOFF * PUNISH
    def deal_avg(self):
        if(self.sat_num>0):
            self.avg_sat_time    /= self.sat_num
            self.PAR_sat_time    /= self.sat_num    
        if(self.unsat_num>0):
            self.avg_unsat_time  /= self.unsat_num
            self.PAR_unsat_time  /= self.unsat_num
        if(self.solved_num>0):
            self.avg_solved_time /= self.solved_num
            self.PAR_solved_time /= self.solved_num
        if(self.all_num>0):
            self.avg_all_time    /= self.all_num
            self.PAR_all_time    /= self.all_num
    def to_string(self, state):
        line = ""
        line += str(state.res) + " "
        line += str(round(state.time,2))
        if state.mono:
            line += "[M]"
        elif state.best:
            line += "[B]"
        line += str()
        return line.ljust(18)

        return super().to_string(state)


class solver_SAT_standard_gnomon(solver):
    def cal_soln(self, ins_name):
        if(not ins_name in self.datas):
            self.datas[ins_name] = states()
            real_file_path = self.res_dir + "/" + ins_name
            fstr = open(real_file_path, "r").read()
                
            if(not len(re.findall(r"s\s+UNSAT", fstr))==0):
                self.datas[ins_name].res = "unsat"
            elif(not len(re.findall(r"s\s+SAT", fstr))==0):
                self.datas[ins_name].res = "sat"
            

            if(not self.datas[ins_name].res == "unknown"):
                timestr = re.findall(r"Total.*s", fstr)[-1].strip('').split()[-1]
                time = float(timestr.strip('s'))
                self.datas[ins_name].time = time
                if (self.datas[ins_name].time > CUTOFF):
                    self.datas[ins_name].res="unknown"
                    self.datas[ins_name].time = CUTOFF*PUNISH
            
            if(not self.datas[ins_name].res == "unknown"):
                
                if(len(re.findall(r"Total.*s", fstr))==0):
                    self.datas[ins_name].time = CUTOFF*PUNISH
                    print("Warning: ", self.print_name, " ", real_file_path, " timeline not found")
                    return super().cal_soln(ins_name)

                timestr = re.findall(r"Total.*s", fstr)[-1].strip('').split()[-1]
                time = float(timestr.strip('s'))
                self.datas[ins_name].time = time
                if (self.datas[ins_name].time > CUTOFF):
                    self.datas[ins_name].res="unknown"
                    self.datas[ins_name].time = CUTOFF*PUNISH
            else:
                if(len(re.findall(r"Total.*s", fstr))==0):
                    self.datas[ins_name].time = CUTOFF*PUNISH
                else:
                    timestr = re.findall(r"Total.*s", fstr)[-1].strip('').split()[-1]
                    time = float(timestr.strip('s'))
                    if(time < CUTOFF * 0.95):
                        print("Warning: ", self.print_name, " ", real_file_path, " time = ", time, " < CUTOFF")
        
        return super().cal_soln(ins_name)
    def to_string(self, state):
        return super().to_string(state)


SOLVER_LEN = 30
SAMPLE_LEN = 20
NUMBER_LEN = 10
print_title = True
class calculater(object):
    solvers     = []
    sample_dirs = []    # sample dirs, [sample_dir, sample_name]s
    def __init__(self, solvers, sample_dirs):
        self.solvers = solvers
        self.sample_dirs = sample_dirs

        split =  "| "  + '-'*(SAMPLE_LEN)
        split += " | " + '-'*(SOLVER_LEN)
        for _ in range(6):
            split += " | " + '-'*(NUMBER_LEN)
        split += " |"
        self.split_line = split

    def __show_in_mark_down(self, samp_name):
        global print_title
        print_title = True # always true, options for user
        if(print_title):
            print_title = False
            title =  "| sample".ljust(SAMPLE_LEN+2)
            title += " | solver".ljust(SOLVER_LEN+3)
            title += " | #SAT".ljust(NUMBER_LEN+3)
            title += " | #UNSAT".ljust(NUMBER_LEN+3)
            title += " | #ALL".ljust(NUMBER_LEN+3)
            title += " | PAR-2".ljust(NUMBER_LEN+3)
            title += " | #Best".ljust(NUMBER_LEN+3)
            title += " | #Mono".ljust(NUMBER_LEN+3)
            title += " |"
            print(title)

            print(self.split_line)

        for slv in self.solvers:
            line =  "| "  + (samp_name + "("+str(self.sample_ins_ct) + ")").ljust(SAMPLE_LEN)
            line += " | " + slv.print_name.ljust(SOLVER_LEN)
            line += " | " + str(slv.sat_num).ljust(NUMBER_LEN)
            line += " | " + str(slv.unsat_num).ljust(NUMBER_LEN)
            line += " | " + str(slv.solved_num).ljust(NUMBER_LEN)
            line += " | " + str(round(slv.PAR_all_time,2)).ljust(NUMBER_LEN)
            line += " | " + str(slv.best_num).ljust(NUMBER_LEN)
            line += " | " + str(slv.mono_num).ljust(NUMBER_LEN)
            line += " |"
            print(line)
        
    def cal_and_show(self):
        fout = open("res.csv", "w")
        fout.write("instance, solver, res, time\n")   # log.csv can be disabled here

        for sample in self.sample_dirs:
            title_line = ""
            for slv in self.solvers:
                title_line += slv.print_name.ljust(18)
                
            samp_dir  = sample[0]
            samp_name = sample[1]
            print_line_ct = 0

            # print options for user
            ##################################################################
            sample_ins_ct = 0
            for slv in self.solvers:
                slv.reset()
            for ins_name in open(samp_dir):
                sample_ins_ct += 1
                ins_name = ins_name.strip()
                best_time = CUTOFF*PUNISH
                solved_ct = 0
                for slv in self.solvers:
                    slv.cal_soln(ins_name)
                    best_time = min(slv.datas[ins_name].time, best_time)
                    if not slv.datas[ins_name].res == "unknown":
                        solved_ct += 1
                if(not best_time == CUTOFF*PUNISH):
                    for slv in self.solvers:
                        if(slv.datas[ins_name].time == best_time):
                            slv.datas[ins_name].best = True
                            slv.best_num += 1
                            if(solved_ct == 1):
                                slv.datas[ins_name].mono = True
                                slv.mono_num += 1    

                line = ""
                no_answer       = True
                answer_this     = "unknown"
                all_can_solve   = True
                have_diff_res   = False
                all_too_easy    = True
                all_can_solve   = True
                for slv in self.solvers:
                    stt = slv.datas[ins_name]
                    line += slv.to_string(stt)
                    fout.write(ins_name + "," + slv.print_name + "," + stt.res + "," + str(stt.time) + "\n")
                        
                    if(stt.res == "unknown" or (stt.res != "unknown" and stt.time > 1)):
                        all_too_easy = False
                    if(not stt.res == "unknown"):
                        no_answer = False
                        answer_this = stt.res
                    elif(stt.res == "unknown"):
                        all_can_solve = False
                line += ins_name
                if(not all_can_solve and not no_answer):
                    have_diff_res = True      
                
                
                ## !!!!!!! change here !!!!!!!
                if(True):
                # if(False):
                # if(have_diff_res):
                # if(all_too_easy):
                # if(no_answer):
                # if(not no_answer and solvers[0].datas[ins_name].time>1):
                    print(line)
                    print_line_ct += 1
                
                ##################################################################

            self.sample_ins_ct = sample_ins_ct
            for slv in self.solvers:
                slv.deal_avg() 
            
            if(print_line_ct>0):
                print("print line ct = ", print_line_ct)
            else:
                print(self.split_line)

            self.__show_in_mark_down(samp_name)
            
           

       

if __name__ == "__main__":
    base_dir = os.getcwd()

    # example1: the first set of experiments
    ##################################################################
    solvers = []        
    solvers.append(solver_SAT_standard_gnomon(os.path.join(base_dir, "res/RLNT"), "RLNT"))
    solvers.append(solver_SAT_standard_gnomon(os.path.join(base_dir, "res/PRS_4"), "PRS_4"))


    samples = []
    samples.append([os.path.join(base_dir, "ins/bench1/part1.txt"), "bench1_part1"])
    samples.append([os.path.join(base_dir, "ins/bench2/all.txt"), "bench2_all"])

    clt = calculater(solvers, samples)
    clt.cal_and_show()
    ##################################################################



    # example2: the second set of experiments 
    ##################################################################
    solvers = []        
    
    solvers.append(solver_SAT_standard_gnomon(os.path.join(base_dir, "res/RLNT"), "RLNT"))
    for i in [4, 8]:
        solvers.append(solver_SAT_standard_gnomon(os.path.join(base_dir, "res/PRS_{}".format(i)), "PRS_{}".format(i)))


    samples = []
    samples.append([os.path.join(base_dir, "ins/bench1/part2.txt"), "bench1_part2"])
    samples.append([os.path.join(base_dir, "ins/bench1/all.txt"), "bench1_all"])

    clt = calculater(solvers, samples)
    clt.cal_and_show()
    ##################################################################


    # example3: prepare data for CDF plot  
    ##################################################################
    solvers = []        
    solvers.append(solver_SAT_standard_gnomon(os.path.join(base_dir, "res/kissat_inc"), "kissat_inc"))
    solvers.append(solver_SAT_standard_gnomon(os.path.join(base_dir, "res/RLNT"), "RLNT"))
    for i in [4, 8]:
        solvers.append(solver_SAT_standard_gnomon(os.path.join(base_dir, "res/PRS_{}".format(i)), "PRS_{}".format(i)))


    samples = []
    samples.append([os.path.join(base_dir, "ins/bench1/all.txt"), "bench1"])

    clt = calculater(solvers, samples)
    clt.cal_and_show()
    ##################################################################
    