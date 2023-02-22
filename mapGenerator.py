import math
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from mapConverter import MapConverter
from shapely.ops import unary_union
from shapely.geometry import Polygon


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

    def merge_roads(self):
        self.road_polygons = [polygon for polygon in self.road_polygons
                              if polygon.is_valid]

        merged = unary_union(self.road_polygons)

        if merged.geom_type == 'MultiPolygon':
            merged = max(merged.geoms, key=lambda x: x.area)

        return merged

    def display_map(self):
        map = self.merge_roads()
        x, y = map.exterior.xy
        plt.plot(x, y, 'k-')
        for interior in map.interiors:
            x, y = interior.xy
            plt.plot(x, y, 'k-')
        plt.show()


if __name__ == '__main__':
    MC = MapConverter("maps/mapTrondheim.json")
    MC.create_map()
    roads = [([[road[0][1][i], road[0][0][i]] for i in range(len(road[0][0]))])
             for road in MC.roads]

    oneway_roads = [road[1] for road in MC.roads]

    road_polygons = []
    print("Generating roads...")
    for i in range(len(roads)):
        RG = RoadGenerator(roads[i], distance=(3 if oneway_roads[i] else 6))
        RG.generate_track()
        road_polygons.append(RG.road_polygon)
    MG = MapGenerator(road_polygons)
    MG.display_map()
