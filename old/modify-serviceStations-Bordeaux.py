import geopandas as gpd
from shapely.geometry import Polygon, Point, MultiPolygon, GeometryCollection, LineString, MultiPoint
import pandas as pd
from shapely.wkt import loads
import math
import myBib as my

def convert_geometries_to_points(geom):
    if isinstance(geom, Polygon):
        return geom.centroid
    elif isinstance(geom, MultiPolygon):
        # If it's a MultiPolygon, calculate the centroid of each polygon and return as a MultiPoint
        centroids = [polygon.centroid for polygon in geom]
        return MultiPoint(centroids)
    elif isinstance(geom, Point):
        return geom
    elif isinstance(geom, GeometryCollection):
        # Handle GeometryCollection by recursively converting each geometry within it
        new_geometries = [convert_geometries_to_points(sub_geom) for sub_geom in geom.geoms]
        return GeometryCollection(new_geometries)
    else:
        return None  # Skip unknown geometry types
    
#Convert Polygons to Points by calculating the average point of each Polygon.
def convert_polygons_to_points(gdf):
    """
    Convert Polygons to Points by calculating the average point of each Polygon.

    Args:
        gdf (gpd.GeoDataFrame): GeoDataFrame containing Polygons.

    Returns:
        gpd.GeoDataFrame: GeoDataFrame with Polygons converted to Points.
    """
    new_features = []

    for index, row in gdf.iterrows():
        new_geometry = convert_geometries_to_points(row['geometry'])
        if new_geometry is not None:
            row['geometry'] = new_geometry
            new_features.append(row)

    # Create a new GeoDataFrame from the modified features
    gdf_with_points = gpd.GeoDataFrame(new_features, crs=gdf.crs)

    return gdf_with_points

#deleate unessesary data from pands geoDataframe
def sort_geodata(gdf):
    """
    Extracts and simplifies data from a GeoJSON-like dictionary containing point geometries.

    Args:
        geojson_data (dict): The input GeoJSON-like dictionary.

    Returns:
        gpd.GeoDataFrame: A simplified GeoDataFrame with 'id', 'x', and 'y' columns for each point feature.
    """
    # Create empty lists to store extracted data
    ids = []
    x_coords = []
    y_coords = []

    # Iterate through the data
    for index, row in gdf.iterrows():
        ids.append(row["id"])
        geo = row["geometry"]
        x_coords.append(geo.x)
        y_coords.append(geo.y)
    
    # Create new Dataframe
    # Create a new GeoDataFrame
    geometry = [Point(x, y) for x, y in zip(x_coords, y_coords)]
    new_gdf = gpd.GeoDataFrame({"id": ids, "geometry": geometry})


    return(new_gdf)

def merge_near_service_stations(gdf, max_lenght=0.250):

    for index, row in gdf.iterrows():
        point = row["geometry"]
        id = row['id']
        for otherindex, otherrow in gdf.iterrows():
            if(index == otherindex):
                continue
            otherPoint = otherrow["geometry"]
            otherid = otherrow['id']

            currlen = my.get_Lenght(point, otherPoint)
            if(currlen < max_lenght):
                gdf = my.delete_element_by_id(gdf, id)
                print(f"deleated, beacuse len={len}")
                break
                
    return gdf



def deleate_Nodes_alone(gdf):
    #check for every Point, if there is another Point nearer than 60 km
    for index, row in gdf.iterrows():
        point = row["geometry"]
        for otherindex, otherrow in gdf.iterrows():
            if(index == otherindex):
                continue
            otherPoint = otherrow["geometry"]
            #print(f"Point: {point}, otherPoint: {otherPoint}")
            lenght = my.get_Lenght(point, otherPoint)
            #print(f"lenght: {lenght}")
            if(lenght > 60):
                gdf = gdf.drop(index)
                #print(f"Service Station {str(index)} was deleated")
                break
    return gdf

    

#set file path and Name
file_path = 'serviceStations-Nodes-Bordeaux.geojson'
name = "Bordeaux"
dataframe1 = my.load_geojson_to_dataframe(file_path)

if dataframe1 is None:
    print("Error, not dataframe given")
    exit(-1)
print(f"Loaded GeoJSON data into a GeoDataFrame from {file_path}.")
  
#print graph with polygons
file_name = "service-Stations-" + name + "-1.0"
my.save_geodataframe_to_geojson(dataframe1, file_name )
my.plot_geo_datafram_service_stations(dataframe1, title=file_name, to_pdf=file_name, )

# Convert Polygons to Points
dataframe2 = convert_polygons_to_points(dataframe1)

#save and print
file_name = "service-Stations-" + name + "-1.1"
my.save_geodataframe_to_geojson(dataframe2, file_name )
my.plot_geo_datafram_service_stations(dataframe2, title=file_name, to_pdf=file_name, )

#deleate unessesary data
dataframe3 = sort_geodata(dataframe2)

#save and print
file_name = "service-Stations-" + name + "-1.2"
my.save_geodataframe_to_geojson(dataframe3, file_name )
my.plot_geo_datafram_service_stations(dataframe3, title=file_name, to_pdf=file_name, )

#delete nodes alone and merge clusters
dataframe4 = deleate_Nodes_alone(dataframe3)
dataframe5 = merge_near_service_stations(dataframe4)

#save and print
file_name = "service-Stations-" + name + "-1.3"
my.save_geodataframe_to_geojson(dataframe5, file_name )
my.plot_geo_datafram_service_stations(dataframe5, title=file_name, to_pdf=file_name, )



#my.plot_geo_datafram_service_stations(dataframe, to_pdf="serviceStations-Nodes-Bordeaux", display=True)
'''
#Print Dataframe
if dataframe is not None:
    
    # You can now work with the loaded GeoDataFrame
    print(f"Loaded GeoJSON data into a GeoDataFrame from {file_path}.")
    #print(dataframe.head())  # Print the first few rows of the DataFrame
    # Perform further analysis or modifications as needed

    # Convert Polygons to Points
    dataframe_with_points = convert_polygons_to_points(dataframe)
    
    # Print the first few rows of the modified GeoDataFrame
    #print(dataframe_with_points.head())


    ##save the dataframe(converted to points)
    my.save_geodataframe_to_geojson(dataframe_with_points,"serviceStations-Nodes-Bordeaux-1.1.geojson" )
    
    #my.plot_geo_datafram_service_stations(dataframe_with_points, title="1.1", to_pdf="serviceStations-Nodes-Bordeaux-1.1", )

#-------------------------------------
    load_1_1 = my.load_geojson_to_dataframe("serviceStations-Nodes-Bordeaux-1.1.geojson")

    #deleate unessesary data
    dataframe_sorted = sort_geodata(load_1_1)

    print("Dataframe:")
    #print(dataframe_sorted)
    print("-------------")
    my.save_geodataframe_to_geojson(dataframe_sorted, "serviceStations-Nodes-Bordeaux-1.2.geojson")
    print("1")
    print(dataframe_sorted.columns)

    my.plot_geo_datafram_service_stations(dataframe_sorted, title="serviceStations-Nodes-Bordeaux-1.2", to_pdf="serviceStations-Nodes-Bordeaux-1.2", display=True)
    #print(dataframe_sorted.head())
'''

'''
#--------------------------------------
    load_1_2 = my.load_geojson_to_dataframe("serviceStations-Nodes-Bordeaux-1.2.geojson")
    modyfied_1_2 = deleate_Nodes_alone(load_1_2)
    my.save_geodataframe_to_geojson(modyfied_1_2, "serviceStations-Nodes-Bordeaux-1.3.geojson")
    my.plot_geo_dataframe_service_stations(modyfied_1_2, to_pdf="serviceStations-Nodes-Bordeaux-1.3", display=True)

    #print(getLenght(Point([ 0,0 ]), Point([50.0359, 00])))
'''
'''
load_1_2 = my.load_geojson_to_dataframe("serviceStations-Nodes-Bordeaux-1.2.geojson")

fin = merge_near_service_stations(load_1_2)
my.save_geodataframe_to_geojson(fin, "serviceStations-Nodes-Bordeaux-1.4.geojson")
my.plot_geo_datafram_service_stations(fin, title="serviceStations-Nodes-Bordeaux-1.3", to_pdf="serviceStations-Nodes-Bordeaux-1.3")
'''