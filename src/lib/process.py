import os
import uuid
import time
import trimesh
import numpy as np
from PySide6.QtCore import (QObject, Signal, Slot, Qt, QThread)

from lib.color import hex_to_rgba
from lib.export import make_folder, export_obj, export_mat
from lib.heightmap import read_raw_heightmap, map_mesh_to_heightmap
from lib.mesh import path_to_polygon, triangulate_polygon
from lib.surfaces import parse_gpl_palette, match_surface
from lib.svg import subtract_higher_layers
from lib.utils import resource_path

max_height_value = 65535

class MeshWorker(QObject):
  progress = Signal(int)        # emit progress percent
  finished = Signal(object)     # emit result when done
  error = Signal(str)
  debug_log = Signal(str)

  def __init__(self, svg_info, raw_path: str, output_path: str, height_value: float):
    super().__init__()
    self._running = True
    self.svg_info = svg_info
    self.raw_path = raw_path

    job_folder = f"meshery-{uuid.uuid4()}"
    self.output_path = os.path.join(output_path, job_folder)
    self.height_value = height_value
    self.palette_file = resource_path("data/palette.gpl")

  @Slot()
  def run(self):
    try:
      # Example long-running loop
      result = 0
      
      # self.debug_log.emit("Parsing SVG file...")
      # svg_info = lib.svg.svg_parse(self.svg_path)
      # self.progress.emit(1)
      
      self.debug_log.emit("Parsing color palette...")
      surface_map = parse_gpl_palette(self.palette_file)
      # self.progress.emit(2)
      layers = []

      layer_index = 0
      for layer in self.svg_info['layers']:
        num_points = max(int(layer['path'].length()) * 20, 100)
        num_points = min(num_points, 10000)
        poly = path_to_polygon(layer['path'], num_points)

        surface, color = match_surface(layer['attr'], surface_map)

        if (surface == None or color == None):
          self.debug_log.emit(f"Unable to determine surface type based on assigned fill color! ({layer["attr"]})")
          return None
        
        self.debug_log.emit(f"Processing surface: {surface}, {num_points} points")

        layers.append({
          "index": layer_index,
          "polygon": poly,
          "attr": layer['attr'],
          "label": surface,
          "surface": surface,
          "color": color
        })

        layer_index += 1
        # self.progress.emit(layer_index)
        # time.sleep(1)   # blocking work simulated

      self.debug_log.emit(f"SVG successfully converted to polygons")
      layers = subtract_higher_layers(layers)
      
      self.debug_log.emit(f"Reading terrain data...")
      terrain_data = read_raw_heightmap(self.raw_path)
      
      max_world_height = (terrain_data['max'] / max_height_value) * self.height_value
      # self.debug_log.emit(f"Calculated max_world_height: {max_world_height}")
    
      # allMeshes = []
      
      
      self.debug_log.emit(f"Creating output folder at: {self.output_path}")
      make_folder(self.output_path)

      layers_completed = 0
      
      for layer in layers:
        if layer['polygon'].is_empty:
          self.debug_log.emit(f"  Skipping empty polygon for {layer['surface']}")
          continue
        
        # triangulate mesh
        boundary_spacing = 0.5
        interior_spacing = 0.8
        if layer['polygon'].area < 1500:
          interior_spacing = 0.25
        if layer['surface'] == "sand" or layer['surface'] == "green":
          interior_spacing = 0.15
        if layer['surface'] == "water":
          interior_spacing = 0.5
        if layer['surface'] == "river":
          interior_spacing = 0.2

        self.debug_log.emit(f"Generating {layer['label']} polygons with spacing {interior_spacing}")
        vertices, faces = triangulate_polygon(layer['polygon'], boundary_spacing, interior_spacing)

        if vertices.shape[0] == 0 or faces.shape[0] == 0:
          self.debug_log.emit(f"  Skipping empty shape for {layer['surface']}")
          continue

        # conform meshes to heightmap
        self.debug_log.emit(f"Conforming {layer['label']} polygon to heightmap")
        vertices = map_mesh_to_heightmap(vertices, terrain_data["data"], self.svg_info["width"], self.svg_info["height"], max_world_height)

        face_colors = np.tile(hex_to_rgba(layer["color"]), (faces.shape[0], 1))
        mesh = trimesh.Trimesh(vertices=vertices, faces=faces, face_colors=face_colors)

        # Create individual OBJ and MTL files
        mtl_filename = os.path.join(self.output_path, f"{layer['surface']}_{layer['index']}.mtl")
        obj_filename = os.path.join(self.output_path, f"{layer['surface']}_{layer['index']}.obj")
        
        color_hex = layer.get('color', 'ffffff')
        
        # export_obj
        export_mat(mtl_filename, layer['surface'], color_hex)
        export_obj(obj_filename, layer['surface'], mesh)

        layers_completed += 1
        self.progress.emit(layers_completed)

      # # self.debug_log.emit(f"Exporting OBJ files to output folder: {self.output_path}")      
      # # lib.export.export_individual_obj_files(allMeshes, layers, self.output_path)
      
      self.finished.emit(result)
    except Exception as e:
      self.finished.emit(None)
      self.error.emit(str(e))

  def stop(self):
      # Called from main thread to request cancellation
      self._running = False





def generate_meshes(args, layers, terrain_data, width, height, debug_log):
  allMeshes = []
  
  for layer in layers:
    if layer['polygon'].is_empty:
      print(f"  Skipping empty polygon for {layer['surface']}")
      continue
    
    # triangulate mesh
    boundary_spacing = 0.5
    interior_spacing = 0.8
    if layer['polygon'].area < 1500:
      interior_spacing = 0.25
    if layer['surface'] == "sand" or layer['surface'] == "green":
      interior_spacing = 0.15
    if layer['surface'] == "water" or layer['surface'] == "river":
      interior_spacing = 0.2

    debug_log(f"Generating {layer['label']} polygon with spacing {interior_spacing}")
    vertices, faces = lib.triangulation.triangulate_polygon_robust(layer['polygon'], boundary_spacing, interior_spacing)

    if vertices.shape[0] == 0 or faces.shape[0] == 0:
      debug_log(f"  Skipping empty shape for {layer['surface']}")
      continue

    # conform meshes to heightmap
    debug_log(f"Conforming {layer['label']} polygon to heightmap")
    vertices = lib.heightmap.map_mesh_to_heightmap_advanced(vertices, terrain_data["data"], width, height, args["height_scale"])

    face_colors = np.tile(lib.color.hex_to_rgba(layer["color"]), (faces.shape[0], 1))
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, face_colors=face_colors)
    
    allMeshes.append(mesh)
  
  return allMeshes
   
def parse_terrain(args, debug_log):
  terrain_data = lib.heightmap.read_raw_heightmap(args["raw_file"])
  debug_log(f"terrain_data:")
  debug_log(f"   resolution: {terrain_data['resolution']}")
  debug_log(f"   min: {terrain_data['min']}")
  debug_log(f"   max: {terrain_data['max']}")
  
  max_world_height = (terrain_data['max'] / max_height_value) * args["height_scale"]
  debug_log(f"   max_world_height: {max_world_height}")

  return terrain_data, max_world_height


def parse_layers(svg_file):
    
    debug_log(f"Parsing SVG...")
    svg_info = lib.svg.svg_parse(args["svg_file"])

    debug_log(f"Parsing color palette...")
    surface_map = lib.surfaces.parse_gpl_palette(args["palette_file"])
    
    debug_log(f"Generating polygons from layers...")
    layers = []
    
    # for path, attr in sort_layers_by_priority(paths, attrs):
    for layer in svg_info['layers']:
      
      num_points = max(int(layer['path'].length()) * 20, 100)
      num_points = min(num_points, 10000)
      poly = lib.mesh.path_to_polygon(layer['path'], num_points)

      surface, color = lib.surfaces.match_surface(layer['attr'], surface_map)

      if (surface == None or color == None):
        debug_log(f"Unable to determine surface type based on assigned fill color! ({attr})", True)
        return None
      print(f"Processing surface: {surface}, {num_points} points")

      layers.append({
          "polygon": poly,
          "attr": layer['attr'],
          "label": surface,
          "surface": surface,
          "color": color
      })

    layers = subtract_higher_layers(layers)
    return layers, svg_info["width"], svg_info["height"]