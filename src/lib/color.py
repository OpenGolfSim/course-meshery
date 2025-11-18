def hex_to_rgba(hex_color, includeAlpha = False):
    """
    Converts a hexadecimal color code (e.g., "#RRGGBB" or "RRGGBB")
    to an RGB tuple (red, green, blue).
    """
    hex_color = hex_color.lstrip('#')  # Remove '#' if present
    if len(hex_color) != 6:
        raise ValueError("Invalid hex color code. Expected 6 characters.")

    r_hex = hex_color[0:2]
    g_hex = hex_color[2:4]
    b_hex = hex_color[4:6]

    r = int(r_hex, 16)
    g = int(g_hex, 16)
    b = int(b_hex, 16)

    if (includeAlpha):
      return (r, g, b, 255)
    
    return (r, g, b)
        