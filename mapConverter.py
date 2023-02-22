import matplotlib.pyplot as plt
from tqdm import tqdm
import json
from pyproj import Transformer


class MapConverter:
    def __init__(self, filename):
        self.filename = filename
        self.data = None
        self.nodes = None
        self.ways = None
        self.roads = None
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
            ways = {element["id"]: element["nodes"] for element in data["elements"]
                    if element["type"] == "way"}

            self.data = data
            self.nodes = nodes
            self.ways = ways

    # ------------------ Process the data ------------------

    def count_nodes(self):
        nodes = self.nodes
        ways = self.ways

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

    def convert_to_coordinates(self):
        nodes = self.nodes
        ways = self.ways

        # convert the nodes to x and y coordinates and create a list of roads
        roads = {}
        for id in tqdm(ways):
            path = ways[id]
            x = []
            y = []
            counts = []
            for node in path:
                lon = (nodes[node]["lon"])
                lat = (nodes[node]["lat"])
                transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857")
                x1, y1 = transformer.transform(lon, lat)
                x.append(x1)
                y.append(y1)
                counts.append(nodes[node]["count"])
            roads[id] = {"nodes": [x, y], "counts": counts}

        # find the smallest x and y values and subtract them from all x and y values
        smallestX = min([min(roads[id]["nodes"][0]) for id in roads])
        smallestY = min([min(roads[id]["nodes"][1]) for id in roads])

        self.smallestX = smallestX
        self.smallestY = smallestY

        for id in roads:
            roads[id]["nodes"][0] = [
                x - smallestX for x in roads[id]["nodes"][0]]
            roads[id]["nodes"][1] = [
                y - smallestY for y in roads[id]["nodes"][1]]

        self.roads = roads

    def merge_roads(self):
        roads = self.roads

        # merge roads that are connected and have a count of 2
        for id in tqdm(roads.copy()):
            if id not in roads:
                continue
            if roads[id]["counts"][0] == 2:
                for id2 in roads.copy():
                    if roads[id]["nodes"][0][0] == roads[id2]["nodes"][0][-1] and roads[id]["nodes"][1][0] == roads[id2]["nodes"][1][-1]:
                        roads[id]["nodes"][0] = roads[id2]["nodes"][0] + \
                            roads[id]["nodes"][0]
                        roads[id]["nodes"][1] = roads[id2]["nodes"][1] + \
                            roads[id]["nodes"][1]
                        roads[id]["counts"] = roads[id2]["counts"] + \
                            roads[id]["counts"]
                        del roads[id2]
            if roads[id]["counts"][-1] == 2:
                for id2 in roads.copy():
                    if roads[id]["nodes"][0][-1] == roads[id2]["nodes"][0][0] and roads[id]["nodes"][1][-1] == roads[id2]["nodes"][1][0]:
                        roads[id]["nodes"][0] = roads[id]["nodes"][0] + \
                            roads[id2]["nodes"][0]
                        roads[id]["nodes"][1] = roads[id]["nodes"][1] + \
                            roads[id2]["nodes"][1]
                        roads[id]["counts"] = roads[id]["counts"] + \
                            roads[id2]["counts"]
                        del roads[id2]

    def get_intersections(self):
        nodes = self.nodes
        # get all nodes with a count higher than 2
        intersections = [node for node in nodes if nodes[node]["count"] > 2]
        return intersections

    # ------------------ Plot the data ------------------

    def plot_data(self):
        nodes = self.nodes
        roads = self.roads

        roadParts = [road["nodes"] for road in roads.values()]
        roads = roadParts

        # plot all roads
        for road in roads:
            plt.plot(road[1], road[0], 'k-')

        # plot all nodes with color depending on count
        for id in nodes:
            lon = (nodes[id]["lon"])
            lat = (nodes[id]["lat"])
            transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857")
            x1, y1 = transformer.transform(lon, lat)
            x1 -= self.smallestX
            y1 -= self.smallestY
            if nodes[id]["count"] == 1:
                plt.plot(y1, x1, 'ro')
            elif nodes[id]["count"] == 2:
                plt.plot(y1, x1, 'go')
            else:
                plt.plot(y1, x1, 'bo')
        plt.show()

    # ------------------ Store the data ------------------
    def store_data(self, filename):
        nodes = self.nodes
        roads = self.roads
        intersections = self.get_intersections()
        smallestX = self.smallestX
        smallestY = self.smallestY

        # write to file in formattedMaps folder
        with open(f'formattedMaps/{filename}.txt', 'w') as f:
            # clear the file if it exists
            f.truncate(0)
            f.write(str(len(intersections)) + " " + str(len(roads))+"\n")
            for intersection in intersections:
                lon = (nodes[intersection]["lon"])
                lat = (nodes[intersection]["lat"])
                transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857")
                x1, y1 = transformer.transform(lon, lat)
                x1 -= smallestX
                y1 -= smallestY
                f.write(str(x1) + " " + str(y1)+"\n")
            y = [road[0] for road in roads if not type(road) == int]
            x = [road[1] for road in roads if not type(road) == int]
            for i in range(len(x)):
                f.write(" ".join([str(x1) for x1 in x[i]])+"\n")
            for i in range(len(y)):
                f.write(" ".join([str(y1) for y1 in y[i]])+"\n")

    def create_map(self):
        self.read_data()
        self.count_nodes()
        self.convert_to_coordinates()
        # self.merge_roads()
        self.get_intersections()


if __name__ == "__main__":
    map = MapConverter("maps/mapKatta.json")
    map.create_map()
    map.plot_data()
    print(map.roads)
