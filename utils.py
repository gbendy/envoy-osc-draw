import re

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