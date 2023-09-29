import math

from pyglet.window import key

import pyglet.shapes

from sensor import Sensor

from utils import polys_intersect
from utils import rad_to_deg

from neural_network import NN

"""
добавил траффик в main
добавил метод create_polygon в Car 
добавил углы машины в переменную points (аналог polygon)
"""


class Car:
    def __init__(self, x, y, width, height, *, mode='Control'):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.mode = mode

        self.speed = 0
        self.acceleration = 0.2
        self.maxSpeed = 3
        self.friction = 0.05
        self.angle = 0

        self.has_damaged = False

        # Controls
        self.keys = dict(left=False, right=False, up=False, down=False)

        # Ray cast
        self.sensor = Sensor(self)
        self.network = NN()
        self.points = self.create_polygon()

    def create_polygon(self):
        points = []
        rad = math.hypot(self.width / 2, self.height / 2)
        alpha = math.atan2(self.width, self.height)
        points.append({
            "x": self.x - math.sin(self.angle - alpha) * rad,
            "y": self.y - math.cos(self.angle - alpha) * rad
        })
        points.append({
            "x": self.x - math.sin(self.angle + alpha) * rad,
            "y": self.y - math.cos(self.angle + alpha) * rad
        })
        points.append({
            "x": self.x - math.sin(math.pi + self.angle - alpha) * rad,
            "y": self.y - math.cos(math.pi + self.angle - alpha) * rad
        })
        points.append({
            "x": self.x - math.sin(math.pi + self.angle + alpha) * rad,
            "y": self.y - math.cos(math.pi + self.angle + alpha) * rad
        })

        return points

    def on_key_press(self, symbol, modifiers):
        if self.mode != 'Control':
            return

        if symbol == key.UP:
            self.keys['up'] = True
        if symbol == key.DOWN:
            self.keys['down'] = True
        elif symbol == key.LEFT:
            self.keys['left'] = True
        elif symbol == key.RIGHT:
            self.keys['right'] = True

    def on_key_release(self, symbol, modifiers):
        if self.mode != 'Control':
            return

        if symbol == key.UP:
            self.keys['up'] = False
        if symbol == key.DOWN:
            self.keys['down'] = False
        elif symbol == key.LEFT:
            self.keys['left'] = False
        elif symbol == key.RIGHT:
            self.keys['right'] = False

    def ai_update(self):
        # NN step
        offsets = []
        for reading in self.sensor.readings:
            offsets.append(1 - reading['offset'])

        nn_response = self.network.step(offsets)

        self.keys['up'] = bool(nn_response[0] + 1)
        self.keys['right'] = bool(nn_response[1] + 1)
        self.keys['down'] = bool(nn_response[2] + 1)
        self.keys['left'] = bool(nn_response[3] + 1)

    def check_collision(self, road_borders, traffic):
        car_polygon = self.create_polygon()

        for border in road_borders:
            if polys_intersect(car_polygon, border):
                return True

        for car in traffic:
            traffic_car_polygon = car.create_polygon()
            if polys_intersect(car_polygon, traffic_car_polygon):
                return True

        if self.y < -10:
            return True

        return False

    def on_update(self, road_borders, traffic):
        # Check for colliding
        self.has_damaged = self.check_collision(road_borders, traffic)

        if self.has_damaged:
            return

        # Update ray casting
        self.sensor.on_update(road_borders, traffic)

        if self.mode == 'AI':
            self.ai_update()

        if self.keys['up']:
            self.speed += self.acceleration

        if self.keys['down']:
            self.speed -= self.acceleration

        if self.speed > self.maxSpeed:
            self.speed = self.maxSpeed

        if self.speed < - self.maxSpeed / 2:
            self.speed = -self.maxSpeed / 2

        if self.speed > 0:
            self.speed -= self.friction

        if self.speed < 0:
            self.speed += self.friction

        if math.fabs(self.speed) < self.friction:
            self.speed = 0

        if self.speed != 0:
            if self.speed > 0:
                flip = 1
            else:
                flip = -1

            if self.keys['left']:
                self.angle -= 0.03 * flip

            if self.keys['right']:
                self.angle += 0.03 * flip

        # Update position of the car
        self.x += math.sin(self.angle) * self.speed
        self.y += math.cos(self.angle) * self.speed

    def draw(self, entities_to_draw, batch, *, color=(0, 0, 0), opacity=500, draw_rays=False):
        car_rect = pyglet.shapes.Rectangle(
            self.x, self.y,
            self.width, self.height,
            color=color, batch=batch)

        car_rect.anchor_x = self.width / 2
        car_rect.anchor_y = self.height / 2
        car_rect.rotation = rad_to_deg(self.angle)
        car_rect.opacity = opacity

        if draw_rays:
            for i in range(self.sensor.ray_count):
                entities_to_draw.append(
                    pyglet.shapes.Line(
                        self.sensor.rays[i][0]['x'], self.sensor.rays[i][0]['y'],
                        self.sensor.readings[i]['x'], self.sensor.readings[i]['y'],
                        2,
                        color=(255, 255, 0),
                        batch=batch
                    )
                )

                entities_to_draw.append(
                    pyglet.shapes.Line(
                        self.sensor.readings[i]['x'], self.sensor.readings[i]['y'],
                        self.sensor.rays[i][1]['x'], self.sensor.rays[i][1]['y'],
                        2,
                        color=(0, 0, 0),
                        batch=batch
                    )
                )

        entities_to_draw.append(car_rect)
