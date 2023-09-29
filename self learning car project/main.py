import pyglet.clock
import pyglet.resource

from car import Car
from road import Road

from generation import Generation

from gui import Button

game_window_width, game_window_height = 500, 700

game_window = pyglet.window.Window(game_window_width, game_window_height, 'Car simulation')
main_batch = pyglet.graphics.Batch()

save_button_image = pyglet.resource.image('icons/save.png')
refresh_button_image = pyglet.resource.image('icons/refresh.png')
upload_button_image = pyglet.resource.image('icons/upload.png')

save_button = Button(5, 10, 24, 24, color=(255, 255, 255), img=save_button_image, batch=main_batch)
refresh_button = Button(39, 10, 24, 24, color=(255, 255, 255), img=refresh_button_image, batch=main_batch)
upload_button = Button(73, 10, 24, 24, color=(255, 255, 255), img=upload_button_image, batch=main_batch)

road = Road(game_window_width / 2, 200)

traffic = [Car(road.get_lane_center(0), game_window_height / 2 + 100, 30, 50),
           Car(road.get_lane_center(0), game_window_height / 2 - 200, 30, 50),
           Car(road.get_lane_center(1), game_window_height / 2 - 80, 30, 50),
           Car(road.get_lane_center(2), game_window_height / 2 + 75, 30, 50),
           Car(road.get_lane_center(1), game_window_height / 2 + 200, 30, 50)]

generation = Generation(game_window_width / 2, 50, 30, 50, amount=70)

# Initial step
generation.on_update(road.borders, traffic)
game_window.push_handlers(save_button)
game_window.push_handlers(refresh_button)
game_window.push_handlers(upload_button)


def save_action(self):
    generation.save()
    generation.save_leader()


def refresh_action(self):
    generation.refresh()


def upload_action(self):
    generation.upload_weights_from_file()


setattr(save_button, 'callback', save_action)
setattr(refresh_button, 'callback', refresh_action)
setattr(upload_button, 'callback', upload_action)


def on_update(dt):
    generation.on_update(road.borders, traffic)


@game_window.event
def on_draw():
    game_window.clear()
    entities_to_draw = []

    bg = pyglet.shapes.Rectangle(
        0, 0,
        game_window_width,
        game_window_height,
        color=(230, 230, 230),
        batch=main_batch)

    # Drawing buttons
    save_button.draw(entities_to_draw, main_batch)
    refresh_button.draw(entities_to_draw, main_batch)
    upload_button.draw(entities_to_draw, main_batch)

    # Drawing road
    road.draw(entities_to_draw, main_batch)

    # Drawing traffic
    for traffic_car in traffic:
        traffic_car.draw(entities_to_draw, main_batch, color=(255, 0, 0))

    # Drawing cars
    # car.draw(entities_to_draw, main_batch, color=(140, 0, 255), draw_rays=True)
    generation.draw(entities_to_draw, main_batch)

    main_batch.draw()
    save_button.icon.draw()
    refresh_button.icon.draw()
    upload_button.icon.draw()


if __name__ == '__main__':
    pyglet.clock.schedule_interval(on_update, 1 / 120.0)
    pyglet.app.run()
