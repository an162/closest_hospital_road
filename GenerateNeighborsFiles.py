import math
import random as rnd

def calculate_distance(coord1, coord2):
    # Calculate the distance between two coordinates using Haversine formula
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    radius = 6371000  # Radius of the Earth in meters

    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)

    a = (math.sin(d_lat / 2) * math.sin(d_lat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(d_lon / 2) * math.sin(d_lon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = radius * c

    return distance

def find_nearby_landmarks(initial_place, landmarks, max_distance):
    nearby_landmarks = {}
    for landmark, coords in landmarks.items():
        distance = calculate_distance(initial_place, coords)
        traffic = rnd.random()
        if distance <= max_distance:
            nearby_landmarks[landmark] = {'coordinates': coords, 'distance': distance, 'traffic': traffic}
    return nearby_landmarks

def save_nearby_landmarks_to_files(initial_place, nearby_landmarks):
    filename = f"{initial_place.replace(' ', '_').lower()}_nearby.txt"
    with open(filename, 'w') as file:
        for nearby_landmark, info in nearby_landmarks.items():
            file.write(f"Nearby Landmark: {nearby_landmark}\n")
            file.write(f"Coordinates: {info['coordinates']}\n")
            file.write(f"Distance: {info['distance']:.2f} meters\n")
            file.write(f"Traffic: {info['traffic']}\n")
            file.write("\n")  # Add a blank line between nearby landmarks
            

# Example landmarks dictionary with coordinates
landmarks = {



'Établissement Hospitalier Spécialisé Chirurgie Cardiaque Clinique Mohamed ABDERRAHMANI': (36.73464096531616, 3.0530593158273867),

}



max_distance = 1500

for initial_place, coords in landmarks.items():
    nearby_landmarks = find_nearby_landmarks(coords, landmarks, max_distance)
    save_nearby_landmarks_to_files(initial_place, nearby_landmarks)
