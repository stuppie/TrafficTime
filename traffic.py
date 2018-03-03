"""
Get traffic data every 4 min

2,500 free directions requests per day
https://developers.google.com/maps/documentation/directions/usage-limits

24 hrs, every 4min -> 360 requests
x 2 directions = 720
"""

import requests
import numpy as np
import datetime as dt
import json
import time
import traceback

try:
    from secret import API_KEY, HOME, WORK
except ImportError:
    print("must set API_KEY. Must provide HOME and WORK addresses. See secret_example for example")


def get_traffic_data(origin, destination):
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {'origin': origin, 'destination': destination,
              'departure_time': 'now', 'mode': 'driving',
              'alternatives': 'true', 'key': API_KEY}

    response = requests.get(url, params=params)
    result = response.json()

    # make sure routes are sorted so the first route is the fastest
    sort_order = np.argsort([x['legs'][0]['duration_in_traffic']['value'] for x in result['routes']])
    result['routes'] = [result['routes'][x] for x in sort_order]

    route = result['routes'][0]
    start_address = route['legs'][0]['start_address']
    end_address = route['legs'][0]['end_address']
    duration_in_traffic = route['legs'][0]['duration_in_traffic']['value']
    duration = route['legs'][0]['duration']['value']
    polyline = route['overview_polyline']['points']
    summary = route['summary']
    distance = route['legs'][0]['distance']['value']
    waypoints = [(route['legs'][0]['steps'][0]['start_location']['lat'],
                  route['legs'][0]['steps'][0]['start_location']['lng'])]
    for step in route['legs'][0]['steps']:
        waypoints.append((step['end_location']['lat'],
                          step['end_location']['lng']))

    data = {'duration_in_traffic': duration_in_traffic, 'duration': duration,
            'summary': summary, 'distance': distance, 'waypoints': waypoints,
            'datetime': dt.datetime.now().isoformat(),
            'start_address': start_address, 'end_address': end_address,
            'start_address_query': origin, 'end_address_query': destination}
    return data


def run(origin, destination):
    data = get_traffic_data(origin, destination)
    with open("traffic.json", 'a') as f:
        f.write(json.dumps(data))
        f.write("\n")


if __name__ == "__main__":
    while True:
        try:
            run(origin=HOME, destination=WORK)
            time.sleep(1)
            run(origin=WORK, destination=HOME)
            time.sleep(1)
        except Exception as e:
            traceback.print_exc()
        finally:
            time.sleep(60 * 4)
