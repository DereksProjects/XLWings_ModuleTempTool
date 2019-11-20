"""
Functions designed to be used as UDF in Excel.  The functions are dependent on
arguments coming from Visual Basic inside Excel

All functions are designed to run through a User Defined Function "Grey Button"
within the Output_Tool.xlsm file 

@author: Derek Holsapple
"""
import pandas as pd  
import os            
import xlwings as xw 
import shutil        
import zipfile      
from Processing.rawDataImport import rawDataImport
from Processing.finalOutputFrame import finalOutputFrame
from Processing.mapProcessing import mapProcessing
from Processing.cleanRawOutput import cleanRawOutput
from Processing.closestLatLon import closestLatLon
from Map.mapTemp import mapTemp
from Map.plotSite import plotSite
from Map.mapGenerator import mapGenerator


def extractAllZip_Files( path ):
    '''
    XL Wings FUNCTION
    
    extractAllZip_Files()
    
    Given a root directory the method will extract all files in sub-directories
    and place them in a destination directory.  CUrrently can process zipped,
    ipw and csv files and place into one single directory
    
    @param path        - String, the path of where you want the program to start 
                                    unzipping files
                            i.e. the program will extract every sub directory 
                                    beyond this path
    @return void       - Program will store extracted files into the 
                                    Python_RawData_Combined directory
    '''
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
                zippedFiles.append(os.path.join(dirpath, x))
            elif x.endswith(".ZIP"):
                zippedFiles.append(os.path.join(dirpath, x))            
    #ReferenceXL wings to give user feedback
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
    myWorkBook.sheets[mySheet].range(32,4).value = \
                                        "Searching and Relocating CSV Files"
    cSV_Files = []
    # Use os walk to cycle through all directories and pull out .csv files
    for dirpath, subdirs, files in os.walk(path + '\RawData'):
        for x in files:
            if x.endswith(".csv"):
                cSV_Files.append(os.path.join(dirpath, x))
            elif x.endswith(".CSV"):
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
    myWorkBook.sheets[mySheet].range(32,4).value = \
                                        "Searching and Relocating .epw Files"    
    ePW_Files = []     
    # Use os walk to cycle through all directories and pull out .csv files
    for dirpath, subdirs, files in os.walk(path + '\RawData'):
        for x in files:
            if x.endswith(".epw"):
                ePW_Files.append(os.path.join(dirpath, x))
            elif x.endswith(".EPW"):
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



def createPickleFiles( currentDirectory ):
    '''
    XL Wings FUNCTION
    
    createPickleFiles()
    
    Cycle through the folder and then put each data frame(csv)
    into an list named df (dataframe)
    
    @param currentDirectory     - String, where the excel file is located 
                                       (passed as an argument from EXCEL using UDF)
    @return void                - dataframes into raw pickle datafiles               
    '''
    #XL Wings
    ##############
    # Use the xl wings caller function to establish handshake with excel
    myWorkBook = xw.Book.caller() 
    #Reference sheet 0    
    mySheet = myWorkBook.sheets[0]
    ##############  
    path = currentDirectory
    myWorkBook.sheets[mySheet].range(48,4).value = \
                                "Merging IWEC , CWEC, and TMY3 data together"
    myWorkBook.sheets[mySheet].range(50,4).value = "Files Processed"
    myWorkBook.sheets[mySheet].range(50,6).value = "Total Files"
    dataFrames = rawDataImport.filesToDataFrame( path ) 
    myWorkBook.sheets[mySheet].range(48,4).value = "Processing files to Pickle"
    #First delete the content of the folder you will be sending the files to.
    # We do this as organization to make sure all the files are current
    for root, dirs, files in os.walk(path + \
                              '\\Pandas_Pickle_DataFrames\\Pickle_RawData'):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))
    for root, dirs, files in os.walk(path + \
                               '\\Pandas_Pickle_DataFrames\\Pickle_FirstRows'):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))
    #Pull out the file names from the file path(.csv files) and return a list 
    # of file names without .csv extension
    fileNames = rawDataImport.filesNameListCSV_EPW( path )
    myWorkBook.sheets[mySheet].range(51,6).value = len(fileNames)
    # Convert the fileNames to have a .pickle extention
    pickleStringList = rawDataImport.pickleNameList( fileNames )
    for i in range( 0 , len( fileNames ) ):
        dataFrames[i].to_pickle( path + \
       '\\Pandas_Pickle_DataFrames\\Pickle_RawData' +'\\'+ pickleStringList[i] )
        myWorkBook.sheets[mySheet].range(51,4).value = i + 1
    # Create the summary pickle
    myWorkBook.sheets[mySheet].range(48,4).value = "Creating Summary Sheet"
    myWorkBook.sheets[mySheet].range(50,4).value = ""
    myWorkBook.sheets[mySheet].range(50,6).value = ""
    myWorkBook.sheets[mySheet].range(51,4).value = ""
    myWorkBook.sheets[mySheet].range(51,6).value = ""
    rawDataImport.createPickleFileFirstRow( path )
    myWorkBook.sheets[mySheet].range(48,4).value = "Pickles Sucessfully Saved"
    
    

def createLevel_1_Pickles( currentDirectory ): 
    '''
    XL Wings FUNCTION
    
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
    for root, dirs, files in os.walk(currentDirectory + \
                              '\\Pandas_Pickle_DataFrames\\Pickle_Level1'):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))
    for root, dirs, files in os.walk(currentDirectory + \
                        '\\Pandas_Pickle_DataFrames\\Pickle_Level1_Summary'):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))
    # This is the largest computation currently
    finalOutputFrame.level_1_df_toPickle( currentDirectory )
    # User feedback
    myWorkBook.sheets[mySheet].range(64,4).value = "All Files Sucessfully Saved"



def createMap_Pickles( currentDirectory ):
    '''
    XL Wings FUNCTION
    
    createMap_Pickles()
    
    Import the summary pickle file.  Process the the lat/lon to render proper 
    formatting for map interpretation.
    Save the pickle to 
    \Pandas_Pickle_DataFrames\Pickle_Map
    
    @param currentDirectory     - String, where the excel file is located 
                                    (passed as an argument from EXCEL using UDF)
    @return void                - Will convert pickle into pickle datafiles  
                                     *Note: this will be used for map rendering                
    '''    
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
    for root, dirs, files in os.walk(currentDirectory + \
                                     '\\Pandas_Pickle_DataFrames\\Pickle_Map'):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))
    mapProcessing.process_Map_Pickle(currentDirectory)
    # User feedback
    myWorkBook.sheets[mySheet].range(76,4).value = "All Files Sucessfully Saved"

  

def outputFileSummary( currentDirectory ):
    '''
    XL Wings FUNCTION
    
    Output a report to a excel sheet with XLWings
    
    param@ currentDirectory      - String, where the excel file is located 
                                        (passed as an argument from EXCEL) 
    @return void                  - Creates a summary csv of all data
    '''    
    #XL Wings
    ##############
    # Use the xl wings caller function to establish handshake with excel
    myWorkBook = xw.Book.caller() 
    #Reference sheet 0    
    mySheet = myWorkBook.sheets[1]
    ##############
    path = currentDirectory
    # create a summary data frame from the helper method
    summary_df = cleanRawOutput.dataSummaryFrame( path )
    columnHeaders_list = list(summary_df)  
    #Output the column names and summary dataframe
    myWorkBook.sheets[mySheet].range(6,1).value = columnHeaders_list
    myWorkBook.sheets[mySheet].range(7,1).value = summary_df.values.tolist()
   


def outputFileSummaryPostProcess( currentDirectory ):
    '''
    XL Wings FUNCTION
    
    Take a summary dataframe from the helper method and output a report to a 
    generated excel sheet
    
    @param currentDirectory      - String, where the excel file is located 
                                    (passed as an argument from EXCEL if using UDF) 
    @return void                 - Creates a summary csv of all data
    '''    
    #XL Wings
    ##############
    # Use the xl wings caller function to establish handshake with excel
    myWorkBook = xw.Book.caller() 
    #Reference sheet 0    
    mySheet = myWorkBook.sheets[1]
    ##############
    path = currentDirectory
    # create a summary data frame
    summary_df = pd.read_pickle( path + '\\Pandas_Pickle_DataFrames\\' + \
                        'Pickle_Level1_Summary\\Pickle_Level1_Summary.pickle')
    columnHeaders_list = list(summary_df)  
    myWorkBook.sheets[mySheet].range(10,1).value = columnHeaders_list
    myWorkBook.sheets[mySheet].range(11,1).value = summary_df.values.tolist()
 


    
def searchRawPickle_Output( currentDirectory , userInput):    
    '''
    XL Wings FUNCTION
    
    searchRawPickle_Output()
    
    1) Take user input being a unique Identifier 
    2) Search pickle files for a match
    3) Output the raw pickle data to the excel sheet
    
    @param currentDirectory    - String, where the excel file is located 
                                    (passed as an argument from EXCEL if using UDF)
    @param userInput           -String, unique Identifier of a location 
    
    @return void               - Output of raw data to excel
    '''    
    #XL Wings
    #############
    # Use the xl wings caller function to establish handshake with excel
    myWorkBook = xw.Book.caller()
    #Reference sheet 1 "This is the second sheet, reference starts at 0"
    mySheet = myWorkBook.sheets[2]
    #############
    path = currentDirectory
    rawfileNames = cleanRawOutput.filesNameList( path )
    summary_df = cleanRawOutput.dataSummaryFrame( path )
    uniqueID_List = cleanRawOutput.stringList_UniqueID_List(rawfileNames)
    booleanSearch = summary_df["Site Identifier Code"].str.find(userInput) 
    for r in range( 0 , len(booleanSearch)):
        if booleanSearch[r] == 0:
            summaryRow_df = summary_df.iloc[r,:]
            break
    for i in range(0 , len( rawfileNames ) ):
        #If the user input is a match with a raw data file
        if userInput == uniqueID_List[i]:
            # Pull out the raw pickle of the located file name
            raw_df = pd.read_pickle( path + \
                '/Pandas_Pickle_DataFrames/Pickle_RawData/' + rawfileNames[i] )
            rawcolumnHeaders_list = list(raw_df)
            summaryColumnHeaders_list = list(summary_df) 
            myWorkBook.sheets[mySheet].range(9,1).value = rawcolumnHeaders_list
            myWorkBook.sheets[mySheet].range(10,1).value = raw_df.values.tolist()
            myWorkBook.sheets[mySheet].range(6,1).value = summaryColumnHeaders_list
            # Output the summary row for that location
            myWorkBook.sheets[mySheet].range(7,1).value =  summaryRow_df.tolist()
            #Stop the search for loop once the file is located
            break  



def search_Level1_Pickle_Output( currentDirectory , userInput):    
    '''
    XL Wings METHOD
    
    search_Level1_Pickle_Output()
    
    1) Take user input being a unique Identifier 
    2) Search the pickle files for a match
    3) Output the raw pickle data to the excel sheet
    
    @param path      -String, path to the folder where this .py file is located
    @param userInput -String, unique Identifier of a location found on sheet one 
    
    @return void    - Output of raw data to excel sheet two
    '''
    #XL Wings
    #############
    # Use the xl wings caller function to establish handshake with excel
    myWorkBook = xw.Book.caller()
    #Reference sheet 1 "This is the second sheet, reference starts at 0"
    mySheet = myWorkBook.sheets[2]
    #############
    path = currentDirectory
    rawfileNames = cleanRawOutput.filesNameList( path )
    summary_df = cleanRawOutput.dataSummaryFrame( path )
    uniqueID_List = cleanRawOutput.stringList_UniqueID_List(rawfileNames)
    booleanSearch = summary_df["Site Identifier Code"].str.find(userInput) 
    for r in range( 0 , len(booleanSearch)):
        if booleanSearch[r] == 0:
            summaryRow_df = summary_df.iloc[r,:]
            break
    for i in range(0 , len( rawfileNames ) ):
        #If the user input is a match with a raw data file
        if userInput == uniqueID_List[i]:
            # Pull out the raw pickle of the located file name
            raw_df = pd.read_pickle( path + \
                '/Pandas_Pickle_DataFrames/Pickle_Level1/' + rawfileNames[i] )
            rawcolumnHeaders_list = list(raw_df)
            summaryColumnHeaders_list = list(summary_df)
            myWorkBook.sheets[mySheet].range(9,1).value = rawcolumnHeaders_list
            myWorkBook.sheets[mySheet].range(10,1).value = raw_df.values.tolist()
            myWorkBook.sheets[mySheet].range(6,1).value = summaryColumnHeaders_list
            myWorkBook.sheets[mySheet].range(7,1).value =  summaryRow_df.tolist()
            #Stop the search for loop once the file is located
            break



def closest_Cities( currentDirectory ,  lat1 , lon1 ):
    '''
    XL Wings FUNCTION
    
    createPickleFiles()
    
    Ask the user to enter a point of interest in Latitude and Longitude in Decimal 
    Degrees.  Return a summary of distances closest to the point of interest. 
    The summary will be sorted from smallest distance to greatest distance.
    
    param@ currentDirectory   - String, where the excel file is located 
                                       (passed as an argument from EXCEL using UDF)
     @param lat1              - Float , Decimal Degrees of the latitude 
                                       (passed as an argument from EXCEL using UDF)
     @param lon1              - Float , Decimal Degrees of the longitude 
                                       (passed as an argument from EXCEL using UDF)
     @return void               - return a summary to excel with locations sorted 
                                     from shortest distance to greatest distance                 
    '''    
    #XL Wings
    ##############
    # Use the xl wings caller function to establish handshake with excel
    myWorkBook = xw.Book.caller() 
    #Reference sheet 0    
    mySheet = myWorkBook.sheets[1]
    ##############
    myWorkBook.sheets[mySheet].range(6,1).value = "Distance From (km)"
    myWorkBook.sheets[mySheet].range(7,1).value = "Latitude"
    myWorkBook.sheets[mySheet].range(8,1).value = lat1
    myWorkBook.sheets[mySheet].range(7,2).value = "Longitude"
    myWorkBook.sheets[mySheet].range(8,2).value = lon1
    closestLocation_df , columnNames_list = \
        closestLatLon.closestLocationFrame( currentDirectory ,  lat1 , lon1 )
    myWorkBook.sheets[mySheet].range(11,1).value = \
        closestLocation_df.values.tolist()
    myWorkBook.sheets[mySheet].range(10,1).value = columnNames_list



def createTempMap(path , mapSelect ):
    '''
    XL Wings FUNCTION
    
    createTempMap()
    
    Import the processed map pickle and create a map using the Bokeh package.
    Bokeh will render a html file containing the map. 
    
    @param path       - String, where the excel file is located 
                                       (passed as an argument from EXCEL using UDF)
    @param mapSelect  - String, used to select what type of map to render
                                - See "MapDewYield.py" for exact string to pass                                  
    
    @return void      - Will render a map          
    '''    
    #XL Wings
    ##############
    # Use the xl wings caller function to establish handshake with excel
    xw.Book.caller() 
    #Reference sheet 0    
    ##############
    mapTemp.outputMapTemp(path , mapSelect )



def outputMapDriver( currentDirectory , mapType ):
    '''
    XL Wings FUNCTIONS
    
    outputMapDriver()
    
    Driver to render a map. 
    
    @param currentDirectory    - String, where the excel file is located 
                                       (passed as an argument from EXCEL using UDF)
    @param mapType             - String, The type of data to display as a map
                           
    @return void               - Void, Renders a world map          
    '''    
    mapGenerator.mapGeneratorDriver(currentDirectory , mapType)



def outputPlotDriver( currentDirectory , fileID , selector ):
    '''
    XL Wings FUNCTIONS
    
    outputPlotDriver()
    
    Driver to render a plot of individual site data. 
    
    @param currentDirectory    - String, where the excel file is located 
                                       (passed as an argument from EXCEL using UDF)
    @param fileID              - String, unique ID of site specific location
                                                                 
    @param selector            - String, select what type data to plot
                                
    @return void               - Void, Renders a data plot of a individual site          
    '''    
    plotSite.xLWingsInterfacePlot( currentDirectory , fileID , selector )