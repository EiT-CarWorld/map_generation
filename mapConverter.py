import matplotlib.pyplot as plt
from tqdm import tqdm
import json
import numpy as np
import geopandas as gpd
from pyproj import Transformer

with open('maps/mapKatta.json') as f:

    # ------------------ Read the data ------------------

    # initializing the nodes
    data = json.load(f)
    nodeList = [element for element in data["elements"]
                if element["type"] == "node"]
    nodes = {node["id"]: node for node in nodeList}
    ways = {element["id"]: element["nodes"] for element in data["elements"]
            if element["type"] == "way"}

    # ------------------ Process the data ------------------

    # count the number of times a node is used
    for id in nodes:
        nodes[id]["count"] = 0

    for id in ways:
        path = ways[id]
        for node in path:
            if node in nodes:
                if node == path[0] or node == path[-1]:
                    nodes[node]["count"] += 1
                else:
                    nodes[node]["count"] += 2

    # convert the nodes to x and y coordinates and create a list of roads
    roads = []
    for id in tqdm(ways):
        path = ways[id]
        x = []
        y = []
        for node in path:
            lon = (nodes[node]["lon"])
            lat = (nodes[node]["lat"])
            transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857")
            x1, y1 = transformer.transform(lon, lat)
            x.append(x1)
            y.append(y1)
        roads.append([x, y])

    # find the smallest x and y values and subtract them from all x and y values
    smallestX = min([min(road[0]) for road in roads if len(road[0]) > 0])
    smallestY = min([min(road[1]) for road in roads if len(road[1]) > 0])
    for road in roads:
        road[0] = [x - smallestX for x in road[0]]
        road[1] = [y - smallestY for y in road[1]]

    # ------------------ Plot the data ------------------

    # plot all roads
    for road in roads:
        plt.plot(road[0], road[1], 'k-')

    # plot all nodes with color depending on count
    for id in nodes:
        lon = (nodes[id]["lon"])
        lat = (nodes[id]["lat"])
        transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857")
        x1, y1 = transformer.transform(lon, lat)
        x1 -= smallestX
        y1 -= smallestY
        if nodes[id]["count"] == 1:
            plt.plot(x1, y1, 'ro')
        elif nodes[id]["count"] == 2:
            plt.plot(x1, y1, 'go')
        else:
            plt.plot(x1, y1, 'bo')

    # ------------------ Store the data ------------------

    # write to file in formattedMaps folder
    with open('formattedMaps/mapKatta.txt', 'w') as f:
        # clear the file if it exists
        f.truncate(0)
        f.write(str(len(roads))+"\n")
        y = [road[0] for road in roads]
        x = [road[1] for road in roads]
        for i in range(len(roads)):
            f.write(" ".join([str(x1) for x1 in x[i]])+"\n")
        for i in range(len(roads)):
            f.write(" ".join([str(y1) for y1 in y[i]])+"\n")

    plt.show()
