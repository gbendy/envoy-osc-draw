from PIL import Image, ImageDraw, ImageColor, ImageChops, ImageFilter
import aggdraw
import json
import sys
import math
import re
import os
import multiprocessing
import signal
import time
import traceback

def from_color(colour):
  if isinstance(colour, str):
    return ImageColor.getrgb(colour)
  if isinstance(colour,dict):
    rgb = from_color(colour.get('rgb',[255,255,255]))
    alpha = colour.get('alpha',255)
    return (rgb[0],rgb[1],rgb[2],alpha)
  else:
    return tuple(colour)

pixel_match = r"((?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)px"
percent_match = r"((?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)%"

def convert_value(p,factor,locals={}):
  if isinstance(p, str):
    # is a string, want to eval it to get our result
    # first of all convert our numeric values
    match = re.search(pixel_match,p)
    while match:
      p = p[0:match.start(0)] + match.group(1) + p[match.end(0):]
      match = re.search(pixel_match,p)

    match = re.search(percent_match,p)
    while match:
      p = p[0:match.start(0)] + str((float(match.group(1)) * factor/100)) + p[match.end(0):]
      match = re.search(percent_match,p)

    #print(eval(p,globals(),locals))
    return eval(p,globals(),locals) #raise 'Unsupported coordinate value {}'.format(p)
  else:
    return p * factor

def convert_coordinate(p,factor,locals={}):
  return convert_value(p,factor,locals)+0.5

def map_point(pt,image,locals={}):
  return (convert_coordinate(pt[0],image.width-1,locals),convert_coordinate(pt[1],image.height-1,locals))

def get_ag_points(pts,image,locals={}):
  points = map(lambda pt: map_point(pt,image,locals) , pts)
  return [item for t in points for item in t]

class BaseDraw:
  def __init__(self,data):
    self.colour = from_color(data.get('colour',data.get('color',[255,255,255,255])))
    self.glow = data.get('glow',False)
    self.glow_scale = data.get('glow_scale',0.5)
    self.glow_colour = from_color(data.get('glow_colour',data.get('glow_color',self.colour)))

class Line(BaseDraw):
  def __init__(self, data):
    super().__init__(data);
    self.colour = from_color(data.get('colour',data.get('color',[255,255,255,255])))
    self.points = data['points']
    self.width = data.get('width',1)
    self.joint = None
    if data.get('curve',False):
      self.joint = 'curve'
    if data.get('close',False):
      self.points.append(self.points[0])
    
  def draw(self, image, draw, adraw, locals, glow=False):
    points = get_ag_points(self.points,image,locals)

    #points = tuple(map(lambda pt: map_point(pt,image) , self.points))
    #points = [item for t in points for item in t]
    pen = aggdraw.Pen(self.glow_colour if glow else self.colour,width=convert_value(self.width,image.width-1,locals))
    adraw.line(points,pen)
    adraw.flush()
    #draw.line(points,fill=self.colour,width=self.width,joint=self.joint)
      
class Trig(BaseDraw):
  def __init__(self,data):
    super().__init__(data);
    self.start = data['start'];
    self.length = data.get('length',1)
    self.period = data.get('period',1)
    self.amplitude = data.get('amplitude',1)
    self.offset = data.get('offset')
    self.width = data.get('width',1)

    method = data.get('method','cos')
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
    return self.op(2 * math.pi * (x+offset) / period) * amplitude

  def draw(self, image, draw, adraw, locals, glow=False):
    pen = aggdraw.Pen(self.glow_colour if glow else self.colour,width=convert_value(self.width,image.width-1,locals))
    start = map_point(self.start,image,locals)
    length = convert_value(self.length,image.width-1,locals)
    period = convert_value(self.period,image.width-1,locals)
    amplitude = convert_value(self.amplitude,image.height-1,locals)
    offset = convert_value(self.offset,image.width-1,locals)

    points = []
    for x in range(int(length)):
      y = self.doop(x,offset,period,amplitude)
      points.extend([x+start[0],y+start[1]])
    # last point which may be fractional
    if x != length:
      y = self.doop(length,offset,period,amplitude)
      points.extend([length+start[0],y+start[1]])

    #print(points)
    adraw.line(points,pen)
    adraw.flush()

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
          l = stills.get(layer['still'],None)
          if l == None:
            raise "Still layer {} unknown".format(layer['still'])
          layer_img = l.copy()
        elif layer['type'] == 'anim':
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

def run(args):
  try:
    data,first,last = args
    Sequence(data).render(first,last)
  except KeyboardInterrupt:
    return
  except Exception as e:
    print(traceback.format_exc())
    return    

def main(argv):
  start_time = time.time()

  if len(argv) == 0:
    print('usage: {} render.json'.format(sys.argv[0]))
    return 1
  
  with open(argv[0]) as f:
    data = json.load(f)

  pool_size = os.cpu_count()*2
  frames = data['frames']
  if frames < pool_size:
    pool_size = frames;
    count = 1
  else:
    count = math.floor(frames / pool_size) + 1
  jobs = []
  for f in range(0, pool_size):
    start = f*count
    end = start + count
    jobs.append([data,start,end if end < frames else frames ])
  
  pool = multiprocessing.Pool(pool_size)
  try:
    pool.map(run, jobs)
    pool.close()
    pool.join()
  except KeyboardInterrupt:
    # Allow ^C to interrupt from any thread.
    print("Caught KeyboardInterrupt, terminating workers")
    pool.terminate()    
 
   #Sequence(data).render()
  print("--- {} seconds ---" .format(time.time() - start_time))

if '__main__' == __name__:
  sys.exit(main(sys.argv[1:]))
