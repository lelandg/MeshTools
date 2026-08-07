# Mesh Transformation Documentation

This document outlines all the transformation-related functionality available in the MeshTools codebase.

## Overview

The MeshTools library provides various transformation capabilities for 3D meshes including:
- Translation (movement in 3D space)
- Rotation (around various axes)
- Scaling (uniform and non-uniform)
- Mirroring/Flipping
- Combined transformations using transformation matrices

## Classes and Methods

### 1. MeshManipulation Class
**File:** `mesh_manipulation.py`

This class provides real-time manipulation of meshes within a 3D viewport using Open3D utilities.

#### Methods:

##### `move_object(dx, dy, dz=0.0, zoom_factor=1.0)`
- **Purpose:** Move and optionally scale the mesh within the 3D viewport
- **Parameters:**
  - `dx`: Movement along X-axis (world units)
  - `dy`: Movement along Y-axis (world units)
  - `dz`: Movement along Z-axis (world units, default=0)
  - `zoom_factor`: Scaling factor (default=1.0, no scaling)
- **Implementation Details:**
  - Uses 4x4 transformation matrices for combined translation and scaling
  - Scales around the mesh center when zoom_factor != 1.0
  - Translation matrix: Sets translation vector in the 4th column
  - Scaling matrix: Scales the upper-left 3x3 submatrix
  - Combined transformation: `scaling_matrix @ translation_matrix`

##### `rotate_object(angle_degrees, counter_clockwise=False)`
- **Purpose:** Rotate the mesh around the Y-axis
- **Parameters:**
  - `angle_degrees`: Rotation angle in degrees
  - `counter_clockwise`: Direction of rotation (default=False)
- **Implementation Details:**
  - Converts degrees to radians
  - Uses Open3D's `get_rotation_matrix_from_axis_angle([0, angle_radians, 0])`
  - Rotates around the mesh center point
  - Y-axis rotation (vertical axis)

### 2. MeshTools Class
**File:** `mesh_tools.py`

This class provides various mesh manipulation utilities using the Trimesh library.

#### Methods:

##### `rotate_mesh(mesh=None, axis='y', angle=90.0)`
- **Purpose:** Rotate a mesh around a specified axis
- **Parameters:**
  - `mesh`: Trimesh object to rotate (optional, uses self.mesh if None)
  - `axis`: Rotation axis ('x', 'y', or 'z')
  - `angle`: Rotation angle in degrees
- **Implementation Details:**
  - Uses SciPy's `Rotation` class for matrix generation
  - Creates rotation vector: `np.radians(angle) * axis_vector`
  - Generates rotation matrix: `R.from_rotvec(rotation_vector).as_matrix()`
  - Applies rotation: `mesh.vertices @ rotation_matrix.T`
  - Preserves vertex colors

##### `flip_mesh(mesh, axis='y')`
- **Purpose:** Mirror/flip a mesh along a specified axis
- **Parameters:**
  - `mesh`: Trimesh object to flip
  - `axis`: Axis to flip along (currently only 'y' supported)
- **Implementation Details:**
  - Uses transformation matrix for flipping
  - Y-axis flip matrix:
    ```
    [1,  0,  0,  0]
    [0, -1,  0,  0]
    [0,  0,  1,  0]
    [0,  0,  0,  1]
    ```
  - Applied using `mesh.apply_transform(flip_matrix)`

##### `add_mirror_mesh(mesh)`
- **Purpose:** Create a mirrored copy of the mesh along the Z-axis
- **Parameters:**
  - `mesh`: Original Trimesh object
- **Implementation Details:**
  - Creates mirrored vertices by negating Z coordinates
  - Adjusts face indices for mirrored vertices
  - Reverses face winding for proper normals
  - Combines original and mirrored meshes
  - Adds stitching faces to create watertight mesh

### 3. Viewport3D Class
**File:** `viewport_3d.py`

Provides high-level rotation controls for the viewport.

#### Methods:

##### `rotate_left(degrees=10.0)`
- **Purpose:** Rotate mesh/viewport to the left
- **Parameters:**
  - `degrees`: Rotation angle (default=10)
- **Implementation:** Calls `mesh_manipulator.rotate_object(degrees, counter_clockwise=False)`

##### `rotate_right(degrees=10)`
- **Purpose:** Rotate mesh/viewport to the right
- **Parameters:**
  - `degrees`: Rotation angle (default=10)
- **Implementation:** Calls `mesh_manipulator.rotate_object(degrees, counter_clockwise=True)`

## Transformation Matrix Format

The codebase uses standard 4x4 homogeneous transformation matrices:

```
[R11  R12  R13  Tx]
[R21  R22  R23  Ty]
[R31  R32  R33  Tz]
[ 0    0    0   1 ]
```

Where:
- R (3x3 upper-left): Rotation/scaling component
- T (3x1 last column): Translation component

## Key Implementation Details

### Coordinate System
- Uses right-handed coordinate system
- Y-axis typically represents the vertical axis
- Rotations follow right-hand rule

### Transform Application Order
When combining transformations:
1. Scaling is applied first (around object center)
2. Rotation is applied second
3. Translation is applied last

### Libraries Used
- **Open3D**: For viewport-based transformations and visualization
- **Trimesh**: For mesh data manipulation and transformation matrices
- **NumPy**: For matrix operations and calculations
- **SciPy**: For rotation matrix generation (via `scipy.spatial.transform.Rotation`)

## Usage Examples

### Basic Translation
```python
# Move object 5 units right, 3 units up
mesh_manipulator.move_object(dx=5.0, dy=3.0)
```

### Rotation
```python
# Rotate 45 degrees counter-clockwise around Y-axis
mesh_manipulator.rotate_object(45, counter_clockwise=True)
```

### Combined Transform
```python
# Move and scale simultaneously
mesh_manipulator.move_object(dx=2.0, dy=1.0, zoom_factor=1.5)
```

### Mesh Rotation with Trimesh
```python
# Rotate mesh 90 degrees around X-axis
rotated = mesh_tools.rotate_mesh(mesh, axis='x', angle=90)
```

### Mirroring
```python
# Flip mesh along Y-axis
flipped = mesh_tools.flip_mesh(mesh, axis='y')

# Create mirrored copy along Z-axis
mirrored = mesh_tools.add_mirror_mesh(mesh)
```

## Notes

- All rotation angles are specified in degrees (converted to radians internally)
- Transformations preserve vertex colors when present
- The mesh center is cached for performance in repeated operations
- Viewport updates are triggered automatically after transformations