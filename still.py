import aggdraw
from PIL import Image, ImageDraw, ImageFilter

from draw_impl import Line, Trig, from_color


class Still:
  def __init__(self, data):
    self.background = from_color(data.get('background', [ 0, 0, 0, 0 ]))
    self.lines = None
    if 'lines' in data:
      self.lines = list(map(Line, data['lines']))
    self.trigs = None
    if 'trigs' in data:
      self.trigs = list(map(Trig, data['trigs']))
    self.glow_kernel = [
                        0, 1, 2, 1, 0,
                        1, 2, 4, 2, 1,
                        2, 4, 8, 4, 1,
                        1, 2, 4, 2, 1,
                        0, 1, 2, 1, 0 ]
    self.glow_kernelsum = sum(self.glow_kernel)
    self._cache = None

  def do_draw(self,drawer,image,draw,adraw,locals):
    if drawer.glow:
      halo = Image.new('RGBA',[image.width,image.height],(0,0,0,0))
      drawer.draw(halo,ImageDraw.Draw(halo),aggdraw.Draw(halo),locals,glow=True)
      filter = ImageFilter.Kernel((5, 5), self.glow_kernel, scale = drawer.glow_scale * self.glow_kernelsum)
      blurred_halo = halo.filter(ImageFilter.GaussianBlur(9))#ImageFilter.GaussianBlur(radius=2))
      blurred_halo.save('aa.png')
      drawer.draw(blurred_halo,ImageDraw.Draw(blurred_halo),aggdraw.Draw(blurred_halo),locals)
      image.alpha_composite(blurred_halo)
    else:
      drawer.draw(image,draw,adraw,locals)

  def draw(self, image, locals):
    ImageDraw.Draw(image).rectangle(((0,0),image.size),fill=self.background)

    if self.lines != None:
      for line in self.lines:
        self.do_draw(line,image,ImageDraw.Draw(image),aggdraw.Draw(image),locals)
        #line.draw(image,draw,adraw,locals)
    if self.trigs != None:
      i=0
      for trig in self.trigs:
        self.do_draw(trig,image,ImageDraw.Draw(image),aggdraw.Draw(image),locals)
        image.save('bb{}.png'.format(i))
        i=i+1
        #trig.draw(image,draw,adraw,locals)

  def cache_image(self, seq):
    if self._cache is None:
      im = Image.new('RGBA', seq.resolution, (0, 0, 0, 0))
      state = {'frame': 0, 'frames': seq.frames, 'frame_p': 0}
      self.draw(im, state)
      self._cache= im

  def copy(self):
    if self._cache is None:
      return None
    return self._cache.copy()

