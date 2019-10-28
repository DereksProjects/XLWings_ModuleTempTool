# -*- coding: utf-8 -*-
"""
Created on Mon Oct 28 07:53:07 2019

Mike Kempes Miami AOI, POA , and day of Year calcualtions derived from MIAMI 
spreadsheet

We used theses to verify that the pvlib was accurate.  The results showed 
that the Kempe AOI used a approximation showing seasonal differnces.  
At most the Kempe AOI was off by 3 degrees.

@author: Derek Holsapple
"""

import numpy as np
import pandas as pd


class kempeCalcs:

    
    def kempePOA_1( level_1_df , surface_tilt ):
    
        '''
        Calculate the Plane of Array
        
        ERRORS: This function is highly inefficenct and needs to be vectored.  
            Poor function design was used to test the accuracy of the pvlib POA
            global calculation.  This function also averages every hour of the
            GHI, DNI and DNI before calculating 
        
        Plane of Array (first POA calc) calculations derived from Mike Kempe's
        model on Miami, FL Data Spreadsheet. Data for spreadsheet came from 
        TMY3 722020TYA.csv
        

        param@ dayOfYear        -datafraem, dataframe containing DNI, GHI, DHI, AOI
        param@ surface_tilt     -float, tilt of solar module
        
        
        return@ level_1_df      -dataframe, level 1 df with Kempe POA calcualtion
        
        '''    
        poa_list = []
        
        for i in range( 0, len(level_1_df.index)):  
            #If you get up to the second last row 
            if i != len(level_1_df.index)-1: 
                #Do mikes average of irradiances
                if np.cos(level_1_df.iloc[i]['Angle of incidence(pvLib)']) > 0:
                    pOA = (level_1_df.iloc[i+1]['Direct normal irradiance']+level_1_df.iloc[i]['Direct normal irradiance'])\
                          *np.cos(level_1_df.iloc[i]['Angle of incidence(pvLib)'])/2+\
                          (level_1_df.iloc[i+1]['Diffuse horizontal irradiance']+level_1_df.iloc[i]['Diffuse horizontal irradiance'])*\
                          (1+np.cos(surface_tilt*np.pi/180))/4+\
                          (level_1_df.iloc[i+1]['Global horizontal irradiance']+level_1_df.iloc[i]['Global horizontal irradiance'])\
                          *level_1_df.iloc[i]['Corrected Albedo']*\
                          (1-np.cos(surface_tilt*np.pi/180))/4
                    poa_list.append(pOA)
                
                else:
                    pOA = (level_1_df.iloc[i+1]['Diffuse horizontal irradiance']+\
                           level_1_df.iloc[i]['Diffuse horizontal irradiance'])*\
                           (1+np.cos(surface_tilt*np.pi/180))/4+(level_1_df.iloc[i+1]['Global horizontal irradiance']+\
                           level_1_df.iloc[i]['Global horizontal irradiance'])*\
                           level_1_df.iloc[i]['Corrected Albedo']*(1-np.cos(surface_tilt*np.pi/180))/4
                    poa_list.append(pOA)
        
            #If your on the last row (hour 8760) then there is no averages to take
            else:
                pOA = (level_1_df.iloc[i]['Diffuse horizontal irradiance'])*\
                      (1+np.cos(surface_tilt*np.pi/180))/4+\
                      (level_1_df.iloc[i]['Global horizontal irradiance'])\
                      *level_1_df.iloc[i]['Corrected Albedo']*\
                      (1-np.cos(surface_tilt*np.pi/180))/4
                poa_list.append(pOA)    
        level_1_df['Kempe POA'] = poa_list
        return level_1_df


        
    def kempeAOIcalc(dayOfYear , surface_tilt , latitude , surface_azimuth ):
        
        '''
        HELPER FUNCTION
        
        kempeAOIcalc()
        
        ERRORS: This calculation is a approximation.  Compared to pvlib AOI 
            there is a difference of up to 3 degrees at most at some points.  
            This is due to a approximation of the earths rotation on a ellipse.  
        
        Calculate the angle of incidence
        
        Angle of Incidence (radians) calculations derived from Mike Kempe's model
        on Miami, FL Data Spreadsheet. Data for spreadsheet came from 
        TMY3 722020TYA.csv
        
        
        
        param@ dayOfYear        -float, day of the year as "hours in a year" 
                                        i.e 365days/8760hours
        param@ surface_tilt     -float, tilt of solar module
        param@ latitude         -float, latitude coordinate 
                                        (Decimal Degree, negative south)
        param@ surface_azimuth  -int, azimuth of solar module (0-360 degrees)
        
        return@ aOI             -float, angle of incidence
        
        '''   
        
        aOI = np.arccos( np.sin(23.45*np.pi/180*np.sin(2*np.pi*(284+dayOfYear)/365.25))\
                        *np.sin(latitude*np.pi/180)*np.cos(surface_tilt*np.pi/180)+\
                        np.sin(23.45*np.pi/180*np.sin(2*np.pi*(284+dayOfYear)/365.25))\
                        *np.cos(latitude*np.pi/180)*np.sin(surface_tilt*np.pi/180)*\
                        np.cos(surface_azimuth*np.pi/180)+np.cos(23.45*np.pi/180*\
                        np.sin(2*np.pi*(284+dayOfYear)/365.25))*np.cos(latitude*np.pi/180)\
                        *np.cos(surface_tilt*np.pi/180)*np.cos((dayOfYear-np.trunc(dayOfYear))*\
                        np.pi*2-np.pi)-np.cos(23.45*np.pi/180*np.sin(2*np.pi*(284+dayOfYear)\
                        /365.25))*np.sin(latitude*np.pi/180)*np.sin(surface_tilt*np.pi/180)\
                        *np.cos(surface_azimuth*np.pi/180)*np.cos((dayOfYear-\
                        np.trunc(dayOfYear))*np.pi*2-np.pi)-np.cos(23.45*np.pi/180*\
                        np.sin(2*np.pi*(284+dayOfYear)/365.25))*np.sin(surface_tilt*\
                        np.pi/180)*np.sin(surface_azimuth*np.pi/180)*np.sin((dayOfYear\
                        -np.trunc(dayOfYear))*np.pi*2-np.pi)  )
    
        return aOI


    def dayOfYear():
        '''
        HELPER FUNCTION
        
        ERRORS: On the spreadsheet there was no correction for latitude.  
            This function needs to take into account latitude to work properly
        
        dayOfYear()
        
        This calculation creates a list of floats representing each day of the year
        
        '''
        dayOfYearDif = 365/8760
        
        dayOfYear_list = [float(0)]
        
        # iterate and add the difference of time to a list being 8760 "hours in a year"
        for i in range(8759):
            dayOfYear_list.append(dayOfYear_list[i] + dayOfYearDif)
        
        return pd.DataFrame(dayOfYear_list) 
    
    
    
    





















