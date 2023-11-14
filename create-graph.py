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
    row = next((node for node in nodes if node['id'] == id), None)

    #returns the lat and long
    return(row['lat'], row['lon'])

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

#splits the json_data and returns a touple (nodes, ways)
def split_array_service_stations(json_data):
    
    ways = []
    nodes = []

    for el in json_data["elements"]:
        if el["type"] == "node":
            nodes.append(el)


        elif el["type"] == "way":
            ways.append(el)

        else:
            print("ERROR: There shouldn't be another type (exept node and way)")
    return (nodes, ways)  
  
#splits the json_data and returns a touple (nodes, highway)
def split_array_highway(json_data):
    
    nodes = []
    highway = []

    for el in json_data["elements"]:
        #is a node
        if el["type"] == "node":
            nodes.append(el)

        elif el["type"] == "way":
            highway.append(el)
        else:
            print("ERROR: There shouldn't be another type (exept node and way)")
    return (nodes, highway)  




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
        centroid_lat = sum(lats) / len(lats)
        centroid_lon = sum(lons) / len(lons)
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


def add_service_to_highway(nodes_highway, service):
    marked_street_nodes = []
    for lat, lon in service:

        #find narest point in nodes
        neares_id = ""
        neares_distance = 900 #km
        for el in nodes_highway:
            distance = get_distance(lat, lon, el['lat'], el['lon'])
            if(distance < neares_distance):
                neares_id = el['id']
        
        #add nearest point to the marked list
        marked_street_nodes.append(neares_id)
    
    return marked_street_nodes
    

def delete_usless_highway_nodes(way_highway, marked_nodes):
    #for every street
    for el in way_highway:
        #chech each point, if its a marked one, if not delete
        marked_ids = []
        for node_id in el['nodes']:
            #check if nodes are marked, if yes add to list
            if node_id in marked_nodes:
                marked_ids.append(node_id)
        #reset list of nodes on the highway to only the marked ones
        el['nodes'] = marked_ids  
    return way_highway
        
        
    


        

filepath_service = "service-stations-Aquitaine.json"
json_data_service = load_json_data(filepath_service)

filepath_highway = "street-Nodes-Aquitaine.json"
json_data_highway = load_json_data(filepath_service)


#nodes_... is a list of dict containing all nodes (of that type)
#way is a list of dict containing all ways of streets or rest areas
nodes_service, way_service = split_array_service_stations(json_data_service)
nodes_highway, way_highway = split_array_highway(json_data_highway)

#service is a list of points (lat, lon)
service = merge_area_to_point(way_service, nodes_service)

#merge to nearest street node
#marked_street_nodes are a list of nodes_highway, which were the clostest to a rest area
marked_street_nodes = add_service_to_highway(nodes_highway, service)

#contains the highways, but only with the marked street nodes. The street nodes which are service stations
highway_only_marked = delete_usless_highway_nodes(nodes_highway, way_highway, marked_street_nodes)





