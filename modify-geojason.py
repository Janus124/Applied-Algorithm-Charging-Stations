import geopandas as gpd

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

# Example usage:
file_path = 'data.geojson'
dataframe = load_geojson_to_dataframe(file_path)

if dataframe is not None:
    # You can now work with the loaded GeoDataFrame
    print(f"Loaded GeoJSON data into a GeoDataFrame from {file_path}.")
    print(dataframe.head())  # Print the first few rows of the DataFrame
    # Perform further analysis or modifications as needed
