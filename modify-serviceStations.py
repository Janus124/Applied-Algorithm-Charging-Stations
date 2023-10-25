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

#Calculate the average point from a list of points with x and y coordinates.
def calculate_average_point(points):
    """
    Calculate the average point from a list of points with x and y coordinates.

    Args:
        points (list of tuple): List of (x, y) coordinate tuples.

    Returns:
        Point: The average point based on the input coordinates.
    """
    if not points:
        return None

    # Calculate the average x and y coordinates
    avg_x = sum(p[0] for p in points) / len(points)
    avg_y = sum(p[1] for p in points) / len(points)

    return Point(avg_x, avg_y)

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

def deleate_Nodes_alone(gdf):
    #check for every Point, if there is another Point nearer than 60 km

    for index, row in gdf.iterrows():
        point = row["geometry"]
        for otherindex, otherrow in gdf.iterrows():
            if(index == otherindex):
                continue
            otherPoint = otherrow["geometry"]
            #print(f"Point: {point}, otherPoint: {otherPoint}")
            lenght = getLenght(point, otherPoint)
            #print(f"lenght: {lenght}")
            if(lenght > 60):
                gdf = gdf.drop(index)
                print(f"Service Station {str(index)} was deleated")
                break
        
    return gdf



# Example usage:
file_path = 'serviceStations-Nodes-Bordeaux.geojson'
dataframe = load_geojson_to_dataframe(file_path)

#Print Dataframe
if dataframe is not None:
    '''
    # You can now work with the loaded GeoDataFrame
    print(f"Loaded GeoJSON data into a GeoDataFrame from {file_path}.")
    print(dataframe.head())  # Print the first few rows of the DataFrame
    # Perform further analysis or modifications as needed

    # Convert Polygons to Points
    dataframe_with_points = convert_polygons_to_points(dataframe)
    
    # Print the first few rows of the modified GeoDataFrame
    print(dataframe_with_points.head())


    ##save the dataframe(converted to points)
    save_geodataframe_to_geojson(dataframe_with_points,"serviceStations-Nodes-Bordeaux-1.1.geojson" )

#-------------------------------------
    load_1_1 = load_geojson_to_dataframe("serviceStations-Nodes-Bordeaux-1.1.geojson")

    #deleate unessesary data
    dataframe_sorted = sort_geodata(load_1_1)

    print("Dataframe:")
    print(dataframe_sorted)
    print("-------------")
    save_geodataframe_to_geojson(dataframe_sorted, "serviceStations-Nodes-Bordeaux-1.2.geojson")

    #print(dataframe_sorted.head())
    '''
#--------------------------------------
    load_1_2 = load_geojson_to_dataframe("serviceStations-Nodes-Bordeaux-1.2.geojson")
    modyfied_1_2 = deleate_Nodes_alone(load_1_2)
    save_geodataframe_to_geojson(modyfied_1_2, "serviceStations-Nodes-Bordeaux-1.3.geojson")


    #print(getLenght(Point([ 0,0 ]), Point([50.0359, 00])))

    