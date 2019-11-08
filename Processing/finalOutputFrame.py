# -*- coding: utf-8 -*-
"""
Created on Tue May 28 12:10:47 2019

Process files to calculate the Plane of Irradiance.

Create a level one filter and store the dataframe as a pickle.  The level one filter
will process the plane of array irradiance along with the solar Zenith.  The majority
of the procesing is conducted in this code.  

To processing is estimated at 6hrs for 3000 files.

@author: Derek Holsapple, Mike Kempe
"""

import pandas as pd
import glob
import os 
import xlwings as xw
# Methods from pvlib to calcualtate solar position and total irradaince
#from Plane_Of_Irradiance_and_Zenith import get_solarposition , get_total_irradiance  # Source code of pvLib
import pvlib
#from Calculate_Solar_Time import localTimeToSolarTime

from Processing.cleanRawOutput import cleanRawOutput
from Processing.energyCalcs import energyCalcs
from Processing.firstClean import firstClean

#from cleanRawOutput import cleanRawOutput
#from energyCalcs import energyCalcs
#from firstClean import firstClean


class finalOutputFrame:


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
    
    dataSource()
    
    From the file paths determine where the source of the data came from. 
    The current function finds data from IWEC (Global), CWEC (Canada) 
    and TMY3 (United States).  These are identified as 
    TYA = TMY3
    CWEC = CWEC
    IWEC = IW2    
    
    @param filePath          -string, file name of the raw data
    
    
    @return                   -string, return the type of data file
    
    '''
    
    def dataSource( filePath ):
    
        #Create a list of ASCII characters from the string
        ascii_list =[ord(c) for c in filePath]
        char_list = list(filePath)
    
            
        #If the first string  does not pass the filter set the sample flag to 0
     #       sampleFlag = 0 
        count = 0 
        # j will be the index referencing the next ASCII character
        for j in range(0, len(ascii_list)):
           
            #Locate first letter "capitalized" T, C, or I
            if ascii_list[j] == 84 or ascii_list[j] == 67 or ascii_list[j] == 73: 
                
                if count == 0:
    
                    #If a letter is encountered increase the counter
                    count = count + 1
    
    
             # If one of the second letters is encountered Y, W 
            elif ascii_list[j] == 89 or ascii_list[j] == 87:
    
                if count == 1:
            
                    count = count + 1
                else:
                    count = 0
            
            # Detect A, E, or 2
            elif ascii_list[j] == 65 or ascii_list[j] == 69 or ascii_list[j] == 50:
            
                if count == 2:
    
                    # Create a string of the unique identifier
                    rawDataSource =  char_list[ j - 2 ] + char_list[ j - 1 ] + char_list[ j ]   
                                    
                    if rawDataSource == "TYA":
                        dataSource = "TMY3"
                        return dataSource
                    elif rawDataSource == "CWE": 
                        dataSource = "CWEC"
                        return dataSource
                    elif rawDataSource == "IW2":
                        dataSource = "IWEC"
                        return dataSource
                    else:
                        count = 0
    
    
                else:
                    count = 0
    
            # If the next ASCII character is not a number reset the counter to 0        
            else:
                count = 0
                
            # If a unique identifier is not located insert string as placeholder so that indexing is not corrupted
            if j == len(ascii_list) - 1 :
                    
                dataSource = "UNKNOWN"       
                        
                    
        return dataSource   
    
    
    
    '''
    EXECUTION METHOD
    
    level_1_df()
    
    Create level 1 filtered pickles calculating the Plane of Irradiance 
    and Solar Position. To calculate the solar position and plane of irradiance 
    the method will use the file Plane_Of_Irradiance_and_Zenith.py.  These methods 
    reference the pvlib library[2]. The level 1 filtering will be a large computation.
    3000 files will take about 6hrs depending upon user cpu power.  The results of 
    computation will be stored as a pandas dataframe .pickle in the below return path.  
    Each location file will contain its own .pickle file.  
    
    Method:
    1) Use a implementation of the NREL SPA algorithm described in [1] to calculate
        the solar positions including the Solar Zenith, Solar Azimuth, and Solar Elevation
        
        *Note all returns will be stored onto a pandas dataframe with other information data
        
        retuns:
        
        Solar Zenith 
        Solar Azimuth 
        Solar Elevation
    
    
    2) Calculate the Plane of Irradiance based off of Solar Zenith [2].
        
        I_{tot} = I_{beam} + I_{sky diffuse} + I_{ground}
        
        retuns:
            
        POA Diffuse	
        POA Direct	
        POA Global	
        POA Ground Diffuse
        POA Sky Diffuse
    
    
        References
        ----------
        [1] I. Reda and A. Andreas, Solar position algorithm for solar radiation
        applications. Solar Energy, vol. 76, no. 5, pp. 577-589, 2004.
        NREL SPA code: http://rredc.nrel.gov/solar/codesandalgorithms/spa/
        
        [2] William F. Holmgren, Clifford W. Hansen, and Mark A. Mikofski. 
        “pvlib python: a python package for modeling solar energy systems.”
        Journal of Open Source Software, 3(29), 884, (2018). 
        https://doi.org/10.21105/joss.00884
        
    @ param currentDirectory  -String, of current working directory    
    @ param surface_tilt      -double, degrees of surface tilt
    @ param surface_azimuth   -double, degrees of surface azimuthe    
                                        
    @ return                  -void, stores processed .pickle files into directory
                                    \Pandas_Pickle_DataFrames\Pickle_Level1 
    '''
    
    def level_1_df_toPickle( currentDirectory ):
       
        # set the current working directory
        path = currentDirectory
        
        #XLWINGS user feedback
            
        wb = xw.Book(path + '\Output_Tool.xlsm')
        mySheet = wb.sheets[0]
    
        
        # Create a list of file names of all the pickles from helper method
        fileNames = finalOutputFrame.filesNameList_RawPickle( path )
        
        #Access the first row summary dataframe to pull out arguments for each location
        # We will need access to each files 
            # Latitude
            # Longitude
            # Universal Time correction
        # Note: index 0 corresponds to the first file location raw data.    
        firstRow_summary_df = pd.read_pickle( path + '\\Pandas_Pickle_DataFrames\\Pickle_FirstRows\\firstRowSummary_Of_CSV_Files.pickle')
        
        #SITE ELEVATION, sub frame needed for calculating the dew yield
        #Create a frame of kilometers converted elevation of all data site locations
        firstRow_summary_df['Site elevation (km)'] = firstRow_summary_df['Site elevation (meters)'].astype(float) / 1000
        
        
        #Initialize lists outside the for loop,  
        #these lists will be used when creating a summary frame
    
    
        
        sumOfHourlyDew_List = []
        
        avgWaterVaporPressure_List = []
        sumWaterVaporPressure_List = []
        
        
    ##############################    
        annual_GHI_List = []
        annual_DNI_List = [] 
        annual_DHI_List = []
        
        annual_POA_Global_List = []
        annual_POA_Direct_List = []
        annual_POA_Diffuse_List = []
        annual_POA_SkyDiffuse_List = []
        annual_POA_GroundDiffuse_List = []
        
        annual_Global_UV_Dose_List = []
        annual_UV_Dose_atLatitude_Tilt_List = []
        annual_Minimum_Ambient_Temperature_List = []
        annual_Average_Ambient_Temperature_List = []
        annual_Maximum_Ambient_Temperature_List = []
        annual_Ambient_Temperature_Range_List = []
        
        annual_hoursThatRHabove85_List = []
        
    #####################################    
        
        averageCell98th_open_rack_cell_glassback_List = []
        averageModule98th_open_rack_cell_glassback_List = []
        annual_Minimum_Module_Temp_open_rack_cell_glassback_List = []
        annual_Average_Module_Temp_open_rack_cell_glassback_List = []
        annual_Maximum_Module_Temp_open_rack_cell_glassback_List = []
        annual_Range_Module_Temp_open_rack_cell_glassback_List = []
        
        averageCell98th_roof_mount_cell_glassback_List = []
        averageModule98th_roof_mount_cell_glassback_List = []   
        annual_Minimum_Module_Temp_roof_mount_cell_glassback_List = []
        annual_Average_Module_Temp_roof_mount_cell_glassback_List = []
        annual_Maximum_Module_Temp_roof_mount_cell_glassback_List = []
        annual_Range_Module_Temp_roof_mount_cell_glassback_List = []
         
        averageCellTemp98th_open_rack_cell_polymerback_List = []
        averageModule98th_open_rack_cell_polymerback_List = []
        annual_Minimum_Module_Temp_open_rack_cell_polymerback_List = []
        annual_Average_Module_Temp_open_rack_cell_polymerback_List = []
        annual_Maximum_Module_Temp_open_rack_cell_polymerback_List = []
        annual_Range_Module_Temp_open_rack_cell_polymerback_List = []
        
        averageCell98th_insulated_back_polymerback_List = []
        averageModule98th_insulated_back_polymerback_List = []
        annual_Minimum_Module_Temp_insulated_back_polymerback_List = []
        annual_Average_Module_Temp_insulated_back_polymerback_List = []
        annual_Maximum_Module_Temp_insulated_back_polymerback_List = []
        annual_Range_Module_Temp_insulated_back_polymerback_List = []
        
        averageCell98th_open_rack_polymer_thinfilm_steel_List = []
        averageModule98th_open_rack_polymer_thinfilm_steel_List = []
        annual_Minimum_Module_Temp_open_rack_polymer_thinfilm_steel_List = []
        annual_Average_Module_Temp_open_rack_polymer_thinfilm_steel_List = []
        annual_Maximum_Module_Temp_open_rack_polymer_thinfilm_steel_List = []
        annual_Range_Module_Temp_open_rack_polymer_thinfilm_steel_List = []
        
        averageCell98th_22x_concentrator_tracker_List = []
        averageModule98th_22x_concentrator_tracker_List = []
        annual_Minimum_Module_Temp_22x_concentrator_tracker_List = []
        annual_Average_Module_Temp_22x_concentrator_tracker_List = []
        annual_Maximum_Module_Temp_22x_concentrator_tracker_List = []
        annual_Range_Module_Temp_22x_concentrator_tracker_List = []
        
    
        
        #Created for sorting data later
        filePath_List = []
        dataSource_List = []
        
        
        #Output to the user how many files have been complete
        wb.sheets[mySheet].range(67,6).value = len(firstRow_summary_df)
    
    # Loop through all the raw data files and first row summary frame     
        for i in range (0 , len(fileNames)):
            
            
            
            #Pull variables out of FirstRowSummmary data frame to be used as arguments for processing
        
            # Pull the arguments latitute and longitude from the first row summary of the first pickle to be processed
            # First file index i will correspond to row i of the first row summary
            # i.e row 1 of FirstRowSummary == File 1 being processed
            latitude = float(firstRow_summary_df.loc[i]['Site latitude']) 
            longitude = float(firstRow_summary_df.loc[i]['Site longitude']) 
            
            #Correct for Universal Time
            # From the first Row summary frame pull out the number of hours by 
            #    which local standard time is ahead or behind Universal Time ( + or -)
            hoursAheadOrBehind = float(firstRow_summary_df.iloc[i]['Site time zone (Universal time + or -)'])
            
            
            
            
            #If the latitude is in the southern hemisphere of the globe then surface azimuth of the panel must be 0 degrees
            if latitude <= 0:
                surface_azimuth = 0
            # If the latitude is in the northern hemisphere set the panel azimuth to 180
            else:
                surface_azimuth = 180
                
            # Set the suface tilt to the latitude   
            # PVlib requires the latitude tilt to always be positve for its irradiance calculations
            surface_tilt = abs(latitude)        
           
    
            # Import the raw dataframe of the individual location to clean and process
            raw_df = pd.read_pickle( path + '\\Pandas_Pickle_DataFrames\\Pickle_RawData\\' + fileNames[i])
        
            level_1_df = firstClean.cleanedFrame( raw_df , hoursAheadOrBehind , longitude )
        
    
    ################  
    # Calculate the Solar Position
    ################
            
            # Create a dataframe that stores all the returns as a series
            # Within each element of the series the returns will be 
                #apparent_zenith (degrees),
                #zenith (degrees),
                #apparent_elevation (degrees),
                #elevation (degrees),
                #azimuth (degrees),
                #equation_of_time (minutes)
           #Uses the NREL spa algorithm to calculate angles
            solarPosition_df = pvlib.solarposition.get_solarposition( level_1_df['Universal Date Time'], 
                                                                                     latitude, 
                                                                                     longitude, 
                                                                                     altitude=None, 
                                                                                     pressure=None, 
                                                                                     method='nrel_numba', 
                                                                                     temperature=12 ) 
            # Add onto the level 1 frame
            level_1_df['Solar Zenith'] = solarPosition_df['zenith'].values
            level_1_df['Solar Azimuth'] = solarPosition_df['azimuth'].values
            level_1_df['Solar Elevation'] = solarPosition_df['elevation'].values
        
        
            # Calculates the angle of incidence of the solar vector on a surface. 
            # This is the angle between the solar vector and the surface normal.
            aoi = pvlib.irradiance.aoi(surface_tilt, surface_azimuth,
                           solarPosition_df['apparent_zenith'], solarPosition_df['azimuth'])
            #Convert to Radians
            level_1_df['Angle of incidence'] = aoi.values
            
        
        
    ################  
    # Calculate the POA
    ################    
            # Create a dataframe that stores all the returns as a series
            # Within each element of the series the returns will be a dictionary referencing
                #poa_global 
                #poa_direct 
                #poa_diffuse
                #poa_sky_diffuse 
                #poa_ground_diffuse
                
     
     
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
            level_1_df['POA Sky Diffuse'] = totalIrradiance_df['poa_sky_diffuse'].values
            

            
    #################
    #Calculate the temperatures of the module and then find the top 98% for the summary frame
    #################
            # Calculate the Module/Cell Temperature for different configurations
            # using the king model 
    
            #’open_rack_cell_glassback’ OUTPUT = Module Temperature/Cell Temperature(C)
            temp_open_rack_cell_glassback_df = pvlib.pvsystem.sapm_celltemp(level_1_df['POA Global'],
                                                                level_1_df['Wind speed'], 
                                                                level_1_df['Dry-bulb temperature'],
                                                                model = 'open_rack_cell_glassback' )
            #’roof_mount_cell_glassback’ OUTPUT = Module Temperature/Cell Temperature(C)
            temp_roof_mount_cell_glassback_df = pvlib.pvsystem.sapm_celltemp(level_1_df['POA Global'],
                                                                level_1_df['Wind speed'], 
                                                                level_1_df['Dry-bulb temperature'],
                                                                model = 'roof_mount_cell_glassback')        
            #’open_rack_cell_polymerback’ OUTPUT = Module Temperature/Cell Temperature(C)
            temp_open_rack_cell_polymerback_df = pvlib.pvsystem.sapm_celltemp(level_1_df['POA Global'],
                                                                level_1_df['Wind speed'], 
                                                                level_1_df['Dry-bulb temperature'],
                                                                model = 'open_rack_cell_polymerback')        
            #’insulated_back_polymerback’  OUTPUT = Module Temperature/Cell Temperature(C)
            temp_insulated_back_polymerback_df = pvlib.pvsystem.sapm_celltemp(level_1_df['POA Global'],
                                                                level_1_df['Wind speed'], 
                                                                level_1_df['Dry-bulb temperature'],
                                                                model = 'insulated_back_polymerback')        
            #’open_rack_polymer_thinfilm_steel’  OUTPUT = Module Temperature/Cell Temperature(C)
            temp_open_rack_polymer_thinfilm_steel_df = pvlib.pvsystem.sapm_celltemp(level_1_df['POA Global'],
                                                                level_1_df['Wind speed'], 
                                                                level_1_df['Dry-bulb temperature'],
                                                                model = 'open_rack_polymer_thinfilm_steel') 
            #’22x_concentrator_tracker’  OUTPUT = Module Temperature/Cell Temperature(C)
            temp_22x_concentrator_tracker_df = pvlib.pvsystem.sapm_celltemp(level_1_df['POA Global'],
                                                                level_1_df['Wind speed'], 
                                                                level_1_df['Dry-bulb temperature'],
                                                                model = '22x_concentrator_tracker')        
            
            
            
            
            
            
            # Calculate the Module temperature with Dew Point #NOTE: Need to add ground temp data to run a proper calculation
            # Add the hourly data back to the frame
    #This function currently needs debugging (semantic error)        
    #        level_1_df['Dew Point Module Temperature (C)'] = level_1_df.apply(lambda x: moduleT( x['Dry-bulb temperature'] , 
    #                                                                                             x['Dew-point temperature'],
    #                                                                                             x['POA Global'], 
    #                                                                                             x['Wind speed'] , 
    #                                                                                             x['Minutes Local Solar Time'] , 
    #                                                                                             x['Station pressure'] , 
    #                                                                                             x['Dry-bulb temperature'] ), axis=1)
            # Add the module temp data to the level 1 frame 
            level_1_df['Cell Temperature(open_rack_cell_glassback)'] = temp_open_rack_cell_glassback_df['temp_cell'].values.tolist()
            level_1_df['Module Temperature(open_rack_cell_glassback)'] = temp_open_rack_cell_glassback_df['temp_module'].values.tolist()
            
            level_1_df['Cell Temperature(roof_mount_cell_glassback)'] = temp_roof_mount_cell_glassback_df['temp_cell'].values.tolist()
            level_1_df['Module Temperature(roof_mount_cell_glassback)'] = temp_roof_mount_cell_glassback_df['temp_module'].values.tolist()        
            
            level_1_df['Cell Temperature(open_rack_cell_polymerback)'] = temp_open_rack_cell_polymerback_df['temp_cell'].values.tolist()
            level_1_df['Module Temperature(open_rack_cell_polymerback)'] = temp_open_rack_cell_polymerback_df['temp_module'].values.tolist()        
            
            level_1_df['Cell Temperature(insulated_back_polymerback)'] = temp_insulated_back_polymerback_df['temp_cell'].values.tolist()
            level_1_df['Module Temperature(insulated_back_polymerback)'] = temp_insulated_back_polymerback_df['temp_module'].values.tolist()        
            
            level_1_df['Cell Temperature(open_rack_polymer_thinfilm_steel)'] = temp_open_rack_polymer_thinfilm_steel_df['temp_cell'].values.tolist()
            level_1_df['Module Temperature(open_rack_polymer_thinfilm_steel)'] = temp_open_rack_polymer_thinfilm_steel_df['temp_module'].values.tolist()        
            
            level_1_df['Cell Temperature(22x_concentrator_tracker)'] = temp_22x_concentrator_tracker_df['temp_cell'].values.tolist()
            level_1_df['Module Temperature(22x_concentrator_tracker)'] = temp_22x_concentrator_tracker_df['temp_module'].values.tolist()        
            
            
            
            
            
            
            
            # Calculate the top 2% of temperature per location and save the average into a summary list
            #  Will need to add this list to the summary dataframe
            # Calculate the top 2% for 'Cell Temperature(King)' , 'Module Temperature(King)' , 'Dew Point Module Temperature (C)'
            
            #Determine how many elements are equal to 2% of the length of the data
            top2Precent = int( len( level_1_df ) * .02 )
            
            
            
            
            # Pull out the top 2% of the data.  for 8760 points it will take the highest 175 values, 
            # These lists will be used in the final summary frame.
            
            
            open_rack_cell_glassback_top2Precent_Cell_Temp = level_1_df.nlargest( top2Precent , 'Cell Temperature(open_rack_cell_glassback)' ) 
            open_rack_cell_glassback_top2Precent_Module_Temp = level_1_df.nlargest( top2Precent , 'Module Temperature(open_rack_cell_glassback)' )
            
            roof_mount_cell_glassback_top2Precent_Cell_Temp = level_1_df.nlargest( top2Precent , 'Cell Temperature(roof_mount_cell_glassback)' ) 
            roof_mount_cell_glassback_top2Precent_Module_Temp = level_1_df.nlargest( top2Precent , 'Module Temperature(roof_mount_cell_glassback)' )        
            
            open_rack_cell_polymerback_top2Precent_Cell_Temp = level_1_df.nlargest( top2Precent , 'Cell Temperature(open_rack_cell_polymerback)' ) 
            open_rack_cell_polymerback_top2Precent_Module_Temp = level_1_df.nlargest( top2Precent , 'Module Temperature(open_rack_cell_polymerback)' )        
            
            insulated_back_polymerback_top2Precent_Cell_Temp = level_1_df.nlargest( top2Precent , 'Cell Temperature(insulated_back_polymerback)' ) 
            insulated_back_polymerback_top2Precent_Module_Temp = level_1_df.nlargest( top2Precent , 'Module Temperature(insulated_back_polymerback)' )        
            
            open_rack_polymer_thinfilm_steel_top2Precent_Cell_Temp = level_1_df.nlargest( top2Precent , 'Cell Temperature(open_rack_polymer_thinfilm_steel)' ) 
            open_rack_polymer_thinfilm_steel_top2Precent_Module_Temp = level_1_df.nlargest( top2Precent , 'Module Temperature(open_rack_polymer_thinfilm_steel)' )        
            
            _22x_concentrator_tracker_top2Precent_Cell_Temp = level_1_df.nlargest( top2Precent , 'Cell Temperature(22x_concentrator_tracker)' ) 
            _22x_concentrator_tracker_top2Precent_Module_Temp = level_1_df.nlargest( top2Precent , 'Module Temperature(22x_concentrator_tracker)' )        
            
            
    
            
            # Find the average of the top 98th percentile for Module/Cell Temperature 
            # This average will be used to plot each location on the map
            
            averageCell_open_rack_cell_glassback = open_rack_cell_glassback_top2Precent_Cell_Temp['Cell Temperature(open_rack_cell_glassback)'].mean(axis = 0, skipna = True) 
            averageModule_open_rack_cell_glassback = open_rack_cell_glassback_top2Precent_Module_Temp['Module Temperature(open_rack_cell_glassback)'].mean(axis = 0, skipna = True) 
            
            averageCell_roof_mount_cell_glassback = roof_mount_cell_glassback_top2Precent_Cell_Temp['Cell Temperature(roof_mount_cell_glassback)'].mean(axis = 0, skipna = True) 
            averageModule_roof_mount_cell_glassback = roof_mount_cell_glassback_top2Precent_Module_Temp['Module Temperature(roof_mount_cell_glassback)'].mean(axis = 0, skipna = True)         
            
            averageCellTemp_open_rack_cell_polymerback = open_rack_cell_polymerback_top2Precent_Cell_Temp['Cell Temperature(open_rack_cell_polymerback)'].mean(axis = 0, skipna = True) 
            averageModule_open_rack_cell_polymerback = open_rack_cell_polymerback_top2Precent_Module_Temp['Module Temperature(open_rack_cell_polymerback)'].mean(axis = 0, skipna = True)         
            
            averageCell_insulated_back_polymerback = insulated_back_polymerback_top2Precent_Cell_Temp['Cell Temperature(insulated_back_polymerback)'].mean(axis = 0, skipna = True) 
            averageModule_insulated_back_polymerback =  insulated_back_polymerback_top2Precent_Module_Temp['Module Temperature(insulated_back_polymerback)'].mean(axis = 0, skipna = True)         
            
            averageCell_open_rack_polymer_thinfilm_steel = open_rack_polymer_thinfilm_steel_top2Precent_Cell_Temp['Cell Temperature(open_rack_polymer_thinfilm_steel)'].mean(axis = 0, skipna = True) 
            averageModule_open_rack_polymer_thinfilm_steel = open_rack_polymer_thinfilm_steel_top2Precent_Module_Temp['Module Temperature(open_rack_polymer_thinfilm_steel)'].mean(axis = 0, skipna = True)         
            
            averageCell_22x_concentrator_tracker = _22x_concentrator_tracker_top2Precent_Cell_Temp['Cell Temperature(22x_concentrator_tracker)'].mean(axis = 0, skipna = True) 
            averageModule_22x_concentrator_tracker = _22x_concentrator_tracker_top2Precent_Module_Temp['Module Temperature(22x_concentrator_tracker)'].mean(axis = 0, skipna = True)         
            
            
    
            
            # Add the 98th percentile temperature averages to these lists to output to the summary frame
            # These will be a list of every location once the loop ends
            
            averageCell98th_open_rack_cell_glassback_List.append(averageCell_open_rack_cell_glassback)
            averageModule98th_open_rack_cell_glassback_List.append(averageModule_open_rack_cell_glassback)
            
            averageCell98th_roof_mount_cell_glassback_List.append(averageCell_roof_mount_cell_glassback)
            averageModule98th_roof_mount_cell_glassback_List.append(averageModule_roof_mount_cell_glassback)        
     
            averageCellTemp98th_open_rack_cell_polymerback_List.append(averageCellTemp_open_rack_cell_polymerback)
            averageModule98th_open_rack_cell_polymerback_List.append(averageModule_open_rack_cell_polymerback)
    
            averageCell98th_insulated_back_polymerback_List.append(averageCell_insulated_back_polymerback)
            averageModule98th_insulated_back_polymerback_List.append(averageModule_insulated_back_polymerback)
    
            averageCell98th_open_rack_polymer_thinfilm_steel_List.append(averageCell_open_rack_polymer_thinfilm_steel)
            averageModule98th_open_rack_polymer_thinfilm_steel_List.append(averageModule_open_rack_polymer_thinfilm_steel)
    
            averageCell98th_22x_concentrator_tracker_List.append(averageCell_22x_concentrator_tracker)
            averageModule98th_22x_concentrator_tracker_List.append(averageModule_22x_concentrator_tracker)
    
        
    
        
            # Calculate the Module temperature with dewpoint 
    #        top2Precent_Module_TempDewPoint = level_1_df.nlargest( top2Precent , 'Dew Point Module Temperature (C)' )
    #        averageModuleTempDewPoint = top2Precent_Module_TempDewPoint['Dew Point Module Temperature (C)'].mean(axis = 0, skipna = True)
    #        averageModuleTempDewPoint_List.append(averageModuleTempDewPoint)
        
        
    #################
    #Calculate the dew point yield for each location.  Find the sum of all hourly data for a yearly yield
    #################
    
            siteElevation = firstRow_summary_df['Site elevation (km)'][i]
            
            level_1_df['Dew Yield'] = level_1_df.apply(lambda x: energyCalcs.dewYield( siteElevation ,
                                                           x['Dew-point temperature'], 
                                                           x['Dry-bulb temperature'] ,
                                                           x['Wind speed'] ,
                                                           x['Total sky cover(okta)']), axis=1 )
             
            #If the hourly dew yield is a negative number then replace the negative number with 0
            level_1_df['Dew Yield'] = level_1_df['Dew Yield'].apply(lambda x: 0.0 if x <= 0 else x)
            
            #get the sum of all the dew produced that year.  
            sumOfHourlyDew = level_1_df['Dew Yield'].sum(axis = 0, skipna = True)
            sumOfHourlyDew_List.append(sumOfHourlyDew)
        
    
        
            #############################################
            #Annual Water Vapor Pressure Average/Sum
            level_1_df['Water Vapor Pressure (kPa)'] = level_1_df.apply(lambda x: energyCalcs.waterVaporPressure( 
                                                           x['Dew-point temperature'], 
                                                           ), axis=1 )
            
            avgWaterVaporPressure = level_1_df['Water Vapor Pressure (kPa)'].mean(skipna = True)
            avgWaterVaporPressure_List.append( avgWaterVaporPressure )
            
            sumWaterVaporPressure = level_1_df['Water Vapor Pressure (kPa)'].sum(skipna = True)
            sumWaterVaporPressure_List.append( sumWaterVaporPressure )
            
    #################
    #Perform other calcualtions for master summary sheet
    #################       
            
    #################
    #Perform other calcualtions for master summary sheet
    #################       
            
            
            
            
            
            
            
            #Calculate the sum of yearly GHI
            sumOfGHI = energyCalcs.whToGJ( level_1_df['Global horizontal irradiance'].sum(axis = 0, skipna = True) )
            annual_GHI_List.append( sumOfGHI )
     
            #Calculate the sum of yearly DNI
            sumOfDNI = energyCalcs.whToGJ( level_1_df['Direct normal irradiance'].sum(axis = 0, skipna = True) )
            annual_DNI_List.append( sumOfDNI )
    
            #Calculate the sum of yearly DHI
            sumOfDHI = energyCalcs.whToGJ( level_1_df['Diffuse horizontal irradiance'].sum(axis = 0, skipna = True) )
            annual_DHI_List.append( sumOfDHI )
    
    
    
            #Calculate the sum of yearly POA global
            sumOfPOA_Global = energyCalcs.whToGJ( totalIrradiance_df['poa_global'].sum(axis = 0, skipna = True) )
            annual_POA_Global_List.append( sumOfPOA_Global )
    
            #Calculate the sum of yearly POA Direct
            sumOfPOA_Direct = energyCalcs.whToGJ( totalIrradiance_df['poa_direct'].sum(axis = 0, skipna = True) )
            annual_POA_Direct_List.append( sumOfPOA_Direct )
    
            #Calculate the sum of yearly POA Diffuse
            sumOfPOA_Diffuse = energyCalcs.whToGJ( totalIrradiance_df['poa_diffuse'].sum(axis = 0, skipna = True) )
            annual_POA_Diffuse_List.append( sumOfPOA_Diffuse )
    
            #Calculate the sum of yearly POA Sky Diffuse
            sumOfPOA_SkyDiffuse = energyCalcs.whToGJ( totalIrradiance_df['poa_sky_diffuse'].sum(axis = 0, skipna = True) )
            annual_POA_SkyDiffuse_List.append( sumOfPOA_SkyDiffuse )
    
            #Calculate the sum of yearly POA Ground Diffuse
            sumOfPOA_GroundDiffuse = energyCalcs.whToGJ( totalIrradiance_df['poa_ground_diffuse'].sum(axis = 0, skipna = True) )
            annual_POA_GroundDiffuse_List.append( sumOfPOA_GroundDiffuse )
    
    
    
    
    
            #Calculate the Global UV Dose, 5% of the annual GHI
            global_UV_Dose = energyCalcs.gJtoMJ( sumOfGHI * .05 )
            annual_Global_UV_Dose_List.append( global_UV_Dose )
    
            #Calculate the annual UV Dose at Latitude Tilt, 5% of the annual GHI
            #Estimate as 5% of global plane of irradiance
            sumOfPOA_Global = energyCalcs.gJtoMJ( energyCalcs.whToGJ(level_1_df['POA Global'].sum(axis = 0, skipna = True) ) )
            uV_Dose_atLatitude_Tilt = sumOfPOA_Global * .05
            annual_UV_Dose_atLatitude_Tilt_List.append( uV_Dose_atLatitude_Tilt )
    
            #Calculate the annual minimum ambient temperature
            minimum_Ambient_Temperature = level_1_df['Dry-bulb temperature'].min()
            annual_Minimum_Ambient_Temperature_List.append( minimum_Ambient_Temperature )
    
            #Calculate the annual average ambient temperature
            average_Ambient_Temperature = level_1_df['Dry-bulb temperature'].mean()
            annual_Average_Ambient_Temperature_List.append( average_Ambient_Temperature )
    
            #Calculate the annual maximum ambient temperature
            maximum_Ambient_Temperature = level_1_df['Dry-bulb temperature'].max()
            annual_Maximum_Ambient_Temperature_List.append( maximum_Ambient_Temperature )
    
            #Calculate the annual range ambient temperature
            ambient_Temperature_Range = maximum_Ambient_Temperature - minimum_Ambient_Temperature
            annual_Ambient_Temperature_Range_List.append( ambient_Temperature_Range )                                                     
    
            hoursRHabove85 = energyCalcs.hoursRH_Above85( level_1_df['Relative humidity'] )
            annual_hoursThatRHabove85_List.append( hoursRHabove85 )
    
    
    
            #Calculate the annual range ambient temperature
     #       sumOf_Precipitation = level_1_df['Liquid percipitation depth'].sum(axis = 0, skipna = True)
     #       annual_Precipitation_List.append( sumOf_Precipitation )
            
            
    ###############################################################################        
    
    
            #Calculate the annual minimum ambient temperature
            minimum_Module_Temp_open_rack_cell_glassback = level_1_df['Module Temperature(open_rack_cell_glassback)'].min()
            annual_Minimum_Module_Temp_open_rack_cell_glassback_List.append( minimum_Module_Temp_open_rack_cell_glassback )
            #Calculate the annual average ambient temperature        
            average_Module_Temp_open_rack_cell_glassback = level_1_df['Module Temperature(open_rack_cell_glassback)'].mean()
            annual_Average_Module_Temp_open_rack_cell_glassback_List.append( average_Module_Temp_open_rack_cell_glassback )
            #Calculate the annual maximum ambient temperature        
            maximum_Module_Temp_open_rack_cell_glassback = level_1_df['Module Temperature(open_rack_cell_glassback)'].max()
            annual_Maximum_Module_Temp_open_rack_cell_glassback_List.append( maximum_Module_Temp_open_rack_cell_glassback )
            #Calculate the annual range ambient temperature        
            range_Module_Temp_open_rack_cell_glassback = maximum_Module_Temp_open_rack_cell_glassback - minimum_Module_Temp_open_rack_cell_glassback
            annual_Range_Module_Temp_open_rack_cell_glassback_List.append ( range_Module_Temp_open_rack_cell_glassback )
            
            
            #Calculate the annual minimum ambient temperature
            minimum_Module_Temp_roof_mount_cell_glassback = level_1_df['Module Temperature(roof_mount_cell_glassback)'].min()
            annual_Minimum_Module_Temp_roof_mount_cell_glassback_List.append( minimum_Module_Temp_roof_mount_cell_glassback )
            #Calculate the annual average ambient temperature        
            average_Module_Temp_roof_mount_cell_glassback = level_1_df['Module Temperature(roof_mount_cell_glassback)'].mean()
            annual_Average_Module_Temp_roof_mount_cell_glassback_List.append( average_Module_Temp_roof_mount_cell_glassback )
            #Calculate the annual maximum ambient temperature        
            maximum_Module_Temp_roof_mount_cell_glassback = level_1_df['Module Temperature(roof_mount_cell_glassback)'].max()
            annual_Maximum_Module_Temp_roof_mount_cell_glassback_List.append( maximum_Module_Temp_roof_mount_cell_glassback )
            #Calculate the annual range ambient temperature        
            range_Module_Temp_roof_mount_cell_glassback = maximum_Module_Temp_roof_mount_cell_glassback - minimum_Module_Temp_roof_mount_cell_glassback
            annual_Range_Module_Temp_roof_mount_cell_glassback_List.append ( range_Module_Temp_roof_mount_cell_glassback )
            
            
            #Calculate the annual minimum ambient temperature
            minimum_Module_Temp_open_rack_cell_polymerback = level_1_df['Module Temperature(open_rack_cell_polymerback)'].min()
            annual_Minimum_Module_Temp_open_rack_cell_polymerback_List.append( minimum_Module_Temp_open_rack_cell_polymerback )
            #Calculate the annual average ambient temperature        
            average_Module_Temp_open_rack_cell_polymerback = level_1_df['Module Temperature(open_rack_cell_polymerback)'].mean()
            annual_Average_Module_Temp_open_rack_cell_polymerback_List.append( average_Module_Temp_open_rack_cell_polymerback )
            #Calculate the annual maximum ambient temperature        
            maximum_Module_Temp_open_rack_cell_polymerback = level_1_df['Module Temperature(open_rack_cell_polymerback)'].max()
            annual_Maximum_Module_Temp_open_rack_cell_polymerback_List.append( maximum_Module_Temp_open_rack_cell_polymerback )
            #Calculate the annual range ambient temperature        
            range_Module_Temp_open_rack_cell_polymerback = maximum_Module_Temp_open_rack_cell_polymerback - minimum_Module_Temp_open_rack_cell_polymerback
            annual_Range_Module_Temp_open_rack_cell_polymerback_List.append ( range_Module_Temp_open_rack_cell_polymerback )
            
                    
            #Calculate the annual minimum ambient temperature
            minimum_Module_Temp_insulated_back_polymerback = level_1_df['Module Temperature(insulated_back_polymerback)'].min()
            annual_Minimum_Module_Temp_insulated_back_polymerback_List.append( minimum_Module_Temp_insulated_back_polymerback )
            #Calculate the annual average ambient temperature        
            average_Module_Temp_insulated_back_polymerback = level_1_df['Module Temperature(insulated_back_polymerback)'].mean()
            annual_Average_Module_Temp_insulated_back_polymerback_List.append( average_Module_Temp_insulated_back_polymerback )
            #Calculate the annual maximum ambient temperature        
            maximum_Module_Temp_insulated_back_polymerback = level_1_df['Module Temperature(insulated_back_polymerback)'].max()
            annual_Maximum_Module_Temp_insulated_back_polymerback_List.append( maximum_Module_Temp_insulated_back_polymerback )
            #Calculate the annual range ambient temperature        
            range_Module_Temp_insulated_back_polymerback = maximum_Module_Temp_insulated_back_polymerback - minimum_Module_Temp_insulated_back_polymerback
            annual_Range_Module_Temp_insulated_back_polymerback_List.append ( range_Module_Temp_insulated_back_polymerback )
            
            
            #Calculate the annual minimum ambient temperature
            minimum_Module_Temp_open_rack_polymer_thinfilm_steel = level_1_df['Module Temperature(open_rack_polymer_thinfilm_steel)'].min()
            annual_Minimum_Module_Temp_open_rack_polymer_thinfilm_steel_List.append( minimum_Module_Temp_open_rack_polymer_thinfilm_steel )
            #Calculate the annual average ambient temperature        
            average_Module_Temp_open_rack_polymer_thinfilm_steel = level_1_df['Module Temperature(open_rack_polymer_thinfilm_steel)'].mean()
            annual_Average_Module_Temp_open_rack_polymer_thinfilm_steel_List.append( average_Module_Temp_open_rack_polymer_thinfilm_steel )
            #Calculate the annual maximum ambient temperature        
            maximum_Module_Temp_open_rack_polymer_thinfilm_steel = level_1_df['Module Temperature(open_rack_polymer_thinfilm_steel)'].max()
            annual_Maximum_Module_Temp_open_rack_polymer_thinfilm_steel_List.append( maximum_Module_Temp_open_rack_polymer_thinfilm_steel )
            #Calculate the annual range ambient temperature        
            range_Module_Temp_open_rack_polymer_thinfilm_steel = maximum_Module_Temp_open_rack_polymer_thinfilm_steel - minimum_Module_Temp_open_rack_polymer_thinfilm_steel
            annual_Range_Module_Temp_open_rack_polymer_thinfilm_steel_List.append ( range_Module_Temp_open_rack_polymer_thinfilm_steel )
            
                    
            #Calculate the annual minimum ambient temperature
            minimum_Module_Temp_22x_concentrator_tracker = level_1_df['Module Temperature(22x_concentrator_tracker)'].min()
            annual_Minimum_Module_Temp_22x_concentrator_tracker_List.append( minimum_Module_Temp_22x_concentrator_tracker )
            #Calculate the annual average ambient temperature        
            average_Module_Temp_22x_concentrator_tracker = level_1_df['Module Temperature(22x_concentrator_tracker)'].mean()
            annual_Average_Module_Temp_22x_concentrator_tracker_List.append( average_Module_Temp_22x_concentrator_tracker )
            #Calculate the annual maximum ambient temperature        
            maximum_Module_Temp_22x_concentrator_tracker = level_1_df['Module Temperature(22x_concentrator_tracker)'].max()
            annual_Maximum_Module_Temp_22x_concentrator_tracker_List.append( maximum_Module_Temp_22x_concentrator_tracker )
            #Calculate the annual range ambient temperature        
            range_Module_Temp_22x_concentrator_tracker = maximum_Module_Temp_22x_concentrator_tracker - minimum_Module_Temp_22x_concentrator_tracker
            annual_Range_Module_Temp_22x_concentrator_tracker_List.append ( range_Module_Temp_22x_concentrator_tracker )
        
                    
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
    ###################################################################################################################################################################        
    ################  
    # Level 1 Data frame complete
    ################ 
            
            #Search the string and determine if the data is TMY3, CWEC, or IWEC
            dataSource_List.append( finalOutputFrame.dataSource(fileNames[i]) )
            
            #List of unique identifiers for reference
            filePath_List.append(fileNames[i])
            
            level_1_df = level_1_df.reindex(columns = ['Local Date Time',
                                                       'Universal Date Time',
                                                       'Local Solar Time',
                                                       'Hourly Local Solar Time',
                                                       'Albedo',
                                                       'Corrected Albedo',
                                                       'Dry-bulb temperature',
                                                       'Dew-point temperature',
                                                       'Relative humidity',
                                                       'Station pressure',
                                                       'Wind direction',
                                                       'Wind speed',
                                                       'Total sky cover',
                                                       'Total sky cover(okta)',
                                                       'Dew Yield',
                                                       'Water Vapor Pressure (kPa)',
                                                       'Global horizontal irradiance',
                                                       'Direct normal irradiance',
                                                       'Diffuse horizontal irradiance',
                                                       'Solar Zenith',
                                                       'Solar Azimuth',
                                                       'Solar Elevation',
                                                       'Angle of incidence',
                                                       'POA Diffuse',
                                                       'POA Direct',
                                                       'POA Global',
                                                       'POA Ground Diffuse',
                                                       'POA Sky Diffuse',
                                                       'Cell Temperature(open_rack_cell_glassback)',
                                                       'Module Temperature(open_rack_cell_glassback)',
                                                       'Cell Temperature(roof_mount_cell_glassback)',
                                                       'Module Temperature(roof_mount_cell_glassback)', 
                                                       'Cell Temperature(open_rack_cell_polymerback)',
                                                       'Module Temperature(open_rack_cell_polymerback)',
                                                       'Cell Temperature(insulated_back_polymerback)',
                                                       'Module Temperature(insulated_back_polymerback)', 
                                                       'Cell Temperature(open_rack_polymer_thinfilm_steel)',
                                                       'Module Temperature(open_rack_polymer_thinfilm_steel)',
                                                       'Cell Temperature(22x_concentrator_tracker)',
                                                       'Module Temperature(22x_concentrator_tracker)'                                                       
                                                       ]) 
             #Put metrics in the final column names
            level_1_df.rename(columns = { 'Albedo' :'Albedo(ratio of reflected solar irradiance to GHI)', 
                                          'Corrected Albedo':'Corrected Albedo(ratio of reflected solar irradiance to GHI)', 
                                          'Dry-bulb temperature':'Dry-bulb temperature(C)',
                                          'Dew-point temperature':'Dew-point temperature(C)',
                                          'Relative humidity':'Relative humidity(%)',
                                          'Station pressure':'Station pressure(mbar)',
                                          'Wind direction':'Wind direction(degrees)',
                                          'Wind speed':'Wind speed(m/s)',
                                          'Total sky cover':'Total sky cover(tenths)',
                                          'Total sky cover(okta)':'Total sky cover(okta)',
                                          'Dew Yield' :'Dew Yield(mmd-1)', 
                                          'Global horizontal irradiance':'Global horizontal irradiance(W/m^2)', 
                                          'Direct normal irradiance':'Direct normal irradiance(W/m^2)',
                                          'Diffuse horizontal irradiance':'Diffuse horizontal irradiance(W/m^2)',
                                          'Solar Zenith':'Solar Zenith(degrees)',
                                          'Solar Azimuth':'Solar Azimuth(degrees)',
                                          'Solar Elevation':'Solar Elevation(degrees)',
                                          'Angle of incidence':'Angle of incidence(degrees)',
                                          'POA Diffuse':'POA Diffuse(W/m^2)',
                                          'POA Direct':'POA Direct(W/m^2)',                                          
                                          'POA Global' :'POA Global(W/m^2)', 
                                          'POA Ground Diffuse':'POA Ground Diffuse(W/m^2)', 
                                          'POA Sky Diffuse':'POA Sky Diffuse(W/m^2)',
                                          'Cell Temperature(open_rack_cell_glassback)':'Cell Temperature(open_rack_cell_glassback)(C)',
                                          'Module Temperature(open_rack_cell_glassback)':'Module Temperature(open_rack_cell_glassback)(C)',
                                          'Cell Temperature(roof_mount_cell_glassback)':'Cell Temperature(roof_mount_cell_glassback)(C)',
                                          'Module Temperature(roof_mount_cell_glassback)':'Module Temperature(roof_mount_cell_glassback)(C)',
                                          'Cell Temperature(open_rack_cell_polymerback)':'Cell Temperature(open_rack_cell_polymerback)(C)',
                                          'Module Temperature(open_rack_cell_polymerback)':'Module Temperature(open_rack_cell_polymerback)(C)',
                                          'Cell Temperature(insulated_back_polymerback)':'Cell Temperature(insulated_back_polymerback)(C)',
                                          'Module Temperature(insulated_back_polymerback)':'Module Temperature(insulated_back_polymerback)(C)',
                                          'Cell Temperature(open_rack_polymer_thinfilm_steel)':'Cell Temperature(open_rack_polymer_thinfilm_steel)(C)',                                          
                                          'Module Temperature(open_rack_polymer_thinfilm_steel)' :'Module Temperature(open_rack_polymer_thinfilm_steel)(C)', 
                                          'Cell Temperature(22x_concentrator_tracker)':'Cell Temperature(22x_concentrator_tracker)(C)', 
                                          'Module Temperature(22x_concentrator_tracker)':'Module Temperature(22x_concentrator_tracker)(C)'
                                          }, inplace = True)
    
            #Store the level 1 processed Data into a pickle
            level_1_df.to_pickle( path + '\Pandas_Pickle_DataFrames\Pickle_Level1' +'\\'+ fileNames[i] )
            
            #Output to the user how many files have been complete
            wb.sheets[mySheet].range(67,4).value = i + 1
        
        
        
    ##############
    # SUMMARY FRAME
    ##############
            
        #Store the processed information into its own frame 
            
        summaryListsAs_df = pd.DataFrame()    
            
        #Update summary sheet with summary stats collected by lists inside the for loop
        summaryListsAs_df["Annual Average (98th Percentile) Cell Temperature__open_rack_cell_glassback (C)"] = averageCell98th_open_rack_cell_glassback_List
        summaryListsAs_df["Annual Average (98th Percentile) Module Temperature__open_rack_cell_glassback (C)"] = averageModule98th_open_rack_cell_glassback_List
        summaryListsAs_df["Annual Minimum Module Temperature__open_rack_cell_glassback (C)"] = annual_Minimum_Module_Temp_open_rack_cell_glassback_List
        summaryListsAs_df["Annual Average Module Temperature__open_rack_cell_glassback (C)"] = annual_Average_Module_Temp_open_rack_cell_glassback_List
        summaryListsAs_df["Annual Maximum Module Temperature__open_rack_cell_glassback (C)"] = annual_Maximum_Module_Temp_open_rack_cell_glassback_List
        summaryListsAs_df["Annual Range of Module Temperature__open_rack_cell_glassback (C)"] = annual_Range_Module_Temp_open_rack_cell_glassback_List
            
        summaryListsAs_df["Annual Average (98th Percentile) Cell Temperature__roof_mount_cell_glassback (C)"] = averageCell98th_roof_mount_cell_glassback_List
        summaryListsAs_df["Annual Average (98th Percentile) Module Temperature__roof_mount_cell_glassback (C)"] = averageModule98th_roof_mount_cell_glassback_List
        summaryListsAs_df["Annual Average (98th Percentile) Module Temperature__roof_mount_cell_glassback (C)"] = averageModule98th_roof_mount_cell_glassback_List
        summaryListsAs_df["Annual Minimum Module Temperature__roof_mount_cell_glassback (C)"] = annual_Minimum_Module_Temp_roof_mount_cell_glassback_List
        summaryListsAs_df["Annual Average Module Temperature__roof_mount_cell_glassback (C)"] = annual_Average_Module_Temp_roof_mount_cell_glassback_List
        summaryListsAs_df["Annual Maximum Module Temperature__roof_mount_cell_glassback (C)"] = annual_Maximum_Module_Temp_roof_mount_cell_glassback_List
        summaryListsAs_df["Annual Range of Module Temperature__roof_mount_cell_glassback (C)"] = annual_Range_Module_Temp_roof_mount_cell_glassback_List
        
        summaryListsAs_df["Annual Average (98th Percentile) Cell Temperature__open_rack_cell_polymerback (C)"] = averageCellTemp98th_open_rack_cell_polymerback_List
        summaryListsAs_df["Annual Average (98th Percentile) Module Temperature__open_rack_cell_polymerback (C)"] = averageModule98th_open_rack_cell_polymerback_List
        summaryListsAs_df["Annual Average (98th Percentile) Module Temperature__open_rack_cell_polymerback (C)"] = averageModule98th_open_rack_cell_polymerback_List
        summaryListsAs_df["Annual Minimum Module Temperature__open_rack_cell_polymerback (C)"] = annual_Minimum_Module_Temp_open_rack_cell_polymerback_List
        summaryListsAs_df["Annual Average Module Temperature__open_rack_cell_polymerback (C)"] = annual_Average_Module_Temp_open_rack_cell_polymerback_List
        summaryListsAs_df["Annual Maximum Module Temperature__open_rack_cell_polymerback (C)"] = annual_Maximum_Module_Temp_open_rack_cell_polymerback_List
        summaryListsAs_df["Annual Range of Module Temperature__open_rack_cell_polymerback (C)"] = annual_Range_Module_Temp_open_rack_cell_polymerback_List
        
        summaryListsAs_df["Annual Average (98th Percentile) Cell Temperature__insulated_back_polymerback (C)"] = averageCell98th_insulated_back_polymerback_List
        summaryListsAs_df["Annual Average (98th Percentile) Module Temperature__insulated_back_polymerback (C)"] = averageModule98th_insulated_back_polymerback_List
        summaryListsAs_df["Annual Average (98th Percentile) Module Temperature__insulated_back_polymerback (C)"] = averageModule98th_insulated_back_polymerback_List
        summaryListsAs_df["Annual Minimum Module Temperature__insulated_back_polymerback (C)"] = annual_Minimum_Module_Temp_insulated_back_polymerback_List
        summaryListsAs_df["Annual Average Module Temperature__insulated_back_polymerback (C)"] = annual_Average_Module_Temp_insulated_back_polymerback_List
        summaryListsAs_df["Annual Maximum Module Temperature__insulated_back_polymerback (C)"] = annual_Maximum_Module_Temp_insulated_back_polymerback_List
        summaryListsAs_df["Annual Range of Module Temperature__insulated_back_polymerback (C)"] = annual_Range_Module_Temp_insulated_back_polymerback_List
        
    
        summaryListsAs_df["Annual Average (98th Percentile) Cell Temperature__open_rack_polymer_thinfilm_steel (C)"] = averageCell98th_open_rack_polymer_thinfilm_steel_List 
        summaryListsAs_df["Annual Average (98th Percentile) Module Temperature__open_rack_polymer_thinfilm_steel (C)"] = averageModule98th_open_rack_polymer_thinfilm_steel_List
        summaryListsAs_df["Annual Average (98th Percentile) Module Temperature__open_rack_polymer_thinfilm_steel (C)"] = averageModule98th_open_rack_polymer_thinfilm_steel_List
        summaryListsAs_df["Annual Minimum Module Temperature__open_rack_polymer_thinfilm_steel (C)"] = annual_Minimum_Module_Temp_open_rack_polymer_thinfilm_steel_List
        summaryListsAs_df["Annual Average Module Temperature__open_rack_polymer_thinfilm_steel (C)"] = annual_Average_Module_Temp_open_rack_polymer_thinfilm_steel_List
        summaryListsAs_df["Annual Maximum Module Temperature__open_rack_polymer_thinfilm_steel (C)"] = annual_Maximum_Module_Temp_open_rack_polymer_thinfilm_steel_List
        summaryListsAs_df["Annual Range of Module Temperature__open_rack_polymer_thinfilm_steel (C)"] = annual_Range_Module_Temp_open_rack_polymer_thinfilm_steel_List
        
    
        summaryListsAs_df["Annual Average (98th Percentile) Cell Temperature__22x_concentrator_tracker (C)"] = averageCell98th_22x_concentrator_tracker_List
        summaryListsAs_df["Annual Average (98th Percentile) Module Temperature__22x_concentrator_tracker (C)"] = averageModule98th_22x_concentrator_tracker_List
        summaryListsAs_df["Annual Average (98th Percentile) Module Temperature__22x_concentrator_tracker (C)"] = averageModule98th_22x_concentrator_tracker_List
        summaryListsAs_df["Annual Minimum Module Temperature__22x_concentrator_tracker (C)"] = annual_Minimum_Module_Temp_22x_concentrator_tracker_List
        summaryListsAs_df["Annual Average Module Temperature__22x_concentrator_tracker (C)"] = annual_Average_Module_Temp_22x_concentrator_tracker_List
        summaryListsAs_df["Annual Maximum Module Temperature__22x_concentrator_tracker (C)"] = annual_Maximum_Module_Temp_22x_concentrator_tracker_List
        summaryListsAs_df["Annual Range of Module Temperature__22x_concentrator_tracker (C)"] = annual_Range_Module_Temp_22x_concentrator_tracker_List
      
        
        summaryListsAs_df["Sum of Yearly Dew(mmd-1)"] = pd.DataFrame(sumOfHourlyDew_List)
        summaryListsAs_df["Annual Global Horizontal Irradiance (GJ/m^-2)"] = annual_GHI_List
        summaryListsAs_df["Annual Direct Normal Irradiance (GJ/m^-2)"] = annual_DNI_List
        summaryListsAs_df["Annual Diffuse Horizontal Irradiance (GJ/m^-2)"] = annual_DHI_List
        summaryListsAs_df["Annual Global UV Dose (MJ/y^-1)"] = annual_Global_UV_Dose_List
        summaryListsAs_df["Annual UV Dose at Latitude Tilt (MJ/y^-1)"] = annual_UV_Dose_atLatitude_Tilt_List
        summaryListsAs_df["Annual Minimum Ambient Temperature (C)"] = annual_Minimum_Ambient_Temperature_List
        summaryListsAs_df["Annual Average Ambient Temperature (C)"] = annual_Average_Ambient_Temperature_List
        summaryListsAs_df["Annual Maximum Ambient Temperature (C)"] = annual_Maximum_Ambient_Temperature_List
        summaryListsAs_df["Annual Range Ambient Temperature (C)"] = annual_Ambient_Temperature_Range_List
#######################################################################################################################################        
        summaryListsAs_df["Annual number of Hours Relative Humidity > to 85%"] = annual_hoursThatRHabove85_List
     
        summaryListsAs_df["Annual POA Global Irradiance (GJ/m^-2)"] = annual_POA_Global_List
        summaryListsAs_df["Annual POA Direct Irradiance (GJ/m^-2)"] = annual_POA_Direct_List 
        summaryListsAs_df["Annual POA Diffuse Irradiance (GJ/m^-2)"] = annual_POA_Diffuse_List 
        summaryListsAs_df["Annual POA Sky Diffuse Irradiance (GJ/m^-2)"] = annual_POA_SkyDiffuse_List
        summaryListsAs_df["Annual POA Ground Diffuse Irradiance (GJ/m^-2)"] = annual_POA_GroundDiffuse_List
         
        #Create the summary frame of Yearly Water Vapor Pressure(kPa) sum/average
        
        summaryListsAs_df["Average of Yearly Water Vapor Pressure(kPa)"] = pd.DataFrame( avgWaterVaporPressure_List )
        summaryListsAs_df["Sum of Yearly Water Vapor Pressure(kPa)"] = pd.DataFrame( sumWaterVaporPressure_List )
    
        # File path was saved for each summary row,  this will be used to correct indexing
        summaryListsAs_df["FilePath"] = pd.DataFrame(filePath_List)
        
        #Data Source list of each data set.  TMY3 or CWEC or IWEC
        summaryListsAs_df["Data Source"] = pd.DataFrame( dataSource_List )
    
        # When organizing files the directory saves files alphabetically causing index errors
        # Correct the indexing error with the summary sheet and file path list to associate correctly
        unique_SummaryStats = summaryListsAs_df['FilePath'].tolist()
        
        
        #Use the helper method to find the unique identifiers
        unique_SummaryStats = cleanRawOutput.stringList_UniqueID_List( unique_SummaryStats ) 
        summaryListsAs_df["Site Identifier Code Stats"] = unique_SummaryStats
    
    
        # Sort the summary stats "rows" the unique identifier
        summaryListsAs_df = summaryListsAs_df.sort_values(by ="Site Identifier Code Stats" )
        summaryListsAs_df = summaryListsAs_df.reset_index()
        summaryListsAs_df = summaryListsAs_df.drop(['index'],  axis=1)
        # Sort the first Row summary information by the Site Identifier Code. "same as Unique Identifier
        firstRow_summary_df = firstRow_summary_df.sort_values(by ="Site Identifier Code" )
        firstRow_summary_df = firstRow_summary_df.reset_index() 
        firstRow_summary_df = firstRow_summary_df.drop(['index'],  axis=1)
        #Combine the dataframes together
    
        # Drop columns for finalized summary output pickle, 
        # This will be the fianlized pickle that the Output tool will use to display through Excel
        firstRow_summary_df = firstRow_summary_df.drop(['WMO region',
                                                    'Time zone code',
                                                    'Site elevation (km)'], 
                                                    axis=1)
        summaryListsAs_df = summaryListsAs_df.drop(['Site Identifier Code Stats'], 
                                                    axis=1)
        
        
        finalSummary_df = pd.concat([ firstRow_summary_df , summaryListsAs_df ], 
                                    axis = 1, join_axes=[ firstRow_summary_df.index ])
    
        finalSummary_df = finalSummary_df.reindex(columns = ['Site Identifier Code', 
                                                             'FilePath',
                                                             'Station name',
                                                             'Station country or political unit',
                                                             'Station State',
                                                             'Data Source',
                                                             'Site latitude',
                                                             'Site longitude',
                                                             'Site time zone (Universal time + or -)',
                                                             'Site elevation (meters)',
                                                             'Koppen-Geiger climate classification',
                                                             
                                                             'Annual Global Horizontal Irradiance (GJ/m^-2)',
                                                             'Annual Direct Normal Irradiance (GJ/m^-2)',
                                                             'Annual Diffuse Horizontal Irradiance (GJ/m^-2)',
                                                             'Annual POA Global Irradiance (GJ/m^-2)',
                                                             'Annual POA Direct Irradiance (GJ/m^-2)',
                                                             'Annual POA Diffuse Irradiance (GJ/m^-2)',
                                                             'Annual POA Sky Diffuse Irradiance (GJ/m^-2)',
                                                             'Annual POA Ground Diffuse Irradiance (GJ/m^-2)',
                                                             'Annual Global UV Dose (MJ/y^-1)',
                                                             'Annual UV Dose at Latitude Tilt (MJ/y^-1)',
                                                             
                                                             'Annual Minimum Ambient Temperature (C)',
                                                             'Annual Average Ambient Temperature (C)',
                                                             'Annual Maximum Ambient Temperature (C)',
                                                             'Annual Range Ambient Temperature (C)',
                                                             'Average of Yearly Water Vapor Pressure(kPa)',
                                                             'Sum of Yearly Water Vapor Pressure(kPa)',
                                                             "Annual number of Hours Relative Humidity > to 85%",
                                                             'Sum of Yearly Dew(mmd-1)',
    
                                                             'Annual Average (98th Percentile) Cell Temperature__open_rack_cell_glassback (C)', 
                                                             'Annual Average (98th Percentile) Module Temperature__open_rack_cell_glassback (C)',
                                                             'Annual Minimum Module Temperature__open_rack_cell_glassback (C)',
                                                             'Annual Average Module Temperature__open_rack_cell_glassback (C)',
                                                             'Annual Maximum Module Temperature__open_rack_cell_glassback (C)',
                                                             'Annual Range of Module Temperature__open_rack_cell_glassback (C)',
                                                             
                                                             'Annual Average (98th Percentile) Cell Temperature__roof_mount_cell_glassback (C)',
                                                             'Annual Average (98th Percentile) Module Temperature__roof_mount_cell_glassback (C)',
                                                             'Annual Minimum Module Temperature__roof_mount_cell_glassback (C)',
                                                             'Annual Average Module Temperature__roof_mount_cell_glassback (C)',
                                                             'Annual Maximum Module Temperature__roof_mount_cell_glassback (C)',
                                                             'Annual Range of Module Temperature__roof_mount_cell_glassback (C)',                                                         
                                                             
                                                             'Annual Average (98th Percentile) Cell Temperature__open_rack_cell_polymerback (C)',
                                                             'Annual Average (98th Percentile) Module Temperature__open_rack_cell_polymerback (C)',
                                                             'Annual Minimum Module Temperature__open_rack_cell_polymerback (C)',
                                                             'Annual Average Module Temperature__open_rack_cell_polymerback (C)',
                                                             'Annual Maximum Module Temperature__open_rack_cell_polymerback (C)',
                                                             'Annual Range of Module Temperature__open_rack_cell_polymerback (C)',                                                         
                                                             
                                                             'Annual Average (98th Percentile) Cell Temperature__insulated_back_polymerback (C)',
                                                             'Annual Average (98th Percentile) Module Temperature__insulated_back_polymerback (C)',
                                                             'Annual Minimum Module Temperature__insulated_back_polymerback (C)',
                                                             'Annual Average Module Temperature__insulated_back_polymerback (C)',
                                                             'Annual Maximum Module Temperature__insulated_back_polymerback (C)',
                                                             'Annual Range of Module Temperature__insulated_back_polymerback (C)',                                                         
                                                             
                                                             'Annual Average (98th Percentile) Cell Temperature__open_rack_polymer_thinfilm_steel (C)',
                                                             'Annual Average (98th Percentile) Module Temperature__open_rack_polymer_thinfilm_steel (C)',
                                                             'Annual Minimum Module Temperature__open_rack_polymer_thinfilm_steel (C)',
                                                             'Annual Average Module Temperature__open_rack_polymer_thinfilm_steel (C)',
                                                             'Annual Maximum Module Temperature__open_rack_polymer_thinfilm_steel (C)',
                                                             'Annual Range of Module Temperature__open_rack_polymer_thinfilm_steel (C)',                                                         
                                                             
                                                             'Annual Average (98th Percentile) Cell Temperature__22x_concentrator_tracker (C)',
                                                             'Annual Average (98th Percentile) Module Temperature__22x_concentrator_tracker (C)', 
                                                             'Annual Minimum Module Temperature__22x_concentrator_tracker (C)',
                                                             'Annual Average Module Temperature__22x_concentrator_tracker (C)',
                                                             'Annual Maximum Module Temperature__22x_concentrator_tracker (C)',
                                                             'Annual Range of Module Temperature__22x_concentrator_tracker (C)',
    
                                                               ])
    
    
        #Create a summary pickle with the processed data
        #This summary frame will be used to output to the map along with summary stats
        finalSummary_df.to_pickle( path + '\Pandas_Pickle_DataFrames\Pickle_Level1_Summary\Pickle_Level1_Summary.pickle')
        firstRow_summary_df.to_pickle( path + '\Pandas_Pickle_DataFrames\Pickle_Level1_Summary\FirstRow_Summary_Summary.pickle')
        summaryListsAs_df.to_pickle( path + '\Pandas_Pickle_DataFrames\Pickle_Level1_Summary\Pickle_Level1_SummaryPart2.pickle')
      
        
        
    
    
    
#Testing    
    
#currentDirectory = r'C:\Users\DHOLSAPP\Desktop\Weather_DatabaseAddingModuleTempRackRanges'
#i = 0














