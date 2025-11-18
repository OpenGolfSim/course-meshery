import numpy as np
import math
import os

def read_raw_heightmap(raw_file):
    # Unity uses 16-bit unsigned, little-endian
    file_size = os.path.getsize(raw_file)  # in bytes
    num_samples = file_size // 2  # 2 bytes per uint16 sample
    # Try to guess the resolution
    width = int(math.sqrt(num_samples))
    height = width
    assert width * height == num_samples, f"Heightmap is not square! {width * height} != {num_samples}"

    with open(raw_file, "rb") as f:
        # data = np.frombuffer(f.read(), dtype=np.uint8)
        data = np.frombuffer(f.read(), dtype=np.uint16)
    heightmap = data.reshape((height, width))
    # Load the RAW file (little-endian)
    # data = np.fromfile(filename, dtype='<u2')  # '<u2' = little-endian uint16
    # heightmap = data.reshape((height, width))

    return {
        "data": heightmap,
        "resolution": width,
        "min": heightmap.min(),
        "max": heightmap.max()
    }


def bilinear_interpolate_height(heightmap, x, z):
    """
    Bilinear interpolation for smooth height sampling
    """
    hm_height, hm_width = heightmap.shape
    
    # Clamp coordinates to valid range
    x = np.clip(x, 0, hm_width - 1)
    z = np.clip(z, 0, hm_height - 1)
    
    # Get integer coordinates
    x0 = int(np.floor(x))
    x1 = min(x0 + 1, hm_width - 1)
    z0 = int(np.floor(z))
    z1 = min(z0 + 1, hm_height - 1)
    
    # Get fractional parts
    fx = x - x0
    fz = z - z0
    
    # Sample heights at four corners
    h00 = heightmap[z0, x0]
    h10 = heightmap[z0, x1]
    h01 = heightmap[z1, x0]
    h11 = heightmap[z1, x1]
    
    # Bilinear interpolation
    h0 = h00 * (1 - fx) + h10 * fx
    h1 = h01 * (1 - fx) + h11 * fx
    
    return h0 * (1 - fz) + h1 * fz

def map_mesh_to_heightmap(vertices, heightmap, svg_width, svg_height, height_scale=1.0):
    # Apply heights with interpolation
    hm_height, hm_width = heightmap.shape
    max_height = 65535.0  # Unity's 16-bit range
    for v in vertices:
        x = (v[0] / svg_width) * hm_width
        z = (v[2] / svg_height) * hm_height
        
        height = bilinear_interpolate_height(heightmap, x, z)
        # v[1] = height * height_scale
        v[1] = ((height / max_height) * height_scale)
    
    return vertices

