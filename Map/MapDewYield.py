
import pandas as pd
from bokeh.plotting import  output_file, show
from bokeh.transform import linear_cmap
from bokeh.models import ColumnDataSource
import bokeh.models as bkm
import bokeh.plotting as bkp
from bokeh.models import LogColorMapper, LogTicker, ColorBar


class mapDewYield:

    def outputMapDew(path , mapSelect ):
        '''
        EXECUTION METHOD
        
        outputMapDew()
        
        Method to create a map of the Dew Yield around the world
        This method will use a package called Bokeh that generates a html file 
        containing the map.  User will have thier defualt browser open and display the map
        
        @param path         - String, of the current working directory                                  
        @param mapSelect    - String, string to select what map to generate
                                    ACCEPTABLE STRINGS AS PARAMETERS
                                       - 'dew_yield'
        
        @return void        - Generates a html Bokeh map
        '''    
    
        if mapSelect == 'dew_yield':
            moduleType = 'Sum of Yearly Dew(mmd-1)'
            htmlString = '_yearly_dew'
            colorSelector = "Viridis256"
            #Assign the upper and lower bounds of the map 
    
    
        
        #Create the html to be exported
        output_file('Yearly_Dew_Yield_Map(mmd-1)' + htmlString + '.html')     
        
        
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

        radius = radiusList
        dew = level_1_df[moduleType]
        station = level_1_df['Station name']
        latitude = level_1_df['Site latitude']
        longitude = level_1_df['Site longitude']
        moduleTemp = level_1_df[moduleType]
        uniqueID = level_1_df['Site Identifier Code']
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
                dew = dew,
                Station = station,
                Latitude = latitude,
                Longitude = longitude,
                Module_Temp = moduleTemp,
                uniqueID = uniqueID,
                elevation = elevation
                ) )
    
        p = bkp.figure(width=1500, 
                   height=900, 
                   tools=tools, 
                   title='IWEC, CWEC, and TMY3 of Average Dew Yield (mmd-1)'  ,
                   
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
                 fill_color = linear_cmap('dew', colorSelector, low=0, high=50),
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
        color_mapper = LogColorMapper(palette= colorSelector, low=1, high=50)
        
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
        ("Lat","@Latitude"),
        ("Lon","@Longitude"),
        ("Yearly_Dew_Yield","@dew" + " (mmd-1)"),
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
    
    
    #TESTING ENVIRONMENT
    #path = r'C:\Users\DHOLSAPP\Desktop\Summer_Project\Weather_Database'
    
    #mapSelect = 'dew_yield'
    
    #outputMapDew(path , mapSelect)
















