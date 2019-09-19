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

VERBOSE = False

def main(ten_draws=True):
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
    
    
if __name__ == '__main__':
    if input('Use 10-draws? [y]/n: ').lower() is not 'n':
        main()
    else:
        main(ten_draws=False)
