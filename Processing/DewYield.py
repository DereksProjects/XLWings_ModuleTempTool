# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 11:03:01 2019

@author: dholsapp
"""

import numpy as np
from numba import jit             # Package that allows direct machine language code calculations



# H is the site elevation in kilometers, *need to convert raw data to kilometers raw data is in meters
# tD is Dewpoint temperature in Celsius
# n = cloud coverage okta, *will need to convert with IW2 data is in tenths
#tA is air temperature "dry bulb temperature"
# windSpeed is air or windspeed measure in m*s^-1  or m/s
# Cut-off windspeed



#mm·d−1

@jit(nopython=True , error_model = 'python') # Numba Machine Language Level ( Fast Processing )
def dewYield( h , tD , tA , windSpeed , n ):
    
    windSpeedCutOff = 4.4 

    dewYield = .37 * ( 1 + ( 0.204323 * h ) - (0.0238893 * h**2 ) - \
               ( 18.0132 - ( 1.04963 * h**2 ) + ( 0.21891 * h**2 ) ) * (10**( -3 ) * tD ) ) * \
               ( ( ( ( tD + 273.15)/285)**4)*(1 - (n/8))) + (0.06 * (tD - tA ) ) * \
               ( 1 + 100 * ( 1 - np.exp( - ( windSpeed / windSpeedCutOff)**20 ) ) )
               
    return dewYield