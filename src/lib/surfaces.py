import re

def match_surface(attr, surfaceColorMap):
    styleAttr = attr.get('style', None)
    colorPattern = r"fill:#([0-9a-f]+);"
    match_obj = re.search(colorPattern, styleAttr, re.IGNORECASE)
    surface = None
    matchedColor = None
    if match_obj:
        matchedColor = match_obj.group(1)
        surface = surfaceColorMap.get(matchedColor, None)
    return (surface, matchedColor)


def parse_gpl_palette(file_path):
    color_map = {}
    hex_line_re = re.compile(
        r'^\s*(\d+)\s+(\d+)\s+(\d+)\s+(#[0-9A-Fa-f]{6})\s+#([^\s]+)\s*$'
    )
    with open(file_path, 'r') as f:
        for line in f:
            match = hex_line_re.match(line)
            if match:
                hex_color = match.group(4).lstrip('#').lower()  # Remove leading '#' and lowercase
                color_name = match.group(5)
                color_map[hex_color] = color_name
    return color_map