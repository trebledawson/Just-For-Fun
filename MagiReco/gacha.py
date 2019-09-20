# #################################################################### #
# gacha.py                                                             #
# Author: picardyThird (2019)                                          #
# -----                                                                #
# This file performs a Monte Carlo simulation of a large number of     #
# rolls on an event banner in the game Magia Record. The objective is  #
# to determine the number of rolls necessary to obtain four copies of  #
# the banner SSR.                                                      #
# #################################################################### #

import time
import random
from statistics import mean, stdev
from math import sqrt
from multiprocessing import Pool
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

VERBOSE = False

def main():
    prompt = input(
        'What would you like to do? [expectation, likelihood, plot] : ')
    if prompt not in ['expectation', 'likelihood', 'plot']:
        raise ValueError('Invalid input')
    elif prompt == 'expectation':
        expected_rolls()
    elif prompt == 'likelihood':
        likelihood()
    elif prompt == 'plot':
        plot_gacha()


def likelihood():
    ten_draws = input('Use 10-draws? [y]/n: ')
    if not ten_draws or ten_draws.lower() != 'n':
        ten_draws = True
    else:
        ten_draws = False
    
    k = input('How many trials would you like to run? [10000]: ')
    if not k:
        k = 10000
    else:
        k = int(k)

    start = time.time()
    p = Pool()
    likelihoods = p.map(trials,  # Ordered list of lists
        [(i, k, ten_draws) for i in range(1001)])
    p.close()
    p.join()
    
    likelihoods = pd.DataFrame(likelihoods,
                               index=range(1001),
                               columns=['Prob(0)', 'Prob(1)', 
                                        'Prob(2)', 'Prob(3)', 
                                        'Prob(4+)'])
    
    likelihoods.to_csv('gacha_likelihoods_' + str(k) + '.csv',
                       float_format='%.6f')
    print('Script runtime: {:.8f} seconds.'.format(time.time() - start))


def trials(args):
    trial = []
    while len(trial) < args[1]:
        trial.append(draw_n(args[0], args[2]))
    
    if args[0] % 100 == 0:
        print('Trials for', args[0], 'rolls completed.')
        
    likelihood = []
    for n_banner in range(5):
        likelihood.append(trial.count(n_banner) / args[1])
        
    return likelihood


def draw_n(n_rolls, ten_draws=True):
    n_banner = 0
    rolls = 0
    pity = 0
    while rolls < n_rolls:
        if ten_draws:
            # Do ten-draws below 90 if there are more than 10 left
            if pity < 90 and n_rolls - rolls > 10:  
                for ten_draw in range(10):
                    roll = random.randint(0, 99)
                    rolls += 1
                    pity += 1
                    if ten_draw < 9:  # First 9 rolls have 1% chance
                        if roll == 0:  # SSR success
                            pity = 0  # Reset pity
                            if random.randint(0, 99) < 60:  # Banner
                                n_banner += 1
                    else:  # 10th roll has 2% chance
                        if roll <= 1:  # SSR Success
                            pity = 0  # Reset pity
                            if random.randint(0, 99) < 60:  # Banner
                                n_banner += 1
            else:  # Do one-rolls from 90-100
                rolls += 1
                pity += 1
                if pity == 100:  # Guaranteed SSR at 100
                    pity = 0  # Reset pity
                    if random.randint(0, 99) < 60:  # Banner
                        n_banner += 1
                else:  # Rolls 91 - 99
                    if random.randint(0, 99) == 0:  # SSR success
                        pity = 0  # Reset pity
                        if random.randint(0, 99) < 60:  # Banner
                            n_banner += 1
        else:
            rolls += 1
            pity += 1
            if pity == 100:  # Guaranteed SSR at 100
                pity = 0  # Reset pity
                if random.randint(0, 99) < 60:  # Banner
                    n_banner += 1
            else:  # Rolls 91 - 99
                if random.randint(0, 99) == 0:  # SSR success
                    pity = 0  # Reset pity
                    if random.randint(0, 99) < 60:  # Banner
                        n_banner += 1
        
        if n_banner >= 4:
            return 4
            
    return n_banner


def expected_rolls():
    ten_draws = input('Use 10-draws? [y]/n: ')
    if not ten_draws or ten_draws.lower() != 'n':
        ten_draws = 'y'
    else:
        ten_draws = 'n'
        
    n = input('How many banner SSR copies do you want to find? [4]: ')
    if not n:
        n = 4
    else:
        n = int(n)
    
    k = input('How many trials would you like to run? [10000]: ')
    if not k:
        k = 10000
    else:
        k = int(k)
    
    start = time.time()
    
    p = Pool()
    rolls = p.map(find_ssr, [(i, n, ten_draws) for i in range(k)])
    p.close()
    p.join()
        
    avg = mean(rolls)
    confidence_999 = 3.291 * (stdev(rolls) / sqrt(k))
    print('Average number of rolls required to get', n,
          'copies of the banner SSR over', k, 'trials: {0:.2f} +/- '
          '{1:.3f} (99.9% confidence)'.format(avg, confidence_999))
    
    print('Script runtime: {:.8f} seconds.'.format(time.time() - start))


def find_ssr(args):
    n_banner = 0
    rolls = 0
    pity = 0
    while n_banner < args[1]:
        if args[2]:
            if pity < 90:  # Do ten-draws below 90
                for ten_draw in range(10):
                    roll = random.randint(0, 99)
                    pity += 1
                    rolls += 1  
                    if ten_draw < 9:  # First 9 rolls have 1% chance
                        if roll == 0:  # SSR success
                            pity = 0  # Reset pity
                            if random.randint(0, 99) < 60:  # Banner
                                n_banner += 1
                    else:  # 10th roll has 2% chance
                        if roll <= 1:  # SSR Success
                            pity = 0  # Reset pity
                            if random.randint(0, 99) < 60:  # Banner
                                n_banner += 1
            else:  # Do one-rolls from 90-100
                pity += 1
                rolls += 1
                if pity == 100:  # Guaranteed SSR at 100
                    pity = 0  # Reset pity
                    if random.randint(0, 99) < 60:  # Banner
                        n_banner += 1
                else:  # Rolls 90 - 99
                    if random.randint(0, 99) == 0:  # SSR success
                        pity = 0  # Reset pity
                        if random.randint(0, 99) < 60:  # Banner
                            n_banner += 1
        else:
            pity += 1
            rolls += 1
            if pity == 100:  # Guaranteed SSR at 100
                pity = 0  # Reset pity
                if random.randint(0, 99) < 60:  # Banner
                    n_banner += 1
            else:  # Rolls 90 - 99
                if random.randint(0, 99) == 0:  # SSR success
                    pity = 0  # Reset pity
                    if random.randint(0, 99) < 60:  # Banner
                        n_banner += 1
    if args[0] % 1000 == 0:
        print('Trials:', args[0], '| Sample rolls:', rolls)
        
    return rolls


def plot_gacha():        
    k = input('How many trials? [10000] : ')
    if not k:
        k = 10000
    else:
        k = int(k)
    filepath = 'gacha_likelihoods_' + str(k) + '.csv'
    
    data = pd.read_csv(filepath, index_col=0)
    data.plot()
    plt.grid()
    plt.xlabel('Number of draws')
    plt.ylabel('Probability')
    plt.title(
        'Probability of Drawing Banner Magical Girl N Times In K Pulls')
    plt.xlim(-10, 1010)

    ev = data @ np.array([0, 1, 2, 3, 4])
    data['Expected Value'] = ev
    data.plot(y='Expected Value', legend=False)
    plt.grid()
    plt.xlabel('Number of draws')
    plt.ylabel('Number of copies')
    plt.title(
        'Expected Number of Copies of Banner Magical Girl in K Pulls')
    plt.xlim(-10, 1010)
    
    plt.figure()
    plt.plot(1 - data.iloc[:, 0])
    plt.grid()
    plt.xlabel('Number of draws')
    plt.ylabel('Probability')
    plt.title('Probability of Drawing At Least One Copy of the Banner Girl in K Pulls')
    plt.xlim(-10, 1010)
    plt.show()
    
    
if __name__ == '__main__':
    main()
