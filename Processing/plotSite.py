# -*- coding: utf-8 -*-
"""
Create a Bokeh Plot of Individual site locations (4,053 locations).  Y-Axis
will be selected data columns found in the processed site location .pickle file.
X-axis will be the number of hours in a year.  
Bokeh plot will have hover features displaying information about each 
specific datapoint.

Created on Mon Nov  4 08:15:40 2019

@author: Derek Holsapple

"""

from Processing.cleanRawOutput import cleanRawOutput
import pandas as pd
from bokeh.plotting import  output_file, show
from bokeh.models import ColumnDataSource
import bokeh.models as bkm
from bokeh.plotting import figure
from bokeh.models import Legend, LegendItem


class plotSite:
    
    def findPickleFile(fileID , currentDirectory):
        '''
        HELPER FUNCTION
        
        findPickleFile()
        
        @param currentDirectory       -String, where the excel file is located       
        @param fileID                 -String, 6 digit Unique ID of site 
                                                    specific location

        @return raw_df, summaryRow_df -Series, Site geographic site location data
                                       -Dataframe, Site location hourly data
        '''
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
        individualPlot()
        
        Create a Bokeh Plot from the processed_level_1 pickles from individual 
        site locations.  Choose which column of the data to be displayed on the 
        y-axis. X-axis will be the number of hours in a year (8760)
        
        @param currentDirectory    - String, where the excel file is located 
        @param fileID              - String, unique ID of site specific location
                                            Currently 4,053 different locations                                                        
        @param selector            - String, column name of the level_1_dataframe 
        @param graphTitle          - String, title of the graph to be rendered 
        @param outputHTML          - String, html of the graph to be rendered
        @param xAxis               - String, x-axis of the graph to be rendered
        @param yAxis               - String, y-axis of the graph to be rendered 
        @param toolTipLabel        - String, hover label of individual datapoint
                                            of the graph to be rendered 
        @param toolTipMetric       - String, title of the graph to be rendered
            
        @return void                - Void  , Renders a data plot of a individual 
                                                site with corrisponding selector          
        ''' 

        #Access the level_1_df site specific, also collect that sites series data
        level_1_df , siteLocation_series = plotSite.findPickleFile(fileID , currentDirectory)
        
        ####BOKEH PLOT########
        
        #Create the html to be exported
        output_file( outputHTML + '.html' ) 
        
        
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
                
    
    
    def xLWingsInterfacePlot( currentDirectory , fileID , selector ): 
        '''
        xLWingsInterfacePlot()
        
        Interface to output custom plots.
        
        @param currentDirectory    - String, where the excel file is located 
                                           (passed as an argument from EXCEL using UDF)
        @param fileID              - String, unique ID of site specific location
                                            Currently 4,053 different locations
                                                                     
        @param selector            - String, select what type data to plot
        
                        ##### selector string options #####
                        
                        DryBulbTemperature
                        DewPointTemperature                                               
                        RelativeHumidity
                        StationPressure
                        WindDirection
                        WindSpeed
                        SolarZenith
                        SolarAzimuth
                        SolarElevation
                        DewYield
                        WaterVaporPressure
                        GlobalHorizontalIrradiance
                        DirectNormalIrradiance
                        DiffuseHorizontalIrradiance
                        AngleOfIncidence
                        POADiffuse
                        POADirect
                        POAGlobal
                        POAGroundDiffuse
                        POASkyDiffuse
                        CellTemperatureOpenRackCellGlassback
                        CellTemperatureRoofMountCellGlassback
                        CellTemperatureOpenRackCellPolymerback
                        CellTemperatureInsulatedBackPolymerback
                        CellTemperatureOpenRackPolymerThinfilmSteel
                        CellTemperature22xConcentratorTracker
                        ModuleTemperatureOpenRackCellGlassback
                        ModuleTemperatureRoofMountCellGlassback
                        ModuleTemperatureOpenRackCellPolymerback
                        ModuleTemperatureInsulatedBackPolymerback
                        ModuleTemperatureOpenRackPolymerThinfilmSteel
                        ModuleTemperature22xConcentratorTracker

            
        @return void    - Void  , Renders a data plot of a individual site with corrisponding selector
                    
        '''
        if selector == 'DryBulbTemperature':
            
            selector = 'Dry-bulb temperature(C)'
            graphTitle = 'Dry-Bulb Temperature (C)'
            outputHTML = 'Dry_Bulb_Temp'
            xAxis = 'Hours in a Year'
            yAxis = 'Dry-Bulb Temperature (C)'
            toolTipLabel = 'Dry-Bulb Temp'
            toolTipMetric = ' (C)'
            
            plotSite.individualPlot(currentDirectory , 
                                    fileID , 
                                    selector, 
                                    graphTitle, 
                                    outputHTML, 
                                    xAxis, 
                                    yAxis, 
                                    toolTipLabel, 
                                    toolTipMetric)
            
        elif selector == 'DewPointTemperature':
            
            selector = 'Dew-point temperature(C)'
            graphTitle = 'Dew Point Temperature (C)'
            outputHTML = 'Dew_Point_Temp'
            xAxis = 'Hours in a Year'
            yAxis = 'Dew Point Temperature (C)'
            toolTipLabel = 'Dew Point Temp'
            toolTipMetric = ' (C)'
            
            plotSite.individualPlot(currentDirectory , 
                                    fileID , 
                                    selector, 
                                    graphTitle, 
                                    outputHTML, 
                                    xAxis, 
                                    yAxis, 
                                    toolTipLabel, 
                                    toolTipMetric)
            
        elif selector == 'Relative humidity':
            
            selector = 'Relative humidity(%)'
            graphTitle = 'Relative Humidity %'
            outputHTML = 'Relative_Humidity'
            xAxis = 'Hours in a Year'
            yAxis = 'Relative Humidity %'
            toolTipLabel = 'Relative Humidity'
            toolTipMetric = ' %'
            
            plotSite.individualPlot(currentDirectory , 
                                    fileID , 
                                    selector, 
                                    graphTitle, 
                                    outputHTML, 
                                    xAxis, 
                                    yAxis, 
                                    toolTipLabel, 
                                    toolTipMetric)
            
        elif selector == 'StationPressure':
            
            selector = 'Station pressure(mbar)'
            graphTitle = 'Station Pressure'
            outputHTML = 'Station_Pressure'
            xAxis = 'Hours in a Year'
            yAxis = 'Station Pressure'
            toolTipLabel = 'Station Pressure'
            toolTipMetric = ' (pressure need to add metric)'
            
            plotSite.individualPlot(currentDirectory , 
                                    fileID , 
                                    selector, 
                                    graphTitle, 
                                    outputHTML, 
                                    xAxis, 
                                    yAxis, 
                                    toolTipLabel, 
                                    toolTipMetric)
            
        elif selector == 'WindDirection':
            
            selector = 'Wind direction(degrees)'
            graphTitle = 'Wind Direction (Degrees)'
            outputHTML = 'Wind_Direction'
            xAxis = 'Hours in a Year'
            yAxis = 'Wind Direction'
            toolTipLabel = 'Wind Direction'
            toolTipMetric = ' (degrees)'
            
            plotSite.individualPlot(currentDirectory , 
                                    fileID , 
                                    selector, 
                                    graphTitle, 
                                    outputHTML, 
                                    xAxis, 
                                    yAxis, 
                                    toolTipLabel, 
                                    toolTipMetric)
            
        elif selector == 'WindSpeed':
            
            selector = 'Wind speed(m/s)'
            graphTitle = 'Wind Speed'
            outputHTML = 'Wind_Speed'
            xAxis = 'Hours in a Year'
            yAxis = 'Wind Speed'
            toolTipLabel = 'Wind Speed'
            toolTipMetric = ' (Need to add metric)'
            
            plotSite.individualPlot(currentDirectory , 
                                    fileID , 
                                    selector, 
                                    graphTitle, 
                                    outputHTML, 
                                    xAxis, 
                                    yAxis, 
                                    toolTipLabel, 
                                    toolTipMetric)
            
        elif selector == 'SolarZenith':
            
            selector = 'Solar Zenith(degrees)'
            graphTitle = 'Solar Zenith (Degrees)'
            outputHTML = 'Solar_Zenith'
            xAxis = 'Hours in a Year'
            yAxis = 'Solar Zenith (Degrees)'
            toolTipLabel = 'Solar Zenith'
            toolTipMetric = ' (Degrees)'
            
            plotSite.individualPlot(currentDirectory , 
                                    fileID , 
                                    selector, 
                                    graphTitle, 
                                    outputHTML, 
                                    xAxis, 
                                    yAxis, 
                                    toolTipLabel, 
                                    toolTipMetric)
            
        elif selector == 'SolarAzimuth':
            
            selector = 'Solar Azimuth(degrees)'
            graphTitle = 'Solar Azimuth (Degrees)'
            outputHTML = 'Solar_Azimuth'
            xAxis = 'Hours in a Year'
            yAxis = 'Solar Azimuth (Degrees)'
            toolTipLabel = 'Solar Azimuth'
            toolTipMetric = ' (Degrees)'
            
            plotSite.individualPlot(currentDirectory , 
                                    fileID , 
                                    selector, 
                                    graphTitle, 
                                    outputHTML, 
                                    xAxis, 
                                    yAxis, 
                                    toolTipLabel, 
                                    toolTipMetric)
            
        elif selector == 'SolarElevation':
            
            selector = 'Solar Elevation(degrees)'
            graphTitle = 'Solar Elevation (Degrees)'
            outputHTML = 'Solar_Elevation'
            xAxis = 'Hours in a Year'
            yAxis = 'Solar Elevation (Degrees)'
            toolTipLabel = 'Solar Elevation'
            toolTipMetric = ' (Degrees)'
            
            plotSite.individualPlot(currentDirectory , 
                                    fileID , 
                                    selector, 
                                    graphTitle, 
                                    outputHTML, 
                                    xAxis, 
                                    yAxis, 
                                    toolTipLabel, 
                                    toolTipMetric)
            
        elif selector == 'DewYield':
            
            selector = 'Dew Yield(mmd-1)'
            graphTitle = 'Dew Yield (mmd-1)'
            outputHTML = 'Dew_Yield'
            xAxis = 'Hours in a Year'
            yAxis = 'Dew Yield (mmd-1)'
            toolTipLabel = 'Dew Yield'
            toolTipMetric = ' (mmd-1)'
            
            plotSite.individualPlot(currentDirectory , 
                                    fileID , 
                                    selector, 
                                    graphTitle, 
                                    outputHTML, 
                                    xAxis, 
                                    yAxis, 
                                    toolTipLabel, 
                                    toolTipMetric)
            
        elif selector == 'WaterVaporPressure':
            
            selector = 'Water Vapor Pressure (kPa)'
            graphTitle = 'Water Vapor Pressure (kPa)'
            outputHTML = 'Water_Vapor_Pressure'
            xAxis = 'Hours in a Year'
            yAxis = 'Water Vapor Pressure (kPa)'
            toolTipLabel = 'Water Vapor Pressure'
            toolTipMetric = ' (kPa)'
            
            plotSite.individualPlot(currentDirectory , 
                                    fileID , 
                                    selector, 
                                    graphTitle, 
                                    outputHTML, 
                                    xAxis, 
                                    yAxis, 
                                    toolTipLabel, 
                                    toolTipMetric)
       
        elif selector == 'GlobalHorizontalIrradiance':
            
            selector = 'Global horizontal irradiance(W/m^2)'
            graphTitle = 'Global Horizontal Irradiance(W/m^2)'
            outputHTML = 'Global_horizontal_irradiance'
            xAxis = 'Hours in a Year'
            yAxis = 'Global Horizontal Irradiance(W/m^2)'
            toolTipLabel = 'GHI'
            toolTipMetric = ' (W/m^2)'
            
            plotSite.individualPlot(currentDirectory , 
                                    fileID , 
                                    selector, 
                                    graphTitle, 
                                    outputHTML, 
                                    xAxis, 
                                    yAxis, 
                                    toolTipLabel, 
                                    toolTipMetric)
    
        elif selector == 'DirectNormalIrradiance':
            
            selector = 'Direct normal irradiance(W/m^2)'
            graphTitle = 'Direct Normal Irradiance (W/m^2)'
            outputHTML = 'Direct_Normal_Irradiance'
            xAxis = 'Hours in a Year'
            yAxis = 'Direct Normal Irradiance (W/m^2)'
            toolTipLabel = 'DNI'
            toolTipMetric = ' (W/m^2)'
            
            plotSite.individualPlot(currentDirectory , 
                                    fileID , 
                                    selector, 
                                    graphTitle, 
                                    outputHTML, 
                                    xAxis, 
                                    yAxis, 
                                    toolTipLabel, 
                                    toolTipMetric)
            
         
        elif selector == 'DiffuseHorizontalIrradiance':
            
            selector = 'Diffuse horizontal irradiance(W/m^2)'
            graphTitle = 'Diffuse Horizontal Irradiance (W/m^2)'
            outputHTML = 'Diffuse_Horizontal_Irradiance'
            xAxis = 'Hours in a Year'
            yAxis = 'Diffuse Horizontal Irradiance (W/m^2)'
            toolTipLabel = 'DHI'
            toolTipMetric = ' (W/m^2)'
            
            plotSite.individualPlot(currentDirectory , 
                                    fileID , 
                                    selector, 
                                    graphTitle, 
                                    outputHTML, 
                                    xAxis, 
                                    yAxis, 
                                    toolTipLabel, 
                                    toolTipMetric)
            
          
        elif selector == 'AngleOfIncidence':
            
            selector = 'Angle of incidence(degrees)'
            graphTitle = 'Angle Of Incidence (degrees)'
            outputHTML = 'Angle_Of_Incidence'
            xAxis = 'Hours in a Year'
            yAxis = 'Angle Of Incidence (degrees)'
            toolTipLabel = 'AOI'
            toolTipMetric = ' (degrees)'
            
            plotSite.individualPlot(currentDirectory , 
                                    fileID , 
                                    selector, 
                                    graphTitle, 
                                    outputHTML, 
                                    xAxis, 
                                    yAxis, 
                                    toolTipLabel, 
                                    toolTipMetric)
        elif selector == 'POADiffuse':
            
            selector = 'POA Diffuse(W/m^2)'
            graphTitle = 'Plane Of Array Diffuse (W/m^2)'
            outputHTML = 'Plane_Of_Array_Diffuse'
            xAxis = 'Hours in a Year'
            yAxis = 'Plane Of Array Diffuse (W/m^2)'
            toolTipLabel = 'POA_Diffuse'
            toolTipMetric = ' (W/m^2)'
            
            plotSite.individualPlot(currentDirectory , 
                                    fileID , 
                                    selector, 
                                    graphTitle, 
                                    outputHTML, 
                                    xAxis, 
                                    yAxis, 
                                    toolTipLabel, 
                                    toolTipMetric)
            
         
        elif selector == 'POADirect':
            
            selector = 'POA Direct(W/m^2)'
            graphTitle = 'Plane Of Array Direct (W/m^2)'
            outputHTML = 'POA_Direct'
            xAxis = 'Hours in a Year'
            yAxis = 'Plane Of Array Direct (W/m^2)'
            toolTipLabel = 'POA Direct'
            toolTipMetric = ' (W/m^2)'
            
            plotSite.individualPlot(currentDirectory , 
                                    fileID , 
                                    selector, 
                                    graphTitle, 
                                    outputHTML, 
                                    xAxis, 
                                    yAxis, 
                                    toolTipLabel, 
                                    toolTipMetric)
        elif selector == 'POAGlobal':
            
            selector = 'POA Global(W/m^2)'
            graphTitle = 'Plane Of Array Global (W/m^2)'
            outputHTML = 'POA_Global'
            xAxis = 'Hours in a Year'
            yAxis = 'Plane Of Array Global (W/m^2)'
            toolTipLabel = 'POA Global'
            toolTipMetric = ' (W/m^2)'
            
            plotSite.individualPlot(currentDirectory , 
                                    fileID , 
                                    selector, 
                                    graphTitle, 
                                    outputHTML, 
                                    xAxis, 
                                    yAxis, 
                                    toolTipLabel, 
                                    toolTipMetric)
        elif selector == 'POAGroundDiffuse':
            
            selector = 'POA Ground Diffuse(W/m^2)'
            graphTitle = 'Plane Of Array Ground Diffuse (W/m^2)'
            outputHTML = 'POA_Ground_Diffuse'
            xAxis = 'Hours in a Year'
            yAxis = 'Plane Of Array Ground Diffuse (W/m^2)'
            toolTipLabel = 'POA Ground Diffuse'
            toolTipMetric = ' (W/m^2)'
            
            plotSite.individualPlot(currentDirectory , 
                                    fileID , 
                                    selector, 
                                    graphTitle, 
                                    outputHTML, 
                                    xAxis, 
                                    yAxis, 
                                    toolTipLabel, 
                                    toolTipMetric)
        elif selector == 'POASkyDiffuse':
            
            selector = 'POA Sky Diffuse(W/m^2)'
            graphTitle = 'Plane Of Array Sky Diffuse (W/m^2)'
            outputHTML = 'POA_Sky_Diffuse'
            xAxis = 'Hours in a Year'
            yAxis = 'Plane Of Array Sky Diffuse (W/m^2)'
            toolTipLabel = 'Water Vapor Pressure'
            toolTipMetric = ' (W/m^2)'
            
            plotSite.individualPlot(currentDirectory , 
                                    fileID , 
                                    selector, 
                                    graphTitle, 
                                    outputHTML, 
                                    xAxis, 
                                    yAxis, 
                                    toolTipLabel, 
                                    toolTipMetric)        
    
        elif selector == 'CellTemperatureOpenRackCellGlassback':
            
            selector = 'Cell Temperature(open_rack_cell_glassback)(C)'
            graphTitle = 'Cell Temperature(open_rack_cell_glassback) (C)'
            outputHTML = 'Cell Temperature_open_rack_cell_glassback'
            xAxis = 'Hours in a Year'
            yAxis = 'Cell Temperature(open_rack_cell_glassback) (C)'
            toolTipLabel = 'Cell Temp'
            toolTipMetric = ' (C)'
            
            plotSite.individualPlot(currentDirectory , 
                                    fileID , 
                                    selector, 
                                    graphTitle, 
                                    outputHTML, 
                                    xAxis, 
                                    yAxis, 
                                    toolTipLabel, 
                                    toolTipMetric)      
        elif selector == 'CellTemperatureRoofMountCellGlassback':
            
            selector = 'Cell Temperature(roof_mount_cell_glassback)(C)'
            graphTitle = 'Cell Temperature(roof_mount_cell_glassback) (C)'
            outputHTML = 'Cell Temperature_roof_mount_cell_glassback'
            xAxis = 'Hours in a Year'
            yAxis = 'Cell Temperature(roof_mount_cell_glassback) (C)'
            toolTipLabel = 'Cell Temp'
            toolTipMetric = ' (C)'
            
            plotSite.individualPlot(currentDirectory , 
                                    fileID , 
                                    selector, 
                                    graphTitle, 
                                    outputHTML, 
                                    xAxis, 
                                    yAxis, 
                                    toolTipLabel, 
                                    toolTipMetric)      
        elif selector == 'CellTemperatureOpenRackCellPolymerback':
            
            selector = 'Cell Temperature(open_rack_cell_polymerback)(C)'
            graphTitle = 'Cell Temperature(open_rack_cell_polymerback) (C)'
            outputHTML = 'Cell Temperature_open_rack_cell_polymerback'
            xAxis = 'Hours in a Year'
            yAxis = 'Cell Temperature(open_rack_cell_polymerback) (C)'
            toolTipLabel = 'Cell Temp'
            toolTipMetric = ' (C)'
            
            plotSite.individualPlot(currentDirectory , 
                                    fileID , 
                                    selector, 
                                    graphTitle, 
                                    outputHTML, 
                                    xAxis, 
                                    yAxis, 
                                    toolTipLabel, 
                                    toolTipMetric)      
        elif selector == 'CellTemperatureInsulatedBackPolymerback':
            
            selector = 'Cell Temperature(insulated_back_polymerback)(C)'
            graphTitle = 'Cell Temperature(insulated_back_polymerback) (C)'
            outputHTML = 'Cell Temperature_insulated_back_polymerback'
            xAxis = 'Hours in a Year'
            yAxis = 'Cell Temperature(insulated_back_polymerback) (C)'
            toolTipLabel = 'Cell Temp'
            toolTipMetric = ' (C)'
            
            plotSite.individualPlot(currentDirectory , 
                                    fileID , 
                                    selector, 
                                    graphTitle, 
                                    outputHTML, 
                                    xAxis, 
                                    yAxis, 
                                    toolTipLabel, 
                                    toolTipMetric)      
        elif selector == 'CellTemperatureOpenRackPolymerThinfilmSteel':
            
            selector = 'Cell Temperature(open_rack_polymer_thinfilm_steel)(C)'
            graphTitle = 'Cell Temperature(open_rack_polymer_thinfilm_steel) (C)'
            outputHTML = 'Cell Temperature_open_rack_polymer_thinfilm_steel'
            xAxis = 'Hours in a Year'
            yAxis = 'Cell Temperature(open_rack_polymer_thinfilm_steel) (C)'
            toolTipLabel = 'Cell Temp'
            toolTipMetric = ' (C)'
            
            plotSite.individualPlot(currentDirectory , 
                                    fileID , 
                                    selector, 
                                    graphTitle, 
                                    outputHTML, 
                                    xAxis, 
                                    yAxis, 
                                    toolTipLabel, 
                                    toolTipMetric)      
        elif selector == 'CellTemperature22xConcentratorTracker':
            
            selector = 'Cell Temperature(22x_concentrator_tracker)(C)'
            graphTitle = 'Cell Temperature(22x_concentrator_tracker) (C)'
            outputHTML = 'Cell Temperature_22x_concentrator_tracker'
            xAxis = 'Hours in a Year'
            yAxis = 'Cell Temperature(22x_concentrator_tracker) (C)'
            toolTipLabel = 'Cell Temp'
            toolTipMetric = ' (C)'
            
            plotSite.individualPlot(currentDirectory , 
                                    fileID , 
                                    selector, 
                                    graphTitle, 
                                    outputHTML, 
                                    xAxis, 
                                    yAxis, 
                                    toolTipLabel, 
                                    toolTipMetric)      
    
        elif selector == 'ModuleTemperatureOpenRackCellGlassback':
            
            selector = 'Module Temperature(open_rack_cell_glassback)(C)'
            graphTitle = 'Module Temperature(open_rack_cell_glassback) (C)'
            outputHTML = 'Module Temperature_open_rack_cell_glassback'
            xAxis = 'Hours in a Year'
            yAxis = 'Module Temperature(open_rack_cell_glassback) (C)'
            toolTipLabel = 'Module Temp'
            toolTipMetric = ' (C)'
            
            plotSite.individualPlot(currentDirectory , 
                                    fileID , 
                                    selector, 
                                    graphTitle, 
                                    outputHTML, 
                                    xAxis, 
                                    yAxis, 
                                    toolTipLabel, 
                                    toolTipMetric)      
        elif selector == 'ModuleTemperatureRoofMountCellGlassback':
            
            selector = 'Module Temperature(roof_mount_cell_glassback)(C)'
            graphTitle = 'Module Temperature(roof_mount_cell_glassback) (C)'
            outputHTML = 'Module Temperature_roof_mount_cell_glassback'
            xAxis = 'Hours in a Year'
            yAxis = 'Module Temperature(roof_mount_cell_glassback) (C)'
            toolTipLabel = 'Module Temp'
            toolTipMetric = ' (C)'
            
            plotSite.individualPlot(currentDirectory , 
                                    fileID , 
                                    selector, 
                                    graphTitle, 
                                    outputHTML, 
                                    xAxis, 
                                    yAxis, 
                                    toolTipLabel, 
                                    toolTipMetric)      
        elif selector == 'ModuleTemperatureOpenRackCellPolymerback':
            
            selector = 'Module Temperature(open_rack_cell_polymerback)(C)'
            graphTitle = 'Module Temperature(open_rack_cell_polymerback) (C)'
            outputHTML = 'Module Temperature_open_rack_cell_polymerback'
            xAxis = 'Hours in a Year'
            yAxis = 'Module Temperature(open_rack_cell_polymerback) (C)'
            toolTipLabel = 'Module Temp'
            toolTipMetric = ' (C)'
            
            plotSite.individualPlot(currentDirectory , 
                                    fileID , 
                                    selector, 
                                    graphTitle, 
                                    outputHTML, 
                                    xAxis, 
                                    yAxis, 
                                    toolTipLabel, 
                                    toolTipMetric)      
        elif selector == 'ModuleTemperatureInsulatedBackPolymerback':
            
            selector = 'Module Temperature(insulated_back_polymerback)(C)'
            graphTitle = 'Module Temperature(insulated_back_polymerback) (C)'
            outputHTML = 'Module Temperature_insulated_back_polymerback'
            xAxis = 'Hours in a Year'
            yAxis = 'Module Temperature(insulated_back_polymerback) (C)'
            toolTipLabel = 'Module Temp'
            toolTipMetric = ' (C)'
            
            plotSite.individualPlot(currentDirectory , 
                                    fileID , 
                                    selector, 
                                    graphTitle, 
                                    outputHTML, 
                                    xAxis, 
                                    yAxis, 
                                    toolTipLabel, 
                                    toolTipMetric)      
        elif selector == 'ModuleTemperatureOpenRackPolymerThinfilmSteel':
            
            selector = 'Module Temperature(open_rack_polymer_thinfilm_steel)(C)'
            graphTitle = 'Module Temperature(open_rack_polymer_thinfilm_steel) (C)'
            outputHTML = 'Module Temperature_open_rack_polymer_thinfilm_steel'
            xAxis = 'Hours in a Year'
            yAxis = 'Module Temperature(open_rack_polymer_thinfilm_steel) (C)'
            toolTipLabel = 'Module Temp'
            toolTipMetric = ' (C)'
            
            plotSite.individualPlot(currentDirectory , 
                                    fileID , 
                                    selector, 
                                    graphTitle, 
                                    outputHTML, 
                                    xAxis, 
                                    yAxis, 
                                    toolTipLabel, 
                                    toolTipMetric)      
        elif selector == 'ModuleTemperature22xConcentratorTracker':
            
            selector = 'Module Temperature(22x_concentrator_tracker)(C)'
            graphTitle = 'Module Temperature(22x_concentrator_tracker) (C)'
            outputHTML = 'Module Temperature_22x_concentrator_tracker'
            xAxis = 'Hours in a Year'
            yAxis = 'Module Temperature(22x_concentrator_tracker) (C)'
            toolTipLabel = 'Module Temp'
            toolTipMetric = ' (C)'
            
            plotSite.individualPlot(currentDirectory , 
                                    fileID , 
                                    selector, 
                                    graphTitle, 
                                    outputHTML, 
                                    xAxis, 
                                    yAxis, 
                                    toolTipLabel, 
                                    toolTipMetric)      
            
