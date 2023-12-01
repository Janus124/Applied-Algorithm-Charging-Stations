import json
import math
import networkx as nx
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from collections import Counter


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

#returns a touple of (lat, lon)
def get_coords(id, nodes):
    
    #find the node with the 'own_id'
    row = next((node for node in nodes if node['id'] == id), None)

    #returns the lat and long
    return(row['lat'], row['lon'])

def get_line(id, nodes):
    row = next((node for node in nodes if node['id'] == id), None)

    return row

#returns the (lat, lon) of the centrois of every sercice station way
def merge_area_to_point(way_service, nodes_service): # service node

    #calcualte for every area the centroid
    centroids = []
    for el in way_service:
        lats = []
        lons = []
        #get the coordinates for every node and add to list
        for ids in el['nodes']:
            lat, lon = get_coords(ids, nodes_service)
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
            if(get_distance(lat1, lon1, lat2, lon2) < 0,1):
                #don't inclde point
                break
        sorted_centroids.append((lat1, lon1))

    return sorted_centroids

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

def go_through_street(nodes_highway, way_highway, service_stations):

    street_data = []
    node_data = []
    street_id_counter = 0

    #for every street 
    for el in way_highway:
        '''
        street data
        id = 1
        old_ids = (10 ,11 )
        nodes = [1 ,2 ,3 , , ]
        ,
        street data
        id = 2
        old_ids = (11 ,10 )
        nodes = [4 ,5 ,6 , , ]

        '''

        '''
        node
        id = 
        lat = 
        lon = 
        is_junction = 
        '''

        street_id = el['id']
        
        radius = 0.2

        #array of the points of a street
        street_nodes_ids = []

        #for every point on the street
        for street_point in el['nodes']:

            point = get_line(street_point, nodes_highway)
            id = point['id']
            lat = point['lat']
            lon = point['lon']



            #point is juction
            if 'tags' in point and point['tags'] and 'highway' in point['tags'] and point['tags']['highway']:
                if 'junction' in point['tags']['highway']:
                    street_nodes_ids.append(id)
                    continue
            
            #point is near servicesation
            else:
                #get neares service staion
                min_distance = 900 #km
                for service_lat, service_lon in service_stations:
                    distance = get_distance(lat, lon, service_lat, service_lon)
                    if min_distance > distance:
                        min_distance = distance
                
                #if service station nearer than radius, keep street node
                if min_distance <= radius:
                    street_nodes_ids.append(id)

            #useless 
             
            #get parallel streets
            #loop through every street node in 100m and add the street id to possible_streets_ids
            possible_streets_ids = []
            for second_street_point in nodes_highway:
                second_street_id = second_street_point['id']
                if 0.1 >= get_distance(lat, lon, second_street_point['lat'], second_street_point['lon']):
                    #currently all points in the radius
                    
                    for find_street in way_highway:
                        if second_street_id in find_street['nodes']:
                            possible_streets_ids.append(second_street_id)


        #1,2,1,2,1,1,1,1,1,,1,1,1,
        #(1,2,)(6,1)
        counter = Counter(possible_streets_ids)
        neighbour_street_id =  counter.most_common(1)[0][0]


        dict_entry = {'id': street_id_counter, 'old_ids': (street_id, neighbour_street_id), 'nodes': street_nodes_ids}
        street_id_counter += 1


        street_data.append(dict_entry)

                

        #find parallel street
        

        #create dict and add to street_



        #get other street
    save_json_data(street_data, 'your streets')
    print(street_data)
    return street_data

def filter_own_streets(streets):

    #delete empty streets
    filtered_streets = []
    for el in streets:
        if len(el['nodes']) > 1: #streets of only one element are usless, no connections
            filtered_streets.append(el)
    
    return filtered_streets

#def create_edges(nodes, streets):


#creates a graph
def create_graph(nodes, ids):

    #Create a graph 
    g = nx.Graph()

    #add_nodes
    for el in nodes:
        if el['id'] in ids and not('tags' in el and el['tags'] and 'highway' in el['tags'] and el['tags']['highway'] and 'junction' in el['tags']['highway']):
            g.add_node(el['id'], pos=(el['lat'], el['lon']))
    
    # Extract node positions
    node_positions = {node: (lon, lat) for node, (lat, lon) in nx.get_node_attributes(g, 'pos').items()}

    # Get the edgelist
    edgelist = list(g.edges())

    # Create a scatter plot of nodes
    plt.figure(figsize=(8, 6))
    nx.draw_networkx_nodes(g, pos=node_positions, node_size=100, node_color='blue', alpha=0.7)


    # Draw edges with weights as labels
    nx.draw_networkx_edges(g, pos=node_positions, edgelist=edgelist, width=2, alpha=0.5, edge_color='gray')
    #edge_labels = nx.get_edge_attributes(g, 'weight')
    #nx.draw_networkx_edge_labels(g, pos=node_positions, edge_labels=edge_labels)

    # Display the plot
    plt.title("Graph of Nodes in France")
    plt.axis('off')  # Turn off axis labels
    plt.show()
   


def create_graph4(nodes, ids, coords):
    # Create a graph
    g = nx.Graph()

    '''# Add nodes
    for el in nodes:
        if el['id'] in ids and 'tags' in el and el['tags'] and 'highway' in el['tags'] and el['tags']['highway'] and not ('junction' in el['tags']['highway']):
            g.add_node(el['id'], pos=(el['lat'], el['lon']), color='red')
    '''

    for i, (lat, lon) in enumerate(coords):
        g.add_node(i+424, pos=(lat, lon), color='blue')

    

    # Extract node positions and colors
    node_positions = {node: (lon, lat) for node, (lat, lon) in nx.get_node_attributes(g, 'pos').items()}
    node_colors = [g.nodes[node]['color'] for node in g.nodes]

    # Get the edgelist
    edgelist = list(g.edges())

    # Create a scatter plot of nodes
    plt.figure(figsize=(8, 6))
    nx.draw_networkx_nodes(g, pos=node_positions, node_size=100, node_color=node_colors, alpha=0.7)

    # Draw edges with weights as labels
    nx.draw_networkx_edges(g, pos=node_positions, edgelist=edgelist, width=2, alpha=0.5, edge_color='gray')

    # Display the plot
    plt.title("Graph of Nodes")
    plt.axis('off')  # Turn off axis labels
    plt.show()


def temp(nodes_highway, our_data):
    important_node_ids = []
    for el in our_data:
        for node_id in el['nodes']:
            important_node_ids.append(node_id)

    return important_node_ids

    





filepath_service = "service-stations-Aquitaine.json"
json_data_service = load_json_data(filepath_service)

filepath_highway = "street-Nodes-Aquitaine.json"
json_data_highway = load_json_data(filepath_highway)




#nodes_... is a list of dict containing all nodes (of that type)
#way is a list of dict containing all ways of streets or rest areas
nodes_service, way_service = split_array_service_stations(json_data_service)
nodes_highway, way_highway = split_array_highway(json_data_highway)

#nodes_service: nodes of the edges of service sations
# array of: {'type': 'node', 'id': 304610017, 'lat': 44.8883184, 'lon': -0.5799906}, {'type': 'node', 'id': 304610018, 'lat': 44.888388, 'lon': -0.5796747}
#way_service: ways of the edges of service stations, ids only contain ids of nodes_service
# array of: {'type': 'way', 'id': 1018761865, 'nodes': [9396560469, 9396560468, 9396560467, 9635617586, 9635617587, 307456719, 9396560469], 'tags': {'highway': 'services'}}
#nodes_highway: nodes of all possible street points
# array of: {'type': 'node', 'id': 10981442267, 'lat': 43.7195563, 'lon': -0.269957}
#way_highway: wasy of the streets. only ontains ids of nodes_highway
# array of {'type': 'way', 'id': 1018760500, 'nodes': [9396528101, 9396528100, 9396528099, 9396528098, 9396528097, 9396528101], 'tags': {'highway': 'services'}}


#service is a list of points (lat, lon), the centroid of every service station
service = merge_area_to_point(way_service, nodes_service)



#go_through_street(nodes_highway, way_highway, service)


'''json_data = load_json_data('your-streets.json')

filtered_streets = filter_own_streets(json_data)

save_json_data(filtered_streets, 'your-street2.json')'''


json_data = load_json_data('your-street2.json')
nodes_ids = temp(nodes_highway, json_data)

create_graph4(nodes_highway, nodes_ids, service)


'''
merge parralel streets


loop trough streets
    1. servie station and service staion
        create edge
    2. service station and junction
        create edge
        loop trough every jucntion and if it is this jucntion, connect 

'''