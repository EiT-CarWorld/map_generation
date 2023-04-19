import matplotlib.pyplot as plt
from tqdm import tqdm
import json
from haversine import haversine, Unit


class MapConverter:
    def __init__(self, filename):
        self.filename = filename
        self.data = None
        self.nodes = None
        self.ways = None
        self.roads = None
        self.local_roads = []
        self.smallestX = None
        self.smallestY = None

    # ------------------ Read the data ------------------

    def read_data(self):

        with open(self.filename) as f:

            # initializing the nodes
            data = json.load(f)
            nodeList = [element for element in data["elements"]
                        if element["type"] == "node"]
            nodes = {node["id"]: node for node in nodeList}
            ways = {element["id"]: [element["nodes"], "oneway" in element["tags"]] for element in data["elements"]
                    if element["type"] == "way" and "tunnel" not in element["tags"]}

            self.data = data
            self.nodes = nodes
            self.ways = ways

    # ------------------ Process the data ------------------

    def convert_to_coordinates(self):
        nodes = self.nodes
        ways = self.ways

        # convert the nodes to x and y coordinates and create a list of roads
        roads = []
        print("Converting map data to local coordinates...")
        for id in tqdm(ways):
            path = ways[id][0]
            x = []
            y = []
            ids = []
            for node in path:
                lon = (nodes[node]["lon"])
                lat = (nodes[node]["lat"])
                x1 = haversine((0, 0), (0, lon), unit=Unit.METERS)
                y1 = haversine((0, 0), (lat, 0), unit=Unit.METERS)
                x.append(x1)
                y.append(y1)
                # add x and y to nodes
                nodes[node]["x"] = x1
                nodes[node]["y"] = y1
                ids.extend([node, ways[id][1], node])
            roads.append([[x, y], ways[id][1]])
            self.local_roads.extend(ids[1:-2])

        # find the smallest x and y values and subtract them from all x and y values
        smallestX = min([min(road[0][0]) for road in roads])
        smallestY = min([min(road[0][1]) for road in roads])
        self.smallestX = smallestX
        self.smallestY = smallestY

        for i in range(len(roads)):
            roads[i][0][0] = [
                x - smallestX for x in roads[i][0][0]]
            roads[i][0][1] = [
                y - smallestY for y in roads[i][0][1]]

        self.roads = roads

    # ------------------ Plot the data ------------------

    def plot_data(self):
        roads = self.roads

        # plot all roads
        for road in roads:
            plt.plot(road[0][0], road[0][1], 'k-')
        plt.show()

    def create_map(self):
        self.read_data()
        self.convert_to_coordinates()
