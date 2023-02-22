import math
import numpy as np
import matplotlib.pyplot as plt
from mapConverter import MapConverter


class RoadGenerator:

    def __init__(self, points, distance=4):
        self.distance = distance
        self.points = points
        self.first_edge_track = []
        self.second_edge_track = []
        self.border_points = [[], []]

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

        # add 5 border points rotating around the end point in a half circle
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

    def get_tracks(self):
        return self. points, self.first_edge_track, self.second_edge_track

    def create_polygon(self):
        polygon = self.border_points[0][::-1]
        for i in range(len(self.first_edge_track)):
            polygon.append(self.first_edge_track[i])
        for i in range(len(self.border_points[1])):
            polygon.append(self.border_points[1][-i-1])
        for i in range(len(self.second_edge_track)):
            polygon.append(self.second_edge_track[-i-1])

        return polygon

    def display_road(self):
        self.generate_track()
        polygon = self.create_polygon()
        polygon = np.array(polygon)
        plt.plot(polygon[:, 0], polygon[:, 1], 'k-')


if __name__ == '__main__':

    RG = RoadGenerator([(0, 0), (1, 1), (2, 1), (3, 2)], distance=0.5)
    RG.display_road()
    RG2 = RoadGenerator([(5, 7), (3, 6), (3, 3), (3, 2)], distance=0.5)
    RG2.display_road()
    plt.show()
