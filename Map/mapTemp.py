
'''
Create a data visualization of processed solar module temperatures using the
King Model. Data visualization will be a global map of module temperatures and
associated fixture type

    *FIXTURE TYPES*
    1) open_rack_cell_glassback
    2) roof_mount_cell_glassback
    3) open_rack_cell_polymerback
    4) insulated_back_polymerback
    5) open_rack_polymer_thinfilm_steel
    6) 22x_concentrator_tracker

All fixture types can be represented in the following categories

    1) 98th Percentile module temperature (All 6 fixture types)
    2) Minimum module temperature
    3) Maximum module temperature
    4) Average module temperature

@author Derek Holsapple
'''

import pandas as pd
from bokeh.plotting import  output_file, show
from bokeh.transform import linear_cmap
from bokeh.models import ColumnDataSource, LinearColorMapper
import bokeh.models as bkm
import bokeh.plotting as bkp
from bokeh.models import LogColorMapper, LogTicker, ColorBar



class mapTemp:

    
    # Rerad the pickle containing the Summary dataframe
    def outputMapTemp(path , mapSelect):
        '''
        EXECUTION METHOD
        
        outputMapTemp()
        
        Method to create a map of the Dew Yield around the world.
        This method will use a package called Bokeh that generates a html file 
        containing the map.  User will have thier defualt browser open and display the map
        
        @param path         - String, of the current working directory                                  
        @param mapSelect    - String, string to select what map to generate
                                    ACCEPTABLE STRINGS AS PARAMETERS
                                       - 'open_rack_cell_glassback'
                                       - 'roof_mount_cell_glassback'
                                       - 'open_rack_cell_polymerback'
                                       - 'insulated_back_polymerback'
                                       - 'open_rack_polymer_thinfilm_steel'
                                       - '22x_concentrator_tracker'                               
        
        @return void        - Generates a html Bokeh map
        '''        
        #Select which solar module temperature calculation the user would like to see
        
        ### 98th percentile maps
        if mapSelect == 'open_rack_cell_glassback98th':
            moduleType = 'Annual Average (98th Percentile) Module Temperature__open_rack_cell_glassback (C)'            
            minTemp = 'Annual Minimum Module Temperature__open_rack_cell_glassback (C)'
            maxTemp = 'Annual Maximum Module Temperature__open_rack_cell_glassback (C)'
            avgTemp = 'Annual Average Module Temperature__open_rack_cell_glassback (C)'
            module98 = 'Annual Average (98th Percentile) Module Temperature__open_rack_cell_glassback (C)'                        
            chartHeader = '98th Percentile Module Temperature Open Rack Cell Glass Back (C)'
            htmlString = '_open_rack_cell_glassback'
            colorSelector = 'Spectral6'
            #Assign the upper and lower bounds of the map 
            mapScaleUpper = 100
            mapScaleLower = 20
            
        elif mapSelect == 'roof_mount_cell_glassback98th':
            moduleType = 'Annual Average (98th Percentile) Module Temperature__roof_mount_cell_glassback (C)'            
            minTemp = 'Annual Minimum Module Temperature__roof_mount_cell_glassback (C)'
            maxTemp = 'Annual Maximum Module Temperature__roof_mount_cell_glassback (C)'
            avgTemp = 'Annual Average Module Temperature__roof_mount_cell_glassback (C)'
            module98 = 'Annual Average (98th Percentile) Module Temperature__roof_mount_cell_glassback (C)'                        
            chartHeader = '98th Percentile Module Temperature Roof Mount Cell Glass Back (C)'
            htmlString = '_roof_mount_cell_glassback'
            colorSelector = 'Spectral6'
            #Assign the upper and lower bounds of the map 
            mapScaleUpper = 100
            mapScaleLower = 20
            
        elif mapSelect == 'open_rack_cell_polymerback98th':
            moduleType = 'Annual Average (98th Percentile) Module Temperature__open_rack_cell_polymerback (C)'            
            minTemp = 'Annual Minimum Module Temperature__open_rack_cell_polymerback (C)'
            maxTemp = 'Annual Maximum Module Temperature__open_rack_cell_polymerback (C)'
            avgTemp = 'Annual Average Module Temperature__open_rack_cell_polymerback (C)'
            module98 = 'Annual Average (98th Percentile) Module Temperature__open_rack_cell_polymerback (C)'                        
            chartHeader = '98th Percentile Module Temperature Open Rack Cell Polymer Back (C)'
            htmlString = '_open_rack_cell_polymerback'
            colorSelector = 'Spectral6'
            #Assign the upper and lower bounds of the map 
            mapScaleUpper = 100
            mapScaleLower = 20
            
        elif mapSelect == 'insulated_back_polymerback98th':
            moduleType = 'Annual Average (98th Percentile) Module Temperature__insulated_back_polymerback (C)'            
            minTemp = 'Annual Minimum Module Temperature__insulated_back_polymerback (C)'
            maxTemp = 'Annual Maximum Module Temperature__insulated_back_polymerback (C)'
            avgTemp = 'Annual Average Module Temperature__insulated_back_polymerback (C)'
            module98 = 'Annual Average (98th Percentile) Module Temperature__insulated_back_polymerback (C)'                        
            chartHeader = '98th Percentile Module Temperature Insulated Back Polymer Back (C)'
            htmlString = '_insulated_back_polymerback'
            colorSelector = 'Spectral6'
            #Assign the upper and lower bounds of the map 
            mapScaleUpper = 100
            mapScaleLower = 20
            
        elif mapSelect == 'open_rack_polymer_thinfilm_steel98th':
            moduleType = 'Annual Average (98th Percentile) Module Temperature__open_rack_polymer_thinfilm_steel (C)'            
            minTemp = 'Annual Minimum Module Temperature__open_rack_polymer_thinfilm_steel (C)'
            maxTemp = 'Annual Maximum Module Temperature__open_rack_polymer_thinfilm_steel (C)'
            avgTemp = 'Annual Average Module Temperature__open_rack_polymer_thinfilm_steel (C)'
            module98 = 'Annual Average (98th Percentile) Module Temperature__open_rack_polymer_thinfilm_steel (C)'        
            chartHeader = '98th Percentile Module Temperature Open Rack Polymer Thin Film Steel (C)'
            htmlString = '_open_rack_polymer_thinfilm_steel'
            colorSelector = 'Spectral6' 
            #Assign the upper and lower bounds of the map 
            mapScaleUpper = 100
            mapScaleLower = 20
            
        elif mapSelect == '22x_concentrator_tracker98th':
            moduleType = 'Annual Average (98th Percentile) Module Temperature__22x_concentrator_tracker (C)'            
            minTemp = 'Annual Minimum Module Temperature__22x_concentrator_tracker (C)'
            maxTemp = 'Annual Maximum Module Temperature__22x_concentrator_tracker (C)'
            avgTemp = 'Annual Average Module Temperature__22x_concentrator_tracker (C)'
            module98 = 'Annual Average (98th Percentile) Module Temperature__22x_concentrator_tracker (C)'            
            chartHeader = '98th Percentile Module Temperature 22x Concentrator Tracker (C)'
            htmlString = '_22x_concentrator_tracker'
            colorSelector = 'Spectral6'
            #Assign the upper and lower bounds of the map 
            mapScaleUpper = 100
            mapScaleLower = 20
            
            
        ### Average Temp Maps  
        elif mapSelect == 'AverageModuleTemperature__open_rack_cell_glassback':
            moduleType = 'Annual Average Module Temperature__open_rack_cell_glassback (C)'
            minTemp = 'Annual Minimum Module Temperature__open_rack_cell_glassback (C)'
            maxTemp = 'Annual Maximum Module Temperature__open_rack_cell_glassback (C)'
            avgTemp = 'Annual Average Module Temperature__open_rack_cell_glassback (C)'
            module98 = 'Annual Average (98th Percentile) Module Temperature__open_rack_cell_glassback (C)'
            chartHeader = 'Annual Average Module Temperature Open Rack Cell Glassback (C)'
            htmlString = 'Average_Temp_open_rack_cell_glassback'
            colorSelector = 'Spectral6'
            #Assign the upper and lower bounds of the map 
            mapScaleUpper = 35
            mapScaleLower = 1
            
        elif mapSelect == 'AverageModuleTemperature__roof_mount_cell_glassback':
            moduleType = 'Annual Average Module Temperature__roof_mount_cell_glassback (C)'
            minTemp = 'Annual Minimum Module Temperature__roof_mount_cell_glassback (C)'
            maxTemp = 'Annual Maximum Module Temperature__roof_mount_cell_glassback (C)'
            avgTemp = 'Annual Average Module Temperature__roof_mount_cell_glassback (C)'
            module98 = 'Annual Average (98th Percentile) Module Temperature__roof_mount_cell_glassback (C)'
            chartHeader = 'Annual Average Module Temperature Roof Mount Cell Glassback (C)'
            htmlString = 'Average_Temp_roof_mount_cell_glassback'
            colorSelector = 'Spectral6'
            #Assign the upper and lower bounds of the map 
            mapScaleUpper = 35
            mapScaleLower = 1 
            
        elif mapSelect == 'AverageModuleTemperature__open_rack_cell_polymerback':
            moduleType = 'Annual Average Module Temperature__open_rack_cell_polymerback (C)'
            minTemp = 'Annual Minimum Module Temperature__open_rack_cell_polymerback (C)'
            maxTemp = 'Annual Maximum Module Temperature__open_rack_cell_polymerback (C)'
            avgTemp = 'Annual Average Module Temperature__open_rack_cell_polymerback (C)'
            module98 = 'Annual Average (98th Percentile) Module Temperature__open_rack_cell_polymerback (C)'
            chartHeader = 'Annual Average Module Temperature Open Rack Cell Polymerback (C)'
            htmlString = 'Average_Temp_open_rack_cell_polymerback'
            colorSelector = 'Spectral6'
            #Assign the upper and lower bounds of the map 
            mapScaleUpper = 35
            mapScaleLower = 1    
            
        elif mapSelect == 'AverageModuleTemperature__insulated_back_polymerback':
            moduleType = 'Annual Average Module Temperature__insulated_back_polymerback (C)'
            minTemp = 'Annual Minimum Module Temperature__insulated_back_polymerback (C)'
            maxTemp = 'Annual Maximum Module Temperature__insulated_back_polymerback (C)'
            avgTemp = 'Annual Average Module Temperature__insulated_back_polymerback (C)'
            module98 = 'Annual Average (98th Percentile) Module Temperature__insulated_back_polymerback (C)'
            chartHeader = 'Annual Average Module Temperature Insulated Back Polymerback (C)'
            htmlString = 'Average_Temp_insulated_back_polymerback'
            colorSelector = 'Spectral6'
            #Assign the upper and lower bounds of the map 
            mapScaleUpper = 35
            mapScaleLower = 1   
            
        elif mapSelect == 'AverageModuleTemperature__open_rack_polymer_thinfilm_steel':
            moduleType = 'Annual Average Module Temperature__open_rack_polymer_thinfilm_steel (C)'
            minTemp = 'Annual Minimum Module Temperature__open_rack_polymer_thinfilm_steel (C)'
            maxTemp = 'Annual Maximum Module Temperature__open_rack_polymer_thinfilm_steel (C)'
            avgTemp = 'Annual Average Module Temperature__open_rack_polymer_thinfilm_steel (C)'
            module98 = 'Annual Average (98th Percentile) Module Temperature__open_rack_polymer_thinfilm_steel (C)'
            chartHeader = 'Annual Average Module Temperature Open Rack Polymer Thinfilm Steel (C)'
            htmlString = 'Average_Temp_open_rack_polymer_thinfilm_steel'
            colorSelector = 'Spectral6'
            #Assign the upper and lower bounds of the map 
            mapScaleUpper = 35
            mapScaleLower = 1   
            
        elif mapSelect == 'AverageModuleTemperature__22x_concentrator_tracker':
            moduleType = 'Annual Average Module Temperature__22x_concentrator_tracker (C)'
            minTemp = 'Annual Minimum Module Temperature__22x_concentrator_tracker (C)'
            maxTemp = 'Annual Maximum Module Temperature__22x_concentrator_tracker (C)'
            avgTemp = 'Annual Average Module Temperature__22x_concentrator_tracker (C)'
            module98 = 'Annual Average (98th Percentile) Module Temperature__22x_concentrator_tracker (C)'
            chartHeader = 'Annual Average Module Temperature 22x Concentrator Tracker (C)'
            htmlString = 'Average_Temp_22x_concentrator_tracker'
            colorSelector = 'Spectral6'
            #Assign the upper and lower bounds of the map 
            mapScaleUpper = 35
            mapScaleLower = 1        
        

        
        
        



        #Create the html to be exported
        output_file('Module_Temperature_Map' + htmlString + '.html') 
        
        # Create the tools used for zooming and hovering on the map
        tools = "pan,wheel_zoom,box_zoom,reset,previewsave"
        
        #Access the .json file to create the map of countries and states
        # THe json files will create layers to overlap the data with
        with open(path + "/Map/countries.geojson", "r") as f:
            countries = bkm.GeoJSONDataSource(geojson=f.read())  
        with open(path + "/Map/us-states.json", "r") as f:
            states = bkm.GeoJSONDataSource(geojson=f.read())      
        
        #Access the processed summary data pickle
        level_1_df = pd.read_pickle(path + "\\Pandas_Pickle_DataFrames\\Pickle_Map\\Pickle_Map.pickle")
    
        # Bring in all the data to display on map
        
        #Radius is the size of the circle to be displayed on the map
        radiusList = []
        for i in range(0, len(level_1_df)):
            #Toggle size of circle
            radiusList.append(2)
        lat = level_1_df['N'].astype(float) #Northing and easting if Needed
        lon = level_1_df['E'].astype(float)
        radius = radiusList
        selector = level_1_df[moduleType]
        station = level_1_df['Station name']
        latitude = level_1_df['Site latitude']
        longitude = level_1_df['Site longitude']
        
        uniqueID = level_1_df['Site Identifier Code']
        dataSource = level_1_df['Data Source']
        
        moduleTemp98 = level_1_df[module98]
        moduleMinTemp = level_1_df[minTemp]            
        moduleMaxTemp = level_1_df[maxTemp]
        moduleAvgTemp = level_1_df[avgTemp]
    
    
    
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
                Module_Temp98 = moduleTemp98,
                Module_Min_Temp = moduleMinTemp,
                Module_Avg_Temp = moduleAvgTemp,
                Module_Max_Temp = moduleMaxTemp,
                uniqueID = uniqueID,
                dataSource = dataSource
                ) )
        
        # Create the figure with the map parameters.  This controls the window
        p = bkp.figure(width=1500, 
                   height=900, 
                   tools=tools, 
                   title= chartHeader ,
                   
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
                 fill_color = linear_cmap('selector', colorSelector, low= mapScaleLower, high= mapScaleUpper),
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
        color_mapper = LinearColorMapper(palette= colorSelector,  low= mapScaleLower, high=mapScaleUpper)
        
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
        
        ("Module Minimum Temp","@Module_Min_Temp" + " (C)"),
        ("Module Average Temp","@Module_Avg_Temp" + " (C)"),
        ("Module Maximum Temp","@Module_Max_Temp" + " (C)"),
        ("98 Percentile Module Temp","@Module_Temp98" + " (C)")
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
    
    
    #TESTING ENVIRONMENT
#path = r'C:\Users\DHOLSAPP\Desktop\XLWings_ModuleTempTool'
#mapTemp.outputMapTemp(path , 'open_rack_cell_glassback')
#mapSelect = 'open_rack_cell_glassback'
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
