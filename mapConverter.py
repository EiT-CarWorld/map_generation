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

    def convert_to_coordinates(self):
        nodes = self.nodes
        ways = self.ways

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
        smallestX = min([min(road[0]) for road in roads])
        smallestY = min([min(road[1]) for road in roads])

        for i in range(len(roads)):
            roads[i][0] = [
                x - smallestX for x in roads[i][0]]
            roads[i][1] = [
                y - smallestY for y in roads[i][1]]

        self.roads = roads

    # ------------------ Plot the data ------------------

    def plot_data(self):
        roads = self.roads

        # plot all roads
        for road in roads:
            plt.plot(road[1], road[0], 'k-')
        plt.show()

    # ------------------ Store the data ------------------
    def store_data(self, filename):
        roads = self.roads

        # write to file in formattedMaps folder
        with open(f'formattedMaps/{filename}.txt', 'w') as f:
            # clear the file if it exists
            f.truncate(0)
            f.write(str(str(len(roads))+"\n"))
            y = [road[0] for road in roads if not type(road) == int]
            x = [road[1] for road in roads if not type(road) == int]
            for i in range(len(x)):
                f.write(" ".join([str(x1) for x1 in x[i]])+"\n")
            for i in range(len(y)):
                f.write(" ".join([str(y1) for y1 in y[i]])+"\n")

    def create_map(self):
        self.read_data()
        self.convert_to_coordinates()
        self.plot_data()


if __name__ == "__main__":
    map = MapConverter("maps/mapKatta.json")
    map.create_map()
