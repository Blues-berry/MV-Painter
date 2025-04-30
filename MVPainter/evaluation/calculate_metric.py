import os 
from glob import glob
from elopy import *
import random
import argparse
import ast
def get_pair_win_rate_single(pair_dir,target = 1):
    # calulate win rate with given pair
    img_paths = glob(os.path.join(pair_dir,'*.png'))
    metric_1 = []
    metric_2 = []
    metric_3 = []
    for img in img_paths:
        final_path = img.replace('.png','_final.txt')

        with open(final_path, 'r') as file:
            line = file.readline()  
            numbers = list(map(int, line.strip().split()))  
            metric_1.append(numbers[0])
            metric_2.append(numbers[1])
            metric_3.append(numbers[2])
    
    win_count_1 = metric_1.count(target)
    win_count_2 = metric_2.count(target)
    win_count_3 = metric_3.count(target)


    return win_count_1 * 100.0 / len(metric_1),win_count_2 * 100.0 / len(metric_1),win_count_3 * 100.0 / len(metric_1)

def get_win_rate(pair_dir_list):

    for pair in pair_dir_list:
        win1,win2,win3 = get_pair_win_rate_single(pair,target=1)
        print("======================================================")
        print(f"{pair} result:")
        print(win1,win2,win3)
        win1,win2,win3 = get_pair_win_rate_single(pair,target=2)
        print(win1,win2,win3)







def get_mean_elo(elo_metric):
    from collections import defaultdict

    totals = defaultdict(float)
    counts = defaultdict(int)

    for entry in elo_metric:
        for name, score in entry:
            totals[name] += score
            counts[name] += 1

    averages = {name: totals[name] / counts[name] for name in totals}

    return averages

    
def get_elo_score(pair_dir_list, player_pairs_list = [('hunyuan','mvpainter')],players = ['hunyuan','mvpainter','mvadapter']):
    # calculate elo score with multi-players and their competition results    
    competition_list_metric_1 = []
    competition_list_metric_2 = []
    competition_list_metric_3 = []
    for pair_idx,pair_dir in enumerate(pair_dir_list):
        img_paths = glob(os.path.join(pair_dir,'*.png'))
        for img in img_paths:
            final_path = img.replace('.png','_final.txt')
            with open(final_path, 'r') as file:
                line = file.readline()  
                numbers = list(map(int, line.strip().split()))  
                player_1 = player_pairs_list[pair_idx][0]
                player_2 = player_pairs_list[pair_idx][1]
                # metric 1
                if numbers[0] == 3:
                    winner = 'draw'
                else:
                    winner = player_pairs_list[pair_idx][numbers[0] - 1]
                competition_list_metric_1.append((player_1,player_2,winner))


                # metric 2
                if numbers[1] == 3:
                    winner = 'draw'
                else:
                    winner = player_pairs_list[pair_idx][numbers[1] - 1]
                competition_list_metric_2.append((player_1,player_2,winner))

                # metric 3
                if numbers[2] == 3:
                    winner = 'draw'
                else:
                    winner = player_pairs_list[pair_idx][numbers[2] - 1]
                competition_list_metric_3.append((player_1,player_2,winner))

    
    # random shuffle 10 times to alleviate elo random effect
    elo_metric_1 = []
    elo_metric_2 = []
    elo_metric_3 = []
    for i in range(100):
        elo_scorer_1 = Implementation()
        elo_scorer_2 = Implementation()
        elo_scorer_3 = Implementation()

        for player in players:
            elo_scorer_1.addPlayer(player)
            elo_scorer_2.addPlayer(player)
            elo_scorer_3.addPlayer(player)

        random.shuffle(competition_list_metric_1)
        random.shuffle(competition_list_metric_2)
        random.shuffle(competition_list_metric_3)

        for m in range(len(competition_list_metric_1)):
            # metric_1
            if competition_list_metric_1[m][2] == 'draw':
                elo_scorer_1.recordMatch(competition_list_metric_1[m][0],competition_list_metric_1[m][1],draw = True)
            else:
                elo_scorer_1.recordMatch(competition_list_metric_1[m][0],competition_list_metric_1[m][1],winner = competition_list_metric_1[m][2])
            
            # metric_2
            if competition_list_metric_2[m][2] == 'draw':
                elo_scorer_2.recordMatch(competition_list_metric_2[m][0],competition_list_metric_2[m][1],draw = True)
            else:
                elo_scorer_2.recordMatch(competition_list_metric_2[m][0],competition_list_metric_2[m][1],winner = competition_list_metric_2[m][2])


            # metric_3
            if competition_list_metric_3[m][2] == 'draw':
                elo_scorer_3.recordMatch(competition_list_metric_3[m][0],competition_list_metric_3[m][1],draw = True)
            else:
                elo_scorer_3.recordMatch(competition_list_metric_3[m][0],competition_list_metric_3[m][1],winner = competition_list_metric_3[m][2])
        
        elo_metric_1.append(elo_scorer_1.getRatingList())
        elo_metric_2.append(elo_scorer_2.getRatingList())
        elo_metric_3.append(elo_scorer_3.getRatingList())
    
    # 创建一个字典来累加每个人的总分
    print("metric 1: ")
    print(get_mean_elo(elo_metric_1))
    print("metric 2: ")
    print(get_mean_elo(elo_metric_2))
    print("metric 3: ")
    print(get_mean_elo(elo_metric_3))



    
    




if __name__ == "__main__":
    pair_hunyuan_mvpainter = '/mnt/xlab-nas-2/shaomingqi.smq/projects/aigc3d_dev/aigc3d/data_process/evaulate_mvpainter/eval_temp/hunyuan-MVPainter-trellis'
    pair_hunyuan_mvadapter = '/mnt/xlab-nas-2/shaomingqi.smq/projects/aigc3d_dev/aigc3d/data_process/evaulate_mvpainter/eval_temp/hunyuan-mvadapter-trellis'
    pair_mvadpter_mvpainter = '/mnt/xlab-nas-2/shaomingqi.smq/projects/aigc3d_dev/aigc3d/data_process/evaulate_mvpainter/eval_temp/mvadapter-MVPainter-trellis'




    pair_result_dirs = [pair_hunyuan_mvpainter,pair_hunyuan_mvadapter,pair_mvadpter_mvpainter]
    pair_names = [('hunyuan','mvpainter'),('hunyuan','mvadapter'),('mvadapter','mvpainter')]
    
    # # get pair win rate
    # get_win_rate(pair_result_dirs)


    # get all ranking scores
    get_elo_score(pair_result_dirs,pair_names)