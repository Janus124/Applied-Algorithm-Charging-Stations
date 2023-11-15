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

#returns the (lat, lon) of the centrois of every sercice station way
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

#returns a list of id. All the nodes in this list repesent a rest area
def add_service_to_highway(nodes_highway, service):
    marked_street_nodes = []
    for lat, lon in service:

        #find narest point in nodes
        neares_id = ""
        second_id = ""
        third_id = ""
        neares_distance = 900 #km
        for el in nodes_highway:
            distance = get_distance(lat, lon, el['lat'], el['lon'])
            if(distance < neares_distance):
                second_id = third_id
                neares_id = second_id
                neares_id = el['id']
        
        #add nearest point to the marked list 
        #if neares point is in the list, second neares, and if that is in the list, third neares
        if(neares_id not in marked_street_nodes):
            marked_street_nodes.append(neares_id)
        elif(second_id not in marked_street_nodes):
            marked_street_nodes.append(second_id)
        elif(third_id not in marked_street_nodes):
            marked_street_nodes.append(third_id)

    #print(marked_street_nodes)
    return marked_street_nodes
    
#deletes every highway node, which is not marked(which doesn't represent a rest area)
def delete_usless_highway_nodes(way_highway, marked_nodes):
    print(marked_nodes)
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
        
#adds a property to each node with name 'own_id' and a index starting with 0
def add_own_id(nodes):
    i = 0
    for el in nodes:
        el['own_id'] = i
        i += 1
    return nodes
    
#gets the lat and long of the node with own_id == id
def get_position_id(id, nodes):
    
    #find the node with the 'own_id'
    row = next((node for node in nodes if node['id'] == id), None)

    #returns the lat and long
    return(row['lat'], row['lon'])
 
#gets the lat and long of the node with own_id == id
def get_position_own_id(id, nodes):
    
    #find the node with the 'own_id'
    row = next((node for node in nodes if node['own_id'] == id), None)

    #returns the lat and long
    return(row['lat'], row['lon'])

def create_edges_array(nodes, ways):
    

    #get all edges with own_id (not the overpass_id)   
    edges = []
    for el in ways:
        way_nodes = el['nodes']
        num = len(way_nodes)
        for i in range (0, num-1):
            #get overpass id
            overpass_id_a = int(way_nodes[i])
            overpass_id_b = int(way_nodes[i+1])

            #get own_id
            anode = next((node for node in nodes if node['id'] == overpass_id_a), None)
            bnode = next((node for node in nodes if node['id'] == overpass_id_b), None)
            
            aid = anode['own_id']
            bid = bnode['own_id']

            #add edge with own_ids
            edges.append((aid, bid))
            print(edges)
    
    
    #deleate doube edges
    unique_edges = []
    for edge in edges:
            if edge not in unique_edges and (edge[1], edge[0]) not in unique_edges:
                unique_edges.append(edge)

    #get lenght of edges
    unique_distance_edges = []
    for a, b in unique_edges:
        lata, lona = get_position_own_id(a, nodes)
        latb, lonb = get_position_own_id(b, nodes)
        distance = get_distance(lata, lona, latb, lonb)
        unique_distance_edges.append((a, b, distance))
    
    #delete edges > 60km
    final_edges = []
    for a, b, dis in unique_distance_edges:
        if dis < 60:
            final_edges.append((a,b, dis))
    
    return final_edges

#deletes all nodes which aren't in the to_keep_ids list (overpass id)
def delete_useless_street_nodes_of_nodes_array(nodes, to_keep_ids):
    sorted_nodes = []
    for el in nodes:
        if el['id'] in to_keep_ids:
            sorted_nodes.append(el)
    
    return sorted_nodes


#creates a graph
def create_graph(nodes, edges):

    #Create a graph 
    g = nx.Graph()

    #add_nodes
    for el in nodes:
        #print(f"nodes: {el['own_id']}, pos=({el['lat']}, {el['lon']})")
        g.add_node(el['own_id'], pos=(el['lat'], el['lon']))

    #add edges with distance
    for el in edges:
        #print(f"edges: {el[0]}, {el[1]}, {el[2]}")
        g.add_edge(el[0], el[1], weight=el[2])
    
    # Extract node positions
    node_positions = {node: (lon, lat) for node, (lat, lon) in nx.get_node_attributes(g, 'pos').items()}

    # Get the edgelist
    edgelist = list(g.edges())

    # Create a scatter plot of nodes
    plt.figure(figsize=(8, 6))
    nx.draw_networkx_nodes(g, pos=node_positions, node_size=200, node_color='blue', alpha=0.7)


    # Draw edges with weights as labels
    nx.draw_networkx_edges(g, pos=node_positions, edgelist=edgelist, width=2, alpha=0.5, edge_color='gray')
    #edge_labels = nx.get_edge_attributes(g, 'weight')
    #nx.draw_networkx_edge_labels(g, pos=node_positions, edge_labels=edge_labels)

    # Display the plot
    plt.title("Graph of Nodes in France")
    plt.axis('off')  # Turn off axis labels
    plt.show()
        

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
#marked_street_nodes are a list of nodes_highway, which were the clostest to a rest area (only a list of ids)
marked_street_nodes = add_service_to_highway(nodes_highway, service)

#contains the highways, but only with the marked street nodes. The street nodes which are service stations
way_highway_only_marked = delete_usless_highway_nodes(way_highway, marked_street_nodes)

#adds own_id proporty, to sort easier
nodes_highway = add_own_id(nodes_highway)

#create the edges with the own_ids
edges_with_own_id = create_edges_array(nodes_highway, way_highway_only_marked)

#list of all street nodes, which represent a rest area
nodes_service_final = delete_useless_street_nodes_of_nodes_array(nodes_highway, marked_street_nodes)

create_graph(nodes_service_final, edges_with_own_id)







