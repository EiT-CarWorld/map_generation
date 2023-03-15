import math
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from mapConverter import MapConverter
from shapely.ops import unary_union
from shapely.geometry import Polygon
import mapbox_earcut as earcut
import itertools


class RoadGenerator:

    def __init__(self, points, distance=4):
        self.distance = distance
        self.points = points
        self.first_edge_track = []
        self.second_edge_track = []
        self.border_points = [[], []]
        self.road_polygon = None

    def points_to_vector(self, p1, p2):
        # return the vector from p1 to p2
        return (p2[0] - p1[0], p2[1] - p1[1])

    def scale_vector_to_size(self, vector, size):
        # scale the vector to the given size
        norm = math.sqrt(vector[0] ** 2 + vector[1] ** 2)
        if norm:
            return (vector[0] / norm * size, vector[1] / norm * size)
        return (0, 0)

    def normalize_vector(self, vector):
        # return the normalized vector (scaled to 1)
        return self.scale_vector_to_size(vector, 1)

    def add_vectors(self, v1, v2):
        # return the sum of the two vectors
        return (v1[0] + v2[0], v1[1] + v2[1])

    def rotate_vector(self, vector, angle):
        # rotate the vector by the given angle
        return (vector[0] * math.cos(angle) - vector[1] * math.sin(angle),
                vector[0] * math.sin(angle) + vector[1] * math.cos(angle))

    def get_border_points(self, p1, p2, p3):

        v1 = self.points_to_vector(p1, p2)
        v2 = self.points_to_vector(p2, p3)
        v1 = self.normalize_vector(v1)
        v2 = self.normalize_vector(v2)
        v3 = self.add_vectors(v1, v2)

        extra_distance = self.distance * (1 - np.dot(v1, v2))/2

        v3 = self.scale_vector_to_size(v3, self.distance+extra_distance)

        top = self.rotate_vector(v3, math.pi / 2)
        bottom = self.rotate_vector(v3, -math.pi / 2)

        self.first_edge_track.append(self.add_vectors(p2, top))
        self.second_edge_track.append(self.add_vectors(p2, bottom))

    def get_end_points(self, p1, p2, start):
        v1 = self.points_to_vector(p1, p2)
        v1 = self.normalize_vector(v1)
        v3 = self.scale_vector_to_size(v1, self.distance)

        top = self.rotate_vector(v3, math.pi / 2)
        bottom = self.rotate_vector(v3, -math.pi / 2)

        # add 9 border points rotating around the end point in a half circle
        for i in range(9):
            angle = math.pi / 2 * i / 4
            if start:
                self.border_points[0].append(self.add_vectors(
                    p1, self.rotate_vector(top, angle)))
            else:
                self.border_points[1].append(self.add_vectors(
                    p2, self.rotate_vector(bottom, angle)))

        if start:
            self.first_edge_track.append(self.add_vectors(p1, top))
            self.second_edge_track.append(self.add_vectors(p1, bottom))
        else:
            self.first_edge_track.append(self.add_vectors(p2, top))
            self.second_edge_track.append(self.add_vectors(p2, bottom))

    def generate_track(self):
        self.get_end_points(self.points[0], self.points[1], start=True)
        for i in range(len(self.points) - 2):
            self.get_border_points(self.points[i], self.points[i + 1],
                                   self.points[i + 2])
        self.get_end_points(self.points[-2], self.points[-1], start=False)
        self.create_polygon()

    def create_polygon(self):
        polygon = self.border_points[0][::-1]
        for i in range(len(self.first_edge_track)):
            polygon.append(self.first_edge_track[i])
        for i in range(len(self.border_points[1])):
            polygon.append(self.border_points[1][-i-1])
        for i in range(len(self.second_edge_track)):
            polygon.append(self.second_edge_track[-i-1])

        self.road_polygon = Polygon(polygon).buffer(0)

    def display_road(self):
        self.generate_track()
        x, y = self.road_polygon.exterior.xy
        plt.plot(x, y, 'k-')

        for interior in self.road_polygon.interiors:
            x, y = interior.xy
            plt.plot(x, y, 'k-')


class MapGenerator:
    def __init__(self, road_polygons):
        self.road_polygons = road_polygons
        self.road_network = None

    def merge_roads(self):
        self.road_polygons = [polygon for polygon in self.road_polygons
                              if polygon.is_valid]

        print("Merging roads...")
        merged = unary_union(self.road_polygons)

        if merged.geom_type == 'MultiPolygon':
            merged = max(merged.geoms, key=lambda x: x.area)

        self.road_network = merged
        print("Road network creation complete!")

    def display_map(self):
        map = self.road_network
        x, y = map.exterior.xy
        plt.plot(x, y, 'k-')
        for interior in map.interiors:
            x, y = interior.xy
            plt.plot(x, y, 'k-')
        # plt.show()

    def triangulate(self):
        poly = self.road_network

        vertices = list(zip(poly.exterior.xy[0], poly.exterior.xy[1]))
        holes = [list(zip(interior.xy[0], interior.xy[1]))
                 for interior in poly.interiors]

        # get hole indexes
        hole_indexes = [len(vertices)]
        for hole in holes:
            hole_indexes.append(hole_indexes[-1] + len(hole))

        # add all hole coordinated to vertices
        for hole in holes:
            vertices += hole

        print("Triangulating...")

        # Triangulate the polygon using earcut
        triangles = earcut.triangulate_float32(vertices, hole_indexes)

        return vertices, triangles


if __name__ == '__main__':
    MC = MapConverter("maps/roundabout.json")
    MC.create_map()
    roads = [([[road[0][0][i], road[0][1][i]] for i in range(len(road[0][0]))])
             for road in MC.roads]
    oneway_roads = [road[1] for road in MC.roads]

    road_polygons = []
    print("Generating roads...")
    for i in tqdm(range(len(roads))):
        RG = RoadGenerator(roads[i], distance=(3 if oneway_roads[i] else 5))
        RG.generate_track()
        road_polygons.append(RG.road_polygon)
    MG = MapGenerator(road_polygons)
    MG.merge_roads()

    MG.display_map()
    plt.show()

    vertices, triangles = MG.triangulate()

    poly = MG.road_network
    new_roads = MC.local_roads
    nodes = MC.nodes

    print("Formatting data...")

    id_locations = {}
    new_nodes = []
    for id in nodes:
        if "x" not in nodes[id]:
            continue
        id_locations[id] = len(new_nodes)
        new_nodes.append([nodes[id]["x"], nodes[id]["y"]])

    for i in range(len(new_roads)):
        elem = new_roads[i]
        new_roads[i] = id_locations[elem] if elem in id_locations else elem

    for i in range(len(new_nodes)):
        new_nodes[i][0] -= MC.smallestX
        new_nodes[i][1] -= MC.smallestY

    total_poly_lines = len(poly.exterior.xy[0])-1
    for interior in poly.interiors:
        total_poly_lines += len(interior.xy[0])-1

    print("Writing to file...")
    with open("formattedMaps/roundabout.txt", "w") as f:
        f.truncate(0)
        f.write(f"{len(new_nodes)} {len(new_roads)//3}\n")
        f.write(
            f"{total_poly_lines} {len(vertices)} {len(triangles)//3}\n")
        print("Nodes:")
        for node in tqdm(new_nodes):
            f.write(f"{node[0]} {node[1]}\n")
        print("Roads:")
        for i in tqdm(range(0, len(new_roads)-2, 3)):
            f.write(
                f"{['T','O'][new_roads[i]]} {new_roads[i+1]} {new_roads[i+2]}\n")
        print("Lines:")
        exterior_coords = poly.exterior.xy
        for i in tqdm(range(len(exterior_coords[0])-1)):
            f.write(
                f"{exterior_coords[0][i]} {exterior_coords[1][i]} {exterior_coords[0][i+1]} {exterior_coords[1][i+1]}\n")
        for interior in tqdm(poly.interiors):
            interior_coords = interior.xy
            for i in range(len(interior_coords[0])-1):
                f.write(
                    f"{interior_coords[0][i]} {interior_coords[1][i]} {interior_coords[0][i+1]} {interior_coords[1][i+1]}\n")
        print("Triangulation:")
        for vertex in tqdm(vertices):
            f.write(f"{vertex[0]} {vertex[1]}\n")
        for i in tqdm(range(0, len(triangles)-2, 3)):
            f.write(f"{triangles[i]} {triangles[i+1]} {triangles[i+2]}\n")

    print("All done!")
