import math

import aggdraw
from PIL import ImageColor

from utils import convert_value, map_point, get_ag_points


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
    points = get_ag_points(self.points, image, locals)

    #points = tuple(map(lambda pt: map_point(pt,image) , self.points))
    #points = [item for t in points for item in t]
    pen = aggdraw.Pen(self.glow_colour if glow else self.colour, width=convert_value(self.width, image.width - 1, locals))
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
    pen = aggdraw.Pen(self.glow_colour if glow else self.colour, width=convert_value(self.width, image.width - 1, locals))
    start = map_point(self.start, image, locals)
    length = convert_value(self.length, image.width - 1, locals)
    period = convert_value(self.period, image.width - 1, locals)
    amplitude = convert_value(self.amplitude, image.height - 1, locals)
    offset = convert_value(self.offset, image.width - 1, locals)

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


def from_color(colour):
  if isinstance(colour, str):
    return ImageColor.getrgb(colour)
  if isinstance(colour,dict):
    rgb = from_color(colour.get('rgb',[255,255,255]))
    alpha = colour.get('alpha',255)
    return (rgb[0],rgb[1],rgb[2],alpha)
  else:
    return tuple(colour)


