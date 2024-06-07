import requests

def search_places(api_key, bbox, keyword=None):
    url = 'https://api.openrouteservice.org/geocode/search'
    params = {
        'api_key': api_key,
        'text': keyword,
        'boundary.rect.min_lat': bbox[0],
        'boundary.rect.min_lon': bbox[1],
        'boundary.rect.max_lat': bbox[2],
        'boundary.rect.max_lon': bbox[3],
        'size': 10  # Limit the number of results to 10
    }
    response = requests.get(url, params=params)
    data = response.json()

    if 'features' in data:
        places = [place['properties']['name'] for place in data['features']]
        return places
    else:
        print('Error:', data)
        return None

# Replace 'YOUR_API_KEY' with your actual OpenRouteService API key
api_key = '5b3ce3597851110001cf6248f4fe92f9f641482bbade894ba57aa967'
#New hospital coordinates:
latitude = 36.76199
longitude = 3.05343
radius = 0.020499
# Bounding box around the new hospital location
# Bounding box around the new hospital location
bbox = [latitude - radius, longitude - radius, latitude + radius, longitude + radius]
  # Define bounding box coordinates around the new hospital

# Example keyword to filter places (optional)
keyword = ['restaurant', 'park', 'pharmacy', 'supermarket']  # Example keywords to search for various types of places

# Example usage:
places = search_places(api_key, bbox, keyword)
if places is not None:
    print('Places found around the new hospital:')
    for place in places:
        print(place)