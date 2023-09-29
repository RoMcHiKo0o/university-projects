# encoding=utf-8
from utils import *


class Sensor:
    def __init__(self, car):
        self.car = car
        self.ray_count = 5
        self.ray_length = 150
        self.ray_spread = math.pi / 2

        self.rays = []
        self.readings = []

    def on_update(self, road_borders, traffic):
        self.readings = []
        self.cast_rays()

        for i in self.rays:
            tmp = self.get_reading(i, road_borders, traffic)
            self.readings.append(tmp)

    @staticmethod
    def get_reading(ray, road_borders, traffic):
        touches = []

        for i in road_borders:
            touch = get_intersection(ray[0], ray[1], i[0], i[1])

            if touch is not None:
                touches.append(touch)
        for traffic_car in traffic:
            for i in range(4):
                touch = get_intersection(ray[0], ray[1], traffic_car.points[i], traffic_car.points[(i + 1) % 4])
                if touch is not None:
                    touches.append(touch)

        if len(touches) == 0:
            return ray[1] | {'offset': 1}
        else:
            offsets = [touch["offset"] for touch in touches]
            min_offset = min(offsets)
            ind = offsets.index(min_offset)
            return touches[ind]

    def cast_rays(self):
        self.rays = []
        for i in range(self.ray_count):
            if self.ray_count == 1:
                tmp = 0.5
            else:
                tmp = i / (self.ray_count - 1)
            ray_angle = lerp(-self.ray_spread / 2, self.ray_spread / 2, tmp) + self.car.angle

            start = {"x": self.car.x, "y": self.car.y}

            end = {"x": self.car.x + math.sin(ray_angle) * self.ray_length,
                   "y": self.car.y + math.cos(ray_angle) * self.ray_length}

            self.rays.append([start, end])
