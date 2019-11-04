# -*- coding: utf-8 -*-
"""
Create a Bokeh Plot of Time Series data


Created on Mon Nov  4 08:15:40 2019

@author: Derek Holsapple

"""

from cleanRawOutput import cleanRawOutput
import pandas as pd
from bokeh.plotting import  output_file, show
from bokeh.models import ColumnDataSource
import bokeh.models as bkm
from bokeh.plotting import figure
from bokeh.io import output_notebook




def findPickleFile(fileID , currentDirectory):

    #Set path
    path = currentDirectory
    
    # Get the file name of each raw data pickle,  the unique identifier is inside this list
    rawfileNames = cleanRawOutput.filesNameList( path )
    
    # Reference the summary frame to pull out the user Input row and display
    summary_df = cleanRawOutput.dataSummaryFrame( path )
    
    #Create a list of unique identifiers for the file string names "See helper functions"
    uniqueID_List = cleanRawOutput.stringList_UniqueID_List(rawfileNames)
    
    booleanSearch = summary_df["Site Identifier Code"].str.find(fileID) 
    for r in range( 0 , len(booleanSearch)):
        if booleanSearch[r] == 0:
            summaryRow_df = summary_df.iloc[r,:]
            break
        
    for i in range(0 , len( rawfileNames ) ):
    
        #If the user input is a match with a raw data file
        if fileID == uniqueID_List[i]:
            # Pull out the raw pickle of the located file name
            raw_df = pd.read_pickle( path + '/Pandas_Pickle_DataFrames/Pickle_Level1/' + rawfileNames[i] )
            
    return raw_df , summaryRow_df




fileID = '010010'
currentDirectory = r'C:\Users\DHOLSAPP\Desktop\XLWings_ModuleTempTool'
htmlString = 'Bokeh_plot'
selector = 'Global horizontal irradiance'
graphTitle = 'Module Temperature(roof_mount_cell_glassback)'





#Access the level_1_df site specific, also collect that sites series data
level_1_df , siteLocation_series = findPickleFile(fileID , currentDirectory)

####BOKEH PLOT########

#Create the html to be exported
output_file('TimeSeries_Module_Temperature_Plot' + htmlString + '.html') 

# Create the tools used for zooming and hovering on the map
tools = "pan,wheel_zoom,box_zoom,reset,previewsave"










# Create a blank figure with labels
p = figure(plot_width = 1200, plot_height = 1200, 
           title = graphTitle,
           x_axis_label = 'Yearly Local Time', y_axis_label = 'Module Temp (C)')



# Bring in all the data to display on plot

#Radius is the size of the circle to be displayed on the map
radiusList = []
for i in range(0, len(level_1_df)):
    #Toggle size of circle
    radiusList.append(2)


radius = radiusList
selector = level_1_df[selector]

localTime = level_1_df['Local Date Time']
universalTime = level_1_df['Universal Date Time']
localSolarTime = level_1_df['Local Solar Time']
hourlyLocalSolarTime = level_1_df['Hourly Local Solar Time']        
        
        




# The Boken map rendering package needs to store data in the ColumnDataFormat
# Store the lat/lon from the Map_pickle.  Formatting for Lat/Lon has been 
# processed prior see "Map_Pickle_Processing.py" file for more details 
# Add other data to create hover labels
source = ColumnDataSource(
    data = dict(
        selector = selector,
        localTime = localTime,
        universalTime = universalTime,
        localSolarTime = localSolarTime,
        hourlyLocalSolarTime = hourlyLocalSolarTime 
        ) )


#circles = p.circle(hourlyLocalSolarTime, selector, size = 5, color = 'red')

circles = p.circle("hourlyLocalSolarTime",
         "selector", 
         source=source , 
         radius= .08 , 
         #fill color will use linear_cmap() to scale the colors of the circles being displayed
         fill_color = 'blue',
         line_color = None,
         # Alpha is the transparency of the circle
          alpha=.90)   






# These are the labels that are displayed when you hover over a spot on the map
#( label , @data), data needs to be inside the ColumnDataSource()
TOOLTIPS = [

("Module Temp","@selector" + " (C)"),
("Local Time","@localTime{%F %H:%M}"),
("Local Solar Time","@localSolarTime{%F %H:%M}"),
("Universal Time","@universalTime{%F %H:%M}"),
("Hourly Local Solar Time","@hourlyLocalSolarTime")
]
#, formatters={"localTime":"datetime"}, mode='vline'

#Create a hover tool that will rinder only the weather stations i.e stations are small black circles
hover_labels = bkm.HoverTool(renderers=[circles],
                     tooltips= TOOLTIPS,formatters={"localTime":"datetime","localSolarTime":"datetime","universalTime":"datetime"},mode='mouse')
#Add the hover tool to the map
p.add_tools(hover_labels)






# Set to output the plot in the notebook
output_notebook()
# Show the plot
show(p)        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        