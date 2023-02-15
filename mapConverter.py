import matplotlib.pyplot as plt
from tqdm import tqdm
import json
import numpy as np


def split_line(p1, p2, width):
    # Calculate the unit normal vector of the line
    diff = p2 - p1
    normal = np.array([-diff[1], diff[0]])
    normal = normal / np.linalg.norm(normal)

    # Multiply the normal vector by half of the width
    normal = normal * (width / 2)

    # Determine which direction the normal vector should point
    mid_point = (p1 + p2) / 2
    if mid_point[0] > 0 and mid_point[1] > 0:
        normal = -normal

    # Calculate the two new end points
    p1_new = p1 - normal
    p2_new = p2 - normal
    p3_new = p1 + normal
    p4_new = p2 + normal

    # Return the two new lines
    return [(p1_new, p2_new), (p3_new, p4_new)]


with open('maps/mapKatta.json') as f:
    data = json.load(f)
    nodeList = [element for element in data["elements"]
                if element["type"] == "node"]
    nodes = {node["id"]: node for node in nodeList}
    paths = [element for element in data["elements"]
             if element["type"] == "way"]
    print(nodes)

    for path in tqdm(paths):
        lon = []
        lat = []
        for node in path["nodes"]:
            lon.append(nodes[node]["lon"])
            lat.append(nodes[node]["lat"])

        plt.plot(lon, lat, color='blue', linestyle='-', marker='')
    plt.show()
