from svgpathtools import parse_path, svg2paths2, parser, path
import lxml.etree as ET
import sys

SVG_NS = "http://www.w3.org/2000/svg"
NSMAP = {"svg": SVG_NS}

def subtract_higher_layers(layers):
  # Sort layers from topmost to bottom (reverse order for subtraction)
  sorted_layers = layers[::-1]
  processed = []
  union_above = None
  for layer in sorted_layers:
    poly = layer['polygon']
    if union_above:
      poly = poly.difference(union_above)
    if poly.is_empty:
      continue
    new_layer = layer.copy()
    # new_layer['label'] = layer['label']
    new_layer['polygon'] = poly
    processed.append(new_layer)
    union_above = poly if union_above is None else union_above.union(poly)
  # Return in original bottom-to-top order
  return processed[::-1]

def get_transform_str(element):
  """
  Recursively computes the full transform from root to this element.
  Returns a 3x3 numpy affine matrix.
  """
  elems = []
  # Walk up the tree (bottom-up)
  while element is not None:
    elems.append(element)
    element = element.getparent()
  for el in reversed(elems):
    transform_str = el.attrib.get("transform")
    if transform_str:
      return transform_str
      
def extract_paths_with_transforms(svg_filename, layer_id_filter = None):
  """
  Yields tuples of (transformed Path, original attributes) for each <path> in the SVG.
  """
  tree = ET.parse(svg_filename)
  root = tree.getroot()
  paths = []
  attrs = []
  if layer_id_filter == None:
    elements = root.xpath(".//svg:path", namespaces=NSMAP)
  else:
    elements = root.xpath(".//svg:g[@id='" + layer_id_filter + "']//svg:path", namespaces=NSMAP)

  for path_elem in elements:
    d = path_elem.attrib.get("d")
    if not d:
      continue
    orig_attrs = dict(path_elem.attrib)
    # Compute the full transform (including all ancestor groups)
    # transform_matrix = get_full_transform(path_elem)
    # Parse the path data
    parsed_path = parse_path(d)
    # Flatten the 3x3 matrix into SVG's a,b,c,d,e,f for path.transform()
    # a, c, e = transform_matrix[0, 0], transform_matrix[0, 1], transform_matrix[0, 2]
    # b, d, f = transform_matrix[1, 0], transform_matrix[1, 1], transform_matrix[1, 2]

    # print(f"path {orig_attrs.get('id')} is continuous? ", parsed_path.iscontinuous())
    # print(f"path {orig_attrs.get('id')} is closed? ", parsed_path.isclosed())
    if not parsed_path.isclosed():
      print(f"Layer contained unclosed path! {orig_attrs.get('id')}")
      sys.exit(1)

    # assert callable(getattr(path, "transform", None)), "transform should be a method"

    transform_str = get_transform_str(path_elem)
    # path2 = Path.transform(a, b, c, d, e, f)
    # Get a 3x3 transform matrix (for example, from svgpathtools.parser)
    tf = parser.parse_transform(transform_str)

    # Apply the transform using the module-level function
    path2 = path.transform(parsed_path, tf)

    paths.append(path2)
    attrs.append(orig_attrs)
    # yield path, orig_attrs
  return paths, attrs

def svg_parse(svg_file, layer_id_filter=None):
  _paths, _attrs, svg_attr = svg2paths2(svg_file)
  
  paths, attrs = extract_paths_with_transforms(svg_file, layer_id_filter)
    
  # Get SVG viewBox dimensions
  vb = svg_attr.get('viewBox', None)
  result = {
    "width": 0,
    "height": 0,
    "layers": []
  }
  if vb:
      vb = list(map(float, vb.split()))
      result["width"], result["height"] = vb[2], vb[3]
  else:
      result["width"] = float(svg_attr['width'])
      result["height"] = float(svg_attr['height'])

  print(f"Parsed SVG file...")
  print(f"  SVG width: {result["width"]}")
  print(f"  SVG height: {result["height"]}")

  if (result["width"] < 1 or result["height"] < 1):
    print(f"SVG file dimensions are invalid: {result["width"]}x{result["height"]}")
    sys.exit(1)
    return

  for path, attr in zip(paths, attrs):
    result["layers"].append({
      "id": attr.get("id"),
      "path": path,
      "attr": attr
    })
  return result
