# -*- coding: utf-8 -*-
"""
Created on Wed May 22 08:45:52 2019

Code designed to be used as UDF for Excel.  This code is dependent on arguments 
coming from VB Code.

All methods can be found in the excel sheet as a button.  

Each UDF python function is separated by a header comment with needed helper 
methods being imported

@author: Derek Holsapple, Mike Kempe
"""

import pandas as pd  # Pandas used to process data
import os            # Operating System package, used for setting directories and navigating directories
import xlwings as xw # XLWings package used to communicate with excel
import shutil        # Package used to move .csv files from one directory to another
import zipfile       # Package used to unzip files in a directory

# All imports beyond this point are helper methods found in the designated .py files

from Processing.rawDataImport import rawDataImport
from Processing.Level_1_Dataframe_to_Pickle import outputFrame
from Processing.Map_Pickle_Processing import process_Map_Pickle

from SearchOutput.RawDataSearch_and_FirstRow_SummaryReport import dataSummaryFrame , filesNameList, dataSummaryFramePostProcess, stringList_UniqueID_List
from SearchOutput.Closest_Lat_Long import closestLocationFrame

from Map.MapTemperature import outputMapTemp
from Map.MapDewYield import outputMapDew

'''
XL Wings Method
extractAllZip_Files()

Given a root directory the method will extract all files in sub-directories
and place them in a destination directory

@param path        - String, the path of where you want the program to start unzipping files
                        i.e. the program will extract every sub directory beyond this path

@return void       - Program will store extracted files into the Python_RawData_Combined directory

'''
###############################################################################
# Unzip/Move CSV Files into RawData Folder 
###############################################################################
def extractAllZip_Files( path ):


    
    #XL Wings
    ##############
    # Use the xl wings caller function to establish handshake with excel
    myWorkBook = xw.Book.caller() 
    #Reference sheet 0    
    mySheet = myWorkBook.sheets[0]
    ##############
    
    myWorkBook.sheets[mySheet].range(32,4).value = "Unzipping Files"



    #Delete the content of the folder you will be sending the files to.
    # We do this as organization to make sure all the files are current
    for root, dirs, files in os.walk(path + '\\Python_RawData_Combined'):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))


#########
#Search for zipped csv files
#########

    zippedFiles = []
    # Use os walk to cycle through all directories and pull out .zip files
    for dirpath, subdirs, files in os.walk(path + '\RawData'):
        for x in files:
            if x.endswith(".zip"):
                #Join the full path to the isolated folder, add to the zipped files list
                # Note: os.path is referencing a method not the raw path argument
                zippedFiles.append(os.path.join(dirpath, x))
            elif x.endswith(".ZIP"):
                #Join the full path to the isolated folder, add to the zipped files list
                # Note: os.path is referencing a method not the raw path argument
                zippedFiles.append(os.path.join(dirpath, x))            
    
    
    myWorkBook.sheets[mySheet].range(34,6).value =  "Total Files"
    myWorkBook.sheets[mySheet].range(35,6).value =  len( zippedFiles )
    
    myWorkBook.sheets[mySheet].range(34,4).value =  "Files Complete"
    
  
    # Unzip all the files and put them into the directory
    for i in range(0 , len( zippedFiles ) ):
        with zipfile.ZipFile( zippedFiles[i] ,"r") as zip_ref:
            # Directory to put files into
            zip_ref.extractall(path + '\Python_RawData_Combined')

        myWorkBook.sheets[mySheet].range(35,4).value = i + 1
   
#########
#Search for csv files through the directories
#########
    
    myWorkBook.sheets[mySheet].range(32,4).value = "Searching and Relocating CSV Files"

    cSV_Files = []
    # Use os walk to cycle through all directories and pull out .csv files
    for dirpath, subdirs, files in os.walk(path + '\RawData'):
        for x in files:
            if x.endswith(".csv"):
                #Join the full path to the isolated folder, add to the csv files list
                # Note: os.path is referencing a method not the raw path argument
                cSV_Files.append(os.path.join(dirpath, x))
                
            elif x.endswith(".CSV"):
                #Join the full path to the isolated folder, add to the csv files list
                # Note: os.path is referencing a method not the raw path argument
                cSV_Files.append(os.path.join(dirpath, x))   
                
    myWorkBook.sheets[mySheet].range(34,6).value =  "Total Files"
    myWorkBook.sheets[mySheet].range(35,6).value =  len( cSV_Files )
    
    myWorkBook.sheets[mySheet].range(34,4).value =  "Files Complete"
    
    # Move all CSV files and put them into the directory  
    for i in range(0 , len( cSV_Files ) ):
        
        shutil.copy(cSV_Files[i], path + '\Python_RawData_Combined')
        myWorkBook.sheets[mySheet].range(35,4).value = i + 1
        
#########
#Search for epw files through the directories
#########        
        
        
    myWorkBook.sheets[mySheet].range(32,4).value = "Searching and Relocating .epw Files"    
   
    ePW_Files = []     
    # Use os walk to cycle through all directories and pull out .csv files
    for dirpath, subdirs, files in os.walk(path + '\RawData'):
        for x in files:
            if x.endswith(".epw"):
                #Join the full path to the isolated folder, add to the csv files list
                # Note: os.path is referencing a method not the raw path argument
                ePW_Files.append(os.path.join(dirpath, x))
                
            elif x.endswith(".EPW"):
                #Join the full path to the isolated folder, add to the csv files list
                # Note: os.path is referencing a method not the raw path argument
                ePW_Files.append(os.path.join(dirpath, x))           
        
    myWorkBook.sheets[mySheet].range(34,6).value =  "Total Files"
    myWorkBook.sheets[mySheet].range(35,6).value =  len( ePW_Files )
    
    myWorkBook.sheets[mySheet].range(34,4).value =  "Files Complete"
    myWorkBook.sheets[mySheet].range(35,4).value =  len( ePW_Files )        

    # Move all .epw files and put them into the directory  
    for i in range(0 , len( ePW_Files ) ):
        
        shutil.copy(ePW_Files[i], path + '\Python_RawData_Combined')
        myWorkBook.sheets[mySheet].range(35,4).value = i + 1        
        
  
    myWorkBook.sheets[mySheet].range(34,6).value =  "Total Files"
    myWorkBook.sheets[mySheet].range(35,6).value =  len( ePW_Files )
    
    
    


###############################
#If zipped files extracted unwanted file types this will delete them
    #Currently only removing .WY3 data from the Canada data that was extracted 
    # from the zipped folders
    myWorkBook.sheets[mySheet].range(32,4).value = "Restructuring data"

    dir_name = path + '\Python_RawData_Combined'
    allFiles = os.listdir(dir_name)
    
    for item in allFiles:
        if item.endswith(".WY3"):
            os.remove(os.path.join(dir_name, item))    
    
    
    
    myWorkBook.sheets[mySheet].range(32,4).value =  "File Organization Complete"
    
    myWorkBook.sheets[mySheet].range(34,6).value =  ''
    myWorkBook.sheets[mySheet].range(35,6).value =  ''
    
    myWorkBook.sheets[mySheet].range(34,4).value =  ''
    myWorkBook.sheets[mySheet].range(35,4).value =  ''  
    
    

###############################################################################
# Create pickle files from CSV files
# Create 1 summary pickle file 
# Create a pickle file for all the raw data 
###############################################################################

'''
XL Wings METHOD

createPickleFiles()

cycle through the folder and then put each data frame(csv)
into an list named df (dataframe)

 @param dataFrames            -List of DataFrames, list of converted datafraems from .csv files


 @return void  -Will convert dataframes into raw pickle datafiles  
                             *Note: the first row of the datafraemw will not be accessed
                             The first line of data will be saved in a different list with 
                             the same index                   
'''

def createPickleFiles( currentDirectory ):

    
    #XL Wings
    ##############
    # Use the xl wings caller function to establish handshake with excel
    myWorkBook = xw.Book.caller() 
    #Reference sheet 0    
    mySheet = myWorkBook.sheets[0]
    ##############
        
    path = currentDirectory
    
    myWorkBook.sheets[mySheet].range(48,4).value = "Merging IWEC , CWEC, and TMY3 data together"
    
    myWorkBook.sheets[mySheet].range(50,4).value = "Files Processed"
    myWorkBook.sheets[mySheet].range(50,6).value = "Total Files"
    
    dataFrames = rawDataImport.filesToDataFrame( path ) 
    
    myWorkBook.sheets[mySheet].range(48,4).value = "Processing files to Pickle"
    
    
    #First delete the content of the folder you will be sending the files to.
    # We do this as organization to make sure all the files are current
    for root, dirs, files in os.walk(path + '\\Pandas_Pickle_DataFrames\\Pickle_RawData'):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))
    for root, dirs, files in os.walk(path + '\\Pandas_Pickle_DataFrames\\Pickle_FirstRows'):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))
    
    
    
    
    #Pull out the file names from the file path(.csv files) and return a list of file names without .csv extension
    fileNames = rawDataImport.filesNameListCSV_EPW( path )
    
    myWorkBook.sheets[mySheet].range(51,6).value = len(fileNames)
    # Convert the fileNames to have a .pickle extention
    pickleStringList = rawDataImport.pickleNameList( fileNames )
    
    for i in range( 0 , len( fileNames ) ):
        dataFrames[i].to_pickle( path + '\\Pandas_Pickle_DataFrames\\Pickle_RawData' +'\\'+ pickleStringList[i] )

        myWorkBook.sheets[mySheet].range(51,4).value = i + 1
    # Create the summary pickle
    
    myWorkBook.sheets[mySheet].range(48,4).value = "Creating Summary Sheet"
    myWorkBook.sheets[mySheet].range(50,4).value = ""
    myWorkBook.sheets[mySheet].range(50,6).value = ""
    myWorkBook.sheets[mySheet].range(51,4).value = ""
    myWorkBook.sheets[mySheet].range(51,6).value = ""
    
    rawDataImport.createPickleFileFirstRow( path )
    
    myWorkBook.sheets[mySheet].range(48,4).value = "Pickles Sucessfully Saved"


###############################################################################
# Process Irradiance Calculations
# Create a pickle file for each location with processed irradiance calculation
###############################################################################

'''
XL Wings METHOD

createPickleFiles()

Import the raw pickle files.  Process the raw pickle files and return solar 
position and irradiance.  Store the processed data as pickles in the following 
directory
\Pandas_Pickle_DataFrames\Pickle_Level1

param@ currentDirectory     - String, where the excel file is located 
                                   (passed as an argument from EXCEL using UDF)

 @return void               - Will convert dataframes into pickle datafiles  
             *Note: each location will be saved as its own .pickle file                 
'''


def createLevel_1_Pickles( currentDirectory ):
    
    #XL Wings
    ##############
    # Use the xl wings caller function to establish handshake with excel
    myWorkBook = xw.Book.caller() 
    #Reference sheet 0    
    mySheet = myWorkBook.sheets[0]
    ##############
    myWorkBook.sheets[mySheet].range(64,4).value = "Processing Files"
    myWorkBook.sheets[mySheet].range(66,4).value = "Files Processed"
    myWorkBook.sheets[mySheet].range(66,6).value = "Total Files"
    
    
    #First delete the content of the folder you will be sending the files to.
    # We do this as organization to make sure all the files are current
    for root, dirs, files in os.walk(currentDirectory + '\\Pandas_Pickle_DataFrames\\Pickle_Level1'):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))
    for root, dirs, files in os.walk(currentDirectory + '\\Pandas_Pickle_DataFrames\\Pickle_Level1_Summary'):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))
    
    # Pass the arguments from Visual Basic
    # The level_1_df_toPickle() will process raw data for irradiance and store 
    #   each location as a pickle in \Pandas_Pickle_DataFrames\Pickle_Level1
    # This is the largest computation currently
    outputFrame.level_1_df_toPickle( currentDirectory )

    # User feedback
    myWorkBook.sheets[mySheet].range(64,4).value = "All Files Sucessfully Saved"


###############################################################################
# Process Map Pickle
# Create a pickle file that processes information for the Map
###############################################################################

'''
XL Wings METHOD

createMap_Pickles()

Import the summary pickle file.  Process the the lat/lon to render proper 
formatting for map interpretation
Save the pickle to 
\Pandas_Pickle_DataFrames\Pickle_Map

param@ currentDirectory     - String, where the excel file is located 
                                   (passed as an argument from EXCEL using UDF)

 @return void               - Will convert pickle into pickle datafiles  
             *Note: this will be used for map rendering                
'''


def createMap_Pickles( currentDirectory ):
    
    #XL Wings
    ##############
    # Use the xl wings caller function to establish handshake with excel
    myWorkBook = xw.Book.caller() 
    #Reference sheet 0    
    mySheet = myWorkBook.sheets[0]
    ##############
    myWorkBook.sheets[mySheet].range(78,4).value = "Processing Files"

    #First delete the content of the folder you will be sending the files to.
    # We do this as organization to make sure all the files are current
    for root, dirs, files in os.walk(currentDirectory + '\\Pandas_Pickle_DataFrames\\Pickle_Map'):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))

    
    # Pass the arguments from Visual Basic
    # The level_1_df_toPickle() will process raw data for irradiance and store 
    #   each location as a pickle in \Pandas_Pickle_DataFrames\Pickle_Level1
    # This is the largest computation currently
    process_Map_Pickle(currentDirectory)

    # User feedback
    myWorkBook.sheets[mySheet].range(76,4).value = "All Files Sucessfully Saved"




###############################################################################
#SUMMARY REPORT, exports a combined list of the first row of each raw data .csv
###############################################################################    
'''
XL Wings METHOD

Take a summary dataframe from the helper method and output a report to a 
generated excel sheet

param@ currentDirectory      - String, where the excel file is located (passed as an argument 
                                                          from EXCEL if using UDF) 

return@ void     - Creates a summary csv of all data

'''

def outputFileSummary( currentDirectory ):
    
    #XL Wings
    ##############
    # Use the xl wings caller function to establish handshake with excel
    myWorkBook = xw.Book.caller() 
    #Reference sheet 0    
    mySheet = myWorkBook.sheets[1]
    ##############
    
    path = currentDirectory
    
    
    # create a summary data frame from the helper method
    summary_df = dataSummaryFrame( path )

    # Pull out the column names
    columnHeaders_list = list(summary_df)  
    

    #Output the column names and summary dataframe
    myWorkBook.sheets[mySheet].range(6,1).value = columnHeaders_list
        # Convert the dataframe into a list and then export the data "removes columns and headers"
    myWorkBook.sheets[mySheet].range(7,1).value = summary_df.values.tolist()

###############################################################################
#SUMMARY REPORT Post-Processed, exports a combined list of the first row of each raw data .csv
###############################################################################    
'''
XL Wings METHOD

Take a summary dataframe from the helper method and output a report to a 
generated excel sheet

param@ currentDirectory      - String, where the excel file is located (passed as an argument 
                                                          from EXCEL if using UDF) 

return@ void     - Creates a summary csv of all data

'''

def outputFileSummaryPostProcess( currentDirectory ):
    
    #XL Wings
    ##############
    # Use the xl wings caller function to establish handshake with excel
    myWorkBook = xw.Book.caller() 
    #Reference sheet 0    
    mySheet = myWorkBook.sheets[1]
    ##############
    
    path = currentDirectory
    
    
    # create a summary data frame from the helper method
    summary_df = dataSummaryFramePostProcess( path )

    # Pull out the column names
    columnHeaders_list = list(summary_df)  
    

    #Output the column names and summary dataframe
    myWorkBook.sheets[mySheet].range(6,1).value = columnHeaders_list
        # Convert the dataframe into a list and then export the data "removes columns and headers"
    myWorkBook.sheets[mySheet].range(7,1).value = summary_df.values.tolist()




###############################################################################
#SEARCH RAW DATA, exports the raw data with user input Unique Identifier
###############################################################################   

'''
XL Wings METHOD

searchRawPickle_Output()

1) Take user input being a unique Identifier 
2) Search the pickle files for a match
3) Output the raw pickle data to the excel sheet

@param path     -String, path to the folder where this .py file is located
@param userInput -String, unique Identifier of a location found on sheet one 

@return void    - Output of raw data to excel sheet two

'''
    
def searchRawPickle_Output( currentDirectory , userInput):    
    
    #XL Wings
    #############
    # Use the xl wings caller function to establish handshake with excel
    myWorkBook = xw.Book.caller()
    #Reference sheet 1 "This is the second sheet, reference starts at 0"
    mySheet = myWorkBook.sheets[2]
    #############
    
    
    #Set path
    path = currentDirectory
    
    
    # Get the file name of each raw data pickle,  the unique identifier is inside this list
    rawfileNames = filesNameList( path )
    
    # Reference the summary frame to pull out the user Input row and display
    summary_df = dataSummaryFrame( path )
    
    #Create a list of unique identifiers for the file string names "See helper functions"
    uniqueID_List = stringList_UniqueID_List(rawfileNames)
    
    
    booleanSearch = summary_df["Site Identifier Code"].str.find(userInput) 
    for r in range( 0 , len(booleanSearch)):
        if booleanSearch[r] == 0:
            summaryRow_df = summary_df.iloc[r,:]
            break
    

    
    for i in range(0 , len( rawfileNames ) ):
      
        #If the user input is a match with a raw data file
        if userInput == uniqueID_List[i]:
            # Pull out the raw pickle of the located file name
            raw_df = pd.read_pickle( path + '/Pandas_Pickle_DataFrames/Pickle_RawData/' + rawfileNames[i] )
            
            # Pull out the column names of Raw data
            rawcolumnHeaders_list = list(raw_df)
            
            # Pull out the column names of the summary frame
            summaryColumnHeaders_list = list(summary_df)
            
            # pull out the row associated with the unique identifier
            # Note: the summary df will have the same index row as the rawFileName list
###########################################################
         #   summaryRow_df = summary_df.iloc[i,:]

#####################################################################################            
            #Output the raw column names 
            myWorkBook.sheets[mySheet].range(9,1).value = rawcolumnHeaders_list
            # Export the raw data frame for that location
            # Convert the dataframe into a list and then export the data "removes columns and headers"
            myWorkBook.sheets[mySheet].range(10,1).value = raw_df.values.tolist()
            
            #Output the summary column names 
            myWorkBook.sheets[mySheet].range(6,1).value = summaryColumnHeaders_list
            # Output the summary row for that location
            # Convert the dataframe into a list and then export the data "removes columns and headers"
            myWorkBook.sheets[mySheet].range(7,1).value =  summaryRow_df.tolist()
            
            #Stop the search for loop once the file is located
            break
        

###############################################################################
#SEARCH RAW DATA, exports the raw data with user input Unique Identifier
###############################################################################   

'''
XL Wings METHOD

searchRawPickle_Output()

1) Take user input being a unique Identifier 
2) Search the pickle files for a match
3) Output the raw pickle data to the excel sheet

@param path     -String, path to the folder where this .py file is located
@param userInput -String, unique Identifier of a location found on sheet one 

@return void    - Output of raw data to excel sheet two

'''
    
def search_Level1_Pickle_Output( currentDirectory , userInput):    
    
    #XL Wings
    #############
    # Use the xl wings caller function to establish handshake with excel
    myWorkBook = xw.Book.caller()
    #Reference sheet 1 "This is the second sheet, reference starts at 0"
    mySheet = myWorkBook.sheets[2]
    #############
    
    
    #Set path
    path = currentDirectory
    
    
    # Get the file name of each raw data pickle,  the unique identifier is inside this list
    rawfileNames = filesNameList( path )
    
    # Reference the summary frame to pull out the user Input row and display
    summary_df = dataSummaryFrame( path )
    
    #Create a list of unique identifiers for the file string names "See helper functions"
    uniqueID_List = stringList_UniqueID_List(rawfileNames)
    
    booleanSearch = summary_df["Site Identifier Code"].str.find(userInput) 
    for r in range( 0 , len(booleanSearch)):
        if booleanSearch[r] == 0:
            summaryRow_df = summary_df.iloc[r,:]
            break
    
    
    
    for i in range(0 , len( rawfileNames ) ):

        #If the user input is a match with a raw data file
        if userInput == uniqueID_List[i]:
            # Pull out the raw pickle of the located file name
            raw_df = pd.read_pickle( path + '/Pandas_Pickle_DataFrames/Pickle_Level1/' + rawfileNames[i] )
            
            # Pull out the column names of Raw data
            rawcolumnHeaders_list = list(raw_df)
            
            # Pull out the column names of the summary frame
            summaryColumnHeaders_list = list(summary_df)
            
            # pull out the row associated with the unique identifier
            # Note: the summary df will have the same index row as the rawFileName list
 #           summaryRow_df = summary_df.iloc[i,:]
            
            #Output the raw column names 
            myWorkBook.sheets[mySheet].range(9,1).value = rawcolumnHeaders_list
            # Export the raw data frame for that location
            # Convert the dataframe into a list and then export the data "removes columns and headers"
            myWorkBook.sheets[mySheet].range(10,1).value = raw_df.values.tolist()
            
            #Output the summary column names 
            myWorkBook.sheets[mySheet].range(6,1).value = summaryColumnHeaders_list
            # Output the summary row for that location
            # Convert the dataframe into a list and then export the data "removes columns and headers"
            myWorkBook.sheets[mySheet].range(7,1).value =  summaryRow_df.tolist()
            
            #Stop the search for loop once the file is located
            break
        
###############################################################################
# Search for Closest Cities with a user input Latitude and Longitude

###############################################################################

'''
XL Wings METHOD

createPickleFiles()

Ask the user to enter a point of interest in Latitude and Longitude in Decimal Degrees.
Return a summary of distances closest to the point of interest.  The summary 
will be sorted from smallest distance to greatest distance.

param@ currentDirectory   - String, where the excel file is located 
                                   (passed as an argument from EXCEL using UDF)
 @param lat1              - Float , Decimal Degrees of the latitude of point of interest
                                   (passed as an argument from EXCEL using UDF)
 @param lon1              - Float , Decimal Degrees of the longitude of point of interest
                                   (passed as an argument from EXCEL using UDF)

 @return void               - return a summary to excel with locations sorted 
                                 from shortest distance to greatest distance                 
'''

def closest_Cities( currentDirectory ,  lat1 , lon1 ):
    
    #XL Wings
    ##############
    # Use the xl wings caller function to establish handshake with excel
    myWorkBook = xw.Book.caller() 
    #Reference sheet 0    
    mySheet = myWorkBook.sheets[1]
    ##############
    
    myWorkBook.sheets[mySheet].range(6,11).value = "Distance From (km)"
    
    myWorkBook.sheets[mySheet].range(7,11).value = "Latitude"
    myWorkBook.sheets[mySheet].range(8,11).value = lat1
    
    myWorkBook.sheets[mySheet].range(7,12).value = "Longitude"
    myWorkBook.sheets[mySheet].range(8,12).value = lon1
    
    closestLocation_df , columnNames_list = closestLocationFrame( currentDirectory ,  lat1 , lon1 )
    
    myWorkBook.sheets[mySheet].range(11,3).value = closestLocation_df.values.tolist()
    
    myWorkBook.sheets[mySheet].range(10,3).value = columnNames_list

###############################################################################
# Output Map of Summary Data
# Create a map from the Map pickle Data
###############################################################################

'''
XL Wings METHOD

createTempMap()

Import the processed map pickle and create a map using the Bokeh package.
Bokeh will render a html file containing the map. 

@param path       - String, where the excel file is located 
                                   (passed as an argument from EXCEL using UDF)
@param mapSelect  - String, used to select what type of map to render
                            - See "MapDewYield.py" for exact string to pass                                  

 @return void     - Will render a map
           
'''


def createTempMap(path , mapSelect ):
    
    #XL Wings
    ##############
    # Use the xl wings caller function to establish handshake with excel
    xw.Book.caller() 
    #Reference sheet 0    
    ##############

    outputMapTemp(path , mapSelect )


'''
XL Wings METHOD

createDewMap()

Import the processed map pickle and create a map using the Bokeh package.
Bokeh will render a html file containing the map. 

@param path       - String, where the excel file is located 
                                   (passed as an argument from EXCEL using UDF)
@param mapSelect  - String, used to select what type of map to render
                            - See "MapDewYield.py" for exact string to pass                                  

 @return void     - Will render a map
           
'''
def createDewMap(path , mapSelect ):
    
    #XL Wings
    ##############
    # Use the xl wings caller function to establish handshake with excel
    xw.Book.caller() 
    #Reference sheet 0    
    ##############

    outputMapDew(path , mapSelect )



userInput = '677650'
path = r'C:\Users\DHOLSAPP\Desktop\Summer_Project\Weather_Database'










