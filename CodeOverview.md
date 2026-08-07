# MeshTools - 3D Mesh Processing Toolkit

## Project Overview

MeshTools is a Python-based 3D mesh processing and visualization toolkit designed for manipulating, fixing, and visualizing 3D mesh objects. The project provides both command-line tools and a programmatic API for various mesh operations including solidification, mirroring, rotation, texture application, and mesh repair.

**Version:** 0.1.1  
**Author:** Leland Green  
**License:** MIT / Creative Commons Zero v1.0 Universal  

## Key Features

- **Mesh Manipulation**: Rotate, mirror, flip, and solidify 3D meshes
- **Mesh Repair**: Fix common mesh issues (holes, duplicate vertices, non-manifold edges)
- **Texture Application**: Apply colors from images to mesh vertices
- **3D Visualization**: Interactive 3D viewport with measurement grids and color gradients
- **Space Mouse Support**: Integration with 3DConnexion space mouse controllers
- **Multiple Format Support**: Works with OBJ, PLY, STL, OFF, GLTF, GLB formats
- **Batch Processing**: Support for wildcard patterns and directory processing

## Core Components

### Main Modules

#### mesh_tools.py
Primary mesh processing module containing the `MeshTools` class with methods for:
- `rotate_mesh()` - Rotate meshes around x, y, or z axes
- `solidify_mesh_with_flat_back()` - Add thickness with flat backing
- `add_mirror_mesh()` - Create mirrored watertight meshes
- `fix_mesh()` - Repair mesh geometry issues
- `apply_colors_from_image()` - Map image colors to mesh vertices
- `print_trimesh_statistics()` - Generate detailed mesh analysis reports

#### viewport_3d.py
Interactive 3D visualization system featuring:
- Real-time mesh display and manipulation
- Measurement grid overlays
- Rainbow gradient coloring
- Keyboard and mouse navigation
- Space mouse controller integration
- Multi-file viewing support

#### mesh_manipulation.py
Low-level mesh transformation utilities:
- `move_object()` - Translate and scale mesh objects
- `rotate_object()` - Apply rotational transformations
- Viewport update management

#### mesh_gradient_colorizer.py
Color gradient application system:
- `apply_gradient_to_mesh()` - Apply depth-based color gradients
- Support for named colors and RGB tuples
- Z-coordinate based color mapping

### Supporting Modules

- **space_mouse_controller.py** - 3DConnexion space mouse integration
- **space_mouse_event_handler.py** - HID device event processing
- **measurement_grid_visualizer.py** - Grid overlay visualization
- **color_transition_gradient_generator.py** - Color transition utilities
- **file_tools.py** - File discovery and pattern matching utilities
- **text_3d.py** - 3D text rendering capabilities

## Command Line Usage

### Basic Mesh Processing
```bash
# Fix mesh issues
python mesh_tools.py input.obj -fix -verbose

# Solidify with flat back at depth -0.3
python mesh_tools.py input.ply -flat -depth -0.3

# Create mirror mesh
python mesh_tools.py input.stl -mirror

# Rotate mesh 90 degrees around x-axis  
python mesh_tools.py input.obj -rotate x:90

# Apply texture from image
python mesh_tools.py input.obj -texture texture.png

# Show mesh statistics
python mesh_tools.py input.obj -info

# Display mesh in 3D viewer
python mesh_tools.py input.obj -show
```

### 3D Viewport
```bash
# View single mesh
python viewport_3d.py mesh.obj

# View newest mesh in directory
python viewport_3d.py /path/to/meshes/

# View multiple meshes with wildcards
python viewport_3d.py *.ply *.obj

# Recursive directory search
python viewport_3d.py models/**/*.stl
```

### Batch Processing Examples
```bash
# Process all PLY files with multiple operations
python mesh_tools.py ./models/*.ply -flat -depth -0.3 -mirror -fix -rotate x:-90 -verbose

# Fix and display all meshes in directory
python mesh_tools.py ./meshes/* -fix -show
```

## Programming API

### Basic Usage
```python
from mesh_tools import MeshTools

# Initialize with mesh file
mesh_tools = MeshTools("input.obj", verbose=True)

# Perform operations
rotated = mesh_tools.rotate_mesh(axis='y', angle=90.0)
solid = mesh_tools.solidify_mesh_with_flat_back(flat_back_depth=-0.5)
mirrored = mesh_tools.add_mirror_mesh(mesh_tools.mesh)
fixed = mesh_tools.fix_mesh(fix_normals=True)

# Apply texture
textured = mesh_tools.apply_colors_from_image(mesh_tools.mesh, "texture.png")

# Export results
solid.export("output_solid.ply")
mirrored.export("output_mirror.stl")
```

### 3D Viewport Integration
```python
from viewport_3d import ThreeDViewport

# Create interactive viewer
viewport = ThreeDViewport(initial_mesh_file="mesh.obj")
viewport.run()
```

## Dependencies

- **numpy** - Numerical computations and array operations
- **trimesh** - Core mesh processing and geometry operations  
- **open3d** - 3D visualization and additional mesh utilities
- **scipy** - Scientific computing, particularly spatial transformations
- **keyboard** - Keyboard input handling for interactive features
- **PIL (Pillow)** - Image processing for texture application
- **matplotlib** - Color mapping and visualization utilities
- **hidapi/hid** - HID device communication for space mouse
- **pygetwindow** - Window management for viewport controls

## Build and Test Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run basic functionality test
python mesh_tools.py --help

# Test 3D viewport
python viewport_3d.py

# Generate documentation (if Doxygen installed)
doxygen
```

## File Structure

```
MeshTools/
├── mesh_tools.py                          # Main CLI and MeshTools class
├── viewport_3d.py                         # 3D visualization system
├── mesh_manipulation.py                   # Low-level mesh transformations
├── mesh_gradient_colorizer.py             # Color gradient utilities
├── space_mouse_controller.py              # Space mouse integration
├── space_mouse_event_handler.py           # HID event processing
├── measurement_grid_visualizer.py         # Grid overlay system
├── color_transition_gradient_generator.py # Color transition utilities
├── file_tools.py                          # File discovery utilities
├── text_3d.py                            # 3D text rendering
├── requirements.txt                       # Python dependencies
├── _version.py                           # Version information
├── config.ini                            # Configuration settings
├── Doxyfile                              # Documentation generation
├── ReadMe.md                             # User documentation
├── Meshes/                               # Sample mesh files
└── Docs/                                 # Additional documentation
    ├── CodeOverview.md
    └── MeshTransforms.md
```

## Known Limitations

- Space mouse support requires manual enabling (`use_space_mouse = True` in viewport_3d.py)
- Some mesh repair operations may be computationally intensive for large meshes
- Texture mapping assumes mesh vertices can be normalized to image coordinates
- File overwriting occurs without prompting in CLI mode

## Development Notes

- Uses trimesh library as primary mesh processing backend
- Open3D provides visualization and additional geometry utilities
- HID device integration supports 3DConnexion space mouse hardware
- Modular design allows individual components to be used independently
- Extensive error handling and verbose logging options available