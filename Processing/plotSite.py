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
from bokeh.models import Legend, LegendItem


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








def individualPlot(currentDirectory , fileID , selector, graphTitle, outputHTML, xAxis, yAxis, toolTipLabel, toolTipMetric):
    
    '''           

    Dry-bulb temperature
    Dew-point temperature
    Relative humidity
    Station pressure
    Wind direction
    Wind speed
    Solar Zenith
    Solar Azimuth
    Solar Elevation
    Dew Yield
    Water Vapor Pressure (kPa) 
    
    Global horizontal irradiance
    Direct normal irradiance
    Diffuse horizontal irradiance
    POA Diffuse
    POA Direct
    POA Global
    POA Ground Diffuse
    POA Sky Diffuse
    
    ####SEPARATRE CELL AND MODULE#######
    Cell Temperature(open_rack_cell_glassback)
    Module Temperature(open_rack_cell_glassback)
    Cell Temperature(roof_mount_cell_glassback)
    Module Temperature(roof_mount_cell_glassback)
    Cell Temperature(open_rack_cell_polymerback)
    Module Temperature(open_rack_cell_polymerback)
    Cell Temperature(insulated_back_polymerback)
    Module Temperature(insulated_back_polymerback)
    Cell Temperature(open_rack_polymer_thinfilm_steel)
    Module Temperature(open_rack_polymer_thinfilm_steel)
    Cell Temperature(22x_concentrator_tracker)
    Module Temperature(22x_concentrator_tracker)   
      
    ''' 
    
    
    #Access the level_1_df site specific, also collect that sites series data
    level_1_df , siteLocation_series = findPickleFile(fileID , currentDirectory)
    
    ####BOKEH PLOT########
    
    #Create the html to be exported
    output_file( outputHTML + '.html' ) 
    
    # Create the tools used for zooming and hovering on the map
#    tools = "pan,wheel_zoom,box_zoom,reset,previewsave"
    
    # Create a blank figure with labels
    p = figure(plot_width = 900, plot_height = 900, 
               title = graphTitle,
               x_axis_label = xAxis, y_axis_label = yAxis)
    
    # Bring in all the data to display on plot
    selector = level_1_df[selector]
    
    localTime = level_1_df['Local Date Time']
    universalTime = level_1_df['Universal Date Time']
    localSolarTime = level_1_df['Local Solar Time']
          
    #Create a Series from 1-8760 (number of hours in a year)
    numberOfHoursPerYear = []        
    for i in range(1,8761):
        numberOfHoursPerYear.append(i)
    numberOfHoursPerYear = pd.Series(numberOfHoursPerYear)            
    
    
    # The Boken map rendering package needs to store data in the ColumnDataFormat
    # Add data to create hover labels
    source = ColumnDataSource(
        data = dict(
            selector = selector,
            localTime = localTime,
            universalTime = universalTime,
            localSolarTime = localSolarTime,
            numberOfHoursPerYear = numberOfHoursPerYear
            ) )
    
    
    circles = p.circle("numberOfHoursPerYear",
             "selector", 
             source=source , 
             radius= 15 , 
             #fill color will use linear_cmap() to scale the colors of the circles being displayed
             fill_color = 'blue',
             line_color = None,
             # Alpha is the transparency of the circle
              alpha=.90)   
    
    
    # These are the labels that are displayed when you hover over a spot on the map
    #( label , @data), data needs to be inside the ColumnDataSource()
    TOOLTIPS = [(toolTipLabel,"@selector" + toolTipMetric),
                ("Local Time","@localTime{%m/%d %H:%M}"),
                ("Local Solar Time","@localSolarTime{%m/%d %H:%M}"),
                ("Universal Time","@universalTime{%m/%d %H:%M}")
                ]
    #, formatters={"localTime":"datetime"}, mode='vline'
    
    #Create a hover tool that will rinder only the weather stations i.e stations are small black circles
    hover_labels = bkm.HoverTool(renderers=[circles],
                         tooltips= TOOLTIPS,formatters={"localTime":"datetime","localSolarTime":"datetime","universalTime":"datetime"},mode='mouse')
    #Add the hover tool to the map
    p.add_tools(hover_labels)
    
    #Add site data to the Legend
    legend = Legend(items=[
        LegendItem(label="Station Name: " + siteLocation_series.iloc[1], index=0),
        LegendItem(label="Site ID Code: "+ siteLocation_series.iloc[0], index=0),
        LegendItem(label="Country: "+ siteLocation_series.iloc[7], index=0),
        LegendItem(label="Latitude: "+ str(siteLocation_series.iloc[4]), index=1),
        LegendItem(label="Longitude: "+ str(siteLocation_series.iloc[5]), index=1),
    ],location = "top_left")
    
    #p.legend.location = "bottom_left"
    
    p.add_layout(legend)
    
    
    # Show the plot
    show(p)        
            
    
fileID = '570830'
currentDirectory = r'C:\Users\DHOLSAPP\Desktop\XLWings_ModuleTempTool'
selector = 'POA Diffuse'
graphTitle = 'Module Temperature(roof_mount_cell_glassback) (C)'
outputHTML = 'HourlyPlotModuleTemp(roof_mount_cell_glassback)'
xAxis = 'Hours in a Year'
yAxis = 'Module Temperature (C)'
toolTipLabel = 'Module Temp'
toolTipMetric = ' (C)'

            
individualPlot(currentDirectory , fileID , selector, graphTitle, outputHTML, xAxis, yAxis, toolTipLabel, toolTipMetric)            
            
      
        
        
        
        
        
        
        
        