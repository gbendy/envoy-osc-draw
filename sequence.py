from PIL import Image

from still import Still


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
        self.stills[name] = Still(still)

    self.anims = None
    if 'anims' in data:
      self.anims = {}
      for name, anim  in data['anims'].items():
        self.anims[name] = Still(anim)

    self.layers = data['layers']

    if self.stills is None:
      for lyr in self.layers:
        if not lyr.get("disable", False):
          # Cache the still image already.
          pass

  def draw(self, frame, stills):
    base_img = Image.new('RGBA',self.resolution,(0,0,0,0))
    locals = {
      'frame': frame,
      'frames': self.frames,
      'frame_p': frame/( 1 if self.frames == 1 else self.frames-1)
    }
    for layer in self.layers:
      if layer.get('disable',False) == False:
        if layer['type'] == 'still':
          l = layer['still']
          if isinstance(l, str):
            l = stills.get(l, None)
            if l == None:
              raise "Still layer {} unknown".format(layer['still'])
          elif isinstance(l, dict):
            l = Still(l)
          layer_img = l.copy()
        elif layer['type'] == 'anim':
          l = layer['anim']
          if isinstance(l, str):
            l = self.anims.get(layer['anim'],None)
            if l == None:
              raise "Anim layer {} unknown".format(layer['anim'])
          layer_img = Image.new('RGBA',self.resolution,(0,0,0,0))
          l.draw(layer_img,locals)

        mode = layer.get('mode','copy')
        if mode == 'copy':
          base_img = layer_img
        elif mode == 'alpha':
          base_img = Image.alpha_composite(base_img,layer_img)
    return base_img

  def render(self,first,last):
    stills = {}
    if self.stills != None:
      locals = {
        'frame': 0,
        'frames': self.frames,
        'frame_p': 0
      }
      for name, still in self.stills.items():
        im = Image.new('RGBA',self.resolution,(0,0,0,0))
        still.draw(im,locals)
        stills[name] = im
    first = 0 if first == None else first
    last = self.frames if last == None else last
    count = last-first
    for f in range(first,last):
      print('{}/{}'.format(f+1-first,count))
      self.save_image(self.draw(f,stills),f)


  def save_image(self, im, frame):
    im.save('{base}{frame:0{width}}.{ext}'.format(base=self.basename,frame=frame,width=self.width,ext=self.extname),self.format)