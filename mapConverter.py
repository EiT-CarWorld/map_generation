import matplotlib.pyplot as plt
from tqdm import tqdm
import json
import numpy as np


with open('maps/mapKatta.json') as f:
    data = json.load(f)
    nodeList = [element for element in data["elements"]
                if element["type"] == "node"]
    nodes = {node["id"]: node for node in nodeList}
    ways = {element["id"]: element["nodes"] for element in data["elements"]
            if element["type"] == "way"}

    roads = []
    for id in tqdm(ways):
        path = ways[id]
        lon = []
        lat = []
        for node in path:
            lon.append(nodes[node]["lon"])
            lat.append(nodes[node]["lat"])
        roads.append((lon, lat))

        plt.plot(lon, lat, color='blue', linestyle='-', marker='')

    # write to file in formattedMaps folder
    with open('formattedMaps/mapKatta.txt', 'w') as f:
        # clear the file if it exists
        f.truncate(0)
        f.write(str(len(roads))+"\n")
        lats = [road[0] for road in roads]
        lons = [road[1] for road in roads]
        for i in range(len(roads)):
            f.write(" ".join([str(lat) for lat in lats[i]])+"\n")
        for i in range(len(roads)):
            f.write(" ".join([str(lon) for lon in lons[i]])+"\n")

    plt.show()
