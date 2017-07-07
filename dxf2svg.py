#!/usr/bin/env python

import dxfgrabber
import json
import math
import sys
import os
import argparse
import dxfref




# SVG TEMPLATES
sys.setrecursionlimit(10000)

# global global_max_x = 0
# global global_max_y = 0
# global global_min_x = 0
# global global_min_y = 0

SVG_PREAMBLE = \
'<svg xmlns="http://www.w3.org/2000/svg" ' \
'version="1.1" viewBox="{0} {1} {2} {3}">\n'

# SVG_MOVE_TO = 'M {0} {1:.2f} '
# SVG_LINE_TO = 'L {0} {1:.2f} '
# SVG_ARC_TO  = 'A {0} {1:.2f} {2} {3} {4} {5:.2f} {6:.2f} '

SVG_MOVE_TO = 'M {0} {1} '
SVG_LINE_TO = 'L {0} {1} '
SVG_ARC_TO  = 'A {0} {1} {2} {3} {4} {5} {6} '

SVG_BACKGRND = \
'<rect x="{0}" y="{1}" width="{2}" height="{3}" stroke="blue" fill="white" />\n'

SVG_PATH = \
'<path d="{0}" fill="none" stroke="{1}" stroke-width="{2:.2f}" />\n'

SVG_LINE = \
'<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" stroke="{4}" stroke-width="{5:.2f}" />\n'

SVG_TEXT = \
'<text x="{0}" y="{1}" font-size="{2}" >{3}</text>\n'

SVG_MTEXT = \
'<text x="{0}" y="{1}"  font-size="{2}" >{3}</text>\n'


SVG_ELLIPSE = \
'<circle cx="{0}" cy="{1}" rx="{2}" ry="{3}" fill="none" />\n'

SVG_CIRCLE = \
'<circle cx="{0}" cy="{1}" r="{2}" stroke="{3}" stroke-width="{4:.2f}" fill="{5}" />\n'

#svg functions

def svg_circle(args):
  if len(args) == 4:
    return SVG_CIRCLE.format(*args, 1, "none")
  elif len(args) == 5:
    return SVG_CIRCLE.format(*args, "none")
  else:
    return SVG_CIRCLE.format(*args)



# SVG DRAWING HELPERS
def angularDifference(startangle, endangle):
  result = endangle - startangle
  while result >= 360:
    result -= 360
  while result < 0:
    result += 360
  return result


def rotate(ox, oy, px, py, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.
    rotate(origin, point, math.radians(10))
    The angle should be given in radians.
    """
    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy

# global global_max_x = 0
# global_max_y = 0
# global_min_x = 0
# global_min_y = 0
#
# def check_max(x, y):
#   # global global_max_x
#   # global global_max_y
#   # global global_min_x
#   # global global_min_y
#   # global_max_x = 0
#   # global_max_y = 0
#   # global_min_x = 0
#   # global_min_y = 0
#   if x > global_max_x:
#     global_max_x = x
#   if y > global_max_y:
#     global_max_y = y
#   if x < global_min_x:
#     global_min_x = x
#   if y < global_min_y:
#     global_min_y = y
#   pass


def add_rotate(basis, point):
  """
  1 - self xforms
  2 - add to base point,
  :param basis:
  :param point:
  :return:
  """
  ox, oy, a, sx, sy, sz = basis

  #scale
  px = point[0] * sx
  py = point[1] * sy
  angle = math.radians(a)

  px = ox + px
  py = oy + py
  #rotate
  rx = (ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy))
  ry = (oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy))

  #translate
  #px = ox + px
  #py = oy + py

  #check_max(rx, ry)
  return rx, ry


def parse_text(str):
  b = "&"
  for char in b:
    str = str.replace(char, "")
  return str


def path_string_from_points(points, basis):
  path_string = SVG_MOVE_TO.format(*add_rotate(basis, points[0]))
  for i in range(1,len(points)):
    path_string += SVG_LINE_TO.format(*add_rotate(basis, points[i]))
  return path_string


def dxf_line_weight_to_svg(e):
  line_weight = e.__dict__.get('line_weight')
  if line_weight is None:
    return 0.25
  elif line_weight == 0:
    return 0.25
  else:
    return line_weight / 25


def handle_entity(svgFile, e, dxfData, basis, layer_color):
  """
  write dxf entity data to a file
  :param svgFile: reference to file
  :param e: dxfentity
  :param dxfData: reference to whole dxf
  :param basis: transformation to apply to entity (if in block)
  :param layer_color: color to apply
  :return: none
  """
  if e.dxftype == 'LINE':
    svgFile.write(SVG_LINE.format(*add_rotate(basis, e.start),
                                  *add_rotate(basis, e.end),
                                  layer_color,
                                  dxf_line_weight_to_svg(e)))

  elif e.dxftype == 'LWPOLYLINE':
    path_string = path_string_from_points(e, basis)
    if e.is_closed:
      path_string += 'Z'
    svgFile.write(SVG_PATH.format(path_string,
                                  layer_color,
                                  dxf_line_weight_to_svg(e)))

  elif e.dxftype == 'CIRCLE':
    svgFile.write(SVG_CIRCLE.format(*add_rotate(basis, e.center),
                                    e.radius,
                                    layer_color,
                                    dxf_line_weight_to_svg(e),
                                    "none"))

  elif e.dxftype == 'TEXT':
    svgFile.write(SVG_TEXT.format(*add_rotate(basis, e.insert),
                                  e.height,
                                  parse_text(e.text)))

  elif e.dxftype == 'MTEXT':
    svgFile.write(SVG_TEXT.format(*add_rotate(basis, e.insert),
                                  e.height,
                                  parse_text(e.raw_text)))

  elif e.dxftype == 'ELLIPSE':
    #print(e, e.start_param, e.end_param, e.center, e.major_axis)
    #svgFile.write(SVG_ELLIPSE.format())
    pass

  elif e.dxftype == 'ARC':
    ext = e.extrusion[2]
    if ext == -1:
      flip = 0
    else:
      flip = 1

    sx, sy = add_rotate(basis, e.center)

    # compute end points of the arc
    x1 = (sx + e.radius * math.cos(math.radians(e.start_angle))) * ext
    y1 = sy + e.radius * math.sin(math.radians(e.start_angle))
    x2 = (sx + e.radius * math.cos(math.radians(e.end_angle))) * ext
    y2 = sy + e.radius * math.sin(math.radians(e.end_angle))
    direction = int(angularDifference(e.start_angle, e.end_angle) > 180)

    path_string = SVG_MOVE_TO.format(x1, y1)
    path_string += SVG_ARC_TO.format(e.radius, e.radius, 0,
                                     direction, flip, x2, y2)
    svgFile.write(SVG_PATH.format(path_string,
                                  layer_color,
                                  dxf_line_weight_to_svg(e)))

  elif e.dxftype == 'INSERT':
    block = dxfData.blocks[e.name]
    for be in block:
      handle_entity(svgFile, be, dxfData,
                    [basis[0] + e.insert[0],
                     basis[1] + e.insert[1],
                     basis[2] + e.rotation,
                     *e.scale],
                     layer_color)
# end: handleEntity


def set_layer_color(e, dxfData, overrides):
  override = overrides.get(dxfData.layers[e.layer].name)
  default = overrides.get('default_color')

  if override is not None:
    layer_color = override.get('color')
  elif default:
    layer_color = default
  else:
    col = dxfData.layers[e.layer].color
    layer_color = "{}{}".format('#', dxfref.CLUT[col][1])
  return layer_color


def saveToSVG(svgFile, dxfData, overrides):
  """

  :param svgFile:
  :param dxfData:
  :param overrides:
  :return:
  """
  minX = dxfData.header['$EXTMIN'][0]
  minY = dxfData.header['$EXTMIN'][1]
  maxX = dxfData.header['$EXTMAX'][0]
  maxY = dxfData.header['$EXTMAX'][1]

  svgFile.write(SVG_PREAMBLE.format(minX, minY, maxX - minX, maxY - minY))
  svgFile.write(SVG_BACKGRND.format(minX, minY, maxX - minX, maxY - minY))

  # build block table
  for entity in dxfData.entities:
    layer = dxfData.layers[entity.layer]
    layer_color = set_layer_color(entity, dxfData, overrides)
    if layer.on and layer_color != 'ignore':
      # and not layer.frozen
      handle_entity(svgFile, entity, dxfData, [0, 0, 0, 1, 1, 1], layer_color)
     
  svgFile.write('</svg>\n')
  pass


def save_layers(json_file, dxf):
  layers = []
  for entity in dxf.layers:
    layers.append(entity.__dict__)
  with open(json_file, 'w') as fp:
    json.dump(layers, fp)


def parse_override_file(override_file, file):
  result = {}

  if os.path.isfile(override_file):
    file_name = file.split('/')[-1].split('.')[0]
    json_data = open(override_file)
    overrides = json.loads(json_data.read())
    file_spec = overrides['files'][file_name]
    if file_spec:
      result = {}
      for k, vs in overrides['categories'].items():
        for layer_name in file_spec[k]:
          result.update({layer_name: vs})
    json_data.close()
  return result


def export_dxf_to_svg():
  overrides = parse_override_file(args.ovr, args.source)

  # grab data from file
  dxfData = dxfgrabber.readfile(args.source)
  print(args.source.split('.')[:-1])

  # convert and save to svg
  svgName = '.'.join(args.source.split('.')[:-1] + ['svg'])
  jsonName = '.'.join(args.source.split('.')[:-1] + ['json'])

  svgFile = open(svgName, 'w')
  saveToSVG(svgFile, dxfData)
  svgFile.close()

  save_layers(jsonName, dxfData)


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description=' ')
  parser.add_argument('--source',  help='source file')
  parser.add_argument('--default_color', help='if color not fount in overrides, use this')
  parser.add_argument('--mode', help='export mode [default, make_json, colors]' )
  parser.add_argument('--ovr',  help='overrides file')

  if len(sys.argv) < 2:
    sys.exit('Usage: {0} file-name'.format(sys.argv[0]))
  args = parser.parse_args()

  # grab data from file
  dxfData = dxfgrabber.readfile(args.source)

  if args.mode == 'make_json':
    jsonName = '.'.join(args.source.split('.')[:-1] + ['json'])
    save_layers(jsonName, dxfData)

  else:
    if args.mode == 'default' and args.default_color:
      overrides = {'default_color': args.default_color}
    elif args.mode == 'default' and not args.default_color:
      overrides = {'default_color': '#000000'}
    elif args.mode == 'colors':
      overrides = {}
    else:
      overrides = parse_override_file(args.ovr, args.source)
      if args.default_color:
        overrides.update({'default_color': args.default_color})

    # convert and save to svg
    svgName = '.'.join(args.source.split('.')[:-1] + ['svg'])

    svgFile = open(svgName, 'w')
    saveToSVG(svgFile, dxfData, overrides)
    svgFile.close()
    #print(global_max_x, global_max_y, global_min_x, global_min_y)
#end: __main__


#python dxf2svg.py --source resources/cl.dxf --ovr resources/overrides.json --default_color "#000000" --mode training
#python dxf2svg.py --source resources/cl.dxf --ovr resources/overrides.json --mode default
#python dxf2svg.py --source resources/cl.dxf --mode make_json
#python dxf2svg.py --source resources/cl.dxf --mode colors



































