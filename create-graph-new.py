import json
import math
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
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
    if(row == None):
        print("Thats a Problem! No Line found")
    return row

#returns the (lat, lon) of the centrois of every sercice station way
def merge_area_to_point(way_service, nodes_service): # service node

    #calcualte for every area the centroid
    centroids = []
    for el in way_service:
        id = -1
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

def point_is_junction(row):
    #point is juction
    if 'tags' in row and row['tags'] and 'highway' in row['tags'] and row['tags']['highway']:
        if 'junction' in row['tags']['highway']:
            return True
        
    return False


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
        
        radius = 1

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

    # Add nodes
    sc = 0
    for el in nodes:
        temp_id = el['id']
        if temp_id in ids:
            if 'tags' in el and el['tags'] and 'highway' in el['tags'] and el['tags']['highway'] and 'junction' in el['tags']['highway']:
                #junction
                g.add_node(el['id'], pos=(el['lat'], el['lon']), color='green')
            else:
                #service station
                sc += 1
                g.add_node(el['id'], pos=(el['lat'], el['lon']), color='red')

               
    
    '''    for el in nodes:
        if el['id'] in ids: #and 'tags' in el and el['tags'] and 'highway' in el['tags'] and el['tags']['highway'] and not ('junction' in el['tags']['highway']):
            g.add_node(el['id'], pos=(el['lat'], el['lon']), color='red')
    '''

    '''for i, (lat, lon) in enumerate(coords):
        g.add_node(i+424, pos=(lat, lon), color='blue')
    '''
    

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

'''#not finished  
def merge_streets(own_data, nodes):
    #Get the old_ids from the first element
    li = []

    temp = own_data[158] # id 830, merges with id 981
    print(temp)
    # Find elements with common old_ids
    for el in own_data[1:]:
        if temp['old_ids'][0] in el['old_ids'] or temp['old_ids'][1] in el['old_ids']:
            for s in el['nodes']:
                li.append(s)
            print (el)
    #matching_elements = [element for element in own_data[1:] if any(old_id in first_old_ids for old_id in element['old_ids'])]
    for el in temp['nodes']:
        li.append(el)
    return li

def merge_points_on_streets(own_data, nodes):

    for i, street in enumerate(own_data):
        new_list = []
        new_list.append(street['nodes'][0])
        for i in range (1, len(street['nodes'])):
            lat, lon = get_coords(street['nodes'][i], nodes)
            lat2, lon2 = get_coords(street['nodes'][i-1], nodes)
            if(get_distance(lat, lon, lat2, lon2) > 1):  #1km
                new_list.append(street['nodes'][i])

        #safe the list
        own_data[i]['nodes'] = new_list
    
    return own_data

#doesn't work proporly
def create_edges1(nodes, own_data):
    #get all junction (for opimisation)
    junction_array = []
    street_array = []
    for row in own_data:
        if point_is_junction(row):
            junction_array.append(row)
        else:
            street_array.append(row)

    all_edges = []
    #go through all streets
    for street in own_data:
        
        #go through all nodes in the street
        for i, street_id in enumerate(street['nodes']):
            dis = 0

            if i == len(street['nodes']):
                #last element, no futher action needed
                continue


            #!!! street_node and next_street_node are youst ids
            street_row = get_line(street_id, nodes)


            next_street_id = street['nodes'][i]
            next_street_row = get_line(next_street_id, nodes)
            if(next_street_row == None):
                print(next_street_id)


            if(point_is_junction(street_row)):
            #street_node is junction

                if(point_is_junction(next_street_row)):
                    #next node ist junction
                    print("Please NOT!!!!!!")
                    #TODO?


                else:
                    #next node is street_node
                    
                    dis_from_junction_to_next_node = get_distance(street_row['lat'], street_row['lon'], next_street_row['lat'], next_street_row['lon'])
                    all_nodes_from_junction = get_all_nodes_from_junction(next_street_id, nodes, own_data)
                    for junc_neighbour_id in all_nodes_from_junction:
                        junc_node_row = get_line(junc_neighbour_id, junction_array)
                        sec_dis = get_distance(street_row['lat'], street_row['lon'], junc_node_row['lat'], junc_node_row['lon'])
                        all_edges.append(street_id, junc_neighbour_id, dis_from_junction_to_next_node + sec_dis)

            else:
            #street_node is street_node

                if(point_is_junction(next_street_row)):
                    #next node ist junction
                    all_nodes_from_junction = get_all_nodes_from_junction(next_street_id, nodes, own_data)
                    dis = get_distance(street_row['lat'], street_row['lon'], next_street_row['lat'], next_street_row['lon'])
                    for junc_neighbour_id in all_nodes_from_junction:
                        junc_node_row = get_line(junc_neighbour_id, junction_array)
                        sec_dis = get_distance(next_street_row['lat'], next_street_row['lon'], junc_node_row['lat'], junc_node_row['lon'])
                        all_edges.append(street_id, junc_neighbour_id, dis + sec_dis)

                else:
                    #next node is street_node
                    dis = get_distance(street_row['lat'], street_row['lon'], next_street_row['lat'], next_street_row['lon'])
                    all_edges.append((street_id, next_street_id, dis))


     #deleate doube edges
    unique_edges = []
    unique_edges_without_dis = []
    for edge in all_edges:
            if edge not in unique_edges_without_dis and (edge[1], edge[0]) not in unique_edges_without_dis and edge[0] != edge[1]:
                unique_edges.append(edge)
                unique_edges.append[edge[0], edge[1]]

    

    
    #delete edges > 60km
    final_edges = []
    for a, b, dis in unique_edges:
        if dis < 60:
            final_edges.append((a,b, dis))
    
    return final_edges


    return all_edges



def get_all_nodes_from_junction(junction_id, nodes, own_data):
    all_nodes_ids= []
    #TODO

    #for all streets
    for street in own_data:
        before = []
        now = []
        after = []
        for i in range (0, len(street['nodes'])):
            now = street['nodes'][i]
            #if el is the junction 
            if(now['id'] == junction_id):

                #if it is the first element
                if i == 0:
                    after = street['nodes'][i+1]
                    all_nodes_ids.append(after)

                #if it is the last element
                elif i == len(street['nodes'] - 1):
                    all_nodes_ids.append(now)


                #if it is a middle element
                else:
                    after = now
                    now = before
                    before = street['nodes'][i+1]
                    #now is the junction

                    all_nodes_ids.append(before)
                    all_nodes_ids.append(after)
    
    print(f"All found nodes from get_all_nodes_from_junction: \{all_nodes_ids}")

    return all_nodes_ids

def create_graph_with_edges(nodes, ids, edges):
    # Create a graph
    g = nx.Graph()

    # Add nodes
    sc = 0
    for el in nodes:
        temp_id = el['id']
        if temp_id in ids:
            if 'tags' in el and el['tags'] and 'highway' in el['tags'] and el['tags']['highway'] and 'junction' in el['tags']['highway']:
                #junction
                g.add_node(el['id'], pos=(el['lat'], el['lon']), color='green')
            else:
                #service station
                sc += 1
                g.add_node(el['id'], pos=(el['lat'], el['lon']), color='red')

               
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

#takes an array out of used nodes and edges
#nodes = {'id = 1 , 'lat' = , 'lon'} no junctions
#edges = (id1, id2, distance)
#returns a array out of (id1, id2, dis, [points also on the path] )
def floyd_warshall(nodes, edges, max_distance=60):

    #add own id for table
    i = 0
    for node in nodes:
        node['own_id'] = i

    


    w, h = len(nodes), len(nodes)
    dist = [[int('inf') for x in range(w)] for y in range(h)]
    prev = [[0 for x in range(w)] for y in range(h)]

    for edge in edges:
        own_id1 = get_own_id_fw(edge[0], nodes)
        own_id2 = get_own_id_fw(edge[1], nodes)

        dist[own_id1, own_id2] = edge[2]
        prev[own_id1, own_id2] = own_id1
    
    for node in nodes:
        dist[node['own_id'], node['own_id']] = 0
        prev[node['own_id'], node['own_id']] = node['own_id']

    for k in range(1, len(nodes)):
        for i in range(1, len(nodes)):
            for j in range(1, len(nodes)):
                if dist[i][j] > dist[i,k] + dist[k][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    prev[i][j] = prev[k][j]

    #get path
    
def get_path_fw(u, v, dist, prev):
    if prev[u][v] == 0:
        return []
    path = [v]
    while ( u != v):
        v = prev[u][v]
        path.appent(v)
    return path


def get_own_id_fw(id, nodes):
    #find the node with the 'own_id'
    row = next((node for node in nodes if node['id'] == id), None)

    return row['own_id']
    '''

filepath_service = "export_1.json"
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



'''our_data = go_through_street(nodes_highway, way_highway, service)
save_json_data(our_data, 'streets1-1.json')


json_data = load_json_data('streets1-1.json')

filtered_streets = filter_own_streets(json_data)

save_json_data(filtered_streets, 'streets2-1.json')'''


json_data = load_json_data('streets2-1.json')
nodes_ids = temp(nodes_highway, json_data)


#te = merge_streets(json_data, nodes_highway)
create_graph4(nodes_highway, nodes_ids, service)


new_own_data = merge_points_on_streets(json_data, nodes_highway)
te = temp(nodes_highway, new_own_data)
create_graph4(nodes_highway, te, service)

all_edges = create_edges1(nodes_highway, new_own_data)
print(all_edges)




create_graph_with_edges(nodes_highway, te, all_edges)

junction = 0
street = 0
for row in new_own_data:
    if(point_is_junction(row)):
        junction += 1
    else:
        street += 1
        

'''
print(len(service))
print(len(set(nodes_ids)))

num_service = 0
num_juction = 0
for id in nodes_ids:
    el = get_line(id, nodes_highway)
    if 'tags' in el and el['tags'] and 'highway' in el['tags'] and el['tags']['highway'] and 'junction' in el['tags']['highway']:
        num_juction += 1
    else:
        num_service += 1


print(f"junc:{num_juction}, ser:{num_service}")
'''

'''
merge parralel streets


loop trough streets
    1. servie station and service staion
        create edge
    2. service station and junction
        create edge
        loop trough every jucntion and if it is this jucntion, connect 

'''