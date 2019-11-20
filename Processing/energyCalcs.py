"""
Contains energy algorithms for processing.

@author: Derek Holsapple
"""

import numpy as np
from numba import jit             
import math



class energyCalcs:

    
    # Numba Machine Language Level
    @jit(nopython=True , error_model = 'python')  
    def dewYield( h , tD , tA , windSpeed , n ):
        '''
        HELPER FUNCTION
        
        Find the dew yield in (mm·d−1).  Calculation taken from journal
        "Estimating dew yield worldwide from a few meteo data"
            -D. Beysens
        
        @param h          -int, site elevation in kilometers
        @param tD         -float, Dewpoint temperature in Celsius
        @param tA         -float, air temperature "dry bulb temperature"
        @param windSpeed  -float, air or windspeed measure in m*s^-1  or m/s
        @param n          -float, Total sky cover(okta)
        @return  dewYield -float, amount of dew yield in (mm·d−1)  
        '''
        windSpeedCutOff = 4.4 
        dewYield = ( 1/12 ) * (.37 * ( 1 + ( 0.204323 * h ) - (0.0238893 * \
                    h**2 ) - ( 18.0132 - ( 1.04963 * h**2 ) + ( 0.21891 * \
                    h**2 ) ) * (10**( -3 ) * tD ) ) * ( ( ( ( tD + 273.15)/ \
                    285)**4)*(1 - (n/8))) + (0.06 * (tD - tA ) ) * ( 1 + 100 * \
                    ( 1 - np.exp( - ( windSpeed / windSpeedCutOff)**20 ) ) ) ) 
        return dewYield
    
    

    def waterVaporPressure( dewPtTemp ):
        '''
        HELPER FUNCTION
        
        waterVaporPressure()
        
        Find the average water vapor pressure (kPa) based on the Dew Point 
        Temperature model created from Mike Kempe on 10/07/19.  
        
        @param dewPtTemp          -float, Dew Point Temperature
        @return                   -float, return water vapor pressur in kPa
        '''    
        return( math.exp(( 3.257532E-13 * dewPtTemp**6 ) - 
                ( 1.568073E-10 * dewPtTemp**6 ) + 
                ( 2.221304E-08 * dewPtTemp**4 ) + 
                ( 2.372077E-7 * dewPtTemp**3) - 
                ( 4.031696E-04 * dewPtTemp**2) + 
                ( 7.983632E-02 * dewPtTemp ) - 
                ( 5.698355E-1)))
    
   
    
    def rH_Above85( rH ):    
        '''
        HELPER FUNCTION
        
        rH_Above85()
        
        Determine if the relative humidity is above 85%.  
        
        @param rH          -float, Relative Humidity %
        @return                   -Boolean, True if the relative humidity is 
                                            above 85% or False if the relative 
                                            humidity is below 85%
        '''         
        if rH > 85:
            return( True )
        else:
            return ( False )
     
        
   
    def hoursRH_Above85( df ):      
        '''
        HELPER FUNCTION
        
        hoursRH_Above85()
        
        Count the number of hours relative humidity is above 85%.  
        
        @param    df     -dataFrame, dataframe containing Relative Humidity %
        @return          -int, number of hours relative humidity is above 85%
        
        '''         
        booleanDf = df.apply(lambda x: energyCalcs.rH_Above85( x ) )
        return( booleanDf.sum() )
        
  

    def whToGJ( wh ):
        '''
        HELPER FUNCTION
        
        whToGJ()
        
        Convert Wh/m^2 to GJ/m^-2 
        
        @param wh          -float, Wh/m^2
        @return                   -float, GJ/m^-2
        
        '''    
        return( 0.0000036 * wh )
    
    

    def gJtoMJ( gJ ):
        '''
        HELPER FUNCTION
        
        gJtoMJ()
        
        Convert GJ/m^-2 to MJ/y^-1
        
        @param gJ          -float, Wh/m^2
        @return            -float, GJ/m^-2
        
        '''    
        return( gJ * 1000 )
    