import geopandas as gpd
from shapely.geometry import Polygon, Point, MultiPolygon, GeometryCollection
import pandas as pd
from shapely.wkt import loads
import math

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

def modify_dataframe(gdf):
    
# deleate all motorway_junction elements if there is a motorway_junction element nearer than distance(100m)  
    # Filter the GeoDataFrame based on the "highway" property
    junction_gdf = gdf[gdf['properties']['highway'] == "motorway_junction"]
    
    #check for every junction, if there is another one nearer than 100m. If yes, deleate it
    distance = 0.1 # distance in km
    for index, row in junction_gdf.iterrows():
        # Access and work with the data in each row
        element_id = row['id']  # Access the 'id' column
        geometry = row['geometry']  # Access the 'geometry' column

        # Extract the coordinates from the geometry
        coordinates = list(geometry.coords) if geometry.type == 'LineString' else list(geometry[0].coords)

        for secindex, secrow in junction_gdf.itterrows():
            secelement_id = secrow['id']  # Access the 'id' column
            secgeometry = secrow['geometry']  # Access the 'geometry' column

            # Extract the coordinates from the geometry
            seccoordinates = list(secgeometry.coords) if secgeometry.type == 'LineString' else list(secgeometry[0].coords)

            if(getLenght(geometry, secgeometry) < 0.1 and element_id is not secelement_id):
                delete_element_by_id(gdf, element_id)
                break

    return gdf
    

file_path = "street-Nodes-Bordeaux.geojson"
dataframe = load_geojson_to_dataframe(file_path)

if dataframe is None:
    print("failure, no datafarme")
    exit(-1)

modified_dataframe = modify_dataframe(dataframe)

# save the dataframe
save_geodataframe_to_geojson(modified_dataframe,"street-Nodes-Bordeaux-1.1.geojson" )



