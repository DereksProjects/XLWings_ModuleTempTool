# -*- coding: utf-8 -*-
"""
One method of this code will create a summary dataframe.  The other method 
searches for a user input Site Identifier Code and displays the raw data

@author: Derek Holsapple
"""


import pandas as pd
import glob
import os 
import xlwings as xw



'''
HELPER METHOD

dataSummaryFrame()

This will be a dataframe used for user reference table
Clean the datafraem and change variables for readability

@param path     -String, path to the folder with the pickle files

@retrun formatted_df  -Dataframe, summarized dataframe for user reference table

'''

def dataSummaryFrame( path ):

    #import the pickle dataframe for the summary report
    formatted_df = pd.read_pickle( path + '\\Pandas_Pickle_DataFrames\\Pickle_FirstRows\\firstRowSummary_Of_CSV_Files.pickle')
    
    
    # Isolate the WMO column, WMO regions = geographical locations (continents)
    wMO_df = formatted_df.loc[:,['WMO region']]
    
    #Set the data type of the frame to a string
    # The numbers needs to be converted to a string, only string to string replacement is allowed
    wMO_df = wMO_df['WMO region'].astype(str)
    
    # Replace the numbers with location names,  Access the 'WMO region' column
    # 1 = Africa
    # 2 = Asia
    # 3 = South America
    # 4 = North and Central America
    # 5 = South West Pacific
    # 6 = Europe
    # 7 = Antartica
    
    wMO_df = wMO_df.replace( {
                               '1' : 'Africa' ,
                               '2' : 'Asia' ,
                               '3' : 'South America' ,
                               '4' : 'North and Central America' ,
                               '5' : 'South West Pacific' ,
                               '6' : 'Europe' ,
                               '7' : 'Antartica' } )
    
    # change the 'WMO region column into the converted continent column
    formatted_df[ 'WMO region' ] = wMO_df
    
    return formatted_df


'''
HELPER METHOD

dataSummaryFrame()

This will be a dataframe used for user reference table
Clean the datafraem and change variables for readability

@param path     -String, path to the folder with the pickle files

@retrun formatted_df  -Dataframe, summarized dataframe for user reference table

'''

def dataSummaryFramePostProcess( path ):

    #import the pickle dataframe for the summary report
    firstRowSummary_df = pd.read_pickle( path + '\\Pandas_Pickle_DataFrames\\Pickle_Level1_Summary\\Pickle_Level1_Summary.pickle')
    
    return firstRowSummary_df
    
'''
OUTPUT METHOD

Take a summary dataframe from the helper method and output a report to a 
generated excel sheet

param@ currentDirectory      - String, where the excel file is located (passed as an argument 
                                                          from EXCEL if using UDF) 

return@ void                 - Creates a summary csv of all data

'''

def outputFileSummary( FileName , currentDirectory ):
    
    
    # Reference which sheet inside the workbook you want to manipulate
    # Create a .csv file to store the new data 
    open( FileName , 'wb')
    # Reference which sheet inside the workbook you want to manipulate
    myWorkBook = xw.Book( FileName )
    
    #Reference sheet 0    
    mySheet = myWorkBook.sheets[0]
    
    path = currentDirectory
    
    
    # create a summary data frame from the helper method
    summary_df = dataSummaryFrame( path )

    # Pull out the column names
    columnHeaders_list = list(summary_df)  
    

    #Output the column names and summary dataframe
    myWorkBook.sheets[mySheet].range(1,1).value = columnHeaders_list
        # Convert the dataframe into a list and then export the data "removes columns and headers"
    myWorkBook.sheets[mySheet].range(2,1).value = summary_df.values.tolist()


'''
HELPER METHOD

filesNameList()

Pull out the file name from the file pathes and return a list of file names

@param path     -String, path to the folder with the pickle files

@retrun allFiles  -String List, filenames without the file path

'''
def filesNameList( path ):
    
    #list of strings of all the files
    allFiles = glob.glob(path + "/Pandas_Pickle_DataFrames/Pickle_RawData/*")
    
    #for loop to go through the lists of strings and to remove irrelavant data
    for i in range( 0, len( allFiles ) ):

        # Delete the path and pull out only the file name using the os package from each file
        temp = os.path.basename(allFiles[i])
        allFiles[i] = temp
        
    return allFiles


'''
OUTPUT METHOD

searchRawPickle_Output()

1) Take user input being a unique Identifier 
2) Search the pickle files for a match
3) Output the raw pickle data to the excel sheet

@param path     -String, path to the folder where this .py file is located
@param userInput -String, unique Identifier of a location found on sheet one 

@return void    - Output of raw data to excel sheet two

'''
    
def searchRawPickle_Output( FileName , currentDirectory , userInput):    
    
    #XL Wings
    # Create a .csv file to store the new data 
    open( FileName , 'wb')
    # Reference which sheet inside the workbook you want to manipulate
    myWorkBook = xw.Book( FileName )
    #Reference sheet 1 "This is the second sheet, reference starts at 0"
    mySheet = myWorkBook.sheets[0]
    
    
    #Set path
    path = currentDirectory
    
    # Get the file name of each raw data pickle,  the unique identifier is inside this list
    rawfileNames = filesNameList( path )
    
    # Reference the summary frame to pull out the user Input row and display
    summary_df = dataSummaryFrame( path )
    
    
    for i in range(0 , len( rawfileNames ) ):
        #Split the string into a list,  The unique identifier will be the 3rd element of this list
        # split the string when the file name gives a "_"
        splitFile = rawfileNames[i].split('_', 3)
        identifier = splitFile[2]
        
        #If the user input is a match with a raw data file
        if userInput == identifier:
            # Pull out the raw pickle of the located file name
            raw_df = pd.read_pickle( path + '/Pandas_Pickle_DataFrames/Pickle_RawData/' + rawfileNames[i] )
            
            # Pull out the column names of Raw data
            rawcolumnHeaders_list = list(raw_df)
            
            # Pull out the column names of the summary frame
            summaryColumnHeaders_list = list(summary_df)
            
            # pull out the row associated with the unique identifier
            # Note: the summary df will have the same index row as the rawFileName list
            summaryRow_df = summary_df.iloc[i,:]
            

            #Output the raw column names 
            myWorkBook.sheets[mySheet].range(4,1).value = rawcolumnHeaders_list
            # Export the raw data frame for that location
            # Convert the dataframe into a list and then export the data "removes columns and headers"
            myWorkBook.sheets[mySheet].range(5,1).value = raw_df.values.tolist()
            
            #Output the summary column names 
            myWorkBook.sheets[mySheet].range(1,1).value = summaryColumnHeaders_list
            # Output the summary row for that location
            # Convert the dataframe into a list and then export the data "removes columns and headers"
            myWorkBook.sheets[mySheet].range(2,1).value =  summaryRow_df.tolist()
            
            #Stop the search for loop once the file is located
            break
 


'''
stringList_UniqueID_List()

This method takes a lists of strings and searches for a unique sample identifier.  
It then takes that unique identifier and creates a list.  If one of the strings 
does not have a unique identifier it will put that original string back into the list

Example List

'690190TYA.pickle',
'GRC_SOUDA(AP)_167460_IW2.pickle',
'GRC_SOUDA-BAY-CRETE_167464_IW2.pickle',
'Test']


Return List

'690190'
'167460'
'167464'
'Test'
 

param@ listOfStrings   -List of Strings , list of strings containing unique identifier

@return                - List of Strings, list of filtered strings with unique identifiers
'''

def stringList_UniqueID_List( listOfStrings ):
    sampleList = []
    #Create a list of ASCII characters to find the sample name from the given string
    for i in range(0, len(listOfStrings)):
        
        #Create a list of ASCII characters from the string
        ascii_list =[ord(c) for c in listOfStrings[i]]
        char_list = list(listOfStrings[i])

        
        #If the first string  does not pass the filter set the sample flag to 0
 #       sampleFlag = 0 
        count = 0 
        # j will be the index referencing the next ASCII character
        for j in range(0, len(ascii_list)):

            #Filter to find a unique combination of characters and ints in sequence
            ###############
            
            # ASCII characters for numbers 0 - 10
            if ascii_list[j] >= 48 and ascii_list[j] <= 57:

                #If a number is encountered increase the counter
                count = count + 1

                # If the count is 6 "This is how many numbers in a row the unique identifier will be"
                if count == 3:
                    # Create a string of the unique identifier
                    sampleList.append( char_list[ j - 2 ] +
                                       char_list[ j - 1 ] + 
                                       char_list[ j ]     + 
                                       char_list[ j + 1 ] + 
                                       char_list[ j + 2 ] + 
                                       char_list[ j + 3 ] )
                    # Stop the search.  The identifier has been located
                    break
            # If the next ASCII character is not a number reset the counter to 0        
            else:
                count = 0
        # If a unique identifier is not located insert string as placeholder so that indexing is not corrupted
        if count == 0 and j == len(ascii_list) - 1 :
                
            sampleList.append(listOfStrings[i])        
                
                
    return sampleList         

















