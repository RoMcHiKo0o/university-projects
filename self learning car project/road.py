import pyglet.shapes

from utils import lerp


class Road:
    def __init__(self, x, width, lane_count=3):
        self.x = x
        self.width = width
        self.lane_count = lane_count

        self.left = x - width / 2
        self.right = x + width / 2

        infinity = 1000000

        self.top = infinity
        self.bottom = -infinity

        top_left = {'x': self.left, 'y': self.top}
        top_right = {'x': self.right, 'y': self.top}
        bottom_left = {'x': self.left, 'y': self.bottom}
        bottom_right = {'x': self.right, 'y': self.bottom}

        self.borders = [
            [bottom_left, top_left],
            [bottom_right, top_right]
        ]

    def get_lane_center(self, lane_index):
        lane_width = self.width / self.lane_count

        return self.left + lane_width / 2 + min(lane_index, self.lane_count - 1) * lane_width

    def draw(self, entities_to_draw, batch):
        entities_to_draw.append(
            pyglet.shapes.Line(
                self.left, self.bottom,
                self.left, self.top,
                width=7, color=(0, 0, 0),
                batch=batch)
        )

        for i in range(1, self.lane_count):
            x = lerp(self.left, self.right, i / self.lane_count)

            entities_to_draw.append(
                pyglet.shapes.Line(x, self.bottom,
                                   x, self.top,
                                   width=3, color=(255, 255, 255),
                                   batch=batch)
            )

        entities_to_draw.append(
            pyglet.shapes.Line(
                self.right, self.bottom,
                self.right, self.top,
                width=7, color=(0, 0, 0),
                batch=batch
            )
        )
