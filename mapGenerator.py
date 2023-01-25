import matplotlib.pyplot as plt
from tqdm import tqdm
import json



with open('mapTrondheim.json') as f:
    data = json.load(f)
    nodeList = [element for element in data["elements"] if element["type"] == "node" ]
    nodes = {node["id"]: node for node in nodeList}
    paths = [element for element in data["elements"] if element["type"] == "way" ]

    for path in tqdm(paths):
        lon = []
        lat = []
        for node in path["nodes"]:
            lon.append(nodes[node]["lon"])
            lat.append(nodes[node]["lat"])

        plt.plot(lon, lat, color='blue', linestyle='-', marker='')
    plt.show()



