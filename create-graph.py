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

#returns a list of id. All the nodes in this list repesent a rest area
def add_service_to_highway(nodes_highway, service):
    marked_street_nodes = []

    for lat, lon in service:
        # Find nearest point in nodes
        nearest_id = ""
        second_id = ""
        third_id = ""
        nearest_distance = float('inf')  # Initialize with positive infinity

        for el in nodes_highway:
            distance = get_distance(lat, lon, el['lat'], el['lon'])
            
             # Check if the ID is not in marked_street_nodes before updating
            if el['id'] not in marked_street_nodes and distance < nearest_distance:
                nearest_id = el['id']
                nearest_distance = distance

        # Add nearest point to the marked list
        if nearest_id not in marked_street_nodes:
            marked_street_nodes.append(nearest_id)

    return marked_street_nodes


#deletes every highway node, which is not marked(which doesn't represent a rest area)
def delete_usless_highway_nodes(way_highway, marked_nodes):
    #print(marked_nodes)
    #for every street
    for el in way_highway:
        #chech each point, if its a marked one, if not delete
        marked_ids = []
        for node_id in el['nodes']:
            #check if nodes are marked, if yes add to list
            if node_id in marked_nodes:
                
                marked_ids.append(node_id)
                print("appended")
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

def create_graph2(nodes, edges, othernodes):

    #Create a graph 
    g = nx.Graph()

    max_own_id = 0

    #add_nodes
    for el in nodes:
        #print(f"nodes: {el['own_id']}, pos=({el['lat']}, {el['lon']})")
        g.add_node(el['own_id'], pos=(el['lat'], el['lon']), color='red')
        if el['own_id'] > max_own_id:
            max_own_id = el['own_id']
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
    #print(f"nodes: \n {nodes} \n edges: \n {edges}, othernodes: \n{othernodes}")
    nx.draw_networkx_nodes(g, pos=node_positions, node_size=200, node_color='blue', alpha=0.7)

    '''# Draw othernodes in a different color
    othernode_positions = {i: (lon, lat) for i, (lat, lon) in enumerate(othernodes)}
    print(othernode_positions)
    nx.draw_networkx_nodes(g, pos=othernode_positions, node_size=200, node_color='red', alpha=0.7)
    '''
    '''for i ,(lat, lon) in enumerate(othernodes):
        g.add_node(el['own_id'], pos=(lat, lon), color='red')'''
    



    # Draw edges with weights as labels
    nx.draw_networkx_edges(g, pos=node_positions, edgelist=edgelist, width=2, alpha=0.5, edge_color='gray')
    #edge_labels = nx.get_edge_attributes(g, 'weight')
    #nx.draw_networkx_edge_labels(g, pos=node_positions, edge_labels=edge_labels)

    # Display the plot
    plt.title("Graph of Nodes in France")
    plt.axis('off')  # Turn off axis labels
    plt.show()

def create_graph3(nodes, edges, ids):
    """
    Creates a graph with colored nodes based on the given IDs.

    Parameters:
    - nodes (list): List of dictionaries representing nodes with 'own_id', 'lat', and 'lon'.
    - edges (list): List of tuples representing edges with the format (node1, node2, weight).
    - ids (list): List of node IDs to be colored red.

    Returns:
    - None: The function plots the graph but doesn't return any value.
    """
    # Create a graph
    g = nx.Graph()

    # Add nodes
    for el in nodes:
        if(el['id'] in ids):
            node_id = el['own_id']
            pos = (el['lat'], el['lon'])
            g.add_node(node_id, pos=pos, color='red' if node_id in ids else 'blue')

    # Add edges with distance
    for el in edges:
        g.add_edge(el[0], el[1], weight=el[2])

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

def create_graph4(nodes, edges, coords):
    # Create a graph
    g = nx.Graph()

    # Add nodes
    for el in nodes:
        node_id = el['own_id']
        pos = (el['lat'], el['lon'])
        g.add_node(node_id, pos=pos, color='red')

    for i, (lat, lon) in enumerate(coords):
        g.add_node(i+424, pos=(lat, lon), color='blue')

    

    # Add edges with distance
    for el in edges:
        g.add_edge(el[0], el[1], weight=el[2])

    # Extract node positions and colors
    node_positions = {node: (lon, lat) for node, (lat, lon) in nx.get_node_attributes(g, 'pos').items()}
    node_colors = [g.nodes[node]['color'] for node in g.nodes]

    # Get the edgelist
    edgelist = list(g.edges())

    # Create a scatter plot of nodes
    plt.figure(figsize=(8, 6))
    nx.draw_networkx_nodes(g, pos=node_positions, node_size=200, node_color=node_colors, alpha=0.7)

    # Draw edges with weights as labels
    nx.draw_networkx_edges(g, pos=node_positions, edgelist=edgelist, width=2, alpha=0.5, edge_color='gray')

    # Display the plot
    plt.title("Graph of Nodes")
    plt.axis('off')  # Turn off axis labels
    plt.show()



def plot_points(coords):
    """
    Plots multiple points on a graph using networkx.

    Parameters:
    - coords (list): A list of tuples representing the coordinates (latitude, longitude) of each point.

    Returns:
    - None: The function plots the points but doesn't return any value.
    """
    # Create a graph
    G = nx.Graph()

    # Add nodes to the graph using coordinates as node labels
    for i, (lat, lon) in enumerate(coords):
        G.add_node(i, pos=(lon, lat))  # Use longitude as x-coordinate and latitude as y-coordinate

    # Extract positions of nodes for plotting
    pos = nx.get_node_attributes(G, 'pos')

    # Draw the graph with nodes at specified positions
    nx.draw(G, pos, with_labels=False, node_size=300, node_color='skyblue', font_size=5, font_color='black')

    '''# Add labels to nodes
    for i, (lat, lon) in enumerate(coords):
        plt.text(lon, lat, f'({lat}, {lon})', fontsize=8, ha='right')'''

    # Display the plot
    plt.title('Plotting Points on a Graph')
    plt.show()


def print_latlon(coords):
        #Create a graph 
    g = nx.Graph()

    #add_nodes
    for i, (lat,lon) in enumerate(coords):
        #print(f"nodes: {el['own_id']}, pos=({el['lat']}, {el['lon']})")
        g.add_node(i, pos=(lat, lon))
    
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


'''
so guys, update time
I implemented all funktion up to the graph creation, but one funktion isn't working correct. It is the add_service_to_highway funktion. 
My idea is: 
1. compute the centroid of every service station and rest area (merge_are_to_point). then we have a list of coordinates.
2. Find for every coordinate the neares "normal" street node and save the id in a list. (add_service_to_highway) and the list is marked_street_nodes.
These node should be the nodes we are working with.
3. modify the highway(delete_usless_highway_nodes). This funktion takes every way (street) and looks for every node in they way, if it is a marked street node or a normal one. normal ones are deleted.
4. add_own_id for easier debugging and better readibility
5. create_edges_arry. Now that we have all the nodes we need and every has a new id, we can create the edges. Also sorts out double edges and calculates the lenght.
6. delete_useless_street_nodes_of_nodes_array. Just for printing the graph. We want to only display the nodes we are using.
7. display graph


Now the add_service_to_highway funktion doesn't work how I inteded it. I don't know how, if it is a programming mistake or a mistake im my approach.
Is there a smarter approach or do you find the mistake?

Once we fix it, we should have the graph and can start with the next tasks.

'''




filepath_service = "service-stations-Aquitaine.json"
json_data_service = load_json_data(filepath_service)

filepath_highway = "street-Nodes-Aquitaine.json"
json_data_highway = load_json_data(filepath_highway)




#nodes_... is a list of dict containing all nodes (of that type)
#way is a list of dict containing all ways of streets or rest areas
nodes_service, way_service = split_array_service_stations(json_data_service)
nodes_highway, way_highway = split_array_highway(json_data_highway)

print(way_highway[-5])
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

#adds own_id proporty, to sort easier
nodes_highway = add_own_id(nodes_highway)


#merge to nearest street node
#marked_street_nodes are a list of nodes_highway, which were the clostest to a rest area (only a list of ids)
marked_street_nodes = add_service_to_highway(nodes_highway, service)

create_graph3(nodes_highway, [], marked_street_nodes)


#deleate all the not marked street nodes out of way_highway
marked_ways = []
#for every street
for el in way_highway:
    #chech each point, if its a marked one, if not delete
    marked_ids = []
    for node_id in el['nodes']:
        #check if nodes are marked, if yes add to list
        if node_id in marked_street_nodes:
            
            marked_ids.append(node_id)
            print("appended")
    #reset list of nodes on the highway to only the marked ones
    if len(marked_ids) > 0:
        marked_ways.append(marked_ids)  


'''way_highway_only_marked = []
for el in nodes_highway:
    if el['id'] in marked_street_nodes:
        way_highway_only_marked.append(el)

#way_highway_only_marked: array of dict: {'type': 'node', 'id': 638664, 'lat': 43.3410243, 'lon': -0.3775863, 'own_id': 282}

#contains the highways, but only with the marked street nodes. The street nodes which are service stations
#way_highway_only_marked2 = delete_usless_highway_nodes(way_highway, marked_street_nodes)

print(way_highway[-5])
print(way_highway_only_marked2[-5])'''

'''
#create the edges with the own_ids
edges_with_own_id = create_edges_array(nodes_highway, way_highway_only_marked)

#create_graph2(nodes_highway, edges_with_own_id, service)
#print_latlon(service)


#list of all street nodes, which represent a rest area
nodes_service_final = delete_useless_street_nodes_of_nodes_array(nodes_highway, marked_street_nodes)

create_graph(nodes_service_final, edges_with_own_id)

'''





