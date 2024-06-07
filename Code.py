import copy
from random import choice
import heapq
import math
from queue import PriorityQueue
from collections import deque
import random
import time
from math import radians, sin, cos, sqrt, atan2



class Node:
    def __init__(self, state, parent=None, action=None, cost=0, path_cost=0, priority=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.cost = cost
        self.path_cost = path_cost
        self.priority=priority

    def __hash__(self):
        if isinstance(self.state, list):
            return hash(tuple(map(tuple, self.state)))
        return hash(self.state)

    def __eq__(self, other):
        return isinstance(other, Node) and self.state == other.state

    def __gt__(self, other):
        if isinstance(other, Node):
            return self.cost > other.cost
        else:
            return NotImplemented

    def __repr__(self):
        return f"Node(state={self.state}, priority={self.priority})"

    
def read_locations(locations_file):
    landmarks = []# list to store names of landmarks 
    coordinates = []# list to store landmark's coordinates
    distances = []# list to store distances
    traffic = []  # list to store traffic values
    
    with open(locations_file, 'r') as file:
        landmark = None
        coord = None
        dist = None
        traff = None

        for line in file:
            line = line.strip()
            if line.startswith("Nearby Landmark:"):
                
                landmark = line.split(": ")[1]
            elif line.startswith("Coordinates:"):
                coord = tuple(map(float, line.split(": ")[1][1:-1].split(", ")))
            elif line.startswith("Distance:"):
                dist = float(line.split(": ")[1].split()[0])
            elif line.startswith("Traffic:"):
                traff = float(line.split(": ")[1].split()[0])
                
                # append other data only once for each landmark
                landmarks.append(landmark)
                coordinates.append(coord)
                distances.append(dist)
                traffic.append(traff)

    return landmarks, coordinates, distances, traffic
def unformat_landmark_name(formatted_name):
    name_parts = formatted_name.split('_nearby.txt')[0].split('_')
    name = ' '.join([part.capitalize() for part in name_parts])
    return name

def format_landmark_name(name):
    formatted_name = name.replace(' ', '_').lower()
    return f"{formatted_name}_nearby.txt"
#------------------------------Ambulane class -------------------------------------
class Ambulance:
    def __init__(self, initial_state, goal_state, state_transition_model,path_cost=0,actions=""):
        self.state = initial_state
        self.goal_state = goal_state
        self.state_transition_model = state_transition_model
        self.actions=actions
        self.path_cost=path_cost

    #function to generate a random patient:

    def get_random_patient(self, filename):
     filename = "random_patients.txt"
     with open(filename, 'r') as file:
        lines = file.readlines()

    # choose a random line from the file
     random_line = random.choice(lines)

    # split the line by ';' to extract the data
     data = random_line.strip().split(';')

    # extract the required information
     name = data[1]
     age = data[2]  
     gender = data[3] 
     initial_state = data[-2]
     service = data[-1]
     return name, age, gender, initial_state, service
    
    #function to calculate the distance between two states

    def calculate_distance(self,lat1,lon1,lat2,lon2):
        lat1 = radians(lat1)
        lon1 = radians(lon1)
        lat2 = radians(lat2)
        lon2 = radians(lon2)

        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = 6371 * c  

        return distance
    
    #function to return a dictionary of hospitals with the needed service

    def hospitals_with_service(self, file, hospitals_dict):
     file = "random_patients.txt"
     hospitals_with_services = {}
     #here we get the service needed for the patient generated randomly from the file of patients
     #_, _, _, _, service = self.get_random_patient(file)
     service = "Cardiology"
     for hospital_name, hospital_info in hospitals_dict.items():
        departments = hospital_info["departments"]
        for department, _ in departments:
            if service == department:
                hospitals_with_services[hospital_name] = hospital_info
                break  # exit the loop once the service is found in a department
     return hospitals_with_services
    
    #function to calculate the best hospital

    def estimate_goal_hospital(self, initial_state,hos_with_services):
     
     file = "random_patients.txt"
     hos_with_services=self.hospitals_with_service(file, hospitals_dict)

     heuristic_values = {}

     initial_state_formatted_path = format_landmark_name(initial_state)
     landmarksIS, coordinatesIS, distancesIS, trafficIS = read_locations(initial_state_formatted_path)
     initial_state_coordinates = next((coord for coord, dist in zip(coordinatesIS, distancesIS) if dist == 0), None)
     for hospital_name, hospital_data in hos_with_services.items():
        hospital_formatted_file_path = format_landmark_name(hospital_name)
        landmarksH, coordinatesH, distancesH, trafficH = read_locations(hospital_formatted_file_path)
        hospital_coordinates = hos_with_services[hospital_name]["coordinates"]
        lat4 = hospital_coordinates[0]
        long4 = hospital_coordinates[1]
        initial_state_coordinates = (initial_state_coordinates[0], initial_state_coordinates[1])
        lat3 = initial_state_coordinates[0]
        long3 = initial_state_coordinates[1]
        distance = self.calculate_distance(lat3, long3, lat4, long4)
        average_traffic = random.random()
        normalized_distance = distance / 10  # normalize distance
        normalized_traffic = average_traffic / 10  # normalize traffic
        adjusted_distance = normalized_distance * 0.8 + normalized_traffic * 0.2  # Adjusted distance with weighted coefficients
        heuristic_values[hospital_name] = adjusted_distance
   
     nearest_hospital = min(heuristic_values, key=heuristic_values.get)
     nearest_hospital_coordinates = hos_with_services[nearest_hospital]["coordinates"]
     return nearest_hospital, nearest_hospital_coordinates
    
    #the heuristic

    def heuristic(self, state):
      state_formatted_path = format_landmark_name(state)
      landmarksS, coordinatesS, distancesS, trafficS = read_locations(state_formatted_path)
      state_coordinates = next((coord for coord, dist in zip(coordinatesS, distancesS) if dist == 0), None)
      state_coordinates = (state_coordinates[0], state_coordinates[1])
      lat1 = state_coordinates[0]
      long1 = state_coordinates[1]
      nearest_hospital, nearest_hospital_coordinates = self.estimate_goal_hospital(initial_state, hospitals_dict)
      nearest_hospital_coordinates = (nearest_hospital_coordinates[0], nearest_hospital_coordinates[1])
      lat2 = nearest_hospital_coordinates[0]
      long2 = nearest_hospital_coordinates[1]
      distance = self.calculate_distance(lat1, long1, lat2, long2)
      normalized_distance = distance / 100  # normalize distance
      average_traffic = random.random()
      normalized_traffic = average_traffic * 10  # normalize traffic
      adjusted_distance = normalized_distance * 0.8 + normalized_traffic * 0.2  # adjusted distance with weighted coefficients


      return adjusted_distance
     
    def is_goal_test(self, state, data_struct='fifo'):
     if data_struct == 'A*':
        nearest_hospital, _ = self.estimate_goal_hospital(state, hospitals_dict)
        return state == nearest_hospital
     elif data_struct == 'ucs' or data_struct == 'fifo':
        if state not in hospitals_dict:
            return False
        hospital_data = hospitals_dict[state]
        departments = hospital_data.get("departments", [])
        for department, capacity in departments:
            if department == self.goal_state:
                current_capacity = random.randint(0, capacity)
                if current_capacity > 0 and current_capacity < capacity:
                    return department == self.goal_state

        return False



    
     
 
                
    def get_valid_actions(self, state):
     landmark_name = state
     formatted_name = format_landmark_name(landmark_name)
    
     formatted_file_path = f'{formatted_name}'  
     landmarks, coordinates, distances, traffics = read_locations(formatted_file_path)

     location_data = {}
     for landmark, coord, distance, traffic in zip(landmarks, coordinates, distances, traffics):
        location_data[landmark] = {'Coordinates': coord, 'Distance': distance, 'Traffic':traffic} 

     self.state_transition_model = {}  
     for landmark, data in location_data.items():
        neighboring_landmarks = [neighbor for neighbor, neighbor_data in location_data.items() if neighbor_data['Distance'] > 0 and neighbor_data['Distance'] < 1500]
        self.state_transition_model[landmark] = neighboring_landmarks

     if state not in self.state_transition_model:
        return []
     return self.state_transition_model[state]

    
    def apply_action(self, state, action):
     if action not in self.get_valid_actions(state):
        return None  
    
     return action
    
    def calculate_cost_to_node(self, state, initial_state):
     state_formatted_path = format_landmark_name(state)
     landmarksS, coordinatesS, distancesS, trafficS = read_locations(state_formatted_path)
     state_coordinates = next((coord for coord, dist in zip(coordinatesS, distancesS) if dist == 0), None)
     state_coordinates = (state_coordinates[0], state_coordinates[1])
     lat1, long1 = state_coordinates
     initial_state_formatted_path = format_landmark_name(initial_state)
     landmarksIS, coordinatesIS, distancesIS, trafficIS = read_locations(initial_state_formatted_path)
     initial_state_coordinates = next((coord for coord, dist in zip(coordinatesIS, distancesIS) if dist == 0), None)
     initial_state_coordinates = (initial_state_coordinates[0], initial_state_coordinates[1])
     lat3, long3 = initial_state_coordinates

     g_of_n = self.calculate_distance(lat1, long1, lat3, long3)
     return g_of_n


        
    def expand_node(self, node, initial_state,heuristic_included=True, local=False,uninformed=False):
       if uninformed==True:
        state = node.state
        valid_neighbors = self.get_valid_actions(state)
        valid_actions = (valid_neighbors)
        child_nodes = []
        for action in valid_actions:
            
            child_state = self.apply_action(state, action)
            child_node = Node(child_state, parent=node, action=action, cost=node.cost + 1)
            child_nodes.append(child_node)
        return child_nodes
       else:
        parent_state = node.state
        valid_actions = self.get_valid_actions(parent_state)
        child_nodes = []

        for action in valid_actions:
         child_state = self.apply_action(parent_state, action)

         if child_state is not None:  
            child_state_formatted_path = format_landmark_name(child_state)
            landmarksC, coordinatesC, distancesC, trafficC = read_locations(child_state_formatted_path)
            child_state_coordinates = next((coord for coord, dist in zip(coordinatesC, distancesC) if dist == 0), None)
            child_state_coordinates = (child_state_coordinates[0], child_state_coordinates[1])
            state_formatted_path = format_landmark_name(parent_state)
            landmarksS, coordinatesS, distancesS, trafficS = read_locations(state_formatted_path)
            parent_state_coordinates = next((coord for coord, dist in zip(coordinatesS, distancesS) if dist == 0), None)
            parent_state_coordinates = (parent_state_coordinates[0], parent_state_coordinates[1])

            # calculate the cost to the node, including both the cost from the initial state and the heuristic value
            g_of_n = self.calculate_cost_to_node(child_state, initial_state)
            h_of_n = self.heuristic(child_state)
            f_of_n = g_of_n + h_of_n
            if heuristic_included == True :
                path_cost = node.path_cost + g_of_n

         
                child_node = Node(child_state, parent=node, action=action, cost=f_of_n, path_cost=path_cost)
                child_nodes.append(child_node)
            elif local:
                        
                        pr=h_of_n
                        child_node = Node(child_state, parent=node, action=action,  cost=g_of_n, priority=pr)#get the cost right here
                        child_nodes.append(child_node)
                        
            else:                    
                     pr=g_of_n
                     child_node = Node(child_state, parent=node, action=action, cost=g_of_n,priority=pr)
                     child_nodes.append(child_node)
          


       return child_nodes



    
    def printNode_uninformed(self,message,node):
        print ("Action = ",end=" ")
        print(node.action,end=" ")
        print(message,end=" ")
        print(node.state)
    def printNode(self, message, node):
      print("Node Information:")
      print("Message:", message)
      print("State:", node.state)
      if node.parent:
          print("Parent State:", node.parent.state)
      print("Action:", node.action)
      print("Cost:", node.cost)

def stochastic_hill_climbing(problem, initial_state):
    print("New search (Stochastic Hill Climbing):")
    initial_node = Node(initial_state, priority=1000000)
    current_node = initial_node
    current_state = initial_node.state
    current_state_priority = initial_node.priority


    while True:
        neighbors = problem.expand_node(current_node, initial_state, heuristic_included=False, local=True, uninformed=False)
        uphill_neighbors = [neighbor for neighbor in neighbors if neighbor.priority < current_state_priority]

        if not uphill_neighbors:
            print(f"No valid neighbors found. Local maximum state: {current_state}")
            break

        chosen_neighbor = random.choice(uphill_neighbors)
        current_state = chosen_neighbor.state
        current_state_priority = chosen_neighbor.priority
        current_node = chosen_neighbor
        print(f"Chosen state: {current_state} with priority: {current_state_priority}")

  
    return current_state

    

def GraphSearchAlgorithm(problem, data_struct='fifo', initial_state=None):


   if data_struct=="stochastic":
    return stochastic_hill_climbing(problem, initial_state)
    
   else:    
    if data_struct == 'fifo':
        frontier = deque() 
    elif data_struct=='ucs'  or  data_struct=="A*":
        frontier = []  
    explored = set()  
    initial_node = Node(problem.state)
    if data_struct=="fifo":
        frontier.append(initial_node)
    else:
       
       heapq.heappush(frontier, (initial_node.cost, initial_node))  

    while frontier:
        if data_struct == 'fifo':
            node = frontier.popleft() 
        else:
             _, node = heapq.heappop(frontier)  

        print("Currently exploring:", node.state)  
        if problem.is_goal_test(node.state, data_struct='fifo'):
            print("Goal state reached:", node.state)  

            return node
        elif problem.is_goal_test(node.state, data_struct='A*'):
            print("Goal state reached:", node.state) 
            return node
        explored.add(node.state)

        if data_struct == 'ucs': 
             children = problem.expand_node(node,initial_state,False)
        elif data_struct=="stochastic":
                children = problem.expand_node(node,initial_state,False,True)           
        elif data_struct == 'A*':
             children = problem.expand_node(node,initial_state,True)
        else:
                children= problem.expand_node(node,initial_state,False,False,True)

        print("Expanding node:", node.state)

        for child_node in children:
            if child_node.state not in explored:
                if data_struct == 'ucs'  or  data_struct=="A*":
                 if not any(child[1].state == child_node.state for child in frontier):
                    heapq.heappush(frontier, (child_node.cost, child_node))  
                else:
                    if child_node not in frontier:
                       
                       frontier.append(child_node)
                explored.add(child_node.state)
   
    return "failure"




    
def format_landmark_name(name):
    formatted_name = name.replace(' ', '_').lower()
    return f"{formatted_name}_nearby.txt"

hospitals_dict = {
    "Etablissement Public Hospitalier ROUIBA": {
        "name": "Etablissement Public Hospitalier ROUIBA",
        "type": "Public",
        "address": "Rue Larbi Abdelsalem, Rouiba, 16000, Algiers, Algeria.",
        "coordinates": (36.73529403582579, 3.2857382799394013),
        "capacity": 140,
        "departments": [
            ("Emergency Care", 10), 
            ("Surgery", 15), 
            ("Radiology", 20), 
            ("Pneumophthisiology", 20), 
            ("Oncology", 10), 
            ("Internal medicine", 10), 
            ("Pediatric", 25), 
            ("University occupational medicine", 30)
        ]
    },
    "Etablissement Public Hospitalier EL HARRACH ( HASSAN BADI)": {
        "name": "Etablissement Public Hospitalier EL HARRACH ( HASSAN BADI)",
        "type": "Public",
        "address": "Rue Larbi Abdelsalem, Rouiba, 16000, Algiers, Algeria.",
        "coordinates": (36.71686756164948, 3.137533070316301),
        "capacity": 80,
        "departments": [
            ("Pediatric", 30), 
            ("Gynecologist", 50)
        ]
    },
    "Etablissement Public Hospitalier EL BIAR (DJILLALI BELKHENCHIR)": {
        "name": "Etablissement Public Hospitalier EL BIAR (DJILLALI BELKHENCHIR)",
        "type": "Public",
        "address": "01, rue des Frères Hadjane.El Biar, Algeria.",
        "coordinates": (36.75616175006669, 3.0415776286784597),
        "capacity": 120,
        "departments": [
            ("General surgery", 10), 
            ("Pediatric surgery", 30), 
            ("Internal Medecine", 10), 
            ("Pediatrics", 10), 
            ("Radiology", 20), 
            ("Dentistry", 25), 
            ("Epidemiology", 15)
        ]
    },
    "Etablissement Public Hospitalier AIN TAYA": {
        "name": "Etablissement Public Hospitalier AIN TAYA",
        "type": "Public",
        "address": "Hai si el haouas . 16612 Ain Taya , Algeria",
        "coordinates": (36.78975064998653, 3.294737283650239),
        "capacity": 140,
        "departments": [
            ("Obstetrics and Gynecology", 20),
            ("Emergency Care", 30),
            ("Internal Medecine", 20),
            ("Pediatrics", 30),
            ("Radiology", 10),
            ("Internal Medecine", 20),
            ("General Surgery", 10)
        ]
    },
    "Etablissement Hospitalier Spécialisé NEURO CHIRURGICAL ALI AIT IDIR": {
        "name": "Etablissement Hospitalier Spécialisé NEURO CHIRURGICAL ALI AIT IDIR",
        "type": "Public",
        "address": "Rue haddad abderazak , bab djedid Alger-Centre , Algeria",
        "coordinates": (36.78755128774451, 3.0580496780885005),
        "capacity": 220,
        "departments": [
            ("Neurology", 30),
            ("Neurosurgery", 110),
            ("Radiology", 100)
        ]
    },
    "Etablissement Hospitalier Spécialisé CNMS DR MAOUCHE MOHAND AMOKRANE": {
        "name": "Etablissement Hospitalier Spécialisé CNMS DR MAOUCHE MOHAND AMOKRANE",
        "type": "Public",
        "address": "Clairval Dely Brahim , Algiers",
        "coordinates": (36.78755128774451, 3.0580496780885005),
        "capacity": 180,
        "departments": [
            ("Anesthesiology & Recovery", 30),
            ("Cardiac surgery", 15),
            ("Cardiology", 15),
            ("Vascular surgery", 30),
            ("Sports medicine", 50),
            ("Psychiatry", 50)
        ]
    },
    "Etablissement Public Hospitalier Rahmouni Djillali": {
        "name": "Etablissement Public Hospitalier Rahmouni Djillali",
        "type": "Public",
        "address": "Av. De Pekin, El Mouradia, 11 chemin El Bachir El Ibrahimi El Mouradia Alger.",
        "coordinates": (36.77310579777404, 3.0417312678966826),
        "capacity": 730,
        "departments": [
            ("Medical Consultations", 50),
            ("Emergency Care", 30),
            ("Surgery", 40),
            ("Medical Imaging", 60),
            ("Laboratory Analyses", 80),
            ("Rehabilitation and Physical Therapy", 70),
            ("Nursing Care", 120),
            ("Specialized Consultations", 200),
            ("Maternity and Obstetrics", 50),
            ("Psychiatry", 30)
        ]
    },
    "Établissement hospitalier spécialisé de Douera": {
        "name": "Établissement hospitalier spécialisé de Douera",
        "type": "Public",
        "address": "Rue el Aichaoui, Douera, Algeria.",
        "coordinates": (36.66737784053592, 2.942714939827355),
        "capacity": 190,
        "departments": [
            ("Orthopedics Service - A", 12),
            ("Orthopedics Service - B", 18),
            ("Surgery", 10),
            ("Physical Medicine and Functional Rehabilitation", 17),
            ("Rheumatology", 13),
            ("Plastic Surgery", 6),
            ("Pathological Anatomy", 4),
            ("Internal Medicine", 3),
            ("Cardiology", 15),
            ("Maxillofacial Surgery", 15),
            ("Pediatrics", 15),
            ("Radiology", 28),
            ("Biological Laboratory", 12),
            ("Forensic Medicine", 15),
            ("Gynecology", 7)
        ]
    },
    "Établissement Public de Santé de Proximité de DRARIA": {
        "name": "Établissement Public de Santé de Proximité de DRARIA",
        "type": "Public",
        "address": "Mosquée Hamza, Debussy (en face la, Draria PXJX+H9 Draria).",
        "coordinates": (36.705840, 2.991820),
        "capacity": 110,
        "departments": [
            ("General Medicine", 25),
            ("Specialized Consultations", 40),
            ("Perinatal Proximity Centers", 15),
            ("Rehabilitation and Post-acute Care (SSR)", 15),
            ("Palliative Care", 5),
            ("Emergency Care", 10)
        ]
    },
    "Etablissement Hospitalier Specialisé En Cancerologie Pierre Et Marie Curie (EHS-CPMC)": {
        "name": "Établissement Hospitalier Spécialisé Anti Cancéreux Pierre Et Marie Curie",
        "type": "Public",
        "address": "rue Tebessi Larbi, Sidi M'Hamed, 16000, Alger.",
        "coordinates": (36.766530, 3.032840),
        "capacity": 140,
        "departments": [
            ("Breast Cancer", 30),
            ("Eye Cancers", 10),
            ("Pediatric Cancers", 20),
            ("Sarcomas", 20),
            ("Lymphomas", 10),
            ("Prostate Cancer", 10),
            ("Nervous System Cancers", 10),
            ("Cervicofacial Cancer", 10),
            ("Gynecological Cancer", 10),
            ("Digestive Cancer", 5),
            ("Bronchopulmonary Cancer", 5)
        ]
    },
    "Établissement Hospitalier Spécialisé Ben Aknoun": {
        "name": "Établissement Hospitalier Spécialisé Ben Aknoun",
        "type": "Public",
        "address": "14 route des deux Bassins, Ben Aknoun, Alger, Algeria",
        "coordinates": (36.753610, 3.022150),
        "capacity": 70,
        "departments": [
            ("Neurology", 10),
            ("Rheumatology", 20),
            ("Orthopedics", 20),
            ("Functional Rehabilitation", 10),
            ("Neuromuscular Exploration", 10)
        ]
    },
 
    "Établissement Hospitalier Spécialisé EN MALADIES INFECTIEUSES Dr EL HADI FLICI": {
        "name": "Établissement Hospitalier Spécialisé EN MALADIES INFECTIEUSES Dr EL HADI FLICI",
        "type": "Public",
        "address": "El Kettar Hospital,Oued Koriche, Alger, Algeria.",
        "coordinates": (36.782110, 3.048820),
        "capacity": 85,
        "departments": [
            ("Infectious Diseases", 40),
            ("Radiology", 10),
            ("Cardiology", 15),
            ("Emergency Care", 10)
        ]
    },
    "Établissement Hospitalier Spécialisé DES URGENCES MEDICO CHIRURGICALES SALIM ZEMIRLI": {
        "name": "Établissement Hospitalier Spécialisé EN MALADIES INFECTIEUSES Dr EL HADI FLICI",
        "type": "Public",
        "address": "21, avenue Pasteur, Khelifa Boukhalfa, Alger-Centre, 16000, Alger, Algeria 123.",
        "coordinates": (36.754720, 3.043950),
        "capacity": 90,
        "departments": [
            ("Orthopedics", 20),
            ("Neurosurgery", 10),
            ("Forensic Medicine", 15),
            ("Internal Medicine", 10),
            ("General Surgery", 20),
            ("Anesthesia - Resuscitation", 15)
        ]
    },
    "EPSP ZERALDA": {
        "name": "EPSP ZERALDA",
        "type": "Public",
        "address": "Villa n°24, Lotissement Est Extension, Zeralda, Algiers",
        "coordinates": (36.70929931706734, 2.844324400864339),
        "capacity": 12,
        "departments": [
            ("Emergency care", 12)
        ]
    },
    "EPSP RGHAYA": {
        "name": "EPSP RGHAYA",
        "type": "Public",
        "address": "RUE SALHI MOHAMED Reghaia – Alger",
        "coordinates": (36.74198161059531, 3.3415335671135518),
        "capacity": 10,
        "departments": [
            ("Emergency care", 10)
        ]
    },
    "EPSP KOUBA": {
        "name": "EPSP KOUBA",
        "type": "Public",
        "address": "RUE SALHI MOHAMED Reghaia – Alger",
        "coordinates": (36.74198161059531, 3.3415335671135518),
        "capacity": 11,
        "departments": [
            ("Emergency care", 11)
        ]
    },
    "EPSP BOUCHAOUI": {
        "name": "EPSP BOUCHAOUI",
        "type": "Public",
        "address": "RUE SALHI MOHAMED Reghaia – Alger",
        "coordinates": (36.74404285867428, 2.9132772143675454),
        "capacity": 9,
        "departments": [
            ("Emergency care", 9)
        ]
    },
    "EPSP BOUZAREAH": {
        "name": "EPSP BOUZAREAH",
        "type": "Public",
        "address": "Rue Ali Remli, Bouzareah, Algiers",
        "coordinates": (36.790235280782255, 3.0168179806065702),
        "capacity": 7,
        "departments": [
            ("Emergency care", 7)
        ]
    },
    "EPSP DERGANA": {
        "name": "EPSP DERGANA",
        "type": "Public",
        "address": "Route Nationale N°24-Bordj El Bahri-Alger",
        "coordinates": (36.71464376624302, 3.209159135003055),
        "capacity": 10,
        "departments": [
            ("Emergency care", 10)
        ]
    },
    "EPSP BARAKI": {
        "name": "EPSP BARAKI",
        "type": "Public",
        "address": "Cité El Badr Bach Djarah Algiers",
        "coordinates": (36.65383807657213, 3.09048933827222),
        "capacity": 12,
        "departments": [
            ("Emergency care", 12)
        ]
    },
    "EPSP BAB EL OUED": {
        "name": "EPSP BAB EL OUED",
        "type": "Public",
        "address": "46 BIS OMAR BEN AISSA Bab El Oued, Algiers",
        "coordinates": (36.79475198557144, 3.0472389382798823),
        "capacity": 11,
        "departments": [
            
            ("Emergency care", 11)
        ]
    },
    "EPS ZERALDA": {
        "name": "EPS ZERALDA",
        "type": "Public",
        "address": "Route du plateaux Zeralda , Alger",
        "coordinates": (36.70049352000346, 2.843014051765208),
        "capacity": 6,
        "departments": [
            ("Cardiology", 3),
            ("Emergency Care", 3)
        ]
    }
}

# problem definition
initial_state = "Mosquée Arafat"
state_transition_model = {}

landmark_name = initial_state
formatted_name = format_landmark_name(landmark_name)

formatted_file_path = f'{formatted_name}'  
landmarks, coordinates, distances, traffic = read_locations(formatted_file_path)

location_data = {}
for landmark, coord, distance, traffic in zip(landmarks, coordinates, distances, traffic):
    location_data[landmark] = {'Coordinates': coord, 'Distance': distance, 'Traffic': traffic}





for landmark, data in location_data.items():
    coordinates = data['Coordinates']
    neighboring_landmarks = [neighbor for neighbor, neighbor_data in location_data.items() if neighbor_data['Distance'] > 0]  # You need to define MAX_DISTANCE
    state_transition_model[landmark] = neighboring_landmarks


def get_user_choice():
    print("Choose an algorithm:")
    print("1. A*")
    print("2. Stochastic Hill Climbing")
    print("3. Uniform Cost Search (UCS)")
    print("4. Breadth-First Search (BFS)")
    choice = input("Enter the number of your choice: ")
    return choice

def main():
    choice = get_user_choice()

    if choice == "1":
        algo = "A*"
    elif choice == "2":
        algo = "stochastic"
    elif choice == "3":
        algo = "ucs"
    elif choice == "4":
        algo = "fifo"
    else:
        print("Invalid choice.")
        return

    
    if algo == "A*":
        start_time = time.time()  

        problem = Ambulance(initial_state, None, state_transition_model)
        goal_state = problem.estimate_goal_hospital(initial_state, hospitals_dict)
        print("Estimated goal hospital:", goal_state)
        problem = Ambulance(initial_state, goal_state, state_transition_model)
        solution = GraphSearchAlgorithm(problem, 'A*', initial_state)

        print("A* Solution:")
        if solution:
            print("Cost:", solution.cost)

    elif algo == "stochastic":
        start_time = time.time()  

        problem = Ambulance(initial_state, None, state_transition_model)
        goal_state = problem.estimate_goal_hospital(initial_state, hospitals_dict)
        problem = Ambulance(initial_state, goal_state, state_transition_model)
        solution = GraphSearchAlgorithm(problem, 'stochastic', initial_state)
        print("Local maximum state (Stochastic Hill Climbing):", solution)

    elif algo == 'ucs':
        start_time = time.time()  

        goal_state = "Emergency Care"
        problem = Ambulance(initial_state, goal_state, state_transition_model)
        solution = GraphSearchAlgorithm(problem, 'ucs', initial_state)

    elif algo == 'fifo':
        start_time = time.time()  

        goal_state = "Emergency Care"
        problem = Ambulance(initial_state, goal_state, state_transition_model)
        solution = GraphSearchAlgorithm(problem, 'fifo', initial_state)

    # Calculate the total execution time
    end_time = time.time()  
    execution_time = end_time - start_time 

    if algo == 'A*':
        print("A* Execution time:", execution_time, "seconds")
    elif algo == 'fifo':
        print("BFS Execution time:", execution_time, "seconds")
    elif algo == "ucs":
        print("UCS Execution time:", execution_time, "seconds")
    elif algo == "steepest":
        print("Stochastic Hill Climbing Execution time:", execution_time, "seconds")

if __name__ == "__main__":
    main()