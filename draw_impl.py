import math

import aggdraw
from PIL import ImageColor
from PIL import ImageDraw

from utils import convert_value, map_point, get_ag_points


class Animatable:
    def __init__(self, drawer, val):
        self.drawer = drawer
        if isinstance(val, Animatable):
            val = val.val
        self.animated = callable(val)
        self.val = val
        if self.animated:
            self.drawer.animated = True

    def __call__(self, *args, **kwargs):
        if self.animated:
            return self.val(*args, **kwargs)
        else:
            return self.val

class AnimatableColour(Animatable):
    def __call__(self, *args, **kwargs):
        rawcol = super().__call__(*args, **kwargs)
        return self.from_color(rawcol)

    @staticmethod
    def from_color(colour):
        if isinstance(colour, str):
            return ImageColor.getrgb(colour)
        if isinstance(colour, dict):
            rgb = from_color(colour.get('rgb', [255, 255, 255]))
            alpha = colour.get('alpha', 255)
            return (rgb[0], rgb[1], rgb[2], alpha)
        else:
            return tuple(colour)

class BaseDraw:
    def __init__(self, data, resolution):
        self.resolution = resolution
        self.animated = False
        self.colour = AnimatableColour(self, data.get('colour', data.get('color', [255, 255, 255, 255])))
        self.glow = data.get('glow', False)
        self.glow_scale = Animatable(self, data.get('glow_scale', 9))
        self.glow_colour = AnimatableColour(self, data.get('glow_colour', data.get('glow_color', self.colour)))


class Background(BaseDraw):
    def __init__(self, data, resolution):
        super().__init__(data, resolution)
        self.colour = AnimatableColour(self, data.get('background', [0, 0, 0, 0]))

    def draw(self, image, state):
        col = self.colour(state)
        ImageDraw.Draw(image).rectangle(((0, 0), image.size), fill=col)


class Line(BaseDraw):
    def __init__(self, data, resolution):
        super().__init__(data, resolution)
        self._points = Animatable(self, data['points'])
        self.width = Animatable(self, data.get('width', 1))
        self.joint = None
        if data.get('curve', False):
            self.joint = 'curve'
        self.close = data.get('close', False)

    def points(self, *args, **kwargs):
        val = self._points(*args, **kwargs)
        if self.close:
            val = list(val)
            val.append(val[0])
        return val

    def draw(self, image, draw, adraw, state, glow=False):
        points = get_ag_points(self.points(state), image, state)

        # points = tuple(map(lambda pt: map_point(pt,image) , self.points))
        # points = [item for t in points for item in t]
        width = self.width(state)
        if isinstance(width, str):
            width = convert_value(width, image.width - 1, state)

        color = self.glow_colour(state) if glow else self.colour(state)
        if self.joint is None:
            pen = aggdraw.Pen(color,
                              width=width)
            adraw.line(points, pen)
            adraw.flush()
        else:
            draw.line(points, fill=color, width=int(width), joint=self.joint)

class FunctionDraw(BaseDraw):
    def __init__(self, data, resolution):
        super().__init__(data, resolution)
        self.width = Animatable(self, data.get('width', 1))
        self.origin = Animatable(self, data.get('origin', [0, 0.5]))
        self.still_callable=data["function"]
        self.params = []
        for param_name, value in data.get("parameters", {}).items():
            self.params.append(param_name)
            setattr(self, param_name, Animatable(self, value))

    def __call__(self, x, state, params):

        return self.still_callable(x, self.resolution, state, **params)

    def draw(self, image, draw, adraw, state, glow=False):
        width = self.width(state)
        origin = self.origin(state)
        origin = (origin[0] * self.resolution[0], origin[1] * self.resolution[1]  * -1)
        col = self.glow_colour(state) if glow else self.colour(state)
        real_width = convert_value(width, image.width-1, state)
        params = {
            p: getattr(self, p)(state)
            for p in self.params
        }
        points = []
        pen = aggdraw.Pen(col, width=real_width)
        for x in range(self.resolution[0]):
            y = self(x, state, params)
            points.extend([x + origin[0], -(y + origin[1])])

        adraw.line(points, pen)
        adraw.flush()

class Trig(BaseDraw):
    def __init__(self, data, resolution):
        super().__init__(data, resolution);
        self.start = data['start'];
        self.length = data.get('length', 1)
        self.period = data.get('period', 1)
        self.amplitude = data.get('amplitude', 1)
        self.offset = data.get('offset')
        self.width = data.get('width', 1)

        method = data.get('method', 'cos')
        if method == 'cos':
            self.op = math.cos
        elif method == 'sin':
            self.op = math.sin
        elif method == 'tan':
            self.op = math.tan
        elif method == 'cosh':
            self.op = math.cosh
        elif method == 'sinh':
            self.op = math.sinh
        elif method == 'tanh':
            self.op = math.tanh
        else:
            raise 'Unsupported trig operation {}'.format(method)

    def doop(self, x, offset, period, amplitude):
        return self.op(2 * math.pi * (x + offset) / period) * amplitude

    def draw(self, image, draw, adraw, state, glow=False):
        pen = aggdraw.Pen(self.glow_colour(state) if glow else self.colour(state),
                          width=convert_value(self.width, image.width - 1, state))
        start = map_point(self.start, image, state)
        length = convert_value(self.length, image.width - 1, state)
        period = convert_value(self.period, image.width - 1, state)
        amplitude = convert_value(self.amplitude, image.height - 1, state)
        offset = convert_value(self.offset, image.width - 1, state)

        points = []
        for x in range(int(length)):
            y = self.doop(x, offset, period, amplitude)
            points.extend([x + start[0], y + start[1]])
        # last point which may be fractional
        if x != length:
            y = self.doop(length, offset, period, amplitude)
            points.extend([length + start[0], y + start[1]])

        # print(points)
        adraw.line(points, pen)
        adraw.flush()


def from_color(colour):
    if isinstance(colour, str):
        return ImageColor.getrgb(colour)
    if isinstance(colour, dict):
        rgb = from_color(colour.get('rgb', [255, 255, 255]))
        alpha = colour.get('alpha', 255)
        return (rgb[0], rgb[1], rgb[2], alpha)
    else:
        return tuple(colour)
