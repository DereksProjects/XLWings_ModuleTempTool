# -*- coding: utf-8 -*-
"""
Created on Tue May 14 15:33:51 2019

This program will access zipped files in a directory and subdirectories. 
It will extract the files and save them into one directory

@author: Derek Holsapple
"""

# importing required modules 
import zipfile
import os
import shutil

'''
Execution Method
extractAllZip_Files()

Given a root directory the method will extract all files in sub-directories
and place them in a destination directory

@param path        - String, the path of where you want the program to start unzipping files
                        i.e. the program will extract every sub directory beyond this path

@return void       - Program will store extracted files into the Python_RawData_Combined directory

'''

def extractAllZip_Files( path ):
    
  #  path = r'C:\Users\DHOLSAPP\Desktop\Summer_Project\International Weather for Energy Calculations CD_files\IWforECalc\IWEC2 Data Files'
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
    
    # Unzip all the files and put them into the directory  
    for i in range(0 , len( zippedFiles ) ):
        with zipfile.ZipFile( zippedFiles[i] ,"r") as zip_ref:
            # Directory to put files into
            zip_ref.extractall(path + '\Python_RawData_Combined')


path = r'C:\Users\DHOLSAPP\Desktop\Summer_Project\Python'
#destination = r"C:\Users\DHOLSAPP\Desktop\Test"    

extractAllZip_Files( path )    


'''
Execution Method
extractAllZip_Files()

Given a root directory the method will extract all files in sub-directories
and place them in a destination directory

@param path        - String, the path of where you want the program to start unzipping files
                        i.e. the program will extract every sub directory beyond this path

@return void       - Program will store extracted files into the Python_RawData_Combined directory

'''
#############################################################################

def extractAllCSV_Files( path  ):
    
  #  path = r'C:\Users\DHOLSAPP\Desktop\Summer_Project\International Weather for Energy Calculations CD_files\IWforECalc\IWEC2 Data Files'
    cSV_Files = []
    # Use os walk to cycle through all directories and pull out .zip files
    for dirpath, subdirs, files in os.walk(path + '\RawData'):
        for x in files:
            if x.endswith(".csv"):
                #Join the full path to the isolated folder, add to the zipped files list
                # Note: os.path is referencing a method not the raw path argument
                cSV_Files.append(os.path.join(dirpath, x))
                
            elif x.endswith(".CSV"):
                #Join the full path to the isolated folder, add to the zipped files list
                # Note: os.path is referencing a method not the raw path argument
                cSV_Files.append(os.path.join(dirpath, x))                
    
    # Unzip all the files and put them into the directory  
    for i in range(0 , len( cSV_Files ) ):
        
        shutil.copy(cSV_Files[i], path + '\Python_RawData_Combined')


#path = r'C:\Users\DHOLSAPP\Desktop\Summer_Project\Python\RawData'
#path = r'C:\Users\DHOLSAPP\Desktop\Summer_Project\Python'
   

#extractAllCSV_Files( path  )    



























