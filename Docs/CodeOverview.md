# MeshTools v0.1.1 - Claude AI Context

## Project Overview
MeshTools is a comprehensive Python toolkit for 3D mesh manipulation and visualization. It provides both command-line utilities and library classes for processing 3D meshes with operations like solidification, mirroring, rotation, fixing, and advanced visualization features.

## Key Features
- **Mesh Processing**: Solidify, mirror, rotate, fix meshes
- **Texture Mapping**: Apply image textures to meshes
- **3D Visualization**: Interactive viewport with measurement grids
- **Space Mouse Support**: Hardware controller integration
- **Gradient Coloring**: Apply color gradients based on mesh depth
- **Multiple Format Support**: OBJ, PLY, STL, OFF, GLTF, GLB

## Core Modules

### mesh_tools.py
Main command-line interface and mesh processing toolkit.
- **Version**: 0.1.0 (CLI shows v0.1.0, but project is v0.1.1)
- **Primary Functions**: 
  - Solidify meshes with flat back (`-f`, `--depth`)
  - Mirror meshes (`-m`)
  - Rotate meshes (`-r axis:degrees`)
  - Fix mesh issues (`-x`, `--normals`)
  - Apply textures (`-t`, `--texture-fit`)
  - Display mesh info (`-i`)
  - Show meshes in 3D viewer (`-s`)

### viewport_3d.py
Interactive 3D mesh viewer with advanced features.
- **Features**:
  - Multi-mesh loading with wildcards
  - Rainbow gradient coloring (toggle with 'C')
  - Measurement grid overlay (toggle with 'G')
  - Depth/percentage grid display (toggle with 'D')
  - Zoom controls ('+'/'-')
  - Mesh deletion (Ctrl+D)
  - Space mouse support (configurable)

### mesh_manipulation.py
Core mesh manipulation operations for the viewport.
- **Operations**: Translation, rotation, scaling
- **Integration**: Works with viewport_3d.py for interactive manipulation

### Additional Specialized Modules

#### mesh_gradient_colorizer.py
- Applies depth-based color gradients to meshes
- Maps Z-coordinates to color transitions

#### measurement_grid_visualizer.py
- Creates 3D measurement grid overlays
- Supports percentage and depth value labeling

#### space_mouse_controller.py & space_mouse_event_handler.py
- Hardware integration for 3D space mouse devices
- Provides 6DOF control for mesh manipulation

#### color_transition_gradient_generator.py
- Generates smooth color transitions
- Used by gradient colorizer and measurement grid

#### text_3d.py
- 3D text rendering for grid labels and annotations

#### file_tools.py
- Utility functions for file operations
- Supports wildcard matching and newest file selection

## Dependencies (requirements.txt)
- numpy - Numerical computations
- open3d - 3D data processing
- pyvista - 3D visualization
- trimesh - Mesh processing
- scipy - Scientific computing
- keyboard - Keyboard input handling
- pygame - Game development library
- hidapi - HID device interface
- matplotlib - Plotting library
- pygetwindow - Window management
- hid - HID device support

## Usage Examples

### Command Line
```bash
# Fix and solidify a mesh with verbose output
python mesh_tools.py mesh.obj -x -f -d -0.3 -v

# Mirror and rotate all PLY files in models directory
python mesh_tools.py ./models/*.ply -m -r x:-90 -v

# View meshes interactively
python viewport_3d.py *.obj *.ply
python viewport_3d.py /path/to/meshes/
```

### Python Library Usage
```python
from mesh_tools import MeshTools

# Initialize with mesh
mesh_tools = MeshTools(mesh=example_mesh, verbose=True)

# Apply operations
mesh_tools.rotate_mesh(axis='X', angle=90)
mesh_tools.add_mirror_mesh(axis='Y')
mesh_tools.fix_mesh()
```

## Configuration
- **config.ini**: Configuration file for viewport and space mouse settings
- **Space Mouse**: Set `use_space_mouse = True` in viewport_3d.py to enable

## Testing
- No specific test framework detected
- Test by running operations on sample meshes in `Meshes/` directory

## Build/Lint Commands
- Install dependencies: `pip install -r requirements.txt`
- Generate documentation: `doxygen` (uses included Doxyfile)

## File Formats Supported
- **Input/Output**: OBJ, PLY, STL, OFF, GLTF, GLB
- **Textures**: Standard image formats via OpenCV/PIL
- **Logs**: Generated with .log extension for mesh statistics

## Recent Changes
- v0.1.1: Added features and improved documentation
- Added .mtl support to OBJ loading
- Code cleanup and organization improvements

## Architecture Notes
- Modular design with specialized classes
- Support for both standalone and submodule usage
- Conditional imports for different usage contexts
- Heavy use of Open3D for 3D operations
- Trimesh for mesh processing and statistics

## Contact
- **Author**: Leland Green
- **Email**: lelandgreenproductions+meshtools@gmail.com
- **License**: Creative Commons Zero v1.0 Universal