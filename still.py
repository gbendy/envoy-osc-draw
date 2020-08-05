import aggdraw
from PIL import Image, ImageDraw, ImageFilter

from draw_impl import Background, Line, Trig, FunctionDraw


class Still:
    def __init__(self, data, resolution):
        self.resolution = resolution
        self.background = Background(data, resolution)
        self.lines = [Line(d, resolution) for d in data.get("lines",[])]
        self.trigs = [Trig(d, resolution) for d in data.get("trigs", [])]
        self.funcs = [FunctionDraw(d, resolution) for d in data.get("functions",[])]
        self._cache = None

    def do_draw(self, drawer, image, draw, adraw, state):
        if drawer.glow:
            halo = Image.new('RGBA', [image.width, image.height], (0, 0, 0, 0))
            drawer.draw(halo, ImageDraw.Draw(halo), aggdraw.Draw(halo), state, glow=True)
            blurred_halo = halo.filter(ImageFilter.GaussianBlur(drawer.glow_scale(state)))  # ImageFilter.GaussianBlur(radius=2))
            drawer.draw(blurred_halo, ImageDraw.Draw(blurred_halo), aggdraw.Draw(blurred_halo), state)
            image.alpha_composite(blurred_halo)
        else:
            drawer.draw(image, draw, adraw, state)

    def draw(self, image, state):
        self.background.draw(image, state)

        for line in self.lines:
            self.do_draw(line, image, ImageDraw.Draw(image), aggdraw.Draw(image), state)
        i = 0
        for trig in self.trigs:
            self.do_draw(trig, image, ImageDraw.Draw(image), aggdraw.Draw(image), state)
        for func in self.funcs:
            self.do_draw(func, image, ImageDraw.Draw(image), aggdraw.Draw(image), state)

    def cache_image(self, seq):
        if self._cache is None:
            im = Image.new('RGBA', seq.resolution, (0, 0, 0, 0))
            state = {'frame': 0, 'frames': seq.frames, 'frame_p': 0}
            self.draw(im, state)
            self._cache = im

    def copy(self):
        if self._cache is None:
            return None
        return self._cache.copy()
