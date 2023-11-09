import geopandas as gpd
from shapely.geometry import Polygon, Point, MultiPolygon, GeometryCollection, LineString
import pandas as pd
from shapely.wkt import loads
import math
import matplotlib.pyplot as plt
import myBib as my

#retuns the coordinates of point or LineString of Id
def get_Points_by_id(gdf, id: int):
    # Filter the GeoDataFrame to find the row with the target ID
    target_row = gdf[gdf['id'] == id]

    return get_Points_of_row(target_row)

#retruns the coordinates of point or LineString of a row of gdf
def get_Points_of_row(target_row):
    if target_row.empty:
        return None  # ID not found
    #print(f"type: {type(target_row['geometry'])}, {target_row['geometry']}")
    
    geo = target_row['geometry']

    if isinstance(geo, Point):
        #point
        return list([geo.x, geo.y])
    elif isinstance(geo, LineString):
        #lineString
        return list(geo.coords)
    else:
        print("Error in get_points_of_row, no Points")
        return -1
        
    


#merges junctions to one node
def merge_junctions(gdf):    
# deleate all motorway_junction elements if there is a motorway_junction element nearer than distance(100m)  
    
    deleated_counter = 0
    # Filter the GeoDataFrame based on the "highway" property
    junction_gdf = gdf[gdf['highway'] == "motorway_junction"]    
    print(f"merging all junction Points. Total points: {len(junction_gdf)}")
    #check for every junction, if there is another one nearer than 100m. If yes, deleate it
    distance = 0.1 # distance in km
    for index, row in junction_gdf.iterrows():
        # Access and work with the data in each row
        element_id = row['id']  # Access the 'id' column
        
        #get coordinates and create point
        coordinates = get_Points_of_row(row)
        first_point = Point(coordinates[0],coordinates[1])

        for secindex, secrow in junction_gdf.iterrows():
            secelement_id = secrow['id']  # Access the 'id' column

            #get coordinates and create point
            seccoordinates = get_Points_of_row(secrow)
            second_point = Point(seccoordinates[0],seccoordinates[1])

            #chekc if the two point are nearer than 250m
            #print(f"Two Points: A:{first_point} - B:{second_point}, lenght: {getLenght(first_point, second_point)}")
            if(my.get_Lenght(first_point, second_point) < 0.25 and element_id is not secelement_id):
                my.delete_element_by_id(gdf, element_id)
                #print(f"point {element_id} deleted, because of {secelement_id}")
                deleated_counter += 1
                break
    print(f"{deleated_counter} Points deleted")
    return gdf
    

file_path = "street-Nodes-Bordeaux.geojson"
name ="Bordeaux"
dataframe1 = my.load_geojson_to_dataframe(file_path)

if dataframe1 is None:
    print("failure, no datafarme")
    exit(-1)

#save and print
file_name = "street-Nodes-" + name + "-1.0"
my.save_geodataframe_to_geojson(dataframe1, file_name)
my.plot_geo_dataframe_highway(dataframe1, title=file_name, to_pdf=file_name, )

#merge junctions to one point
dataframe2 = merge_junctions(dataframe1)

#save and print
file_name = "street-Nodes-" + name + "-1.1"
my.save_geodataframe_to_geojson(dataframe2, file_name)
my.plot_geo_dataframe_highway(dataframe2, title=file_name, to_pdf=file_name, )


'''
# save the dataframe
my.save_geodataframe_to_geojson(modified_dataframe,"street-Nodes-Bordeaux-1.1.geojson" )

my.plot_geo_dataframe_highway(dataframe, to_pdf="street-Nodes-Bordeaux")
my.plot_geo_dataframe_highway(modified_dataframe, to_pdf="street-Nodes-bordeaux-1.1")

'''
