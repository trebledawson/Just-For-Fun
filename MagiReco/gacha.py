# #################################################################### #
# gacha.py                                                             #
# Author: Glenn Dawson (2019)                                          #
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
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

VERBOSE = False

def main():
    prompt = input('What would you like to do? [expectation, likelihood, plot] :')
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
    likelihoods = pd.DataFrame(index=range(1001),
                               columns=['Prob(0)', 'Prob(1)', 
                                        'Prob(2)', 'Prob(3)', 
                                        'Prob(4+)'])
                                        
    for n_rolls in range(1001):
        trials = []
        while len(trials) < k:
            trials.append(draw_n(n_rolls, ten_draws))
            
        for n_banner in range(5):
            if n_banner < 4:
                col = 'Prob(' + str(n_banner) + ')'
            else:
                col = 'Prob(4+)'
            
            probability = trials.count(n_banner) / k
            likelihoods.loc[n_rolls, col] = probability
            
        if n_rolls % 100 == 0:
            print('Trials for', n_rolls, 'rolls completed.')
    
    likelihoods.to_csv('gacha_likelihoods_smooth_' + str(k) + '.csv',
                       float_format='%.6f')
    print('Script runtime: {:.8f} seconds.'.format(time.time() - start))


def draw_n(n_rolls, ten_draws=True):
    n_banner = 0
    rolls = 0
    pity = 0
    while rolls < n_rolls:
        if ten_draws:
            if pity < 90:  # Do ten-draws below 90
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
            else:  # Rolls 90 - 99
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
    rolls = []
    spooks = []
    
    while len(rolls) < k:
        n_rolls, n_spooks = find_ssr(n, ten_draws)
        rolls.append(n_rolls)
        spooks.append(n_spooks)
        if len(rolls) % 1000 == 0:
            print('Trials:', len(rolls), '| Sample rolls:', n_rolls, 
                  '| Sample spooks:', n_spooks)
        
    avg = mean(rolls)
    confidence_999 = 3.291 * (stdev(rolls) / sqrt(k))
    print('Average number of rolls required to get', n,
          'copies of the banner SSR over', k, 'trials: {0:.2f} +/- '
          '{1:.3f} (99.9% confidence)'.format(avg, confidence_999))
      
    avg_s = mean(spooks)
    confidence_999_s = 3.291 * (stdev(spooks) / sqrt(k))
    print('Average number of spooks drawn while rolling for', n,
          'copies of the banner SSR over', k, 'trials: {0:.2f} +/- '
          '{1:.3f} (99.9% confidence)'.format(avg_s, confidence_999_s))
    
    print('Script runtime: {:.8f} seconds.'.format(time.time() - start))


def find_ssr(n=4, ten_draws=True):
    n_banner = 0
    n_spook = 0
    rolls = 0
    pity = 0
    while n_banner < n:
        if ten_draws:
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
                                if VERBOSE:
                                    print('Banner', n_banner, 
                                          'found in', rolls, 'rolls.')
                            else:  # Spook!
                                n_spook += 1
                                if VERBOSE:
                                    print('Spooked! Total spooks:', 
                                          n_spook)
                    else:  # 10th roll has 2% chance
                        if roll <= 1:  # SSR Success
                            pity = 0  # Reset pity
                            if random.randint(0, 99) < 60:  # Banner
                                n_banner += 1
                                if VERBOSE:
                                    print('Banner', n_banner, 
                                          'found in', rolls, 'rolls.')
                            else:  # Spook!
                                n_spook += 1
                                if VERBOSE:
                                    print('Spooked! Total spooks:', 
                                          n_spook)
            else:  # Do one-rolls from 90-100
                pity += 1
                rolls += 1
                if pity == 100:  # Guaranteed SSR at 100
                    pity = 0  # Reset pity
                    if random.randint(0, 99) < 60:  # Banner
                        n_banner += 1
                        if VERBOSE:
                            print('Banner', n_banner, 
                                  'found in', rolls, 'rolls.')
                    else:  # Spook!
                        n_spook += 1
                        if VERBOSE:
                            print('Spooked! Total spooks:', 
                                  n_spook)
                else:  # Rolls 90 - 99
                    if random.randint(0, 99) == 0:  # SSR success
                        pity = 0  # Reset pity
                        if random.randint(0, 99) < 60:  # Banner
                            n_banner += 1
                            if VERBOSE:
                                print('Banner', n_banner, 
                                      'found in', rolls, 'rolls.')
                        else:  # Spook!
                            n_spook += 1
                            if VERBOSE:
                                print('Spooked! Total spooks:', 
                                      n_spook)
        else:
            pity += 1
            rolls += 1
            if pity == 100:  # Guaranteed SSR at 100
                pity = 0  # Reset pity
                if random.randint(0, 99) < 60:  # Banner
                    n_banner += 1
                    if VERBOSE:
                        print('Banner', n_banner, 
                              'found in', rolls, 'rolls.')
                else:  # Spook!
                    n_spook += 1
                    if VERBOSE:
                        print('Spooked! Total spooks:', 
                              n_spook)
            else:  # Rolls 90 - 99
                if random.randint(0, 99) == 0:  # SSR success
                    pity = 0  # Reset pity
                    if random.randint(0, 99) < 60:  # Banner
                        n_banner += 1
                        if VERBOSE:
                            print('Banner', n_banner, 
                                  'found in', rolls, 'rolls.')
                    else:  # Spook!
                        n_spook += 1
                        if VERBOSE:
                            print('Spooked! Total spooks:', 
                                  n_spook)
    return rolls, n_spook


def plot_gacha():
    smooth = input('Smooth plot? y/[n] : ')
    if smooth == 'y':
        smooth = True
    else:
        smooth = False
        
    k = input('How many trials? [10000] : ')
    if not k:
        k = 10000
    else:
        k = int(k)
    
    if smooth:
        filepath = 'gacha_likelihoods_smooth_' + str(k) + '.csv'
    else:
        filepath = 'gacha_likelihoods_' + str(k) + '.csv'
    data = pd.read_csv(filepath, index_col=0)
    data.plot()
    plt.grid()
    plt.xlim(-10, 1010)

    ev = data @ np.array([0, 1, 2, 3, 4])
    data['Expected Value'] = ev
    
    data.plot(y='Expected Value', legend=False)
    plt.grid()
    plt.xlim(-10, 1010)
    plt.show()
    
    
if __name__ == '__main__':
    main()
