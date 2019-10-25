# -*- coding: utf-8 -*-
"""
This is a development enviornment to match Mike Kempes POA calculations from excel sheet
The methods developed here will be implemented in the Procvessing file for 
comparison against all TMY3 data

@author: DHOLSAPP
"""

import pandas as pd
import glob
import os 
from Calculate_Solar_Time import localTimeToSolarTime
import datetime as dt
from datetime import datetime, timedelta
import numpy as np
import pvlib
import math
'''
HELPER METHOD

filesNameList_RawPickle()

Pull out the file name from the file pathes and return a list of file names

@param path       -String, path to the folder with the pickle files

@retrun allFiles  -String List, filenames without the file path

'''
def filesNameList_RawPickle( path ):
    
    #list of strings of all the files
    allFiles = glob.glob(path + "/Pandas_Pickle_DataFrames/Pickle_RawData/*")
    
    #for loop to go through the lists of strings and to remove irrelavant data
    for i in range( 0, len( allFiles ) ):

        # Delete the path and pull out only the file name using the os package from each file
        temp = os.path.basename(allFiles[i])
        allFiles[i] = temp
        
    return allFiles

'''
HELPER METHOD

my_to_datetime()

Create a datetime object from a string of Date and Time.  This method will also 
correct the raw data from referencing 24:00 and change it to the next day being 00:00 

@param date_str   -String, of Date and Time

@return datetime  -dateTime object, return a datetime object of the string passed

'''
def my_to_datetime(date_str):
    
    #If the time is not 24:00
    if date_str[11:13] != '24':
        # Return the date time object without any changes
        return pd.to_datetime(date_str, format='%m/%d/%Y %H:%M')
    
    # Correct the 24:00 by changing 24 to 0
    date_str = date_str[0:11] + '00' + date_str[13:]
    # Add 1 day to the date time object and return
    return pd.to_datetime(date_str, format='%m/%d/%Y %H:%M') + \
           dt.timedelta(days=1)


'''
HELPER METHOD

universalTimeCorrected()

Create a datetime object from a string of Date and Time.  This method will also 
correct the raw data from referencing 24:00 and change it to the next day being 00:00 

@param dateTimeObj          -dateTime object, of Local Date and Time
@param hoursAheadorBehind   -int, How many hours the local time is ahead or 
                                        behind of Universal Time

@return universalTime       -dateTime object, return a datetime object of the
                                                 Universal Time


'''

def universalTimeCorrected(dateTimeObj, hoursAheadOrBehind):
    #*See column "D1" of raw data for universal time correction
    #If the location is behind( negative int) then you will add to the local time
    #If the location is ahead ( positive int) then you will subtract to the local time
    universalTime = dateTimeObj + timedelta(hours=-(hoursAheadOrBehind))
    return universalTime


def degreesToRadians( degrees ):
    return math.radians( degrees / math.pi)


def dayOfYear():
    dayOfYearDif = 365/8760
    
    dayOfYear_list = [float(0)]
    
    # iterate and add the difference of time to a list being 8760 "hours in a year"
    for i in range(8759):
        dayOfYear_list.append(dayOfYear_list[i] + dayOfYearDif)
    
    return pd.DataFrame(dayOfYear_list) 



'''
Calculate the angle of incidence

Angle of Incidence (radians) calculations derived from Mike Kempe's model on Miami, FL Data Spreadsheet.
Data for spreadsheet came from TMY3 722020TYA.csv



param@ dayOfYear        -float, day of the year as "hours in a year" i.e 365days/8760hours
param@ surface_tilt     -float, tilt of solar module
param@ latitude         -float, latitude coordinate (Decimal Degree, negative south)
param@ surface_azimuth  -int, azimuth of solar module (0-360 degrees)

return@ aOI             -float, angle of incidence

'''

def kempeAOIcalc(dayOfYear , surface_tilt , latitude , surface_azimuth ):
       
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


def cleanedFrame( firstRow_summary_df, fileNames , index ):    
    raw_df = pd.read_pickle( path + '\\Pandas_Pickle_DataFrames\\Pickle_RawData\\' + fileNames[index])
    
    level_1_df = raw_df.loc[:,['Date (MM/DD/YYYY)', 
                               'Time (HH:MM)',
                               'Albedo',
                               'Global horizontal irradiance',
                               'Direct normal irradiance',
                               'Diffuse horizontal irradiance',
                               'Dry-bulb temperature',
                               'Dew-point temperature',
                               'Relative humidity',
                               'Station pressure',
                               'Wind direction',
                               'Wind speed',
                               'Total sky cover',
                               'Precipitable water',
                               'Liquid percipitation depth']]
    ###############
    # Correct data to pull out metrics, create sub data frames for processing
            # Predicted Albedo needs to be .2 if data is not provided
            # Total sky coverage is currently in tenths, Needs to be in okta(1/8)
    
    ###############
            
    #ALBEDO CORRECTION, subframe not needed. IWEC data all contained NA data for Albedo    
    
    # If Albedo contains NA data then replace NA with .2 (Defualt Value for Albedo)
    level_1_df.Albedo = level_1_df.Albedo.fillna(.2)
    
    # Correcting the Albedo
    #If the Albedo falls below 0 then correect the Albedo to 0.133
    #Lambda starts at the first element of the row being named "x" and processes until the last element of the dataframe
    level_1_df['Corrected Albedo'] = level_1_df.Albedo.apply(lambda x: 0.133 if x <= 0 or x >= 100 else x)
    
    # TOTAL SKY COVERAGE, sub data frame needed to change sky coverage scale from tenths(1/10) to okta(1/8)
                        # Okta frame will be used to calculate the estimated yearly dew yield
    level_1_df['Total sky cover(okta)'] = (level_1_df['Total sky cover'].astype(float) * 8) / 10
    
    
    
    
    
    ################         
    #Create Date Time objects as columns, this includes finding Solar Time
    ################       
    #Create a data frame to store a combined string frame of Date column and Time column
    DateTimeStrings = level_1_df['Date (MM/DD/YYYY)'].str.cat(level_1_df['Time (HH:MM)'],sep=" ")
    
    # Create a new column of the level_1_df named Local Date Time
    # Use the DateTimeStrings frame to convert to a date time objects
    # Store the new date time objects into the Local Date Time column
    #Note: The my_to_datetime() will correct 24:00 to the next day at 0:00
    level_1_df['Local Date Time'] = DateTimeStrings.apply(lambda x: my_to_datetime(x))
    
    
    #Correct for Universal Time
    # From the first Row summary frame pull out the number of hours by 
    #    which local standard time is ahead or behind Universal Time ( + or -)
    hoursAheadOrBehind = float(firstRow_summary_df.iloc[83]['Site time zone (Universal time + or -)'])
    
    # Correct the datetime object to universal time
    # Use the helper method universalTimeCorrected() to process each local 
    #     date time object
    # Create a new column in the level_1_df to store the Universal Date time object
    level_1_df['Universal Date Time'] = level_1_df['Local Date Time'].apply(lambda x: universalTimeCorrected(x, hoursAheadOrBehind))
    
    
    #Calculate the Local Solar time
    # Use the localTimeToSolarTime() helper method
    # Create a new column in the level_1_df to store the Universal Date time object
    level_1_df['Local Solar Time'] = level_1_df.apply(lambda x: localTimeToSolarTime( longitude , hoursAheadOrBehind , x['Local Date Time']), axis=1)
     
    #Create another column of the hourly numeric Local Solar Time
    level_1_df['Hourly Local Solar Time'] = level_1_df['Local Solar Time'].apply(lambda x: x.hour + (x.minute/60))
    #We also need the hourly local time in minutes
    level_1_df['Minutes Local Solar Time'] = level_1_df['Local Solar Time'].apply(lambda x: x.hour*60  + x.minute)
    #Calculalte the dayOfYear i.e. 365/8760 per hour of a year
    level_1_df['Day of Year'] = dayOfYear()
    
    
    ################################################################
    # Slight Clean up the frame before processing 
    
    # Drop the old Date and Time (Strings) columns
    level_1_df = level_1_df.drop(columns=['Date (MM/DD/YYYY)', 'Time (HH:MM)' ])
    
    # Re index the column headings in a more organized format 
    level_1_df = level_1_df.reindex(columns = ['Local Date Time', 
                                               'Local Solar Time',
                                               'Hourly Local Solar Time',
                                               'Minutes Local Solar Time',
                                               'Universal Date Time',
                                               'Day of Year',
                                               'Albedo', 
                                               'Corrected Albedo',
                                               'Global horizontal irradiance',
                                               'Direct normal irradiance', 
                                               'Diffuse horizontal irradiance',
                                               'Dry-bulb temperature',
                                               'Dew-point temperature',
                                               'Relative humidity',
                                               'Station pressure',
                                               'Wind direction',
                                               'Wind speed',
                                               'Total sky cover',
                                               'Total sky cover(okta)',
                                               'Precipitable water',
                                               'Liquid percipitation depth'
                                               ])
    
    
    return level_1_df  



path = r'C:\Users\DHOLSAPP\Desktop\Weather_DatabaseAddingModuleTempRackRanges'

# Create a list of file names of all the pickles from helper method
fileNames = filesNameList_RawPickle( path )


raw_df = pd.read_pickle( path + '\\Pandas_Pickle_DataFrames\\Pickle_RawData\\' + fileNames[83])
firstRow_summary_df = pd.read_pickle( path + '\\Pandas_Pickle_DataFrames\\Pickle_FirstRows\\firstRowSummary_Of_CSV_Files.pickle')

#SITE ELEVATION, sub frame needed for calculating the dew yield
#Create a frame of kilometers converted elevation of all data site locations
firstRow_summary_df['Site elevation (km)'] = firstRow_summary_df['Site elevation (meters)'].astype(float) / 1000

        
#Pull variables out of FirstRowSummmary data frame to be used as arguments for processing

# Pull the arguments latitute and longitude from the first row summary of the first pickle to be processed
# First file index i will correspond to row i of the first row summary
# i.e row 1 of FirstRowSummary == File 1 being processed
latitude = float(firstRow_summary_df.loc[83]['Site latitude']) 
longitude = float(firstRow_summary_df.loc[83]['Site longitude']) 

surface_tilt = abs(latitude)

level_1_df = cleanedFrame( firstRow_summary_df , fileNames , 83 )

#If the latitude is in the southern hemisphere of the globe then surface azimuth of the panel must be 0 degrees
if latitude <= 0:
    surface_azimuth = 0
# If the latitude is in the northern hemisphere set the panel azimuth to 180
else:
    surface_azimuth = 180


###################################################################################
#Calculate the AOI with Kempe Model
level_1_df['Angle of incidence(Kempe)'] = level_1_df.apply(lambda x: kempeAOIcalc(x['Day of Year'] , surface_tilt , latitude , surface_azimuth ), axis=1)




#Compare Kempe AOI model to pvLib
solarPosition_df = pvlib.solarposition.get_solarposition( level_1_df['Universal Date Time'], 
                                                                         latitude, 
                                                                         longitude, 
                                                                         altitude=None, 
                                                                         pressure=None, 
                                                                         method='nrel_numba' ) 
# Calculates the angle of incidence of the solar vector on a surface. 
# This is the angle between the solar vector and the surface normal.
aoi = pvlib.irradiance.aoi(surface_tilt, surface_azimuth,
                           solarPosition_df['apparent_zenith'], solarPosition_df['azimuth'])

#aoi['aoi (radians)'] = aoi.apply(lambda x: degreesToRadians(x['aoi'], axis=1)
aoiRadians = np.radians(aoi).to_frame()
level_1_df['Angle of incidence(pvLib)'] = aoiRadians['aoi'].values
##############################################################################








'''


Plane of Irradiance (1st calculation) V column on excel

P7= AOI     NEED to CLACULATE BEFORE
G8 = DNI
H8 = DHI
F8 = GHI
O8 = Corrected Albedo, his is at .15 not... .133
I1 = surface_tilt "array tilt"


=+IF(COS(P7)>0,(G8+G7)*COS(P7)/2+(H8+H7)*
(1+COS($I$1*PI()/180))/4+(F8+F7)*O7*(1-COS($I$1*PI()/180))/4,

else
(H8+H7)*(1+COS($I$1*PI()/180))/4+(F8+F7)*O7*(1-COS($I$1*PI()/180))/4)

'''







    

























