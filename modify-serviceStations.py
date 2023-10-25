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
dataframe = my.load_geojson_to_dataframe(file_path)

#Print Dataframe
if dataframe is not None:
    
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
    
#--------------------------------------
    load_1_2 = load_geojson_to_dataframe("serviceStations-Nodes-Bordeaux-1.2.geojson")
    modyfied_1_2 = deleate_Nodes_alone(load_1_2)
    save_geodataframe_to_geojson(modyfied_1_2, "serviceStations-Nodes-Bordeaux-1.3.geojson")


    #print(getLenght(Point([ 0,0 ]), Point([50.0359, 00])))

    