from shapely.geometry import Polygon, Point
import numpy as np
from matplotlib.tri import Triangulation

def densify_polygon_boundary(coords, target_spacing):
    """
    Add more points along polygon edges for smoother boundaries
    """
    coords = np.array(coords)
    densified = [coords[0]]  # Start with first point

    for i in range(len(coords)):
        p1 = coords[i]
        p2 = coords[(i + 1) % len(coords)]
        
        # Calculate distance and number of segments needed
        dist = np.linalg.norm(p2 - p1)
        num_segments = max(1, int(dist / target_spacing))
        
        # Add intermediate points
        for j in range(1, num_segments + 1):
            t = j / num_segments
            point = p1 + t * (p2 - p1)
            densified.append(point)

    return np.array(densified[:-1])  # Remove duplicate last point

def densify_polygon(poly: Polygon, target_spacing=2.0):
    """
    Densify polygon exterior and holes for smoother triangulation
    """
    if poly.is_empty:
        return poly
    
    # Densify exterior
    exterior_coords = poly.exterior.coords[:-1]  # Remove duplicate last point
    densified_exterior = densify_polygon_boundary(exterior_coords, target_spacing)
    
    # Densify holes
    densified_holes = []
    for hole in poly.interiors:
        hole_coords = hole.coords[:-1]
        densified_hole = densify_polygon_boundary(hole_coords, target_spacing)
        densified_holes.append(densified_hole)
    
    return Polygon(densified_exterior, holes=densified_holes)

def path_to_polygon(path, num_points=1000):
    points = [path.point(t) for t in np.linspace(0, 1, num_points)]
    coords = [(pt.real, pt.imag) for pt in points]
    return Polygon(coords)

def triangulate_polygon(poly: Polygon, boundary_spacing=1.0, interior_spacing=3.0):
    """
    Polygon triangulation using matplotlib's triangulation with densified boundaries
    """
    if poly.is_empty:
        return [], []
    
    
    # Step 1: Densify polygon boundaries for smoother edges
    densified_poly = densify_polygon(poly, boundary_spacing)
    
    # Get all boundary points (densified)
    exterior = np.array(densified_poly.exterior.coords[:-1])
    
    if len(exterior) < 3:
        return [], []
    
    # Step 2: Create a dense grid of interior points
    minx, miny, maxx, maxy = densified_poly.bounds
    
    # Create grid resolution based on interior spacing
    x_points = np.arange(minx + interior_spacing, maxx, interior_spacing)
    y_points = np.arange(miny + interior_spacing, maxy, interior_spacing)
    
    interior_points = []
    for x in x_points:
        for y in y_points:
            point = Point(x, y)
            if densified_poly.contains(point):
                interior_points.append([x, y])
    
    # Step 3: Add hole boundaries (densified)
    hole_points = []
    if densified_poly.interiors:
        for interior in densified_poly.interiors:
            hole_coords = np.array(interior.coords[:-1])
            if len(hole_coords) >= 3:
                hole_points.extend(hole_coords.tolist())
    
    # Step 4: Combine all points
    all_boundary_points = exterior.tolist()
    if hole_points:
        all_boundary_points.extend(hole_points)
    if interior_points:
        all_boundary_points.extend(interior_points)
    
    all_points = np.array(all_boundary_points)
    
    print(f"triangulation: {len(exterior)} exterior, {len(hole_points)} hole, {len(interior_points)} interior points")
    
    # Step 5: Create triangulation
    tri = Triangulation(all_points[:, 0], all_points[:, 1])
    
    # Step 6: Filter triangles to ensure they're inside the polygon
    triangles = tri.triangles
    valid_triangles = []
    
    for triangle in triangles:
        # Check if triangle centroid is inside polygon
        triangle_points = all_points[triangle]
        centroid = np.mean(triangle_points, axis=0)
        
        if poly.contains(Point(centroid)):
            # Ensure counter-clockwise winding
            valid_triangles.append([triangle[0], triangle[2], triangle[1]])
    
    if not valid_triangles:
        return [], []
    
    # Convert to 3D vertices
    vertices = np.zeros((len(all_points), 3))
    vertices[:, 0] = all_points[:, 0]  # X
    vertices[:, 1] = 0.0               # Y
    vertices[:, 2] = all_points[:, 1]  # Z
    
    faces = np.array(valid_triangles)
    
    print(f"    Robust triangulation result: {len(vertices)} vertices, {len(faces)} triangles")
    return vertices, faces

