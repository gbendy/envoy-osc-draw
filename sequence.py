from PIL import Image

from still import Still
from layer import Layer

class Sequence:
  def __init__(self, data):
    self.resolution = data['resolution']
    self.frames = data['frames']
    self.basename = data['output']['basename']
    self.width = data['output']['width']
    self.extname = data['output']['extname']
    self.format = data['output']['format']
    self.stills = None
    if 'stills' in data:
      self.stills = {}
      for name, still  in data['stills'].items():
        self.stills[name] = Still(still, resolution=self.resolution)

    self.anims = None
    if 'anims' in data:
      self.anims = {}
      for name, anim  in data['anims'].items():
        self.anims[name] = Still(anim, resolution=self.resolution)

    for lyr in data['layers']:
      self.layers = [ Layer(lyr, self) for lyr in data['layers'] ]

  def draw(self, frame):
    locals = {
      'frame': frame,
      'frames': self.frames,
      'frame_p': frame/( 1 if self.frames == 1 else self.frames-1)
    }
    base_img = None
    for layer in self.layers:
      if layer.active:
        if layer.is_still:
          layer_img = layer.still.copy()
        elif layer.is_anim:
          layer_img = Image.new('RGBA',self.resolution,(0,0,0,0))
          layer.still.draw(layer_img,locals)
        if layer.copy_layer:
          base_img = layer_img
        elif layer.alpha_layer:
          if base_img is None:
            base_img = Image.new('RGBA', self.resolution, (0, 0, 0, 0))
          base_img = Image.alpha_composite(base_img,layer_img)
    return base_img

  def render(self,first,last):
    first = 0 if first is None else first
    last = self.frames if last is None else last
    count = last-first
    for f in range(first,last):
      print('{}/{}'.format(f+1-first,count))
      self.save_image(self.draw(f),f)


  def save_image(self, im, frame):
    im.save('{base}{frame:0{width}}.{ext}'.format(base=self.basename,frame=frame,width=self.width,ext=self.extname),self.format)