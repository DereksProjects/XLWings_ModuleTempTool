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

#Take the list of strings and append the pandas df to have the unique IDs
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
                elif rawDataSource == "CWE": 
                    dataSource = "CWEC"
                elif rawDataSource == "IW2":
                    dataSource = "IWEC"

                # Stop the search.  The identifier has been located
                break

            else:
                count = 0

        # If the next ASCII character is not a number reset the counter to 0        
        else:
            count = 0
            
        # If a unique identifier is not located insert string as placeholder so that indexing is not corrupted
        if count == 0 and j == len(ascii_list) - 1 :
                
            dataSource = "UNKNOWN"       
                    
                
    return dataSource   


TMY3_test = "690150TYA.pickle"

CWEC_test = "CAN_AB_BOW_3010730_CWEC.pickle"

IWEC_test = "ZWE_RUSCAPE_678810_IW2.pickle"



print( dataSource( TMY3_test ) )