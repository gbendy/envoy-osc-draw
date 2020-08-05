import re

pixel_match = r"((?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)px"
percent_match = r"((?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)%"


def convert_value(p,factor,state={}):
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

    #print(eval(p,globals(),state))
    return eval(p,globals(),state)
  else:
    return p * factor


def convert_coordinate(p,factor,state={}):
  return convert_value(p,factor,state)+0.5


def map_point(pt,image,state={}):
  return (convert_coordinate(pt[0],image.width-1,state),convert_coordinate(pt[1],image.height-1,state))


def get_ag_points(pts,image,state={}):
  points = map(lambda pt: map_point(pt,image,state) , pts)
  return [item for t in points for item in t]


def animate_keyvals(keyvals, state):
  frame = state["frame"]
  last_f = None
  last_val = None
  for f, val in keyvals:
    if frame < f:
      if last_f is None:
        return val
      else:
        ratio = (frame - last_f)/(f-last_f)
        return ratio * val + (1.0 - ratio) * last_val
    last_f = f
    last_val = val
  return last_val

def animator_keyvals(keyvals):
  def func(state):
    return animate_keyvals(keyvals, state)
  return func