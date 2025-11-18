import sys
import os
import uuid

from lib.color import hex_to_rgba

def make_folder(directory_path):
  try:
    # Create the directory, including any necessary parent directories
    # and don't raise an error if the directory already exists
    os.makedirs(directory_path)
    print(f"Directory '{directory_path}' created successfully")
  except OSError as e:
    # Handle other potential OS errors (e.g., permission issues, invalid path)
    print(f"Error creating directory '{directory_path}': {e}")
    sys.exit(1)

def export_mat(mtl_filename, surface, color_hex):
  r, g, b = hex_to_rgba(color_hex)
  # Write MTL file
  with open(mtl_filename, 'w') as mtl_file:
      mtl_file.write(f"# Material for {surface}\n")
      mtl_file.write(f"newmtl {surface}_material\n")
      mtl_file.write(f"Kd {r:.6f} {g:.6f} {b:.6f}\n")  # Diffuse color
      mtl_file.write(f"Ka {r*0.3:.6f} {g*0.3:.6f} {b*0.3:.6f}\n")  # Ambient
      mtl_file.write(f"Ks 0.1 0.1 0.1\n")  # Specular
      mtl_file.write(f"Ns 10.0\n")  # Shininess
      mtl_file.write(f"d 1.0\n")  # Transparency

def export_obj(obj_filename, surface, mesh):
  # Write OBJ file
  with open(obj_filename, 'w') as obj_file:
      obj_file.write(f"# {surface} mesh\n")
      obj_file.write(f"mtllib {os.path.basename(obj_filename)}\n")
      obj_file.write(f"o {surface}\n")
      obj_file.write(f"usemtl {surface}_material\n\n")
      
      # Write vertices
      for vertex in mesh.vertices:
        obj_file.write(f"v {vertex[0]:.6f} {vertex[1]:.6f} {vertex[2]:.6f}\n")
      
      # Write faces
      for face in mesh.faces:
        # OBJ uses 1-based indexing
        f1 = face[0] + 1
        f2 = face[1] + 1
        f3 = face[2] + 1
        obj_file.write(f"f {f1} {f2} {f3}\n")
