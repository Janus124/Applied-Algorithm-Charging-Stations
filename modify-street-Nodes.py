import geopandas as gpd
from shapely.geometry import Polygon, Point, MultiPolygon, GeometryCollection, LineString
import pandas as pd
from shapely.wkt import loads
import math
import matplotlib.pyplot as plt
import myBib as my

#Load GeoJSON data from a file into a GeoDataFrame.
def load_geojson_to_dataframe(file_path):
    """
    Load GeoJSON data from a file into a GeoDataFrame.

    Args:
        file_path (str): The path to the GeoJSON file.

    Returns:
        gpd.GeoDataFrame: A GeoDataFrame containing the GeoJSON data.
    """
    try:
        gdf = gpd.read_file(file_path)
        return gdf
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    
#Save a GeoDataFrame to a GeoJSON file.
def save_geodataframe_to_geojson(gdf, output_file):
    """
    Save a GeoDataFrame to a GeoJSON file.

    Args:
        gdf (gpd.GeoDataFrame): The GeoDataFrame to be saved.
        output_file (str): The path to the output GeoJSON file.
    """
    try:
        gdf.to_file(output_file, driver="GeoJSON")
        print(f"GeoDataFrame saved to {output_file}")
    except Exception as e:
        print(f"Error saving GeoDataFrame to {output_file}: {str(e)}")

#Deletes the element of id in the gdf   
def delete_element_by_id(gdf, element_id):
    """
    Delete an element from a GeoDataFrame by its ID.
    
    Parameters:
        gdf (geopandas.GeoDataFrame): The GeoDataFrame to be modified.
        element_id: The ID of the element to be deleted.

    Returns:
        geopandas.GeoDataFrame: The modified GeoDataFrame with the element removed.
    """
    # Use boolean indexing to select all elements except the one with the given ID
    filtered_gdf = gdf[gdf['id'] != element_id]

    return filtered_gdf

#calculates the distance between two points using habersines euation (in km)
def getLenght(a : Point, b: Point):
    # Radius of the Earth in kilometers
    R = 6371.0

    #get Coordinates
    lat1 = a.x
    lon1 = a.y
    lat2 = b.x
    lon2 = b.y

    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Haversine formula
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c

    #print(f"distance: {distance}")
    return distance

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
def modify_dataframe1(gdf):    
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
            if(getLenght(first_point, second_point) < 0.25 and element_id is not secelement_id):
                delete_element_by_id(gdf, element_id)
                #print(f"point {element_id} deleted, because of {secelement_id}")
                deleated_counter += 1
                break
    print(f"{deleated_counter} Points deleted")
    return gdf
    
def plot_gdf(gdf):
    gdf.plot()
    plt.show()

file_path = "street-Nodes-Bordeaux.geojson"
dataframe = load_geojson_to_dataframe(file_path)

if dataframe is None:
    print("failure, no datafarme")
    exit(-1)

modified_dataframe = modify_dataframe1(dataframe)


# save the dataframe
save_geodataframe_to_geojson(modified_dataframe,"street-Nodes-Bordeaux-1.1.geojson" )

my.plot_geo_dataframe(dataframe, legend_title="aaaaaaaaaaaaaa")
my.plot_geo_dataframe(dataframe, to_pdf="street-Nodes-Bordeaux")
my.plot_geo_dataframe(modified_dataframe, to_pdf="street-Nodes-bordeaux-1.1")


