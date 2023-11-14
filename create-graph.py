import json
import math
import networkx as nx
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

def load_json_data(file_path):
    """
    Loads JSON data from a file.

    Parameters:
    - file_path (str): The path to the JSON file.

    Returns:
    - dict: The loaded JSON data.
    """
    with open(file_path, 'r') as file:
        json_data = json.load(file)
    return json_data

def save_json_data(data, file_path):
    # Save the dictionary to a file
    with open(f"{file_path}", "w") as f:
        json.dump(data, f)
    
#returns a touple of (lat, lon)
def get_coords(id, nodes):
    
    #find the node with the 'own_id'
    row = next((node for node in nodes if node['own_id'] == id), None)

    #returns the lat and long
    return(row['lat'], row['lon'])


#splits the json_data and returns a touple (nodes, highway, service)
def split_array(json_data):
    
    nodes = []
    highway = []
    service = []

    for el in json_data["elements"]:
        #is a node
        if el["type"] == "node":
            nodes.append(el)

        #is a way, than check if service station and rest_area or motorway and trunk 
        elif el["type"] == "way":
            tags = el["tags"]
            if tags["highway"] == "motorway" or tags["highway"] == "trunk":
                highway.append(el)
            elif tags["highway"] == "services" or tags["highway"] == "rest_area":
                service.append(el)
            else:
                print("ERROR: There shouldn't be another highway exempt the 4.")
        else:
            print("ERROR: There shouldn't be another type (exept node and way)")
    return (nodes, highway, service)  

#calculates the distance between two points and returns the distance in km
def get_distance(lat1, lon1, lat2, lon2):

    R = 6371.0

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
    
    #return distance in km
    return distance



def merge_area_to_point(service, nodes):

    #calcualte for every area the centroid
    centroids = []
    for el in service:
        lats = []
        lons = []
        #get the coordinates for every node and add to list
        for ids in el['nodes']:
            lat, lon = get_coords(ids, nodes)
            lats.append(lat)
            lons.append(lon)
        
        #calculate centroid
        centroid_lat = sum(lats) / len(lat)
        centroid_lon = sum(lon) / len(lons)
        centroids.append((centroid_lat, centroid_lon))

    #deleate centroids, which are nearer than 0,2m
    sorted_centroids = []
    for lat1, lon1 in centroids:
        for lat2, lon2 in centroids:
            if(get_distance(lat1, lon1, lat2, lon2) > 0,2):
                #don't inclde point
                break
        sorted_centroids.append((lat1, lon1))

    return sorted_centroids

def add_service_to_highway(nods, highway)


        

filepath = "all_nodes-Aquitaine.json"
json_data = load_json_data(filepath)

#nodes is a list of dict containing all nodes
#highway is a list of dict, containing all ways for highways
#service is a list of dict, containing all ways for restareas
nodes, highway, service = split_array(json_data)

#service is a list of points
service = merge_area_to_point(service)





