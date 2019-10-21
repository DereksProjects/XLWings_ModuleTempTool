# -*- coding: utf-8 -*-
"""
Created on Tue Jul  2 12:35:02 2019

@author: DHOLSAPP
"""

import pandas as pd
from pyproj import Proj, transform

'''
Helper Method
LongLat_to_EN()

Convert a Lat/Lon to webmercator

@param long   - float, of the longitude
@param lat    - float, of the latitude

@return tuple       - return a tuple of the Lat and Lon in webmercator form

'''
#helper function to convert lat/long to easting/northing for mapping
#this relies on functions from the pyproj library
def LongLat_to_EN(long, lat):
    try:
      easting, northing = transform(
        Proj(init='epsg:4326'), Proj(init='epsg:3857'), long, lat)
      return easting, northing
    except:
      return None, None


'''
Main Method
process_Map_Pickle()

Read the summary pickle and add on additional map rendering requiremnts.  
Currently the only thing that needs to be processed is the lat/lon to webmercator

@param currentDirectory   - String, the path of where the excel file is located

@return void       - Program will store create a pickle to produce a map

'''
def process_Map_Pickle(currentDirectory):
    # First access the Summary pickle.  The Map pickle being created will be the summary pickle with map formatting
    path = currentDirectory
    level_1_df = pd.read_pickle(path + "\\Pandas_Pickle_DataFrames\\Pickle_Level1_Summary\\Pickle_Level1_Summary.pickle")
    
    #Convert the lat/lon frames into floats
    level_1_df['Site longitude'] = level_1_df['Site longitude'].astype(float)
    level_1_df['Site latitude'] = level_1_df['Site latitude'].astype(float)
    
    #Use helper method to convert all lat/long to webmercator and stores in new column
    level_1_df['E'], level_1_df['N'] = zip(*level_1_df.apply(lambda x: LongLat_to_EN(x['Site longitude'], x['Site latitude']), axis=1))
    
    #Create the pickle and name it Pickle_Map.pickle
    level_1_df.to_pickle( path + '\Pandas_Pickle_DataFrames\Pickle_Map\Pickle_Map.pickle')


#path = r'C:\Users\DHOLSAPP\Desktop\Summer_Project\Python'
#process_Map_Pickle(path)