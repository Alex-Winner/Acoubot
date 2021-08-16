import numpy as np
import matplotlib.pyplot as plt
import cv2 as cv
import pandas as pd
from scipy import constants
import acoustics


def dbspl_check(analyzed_noise_dba):

    # analyzed_noise_spectrum= #dBspl
    # analyzed_snr
    # analyzed_rt60

    noise_state = dba_status(analyzed_noise_dba)
    if noise_state == 1:
        print('High Noise level')
    if noise_state == 2:
        print('limited noise level')
    if noise_state == 3:
        print('Good noise level')

    return noise_state


def dba_status(dba):
    if dba <= 35:
        return 3
    if dba > 35 and dba <= 40:
        return 2
    if dba > 40:
        return 1


def hist_compare(pic1, pic2):
    hist_comp = cv.compareHist(pic1, pic2, cv.HISTCMP_CORREL)
    return hist_comp


def spectrum_matching(bench_spect, mode):
    bench_hist = np.array(bench_spect, dtype=np.float32)
    if mode == 1:
        df = pd.read_csv(r'noise_profile.csv')
        list_of_rows = [list(row) for row in df.values]
        row_array = np.array(list_of_rows)
        for n in range(row_array.shape[0]):
            check_name = row_array[n, 0]
            check_spect = row_array[n, 1:(row_array.shape[1]-1)]
            check_spect = list(map(int, check_spect))
            check_hist = np.array(check_spect, dtype=np.float32)
            compare_score_new = hist_compare(bench_hist, check_hist)
            if n == 0:
                compare_score_old = compare_score_new
                closest_match_spect = check_spect
                closest_match_name = check_name
            else:
                if compare_score_new > compare_score_old:
                    compare_score_old = compare_score_new
                    closest_match_spect = check_spect
                    closest_match_name = check_name
        return closest_match_name, closest_match_spect
    elif mode == 2:
        df = pd.read_csv(r'Sound_Absorption_Profile.csv')
        list_of_rows = [list(row) for row in df.values]
        row_array = np.array(list_of_rows)
        for n in range(row_array.shape[0]):
            check_name = row_array[n, 0]
            check_spect = row_array[n, 1:]
            check_spect = list(map(float, check_spect))
            check_hist = np.array(check_spect, dtype=np.float32)
            compare_score_new = hist_compare(bench_hist, check_hist)
            if n == 0:
                compare_score_old = compare_score_new
                farthest_match_spect = check_spect
                farthest_match_name = check_name
            else:
                if compare_score_new < compare_score_old:
                    compare_score_old = compare_score_new
                    farthest_match_spect = check_spect
                    farthest_match_name = check_name
        return farthest_match_name, farthest_match_spect


def SAC_subtraction(SAC):
    bench_hist = np.array(SAC, dtype=np.float32)
    df = pd.read_csv(r'Sound_Absorption_Profile.csv')
    
    #transforms the csv file 
    #from panda format to list array
    #and then transforms csv from list array to numpy array
    list_of_rows = [list(row) for row in df.values]
    row_array = np.array(list_of_rows)
    
    #subtracts the sampled alpha (sound absorption coefficient)
    #with the database sampled alpha
    #and stores the answer in a new array 
    sublist = []
    top3_sac = []
    for n in range(row_array.shape[0]):
        check_spect = row_array[n, 1:]
        check_spect = list(map(float, check_spect))
        check_hist = np.array(check_spect, dtype=np.float32)
        sub_new = np.sum(np.subtract(check_hist, bench_hist))
        sublist.append(sub_new)
    
    #finds the top 3 Absorption coefficients
    #by 
    n = 0
    while n < 3:
        t = sublist.index(max(sublist))
        temp = row_array[t, :]
        top3_sac.append(temp)
        sublist.pop(t)
        n += 1
    top3_sac = np.array(top3_sac)
    return top3_sac


def optimal_RT60(S_sac, alpha_sac, S_database, alpha_database, RT60, V):
    opt_RT60 = RT60
    S_temp = 0.1
    alpha_database = np.array(alpha_database)
    while np.amax(opt_RT60) >= 0.6 and S_temp<=S_database and np.mean(opt_RT60)>0.5:
        Sa_check = np.subtract(
            np.add((S_sac*alpha_sac), (S_temp*alpha_database)), (S_temp*alpha_sac))
        opt_RT60 = (V * 24 * np.log(10)) / \
            (Sa_check * constants.speed_of_sound)
        S_temp += 0.1
        S_temp = round(S_temp,1)
        current_RT60=np.mean(opt_RT60)
    return opt_RT60, S_temp


def problem2solution_noise(dba_data, noise_data):
    # checks db_spl level.
    dba_state = dbspl_check(dba_data)

    match_noise_name = 0
    match_noise_spect = 0

    # if db_spl level is above 40dbA it will initiate a band scan
    # it will find the closest band pattern from the database
    if dba_state == 1:
        mode = 1
        #freq=(63 ,	125 ,	250 ,	500 ,	1000 ,	2000 ,	4000 ,	8000 )
        match_noise_name, match_noise_spect = spectrum_matching(
            noise_data, mode)
        if match_noise_name == 'Car Horn':
            
            print(match_noise_name)
            print('1')
        elif match_noise_name == 'Window Air-Conditioning Unit':
            print(match_noise_name)
        elif match_noise_name == 'Computer Equipment Room':
            print(match_noise_name)
        elif match_noise_name == 'Mechanical Equipment Room':
            print(match_noise_name)
        elif match_noise_name == 'Classroom':
            print(match_noise_name)
            
        else:
            print(match_noise_name)
    return match_noise_name, match_noise_spect, dba_state



def check_RT60(RT60):
    
    
    
    
    return
    
def problem2solution_rt60(RT60, V, S, S_tunable_wall):
    # SAC= Sound absorption coefficient
    SAC = (V * 24 * np.log(10)) / (S * constants.speed_of_sound * RT60)

    mode = 2
    # match_RT60_name, match_RT60_spect = spectrum_matching(SAC, mode)
    RT_60_sabine = acoustics.room.t60_sabine(
        S, np.mean(SAC), V, c=constants.speed_of_sound)
    #print('Mean RT_60 sabine = ' + str("{:.2f}".format(np.mean(RT_60_sabine))))
    top_3_alpha = SAC_subtraction(SAC)
    RT60_TOP3 = [['Panel Type', 'Estimated New RT60', 'Space of Panel']]
    for n in range(3):
        match_alpha_spect = top_3_alpha[n, 1:]
        match_alpha_spect = list(map(float, match_alpha_spect))
        
        # match_alpha_spect=
        # S_sac,alpha_sac,S_database,alpha_database,RT60,V
        
        RT60_new, S_panel = optimal_RT60(
            S, SAC, S_tunable_wall, match_alpha_spect, RT60, V)
        S_panel = round(S_panel, 2)
        # RT60_TOP3=[[top_3_alpha[n,0],RT60_new,S_panel]]
        
        RT60_TOP3.append([top_3_alpha[n, 0], RT60_new, S_panel])
        #print(S_panel)
        print('Recommended added surface = ' +
              str("{:.2f}".format(S_panel))+'m^2')
        print('Mean RT_60 calculated = ' +
              str("{:.2f}".format(np.mean(RT60_new))))
    RT60_TOP3 = np.array(RT60_TOP3, dtype=object)
    return SAC, RT60_TOP3

##simulation data##

#dba_data = 56.86328584849456
#S = 63.99762
#V = 32.969404
# RT60 = ([0.3254379090656747, 0.34270609427500387, 0.3228664609702526,
#        0.2446294462364459, 0.25415510017795395, 0.24443892962823643])
#RT60 = np.array(RT60)+0.4
# noise_data = ([64.51018045149306, 59.79445651450761, 49.681341221556266, 49.00627307470151,
#              44.49736542763975, 40.83630334252646, 41.37733787786285, 36.47498512720693])
#S_tunable_wall = np.sum([5,      3.35282,    2.159,      5.1308,     10.6426])
#problem2solution(dba_data, noise_data, RT60, V, S, S_tunable_wall)
#
#
# print('end')
# plt.show()
