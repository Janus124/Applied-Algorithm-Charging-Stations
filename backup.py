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

def split_array(json_data):
    
    ways = []
    nodes = []

    for el in json_data["elements"]:
        if el["type"] == "node":
            nodes.append(el)


        elif el["type"] == "way":
            ways.append(el)

        else:
            print("ERROR: There shouldn't be another type (exept node and way)")
    return (ways, nodes)    

'''
def rename(ways, nodes):

    i = 0
    counter = 0
    for el in nodes:

        oldid = el['id']
        el['id'] = i
        newid = i
        #print(f"changed id from {oldid} to {i}")
        
        #change the number in the ways-dic
        for el in ways:
            wayid = el['id']
            #print(el)
            for id in el["nodes"]:
                #print(f"{el['id']} , {id}")
                #print(f"id={id}, oldid:{oldid}, newid:{newid}")
                if id == oldid:
                    print (f"id changed from {oldid} to {newid}")
                    counter+=1
                    #print(ways['id' == el['id]']])
                    id = newid        
        
        i += 1
    print(counter)
    return (ways, nodes)

def create_ways_array_old(ways):

    edges = []

    for el in ways:
        nodes = el['nodes']
        num = len(nodes)
        for i in range (0, num-1):
            edges.append((nodes[i], nodes[i+1]))
    
    #print(edges)
    return edges

'''

def add_own_id(nodes):
    i = 0
    for el in nodes:
        el['own_id'] = i
        i += 1
    return nodes

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

def get_position(id, nodes):
    
    #find the node with the 'own_id'
    row = next((node for node in nodes if node['own_id'] == id), None)

    #returns the lat and long
    return(row['lat'], row['lon'])

def create_edges_array(nodes, ways):

    #get all edges    
    edges = []
    for el in ways:
        way_nodes = el['nodes']
        num = len(way_nodes)
        for i in range (0, num-1):
            overpass_id_a = int(way_nodes[i])
            overpass_id_b = int(way_nodes[i+1])
            anode = next((node for node in nodes if node['id'] == overpass_id_a), None)
            bnode = next((node for node in nodes if node['id'] == overpass_id_b), None)
            
            aid = anode['own_id']
            bid = bnode['own_id']
            edges.append((aid, bid))
    

    #deleate doube edges
    unique_edges = []
    for edge in edges:
            if edge not in unique_edges and (edge[1], edge[0]) not in unique_edges:
                unique_edges.append(edge)

    #get lenght of edges
    unique_distance_edges = []
    #calculates the distance between two points using habersines euation (in km)
    for a, b in unique_edges:
        lata, lona = get_position(a, nodes)
        latb, lonb = get_position(b, nodes)
        distance = get_distance(lata, lona, latb, lonb)
        unique_distance_edges.append((a, b, distance))
    
    #delete edges > 60km
    final_edges = []
    for a, b, dis in unique_distance_edges:
        if dis < 60:
            final_edges.append((a,b, dis))
    
    return final_edges


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

def del_nodes_oudside(nodes):

    paris = (48.8566, 2.3522)
    max_distance = 900 #km
    #every node has to be in a 900km radius around paris (to exclude the nodes in africe, america, ..)
    
    valid_nodes = []
    for el in nodes:
        pos = (el['lat'], el['lon'])
        distance = get_distance(paris[0], paris[1], pos[0], pos[1])
        if distance < 900:
            valid_nodes.append(el)
        else:
            print(f"NOTE: Node was deleated because of distance: {distance}")

    print(f"bevore: {len(nodes)}, after: {len(valid_nodes)}")


def create_all(filepath):

    json_data = load_json_data(filepath)
    ways, nodes = split_array(json_data)

    nodes = add_own_id(nodes)

    nodes = del_nodes_oudside(nodes)
    edges = create_edges_array(nodes, ways)

    create_graph(nodes, edges)


filepath = "service-stations-Aquitaine.json"
create_all(filepath)

filepath = "service-stations-France.json"
#create_all(filepath)

