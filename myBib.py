import geopandas as gpd
from shapely.geometry import Polygon, Point, MultiPolygon, GeometryCollection, LineString
import pandas as pd
from shapely.wkt import loads
import math
import matplotlib.pyplot as plt
import os #to work with files, directories and other system ressourses

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
def get_Lenght(a : Point, b: Point):
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

#plots the graph ( if to_pdf has a name also to pdf)
def plot_geo_dataframe(gdf, title="Map", legend_title="Legend", xlabel="Longitude", ylabel="Latitude", legend=True, to_pdf='', display=False):
    # Create a plot
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    
    # Plot the GeoDataFrame
    gdf.plot(column='highway', ax=ax, legend=legend, legend_kwds={'title': legend_title})
    
    # Set plot title and axis labels
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    
    # Display the legend
    if legend:
        ax.get_legend().set_bbox_to_anchor((1.3, 1))
    
    # Save the plot as a PDF in the "pdfs" folder if 'to_pdf' is not empty
    if to_pdf:
        pdf_path = os.path.join('pdfs', to_pdf)
        if not pdf_path.endswith(".pdf"):
            pdf_path += ".pdf"
        plt.savefig(pdf_path, bbox_inches='tight', pad_inches=0)

    # Show the plot
    if display:
        plt.show()