import pyglet.shapes


class Button:
    def __init__(self, x, y, width, height, color=(0, 0, 0), border_color=(0, 0, 0), img=None, batch=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.border_color = border_color
        self.img = img
        self.icon = pyglet.sprite.Sprite(img=self.img, x=self.x, y=self.y, batch=batch)

        self.button = None
        self.active = False

    def on_mouse_press(self, x, y, button, modifiers):
        if self.x < x < self.x + self.width:
            if self.y < y < self.y + self.height:
                if hasattr(self, 'callback'):
                    self.callback(self)
                    print("<Mouse x='%s' y='%s' save_button='%s'>" % (x, y, button))

    def draw(self, entities_to_draw, batch):
        self.button = pyglet.shapes.BorderedRectangle(self.x, self.y, self.width, self.height, border=2, batch=batch)
        self.button.color = self.color
        self.button.border_color = self.border_color

        entities_to_draw.append(self.button)
