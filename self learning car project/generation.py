from car import Car
import numpy as np

from copy import deepcopy


class Generation:
    def __init__(self, x, y, width, height, *, amount):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.amount = amount

        self.cars = []
        for i in range(amount):
            self.cars.append(Car(x, y, width, height, mode='AI'))

        self.path = 'leader_weights.npy'
        self.current_leader_hidden_layer = None
        self.current_leader_output_layer = None
        self.upload_weights_from_file()
        # self.current_leader_hidden_layer = deepcopy(self.cars[0].network.hidden_layer)
        # self.current_leader_output_layer = deepcopy(self.cars[0].network.output_layer)

    def save(self):
        self.current_leader_hidden_layer = deepcopy(self.cars[0].network.hidden_layer)
        self.current_leader_output_layer = deepcopy(self.cars[0].network.output_layer)

    def refresh(self):
        self.cars = []
        for i in range(self.amount):
            car = Car(self.x, self.y, self.width, self.height, mode='AI')
            car.network.mutate(self.current_leader_hidden_layer, self.current_leader_output_layer, 0.1)
            self.cars.append(car)

    def select_leader(self):
        self.cars = sorted(self.cars, key=lambda car: car.y, reverse=True)

    def save_leader(self):
        leader = self.cars[0]
        weights = [leader.network.hidden_layer, leader.network.output_layer]
        print(leader.network.output_layer)

        np.save(self.path, weights, allow_pickle=True)

    def upload_weights_from_file(self):
        upload_leader_hidden_layer, upload_leader_output_layer = np.array(np.load(self.path, allow_pickle=True))
        print('Upload: ', upload_leader_output_layer)
        self.current_leader_hidden_layer = deepcopy(upload_leader_hidden_layer)
        self.current_leader_output_layer = deepcopy(upload_leader_output_layer)

    def on_update(self, road_borders, traffic):
        for car in self.cars:
            old_x, old_y = car.x, car.y
            car.on_update(road_borders, traffic)
            if car.x - old_x == 0 and car.y - old_y == 0:
                car.has_damaged = True

        self.select_leader()

    def draw(self, entities_to_draw, batch):
        current_color = (0, 0, 255)

        self.cars[0].draw(entities_to_draw, batch, color=current_color, draw_rays=True)

        for car in self.cars[1:]:
            if not car.has_damaged:
                car.draw(entities_to_draw, batch, color=(0, 0, 255), opacity=40)
            else:
                car.draw(entities_to_draw, batch, color=(142, 142, 142), opacity=100)
