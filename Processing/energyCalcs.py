# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 11:03:01 2019

@author: dholsapp
"""

import numpy as np
from numba import jit             # Package that allows direct machine language code calculations
import math


# H is the site elevation in kilometers, *need to convert raw data to kilometers raw data is in meters
# tD is Dewpoint temperature in Celsius
# n = cloud coverage okta, *will need to convert with IW2 data is in tenths
#tA is air temperature "dry bulb temperature"
# windSpeed is air or windspeed measure in m*s^-1  or m/s
# Cut-off windspeed



#mm·d−1

class energyCalcs:


    @jit(nopython=True , error_model = 'python') # Numba Machine Language Level ( Fast Processing )
    def dewYield( h , tD , tA , windSpeed , n ):
        
        windSpeedCutOff = 4.4 
    
        dewYield = .37 * ( 1 + ( 0.204323 * h ) - (0.0238893 * h**2 ) - \
                   ( 18.0132 - ( 1.04963 * h**2 ) + ( 0.21891 * h**2 ) ) * (10**( -3 ) * tD ) ) * \
                   ( ( ( ( tD + 273.15)/285)**4)*(1 - (n/8))) + (0.06 * (tD - tA ) ) * \
                   ( 1 + 100 * ( 1 - np.exp( - ( windSpeed / windSpeedCutOff)**20 ) ) )
                   
        return dewYield
    
    
    '''
    HELPER METHOD
    
    waterVaporPressure()
    
    Find the average water vapor pressure (kPa) based on the Dew Point Temperature 
    model created from Mike Kempe on 10/07/19.  
    
    @param dewPtTemp          -float, Dew Point Temperature
    
    
    @return                   -float, return water vapor pressur in kPa
    
    '''
    
    def waterVaporPressure( dewPtTemp ):
    
        return( math.exp(( 3.257532E-13 * dewPtTemp**6 ) - 
                ( 1.568073E-10 * dewPtTemp**6 ) + 
                ( 2.221304E-08 * dewPtTemp**4 ) + 
                ( 2.372077E-7 * dewPtTemp**3) - 
                ( 4.031696E-04 * dewPtTemp**2) + 
                ( 7.983632E-02 * dewPtTemp ) - 
                ( 5.698355E-1))
                
                )
    
    '''
    HELPER METHOD
    
    rH_Above85()
    
    Determine if the relative humidity is above 85%.  
    
    @param rH          -float, Relative Humidity %
    
    
    @return                   -Boolean, True if the relative humidity is abover 85% and 
                                        return False if the relative humidity is below 85%
    
    '''    
    def rH_Above85( rH ):    
        if rH > 85:
            return( True )
        else:
            return ( False )
     
    '''
    HELPER METHOD
    
    hoursRH_Above85()
    
    Count the number of hours relative humidity is above 85%.  
    
    @param    df          -dataFrame, dataframe containing Relative Humidity %
    
    
    @return              -int, number of hours relative humidity is above 85%
    
    '''    
    def hoursRH_Above85( df ):      
        
        booleanDf = df.apply(lambda x: energyCalcs.rH_Above85( x ) )
        return( booleanDf.sum() )
        
    #test = level_1_df['Relative humidity'].apply(lambda x: rH_Above85( x ) )    
    #test2 =  hoursRH_Above85( level_1_df['Relative humidity'] )   
    '''
    HELPER METHOD
    
    whToGJ()
    
    Convert Wh/m^2 to GJ/m^-2 
    
    @param wh          -float, Wh/m^2
    
    
    @return                   -float, GJ/m^-2
    
    '''
    def whToGJ( wh ):
    
        return( 0.0000036 * wh )
    
    '''
    HELPER METHOD
    
    gJtoMJ()
    
    Convert GJ/m^-2 to MJ/y^-1
    
    @param gJ          -float, Wh/m^2
    
    
    @return            -float, GJ/m^-2
    
    '''
    def gJtoMJ( gJ ):
    
        return( gJ * 1000 )