# -*- coding: utf-8 -*-
"""
This is a development enviornment to match Mike Kempes POA calculations from excel sheet
The methods developed here will be implemented in the Procvessing file for 
comparison against all TMY3 data

@author: DHOLSAPP
"""

import pandas as pd
import glob
from Calculate_Solar_Time import localTimeToSolarTime
import datetime as dt
from kempeCalcs import kempeCalcs
import pvlib
import numpy as np
from firstClean import firstClean



def filesNameList_RawPickle( path ):
    '''
    HELPER METHOD
    
    filesNameList_RawPickle()
    
    Pull out the file name from the file pathes and return a list of file names
    
    @param path       -String, path to the folder with the pickle files
    
    @retrun allFiles  -String List, filenames without the file path
    
    '''
    
    #list of strings of all the files
    allFiles = glob.glob(path + "/Pandas_Pickle_DataFrames/Pickle_RawData/*")
    
    #for loop to go through the lists of strings and to remove irrelavant data
    for i in range( 0, len( allFiles ) ):

        # Delete the path and pull out only the file name using the os package from each file
        temp = os.path.basename(allFiles[i])
        allFiles[i] = temp
        
    return allFiles








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

#If the latitude is in the southern hemisphere of the globe then surface azimuth of the panel must be 0 degrees
if latitude <= 0:
    surface_azimuth = 0
# If the latitude is in the northern hemisphere set the panel azimuth to 180
else:
    surface_azimuth = 180


# 83 is the index of MIAMI FL from TMY3
level_1_df = firstClean.cleanedFrame( raw_df , fileNames , 83 )
###################################################################################

#Calculate the AOI with Kempe Model
level_1_df['Angle of incidence(Kempe)'] = level_1_df.apply(lambda x: kempeCalcs.kempeAOIcalc(x['Day of Year'] , 
                                                           surface_tilt , 
                                                           latitude , 
                                                           surface_azimuth ), axis=1)




#Compare Kempe AOI model to pvLib
solarPosition_df = pvlib.solarposition.get_solarposition( level_1_df['Universal Date Time'], 
                                                                         latitude, 
                                                                         longitude, 
                                                                         altitude=None, 
                                                                         pressure=None, 
                                                                         method='nrel_numba' ) 


# Add onto the level 1 frame
level_1_df['Solar Zenith'] = solarPosition_df['zenith'].values
level_1_df['Solar Azimuth'] = solarPosition_df['azimuth'].values
level_1_df['Solar Elevation'] = solarPosition_df['elevation'].values

################  
# Calculate the POA
################    
totalIrradiance_df = pvlib.irradiance.get_total_irradiance(surface_tilt, 
                                                                 surface_azimuth, 
                                                                 level_1_df['Solar Zenith'], 
                                                                 level_1_df['Solar Azimuth'], 
                                                                 level_1_df['Direct normal irradiance'], 
                                                                 level_1_df['Global horizontal irradiance'], 
                                                                 level_1_df['Diffuse horizontal irradiance'], 
                                                                 dni_extra=None, 
                                                                 airmass=None, 
                                                                 albedo= level_1_df['Corrected Albedo'], 
                                                                 surface_type=None, 
                                                                 model= 'isotropic', 
                                                                 model_perez='allsitescomposite1990')   





#Add the new data as new columns of the level_1_data
level_1_df['POA Diffuse'] = totalIrradiance_df['poa_diffuse'].values
level_1_df['POA Direct'] = totalIrradiance_df['poa_direct'].values
level_1_df['POA Global'] = totalIrradiance_df['poa_global'].values
level_1_df['POA Ground Diffuse'] = totalIrradiance_df['poa_ground_diffuse'].values
level_1_df['POA Sky Diffuse'] = totalIrradiance_df['poa_sky_diffuse']





# Calculates the angle of incidence of the solar vector on a surface. 
# This is the angle between the solar vector and the surface normal.
aoi = pvlib.irradiance.aoi(surface_tilt, surface_azimuth,
                           solarPosition_df['apparent_zenith'], solarPosition_df['azimuth'])


aoiRadians = np.radians(aoi).to_frame()
level_1_df['Angle of incidence(pvLib)'] = aoiRadians['aoi'].values
##############################################################################



    
level_1_df = kempeCalcs.kempePOA_1( level_1_df , surface_tilt )    


#Make A CSV file from frame   
level_1_df.to_csv( r'C:\Users\DHOLSAPP\Desktop\XLWings_ModuleTempTool\POA_compare.csv' )





    

























