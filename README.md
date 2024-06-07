# Just For Fun
A collection of fun mini-projects.

## MagiReco
A small Monte Carlo simulation of gacha rolls in the mobile game Magia Record. Simulates the average number of rolls required to obtain N copies of an event character, along with a 99.9% confidence interval. Also returns the average number of "spooks", or SSR draws that are _not_ the event character, along with an 99.9% confidence interval.

## Set-vs-Keys
An investigation into the unexpected different behavior between set difference and view difference in Python. Notably, set difference appears to be faster for set sizes smaller than 4096; however, above this size the set difference lags considerably at low overlaps due to the probe implementation (found in [setobject.c](https://github.com/python/cpython/blob/main/Objects/setobject.c)).
