# -*- coding: utf-8 -*-
"""
Created on Tue May 28 08:52:03 2019

Search for the closest cities with a user specifc Latitude and Longitude in
Decimal Degrees.  Return a dataframe of the closest locations starting from 
user defined lat/lon

Assumed that users will be using Decimal degrees to define Latitude and Longitude

Will use Haversine formula to calculate the distance on a sphere ( the globe )

@author: Derek Holsapple
"""

from math import cos, asin, sqrt
import pandas as pd

class closestLatLon:    

    
    
    def distance(lat1, lon1, lat2, lon2):
        
        '''
        HELPER FUNCTION
        
        distance()
        
        Function to measure the distance(kilometers) between two Lat/Lon
        
        @param lat1       -Float, Latitude of location 1 in Decimal Degrees
        @param lon1       -Float, Longitude of location 1 in Decimal Degrees
        @param lat2       -Float, Latitude of location 2 in Decimal Degrees
        @param lon2       -Float, Longitude of location 2 in Decimal Degrees
        
        @return allFiles  -Float, distance in miles the two locations are apart
        
        '''
        #Haversine formula to calculate the distance of a Lat/Long on the globe
        p = 0.017453292519943295
        a = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p)*cos(lat2*p) * \
            (1-cos((lon2-lon1)*p)) / 2
        return 12742 * asin(sqrt(a))
    
    

    def calcDistanceFrame(currentDirectory ,  lat1 , lon1 ):
        '''
        HELPER FUNCTION
        
        calcDistanceFrame()
        
        Method to return a dataframe of calculated distance from a given 
        Latitude and Longitude input.  
        
        @param currentDirectory - String, of the current working directory                                  
        @param lat1             - Float, given Latitude in Decimal Degrees
        @param lon1             - Float, given Longitude in Decimal Degrees
        
        @return firstRow_summary_df  -Dataframe, dataframe of summary stats with 
                                                    distance from point of interest
        '''
        path = currentDirectory
    
        #Access the first row summary frame
        firstRow_summary_df = pd.read_pickle( path + \
                        '\\Pandas_Pickle_DataFrames\\Pickle_Level1_Summary' +
                        '\\Pickle_Level1_Summary.pickle')  
        # Create a lat and long frame 
        latLong_df = firstRow_summary_df[['Site latitude', \
                                'Site longitude']].astype(float)
        # Create a Distance column between every Lat and Long 
        firstRow_summary_df['Distance(km)'] = latLong_df.apply(lambda x: \
                            closestLatLon.distance(lat1, 
                                                   lon1, 
                                                   x['Site latitude'], 
                                                   x['Site longitude']) , 
                                                   axis=1)
        return firstRow_summary_df    
         
    

    
    def closestLocationFrame( currentDirectory ,  lat1 , lon1 ):
        '''
        HELPER FUNCTION
        
        closestLocationList()
        
        Function to sort the dataframe from closest location to farthest location.
        
        @param currentDirectory      - String, of the current working directory                                  
        @param lat1                  - Float, given Latitude in Decimal Degrees
        @param lon1                  - Float, given Longitude in Decimal Degrees
        
        @return firstRow_summary_df  - Dataframe, dataframe of summary stats with 
                                                    distance from point of interest
        @return columnNames          - List of Strings, list of the column 
                                                        names for the dataFrame                                            
        '''        
        firstRow_summary_df = closestLatLon.calcDistanceFrame(currentDirectory,
                                                              lat1 , 
                                                              lon1 )
        closeLocationsList = []
        for i in range(0 , len(firstRow_summary_df)):
            # Find the index number row of the closest city
            closeLocationIndex = firstRow_summary_df['Distance(km)']\
                                    .idxmin(axis=0, skipna=True)
            # reference the closest index and turn the series into a list
            tempClose = firstRow_summary_df.loc[closeLocationIndex, : ].\
                                    values.tolist()
            # Put the closest location on top of the list
            closeLocationsList.append(tempClose)
            # Remove the closest index location
            firstRow_summary_df = firstRow_summary_df\
                                    .drop([closeLocationIndex] , axis=0)
        # Create a list of column names to output to excel    
        columnNames = list(firstRow_summary_df)    
                # Create a dataframe of all the sorted data
        closeLocationsFrame = pd.DataFrame(data = closeLocationsList , \
                                           columns = columnNames)
        columnNames = list(closeLocationsFrame.columns)
        columnNames = [columnNames[-1]] + columnNames[:-1]
        closeLocationsFrame = closeLocationsFrame[columnNames]

        return closeLocationsFrame , columnNames
