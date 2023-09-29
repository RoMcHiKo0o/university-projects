import math
import random


def deg_to_rad(d):
    return d / 180 * math.pi


def rad_to_deg(r):
    return r / math.pi * 180


def lerp(a, b, t):
    return a + (b - a) * t


def get_intersection(A, B, C, D):
    t_top = (D["x"] - C["x"]) * (A["y"] - C["y"]) - (D["y"] - C["y"]) * (A["x"] - C["x"])
    u_top = (C["y"] - A["y"]) * (A["x"] - B["x"]) - (C["x"] - A["x"]) * (A["y"] - B["y"])
    bottom = (D["y"] - C["y"]) * (B["x"] - A["x"]) - (D["x"] - C["x"]) * (B["y"] - A["y"])
    if bottom != 0:
        t = t_top / bottom
        u = u_top / bottom
        if 0 <= t <= 1 and 0 <= u <= 1:
            return {"x": lerp(A["x"], B["x"], t),
                    "y": lerp(A["y"], B["y"], t),
                    "offset": t}
        else:
            return None
    return None


def polys_intersect(poly1, poly2):
    for i in range(len(poly1)):
        for j in range(len(poly2)):
            touch = get_intersection(poly1[i], poly1[(i + 1) % len(poly1)], poly2[j], poly2[(j + 1) % len(poly2)])
            if touch:
                return True
    return False


def get_rgba(value):
    alpha = abs(value)
    r = 0 if value < 0 else 255
    g = r
    b = 0 if value > 0 else 255
    return "rgba(" + str(r) + "," + str(g) + "," + str(b) + "," + str(alpha) + ")"


def get_random_color():
    hue = 290 + random.random() * 260
    return "hsl(" + str(hue) + ", 100%, 60%)"
