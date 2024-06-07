from timeit import default_timer as timer
from collections import defaultdict
from multiprocessing import Pool

import numpy as np
import matplotlib.pyplot as plt


def trend_plot():
    n_elements = 4096
    n_trials = 1000
    overlaps = np.linspace(0, 1.0, 100)
    
    set_results = []
    key_results = []
    
    tic = timer()
    pool = Pool()
    for overlap in overlaps:
        overlap_tic = timer()
        results = pool.starmap(
            run_trial, 
            [(overlap, n_elements) for n in range(n_trials)]
        )
        results = np.array(results)
        set_results.append(np.mean(results[:, 0]) * 1000)
        key_results.append(np.mean(results[:, 1]) * 1000)
        print(f'Overlap: {overlap * 100:.3f}% ({timer() - overlap_tic:.3f}s)')
    pool.close()
    pool.join()
    print(f'Total computation time: {timer() - tic:.3f} seconds')
    
    plt.plot(overlaps * 100, set_results, label='Set difference')
    plt.plot(overlaps * 100, key_results, label='Key difference')
    
    plt.xlabel('Overlap (%)')
    plt.ylabel('Time (ms)')
    plt.title(f'Set difference vs. key difference mean runtime '
              f'({n_elements} elements, {n_trials} trials)')
    plt.grid()
    plt.legend()
    
    plt.show()
    

def statistical_trials():
    n_elements = 10_000
    n_trials = 10_000
    overlaps = [1.0, 0.75, 0.50, 0.25, 0.0]
    
    full_tic, tic = timer(), timer()
    results = defaultdict(list)
    for trial in range(n_trials):
        if trial % 1000 == 0:
            print(f'{trial} / {n_trials} ({timer() - tic:.3f}s)')
            tic = timer()
        for overlap in overlaps:
            set_time, key_time = run_trial(overlap, n_elements)
            results[(overlap, 'set')].append(set_time)
            results[(overlap, 'key')].append(key_time)
    print(f'Total computation time: {timer() - full_tic:.3f} seconds')
    
    print(f'\n'
          f'Set size: {n_elements}'
          f'\n')
    
    print('===== set(x) - set(y) =====')
    for overlap in overlaps:
        print(f'overlap={int(100 * overlap):>3}% | '
              f'Mean: {np.mean(results[(overlap, "set")]) * 1000:.3f} ms | '
              f'Std: {np.std(results[(overlap, "set")]) * 1000:.3f} ms | '
              f'Min: {np.min(results[(overlap, "set")]) * 1000:.3f} ms | '
              f'Max: {np.max(results[(overlap, "set")]) * 1000:.3f} ms')
    
    print('\n')
    
    print('===== x.keys() - y.keys() =====')
    for overlap in overlaps:
        print(f'overlap={int(100 * overlap):>3}% | '
              f'Mean: {np.mean(results[(overlap, "key")]) * 1000:.3f} ms | '
              f'Std: {np.std(results[(overlap, "key")]) * 1000:.3f} ms | '
              f'Min: {np.min(results[(overlap, "key")]) * 1000:.3f} ms | '
              f'Max: {np.max(results[(overlap, "key")]) * 1000:.3f} ms')
    
    print(f'\n'
          f'Average of {n_trials} trials.')


def statistical_trials_with_pool():
    n_elements = 10_000
    n_trials = 10_000
    overlaps = [1.0, 0.75, 0.50, 0.25, 0.0]
    
    tic = timer()
    results = dict()
    pool = Pool()
    for overlap in overlaps:
        overlap_tic = timer()
        times = pool.starmap(
            run_trial, 
            [(overlap, n_elements) for n in range(n_trials)]
        )
        times = np.array(times)
        results[(overlap, 'set')] = {
            'mean': np.mean(times[:, 0]) * 1000,
            'std': np.std(times[:, 0]) * 1000,
            'min': np.min(times[:, 0]) * 1000,
            'max': np.max(times[:, 0]) * 1000
        }
        results[(overlap, 'key')] = {
            'mean': np.mean(times[:, 1]) * 1000,
            'std': np.std(times[:, 1]) * 1000,
            'min': np.min(times[:, 1]) * 1000,
            'max': np.max(times[:, 1]) * 1000
        }
        print(f'Overlap: {overlap * 100:.3f}% ({timer() - overlap_tic:.3f}s)')
    pool.close()
    pool.join()
    print(f'Total computation time: {timer() - tic:.3f} seconds')
    
    print(f'\nSet size: {n_elements}\n')
    
    print('===== set(x) - set(y) =====')
    for overlap in overlaps:
        print(f'overlap={int(100 * overlap):>3}% | '
              f'Mean: {results[(overlap, "set")]["mean"]:.3f} ms | '
              f'Std: {results[(overlap, "set")]["std"]:.3f} ms | '
              f'Min: {results[(overlap, "set")]["min"]:.3f} ms | '
              f'Max: {results[(overlap, "set")]["max"]:.3f} ms')
    
    print('\n')
    
    print('===== x.keys() - y.keys() =====')
    for overlap in overlaps:
        print(f'overlap={int(100 * overlap):>3}% | '
              f'Mean: {results[(overlap, "key")]["mean"]:.3f} ms | '
              f'Std: {results[(overlap, "key")]["std"]:.3f} ms | '
              f'Min: {results[(overlap, "key")]["min"]:.3f} ms | '
              f'Max: {results[(overlap, "key")]["max"]:.3f} ms')
    
    print(f'\nAverage of {n_trials} trials.')
    

def run_trial(overlap=1.0, n_elements=10_000):
    n_overlap = int(n_elements * overlap)
    elements_x = np.arange(n_elements)
    elements_y = np.arange(n_elements)
    elements_y[n_overlap:] *= -1
    np.random.shuffle(elements_x)
    np.random.shuffle(elements_y)
    
    x = {e: None for e in elements_x}
    y = {e: None for e in elements_y}
    
    if np.random.uniform() < 0.5:
        tic = timer()
        p = set(x) - set(y)
        set_time = timer() - tic
        
        tic = timer()
        q = x.keys() - y.keys()
        key_time = timer() - tic
    else:
        tic = timer()
        q = x.keys() - y.keys()
        key_time = timer() - tic
        
        tic = timer()
        p = set(x) - set(y)
        set_time = timer() - tic
    
    return set_time, key_time
    
    
if __name__ == '__main__':
    trend_plot()
    # statistical_trials()
    # statistical_trials_with_pool()
