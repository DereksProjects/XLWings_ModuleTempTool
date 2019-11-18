# -*- coding: utf-8 -*-
"""
Created on Mon Nov 18 09:32:20 2019

Create a driver to generate a map from the processed level_1_dataframe

@author: DHOLSAPP
"""


import pandas as pd
from bokeh.plotting import  output_file, show
from bokeh.transform import linear_cmap
from bokeh.models import ColumnDataSource, LinearColorMapper
import bokeh.models as bkm
import bokeh.plotting as bkp
from bokeh.models import LogTicker, ColorBar


class mapGenerator:

    def mapGenerator(path , mapSelect , htmlString , title, 
                     scaleMin, scaleMax, metric):
        '''
        HELPER FUNCTION
        
        mapGenerator()
        
        Generate a map from the processed level_1_dataframe and diplay as a 
            bokeh map of the earth for each weather station
        
        @param path        - String, of the current working directory                                  
        @param mapSelect   - String, string to select what map to generate
 
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
         'Sum of Yearly Dew(mmd-1)'

        @param htmlString - String, what to name the html 
        @param title      - String, title of the map
        @param scaleMin   - Float,  minimum value of the scale
        @param scaleMax   - Float,  maximum value of the scale        
        @param metric     - String, metric of the value being measured        
        
        @return           -void, Bokeh map as a html
        '''    
        colorSelector = "Viridis256"

        #Create the html to be exported
        output_file(htmlString + '.html')     
        
        # Create the tools used for zooming and hovering on the map
        tools = "pan,wheel_zoom,box_zoom,reset,previewsave"
        
        #Access the .json file to create the map of countries and states
        # The json files will create layers to overlap the data with
        with open(path + "/Map/countries.geojson", "r") as f:
            countries = bkm.GeoJSONDataSource(geojson=f.read())  
        with open(path + "/Map/us-states.json", "r") as f:
            states = bkm.GeoJSONDataSource(geojson=f.read())              
        #Access the processed summary data pickle
        level_1_df = pd.read_pickle(path + "\\Pandas_Pickle_DataFrames\\Pickle_Map\\Pickle_Map.pickle")
        
        #Radius is the size of the circle to be displayed on the map
        radiusList = []
        for i in range(0, len(level_1_df)):
            #Toggle size of circle
            radiusList.append(2)

        radius = radiusList
        selector = level_1_df[mapSelect]
        station = level_1_df['Station name']
        latitude = level_1_df['Site latitude']
        longitude = level_1_df['Site longitude']
        moduleTemp = level_1_df[mapSelect]
        uniqueID = level_1_df['Site Identifier Code']
        dataSource = level_1_df['Data Source']
        elevation = level_1_df['Site elevation (meters)'].astype(float)
    
        # The Boken map rendering package needs to store data in the ColumnDataFormat
        # Store the lat/lon from the Map_pickle.  Formatting for Lat/Lon has been 
        # processed prior see "Map_Pickle_Processing.py" file for more details 
        # Add other data to create hover labels
        source = ColumnDataSource(
            data = dict(
                Lat = latitude,
                Lon = longitude,
                radius = radius,
                selector = selector,
                Station = station,
                Latitude = latitude,
                Longitude = longitude,
                Module_Temp = moduleTemp,
                uniqueID = uniqueID,
                elevation = elevation,
                dataSource = dataSource
                ) )
    
        p = bkp.figure(width=1500, 
                   height=900, 
                   tools=tools, 
                   title = title  ,
                   
                   x_axis_type="mercator",
                   y_axis_type="mercator",
    
                   x_axis_label='Longitude', 
                   y_axis_label='Latitude')
    
        p.x_range = bkm.Range1d(start=-180, end=180)
        p.y_range = bkm.Range1d(start=-90, end=90)
    
    
        #Create the datapoints as overlapping circles
        p.circle("Lon",
                 "Lat", 
                 source= source , 
                 radius="radius" , 
                 #fill color will use linear_cmap() to scale the colors of the circles being displayed
                 fill_color = linear_cmap('selector', colorSelector, low = scaleMin, high = scaleMax),
                 line_color =None,  
                 # Alpha is the transparency of the circle
                 alpha=0.3)
        #Stations will be the black dots displayed on the map
        stations = p.circle("Lon",
                 "Lat", 
                 source=source , 
                 radius= .1 , 
                 #fill color will use linear_cmap() to scale the colors of the circles being displayed
                 fill_color = 'black',
                 line_color = None,
                 # Alpha is the transparency of the circle
                  alpha=.99)   
        
    
        #Create the scale bar to the right of the map
        
        # Create color mapper to make the scale bar on the right of the map
        # palette = color scheme of the mapo
        # low/high sets the scale of the data, use the minimum value and maximum value of the data we are analyzing
        color_mapper = LinearColorMapper(palette= colorSelector, low=scaleMin, high= scaleMax)
        
        # color bar will be scale bar set to the right of the map
        color_bar = ColorBar(color_mapper=color_mapper, ticker=LogTicker(),
                         label_standoff=12, border_line_color=None, location=(0,0))
        # Assign the scale bar to " p " and put it to the right
        p.add_layout(color_bar, 'right')
        
    
        # These are the labels that are displayed when you hover over a spot on the map
        #( label , @data), data needs to be inside the ColumnDataSource()
        TOOLTIPS = [
        ("Station","@Station") ,
        ("Site ID","@uniqueID"),
        ("Data Source", "@dataSource"),
        ("Lat","@Latitude"),
        ("Lon","@Longitude"),
        (htmlString ,"@selector" + " " + metric),
        ("Elevation","@elevation" + " (m)")
        ]
        
        #Create a hover tool that will rinder only the weather stations i.e stations are small black circles
        hover_labels = bkm.HoverTool(renderers=[stations],
                             tooltips= TOOLTIPS )
        #Add the hover tool to the map
        p.add_tools(hover_labels)
        #Overlay the Country and States boarders
        p.patches("xs", "ys", color="white", line_color="black", source=countries , fill_alpha = 0 , line_alpha = 1)
        p.patches("xs", "ys", color="white", line_color="black", source=states , fill_alpha = 0 , line_alpha = 1)
        #Display the plot
        show(p)



    def mapGeneratorDriver(path , mapType):

        '''
        DRIVER FUNCTION
        
        mapGeneratorDriver()
        
        Create a map from the list of variables
        
        @param path        - String, of the current working directory                                  
        @param mapType     - String, string to select what map to generate

            Annual GHI
            Annual DNI
            Annual DHI
            Annual POA Global Irradiance
            Annual POA Direct Irradiance
            Annual POA Diffuse Irradiance
            Annual POA Sky Diffuse Irradiance
            Annual POA Ground Diffuse Irradiance
            Annual Global UV Dose
            Annual UV Dose at Latitude Tilt
            
            Annual Minimum Ambient Temperature
            Annual Average Ambient Temperature
            Annual Maximum Ambient Temperature
            Annual Range Ambient Temperature
            Average of Yearly Water Vapor Pressure
            Sum of Yearly Water Vapor Pressure
            Annual Hours Relative Humidity > 85%
            Sum of Yearly Dew
        '''
        
        if mapType == 'Annual GHI':
            title = 'Annual Global Horizontal Irradiance (GJ/m^-2)'    
            mapSelect = 'Annual Global Horizontal Irradiance (GJ/m^-2)'
            htmlString = 'Annual_Global_Horizontal_Irradiance'    
            scaleMin = 1
            scaleMax = 8
            metric = "(GJ/m^-2)"
            mapGenerator.mapGenerator(path , mapSelect , htmlString , title, 
                                      scaleMin, scaleMax , metric)
            
        elif mapType == 'Annual DNI':
            title = 'Annual Direct Normal Irradiance (GJ/m^-2)'    
            mapSelect = 'Annual Direct Normal Irradiance (GJ/m^-2)'
            htmlString = 'Annual_Direct_Normal_Irradiance'    
            scaleMin = 1
            scaleMax = 10
            metric = "(GJ/m^-2)"
            mapGenerator.mapGenerator(path , mapSelect , htmlString , title, 
                                      scaleMin, scaleMax , metric)
    
        elif mapType == 'Annual DHI':
            title = 'Annual Diffuse Horizontal Irradiance (GJ/m^-2)'    
            mapSelect = 'Annual Diffuse Horizontal Irradiance (GJ/m^-2)'
            htmlString = 'Annual_Diffuse_Horizontal_Irradiance'    
            scaleMin = 1
            scaleMax = 4
            metric = "(GJ/m^-2)"
            mapGenerator.mapGenerator(path , mapSelect , htmlString , title, 
                                      scaleMin, scaleMax , metric)
    
        elif mapType == 'Annual POA Global Irradiance':
            title = 'Annual POA Global Irradiance (GJ/m^-2)'    
            mapSelect = 'Annual POA Global Irradiance (GJ/m^-2)'
            htmlString = 'Annual_POA_Global_Irradiance'    
            scaleMin = 1
            scaleMax = 8
            metric = "(GJ/m^-2)"
            mapGenerator.mapGenerator(path , mapSelect , htmlString , title, 
                                      scaleMin, scaleMax , metric)

        elif mapType == 'Annual POA Direct Irradiance':
            title = 'Annual POA Direct Irradiance (GJ/m^-2)'    
            mapSelect = 'Annual POA Direct Irradiance (GJ/m^-2)'
            htmlString = 'Annual_POA_Direct_Irradiance'    
            scaleMin = 1
            scaleMax = 8
            metric = "(GJ/m^-2)"
            mapGenerator.mapGenerator(path , mapSelect , htmlString , title, 
                                      scaleMin, scaleMax , metric)

        elif mapType == 'Annual POA Diffuse Irradiance':
            title = 'Annual POA Diffuse Irradiance (GJ/m^-2)'    
            mapSelect = 'Annual POA Diffuse Irradiance (GJ/m^-2)'
            htmlString = 'Annual_POA_Diffuse_Irradiance'    
            scaleMin = 1
            scaleMax = 4
            metric = "(GJ/m^-2)"
            mapGenerator.mapGenerator(path , mapSelect , htmlString , title, 
                                      scaleMin, scaleMax , metric)
            
        elif mapType == 'Annual POA Sky Diffuse Irradiance':
            title = 'Annual POA Sky Diffuse Irradiance (GJ/m^-2)'    
            mapSelect = 'Annual POA Sky Diffuse Irradiance (GJ/m^-2)'
            htmlString = 'Annual_POA_Sky_Diffuse_Irradiance'    
            scaleMin = 1
            scaleMax = 4
            metric = "(GJ/m^-2)"
            mapGenerator.mapGenerator(path , mapSelect , htmlString , title, 
                                      scaleMin, scaleMax , metric)            

        elif mapType == 'Annual POA Ground Diffuse Irradiance':
            title = 'Annual POA Ground Diffuse Irradiance (GJ/m^-2)'    
            mapSelect = 'Annual POA Ground Diffuse Irradiance (GJ/m^-2)'
            htmlString = 'Annual_POA_Ground Diffuse_Irradiance'    
            scaleMin = .01
            scaleMax = .40
            metric = "(GJ/m^-2)"
            mapGenerator.mapGenerator(path , mapSelect , htmlString , title, 
                                      scaleMin, scaleMax , metric)            

        elif mapType == 'Annual Global UV Dose':
            title = 'Annual Global UV Dose (MJ/y^-1)'    
            mapSelect = 'Annual Global UV Dose (MJ/y^-1)'
            htmlString = 'Annual_Global UV_Dose'    
            scaleMin = 100
            scaleMax = 400
            metric = "(MJ/y^-1)"
            mapGenerator.mapGenerator(path , mapSelect , htmlString , title, 
                                      scaleMin, scaleMax , metric)            

        elif mapType == 'Annual UV Dose at Latitude Tilt':
            title = 'Annual UV Dose at Latitude Tilt (MJ/y^-1)'    
            mapSelect = 'Annual UV Dose at Latitude Tilt (MJ/y^-1)'
            htmlString = 'Annual_UV_Dose_at_Latitude_Tilt'    
            scaleMin = 100
            scaleMax = 400
            metric = "(MJ/y^-1)"
            mapGenerator.mapGenerator(path , mapSelect , htmlString , title, 
                                      scaleMin, scaleMax , metric)            

        elif mapType == 'Annual Minimum Ambient Temperature':
            title = 'Annual Minimum Ambient Temperature (C)'    
            mapSelect = 'Annual Minimum Ambient Temperature (C)'
            htmlString = 'Annual_Minimum_Ambient_Temperature'    
            scaleMin = -50
            scaleMax = 25
            metric = "(C)"
            mapGenerator.mapGenerator(path , mapSelect , htmlString , title, 
                                      scaleMin, scaleMax , metric) 

        elif mapType == 'Annual Average Ambient Temperature':
            title = 'Annual Average Ambient Temperature (C)'    
            mapSelect = 'Annual Average Ambient Temperature (C)'
            htmlString = 'Annual_Average_Ambient_Temperature'    
            scaleMin = 1
            scaleMax = 30
            metric = "(C)"
            mapGenerator.mapGenerator(path , mapSelect , htmlString , title, 
                                      scaleMin, scaleMax , metric) 

        elif mapType == 'Annual Maximum Ambient Temperature':
            title = 'Annual Maximum Ambient Temperature (C)'    
            mapSelect = 'Annual Maximum Ambient Temperature (C)'
            htmlString = 'Annual_Maximum_Ambient_Temperature'    
            scaleMin = 1
            scaleMax = 50
            metric = "(C)"
            mapGenerator.mapGenerator(path , mapSelect , htmlString , title, 
                                      scaleMin, scaleMax , metric) 

        elif mapType == 'Annual Range Ambient Temperature':
            title = 'Annual Range Ambient Temperature (C)'    
            mapSelect = 'Annual Range Ambient Temperature (C)'
            htmlString = 'Annual_Range_Ambient_Temperature'    
            scaleMin = 1
            scaleMax = 80
            metric = "(C)"
            mapGenerator.mapGenerator(path , mapSelect , htmlString , title, 
                                      scaleMin, scaleMax , metric) 

        elif mapType == 'Average of Yearly Water Vapor Pressure':
            title = 'Average Yearly Water Vapor Pressure (kPa)'    
            mapSelect = 'Average of Yearly Water Vapor Pressure(kPa)'
            htmlString = 'Average_Yearly_Water_Vapor_Pressure_Map'    
            scaleMin = .1
            scaleMax = 3.2
            metric = "(kPa)"
            mapGenerator.mapGenerator(path , mapSelect , htmlString , title, 
                                      scaleMin, scaleMax , metric)

        elif mapType == 'Sum of Yearly Water Vapor Pressure':
            title = 'Sum of Yearly Water Vapor Pressure(kPa)'    
            mapSelect = 'Sum of Yearly Water Vapor Pressure(kPa)'
            htmlString = 'Sum_of_Yearly_Water_Vapor_Pressure'    
            scaleMin = 1000
            scaleMax = 25000
            metric = "(kPa)"
            mapGenerator.mapGenerator(path , mapSelect , htmlString , title, 
                                      scaleMin, scaleMax , metric)

        elif mapType == 'Annual Hours Relative Humidity > 85%':
            title = 'Annual number of Hours Relative Humidity > to 85%'    
            mapSelect = 'Annual number of Hours Relative Humidity > to 85%'
            htmlString = 'Annual_number_of_Hours_Relative_Humidity_greater_85%'    
            scaleMin = 100
            scaleMax = 5000
            metric = "(hours)"
            mapGenerator.mapGenerator(path , mapSelect , htmlString , title, 
                                      scaleMin, scaleMax , metric)

        elif mapType == 'Sum of Yearly Dew':
            title = 'Sum of Yearly Dew(mmd-1)'    
            mapSelect = 'Sum of Yearly Dew(mmd-1)'
            htmlString = 'Sum_of_Yearly_Dew'    
            scaleMin = 1
            scaleMax = 50
            metric = "(mmd-1)"
            mapGenerator.mapGenerator(path , mapSelect , htmlString , title, 
                                      scaleMin, scaleMax , metric)
