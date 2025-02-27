## Overview
This user documentation provides a guide to the command-line usage of a Python toolset called **Mesh Tools**. The tool is designed for performing various operations on 3D meshes. Below is an overview of its features, usage, and examples.

The `mesh_tools.py` module is designed to simplify and enhance the processing of 3D mesh objects in Python. It provides a variety of tools to manipulate and adjust meshes, making it useful for designers, developers, or anyone working on 3D geometry tasks such as rotation, solidification, mirroring, and more.
---

# Command Line Usage for **Mesh Tools**

python mesh_tools.py [-h] [--output OUTPUT] [-depth DEPTH] [-flat] [-mirror] [--rotate ROTATE] [-fix] [--normals] [--show] [--verbose] input_mesh

Mesh Tools

positional arguments:
  input                 Input mesh file path.

options:
  --output OUTPUT, -o OUTPUT
                        Optional output mesh file name. Default: <input>_<suffix>.<ext> where suffix is 'solid', 'mirror', or 'fixed'. Example usage: "python mesh_tools.py mesh.ply -f -depth -0.3 -mirror -fix" Produces three meshes: solid, mirror, and fixed in the same folder as the original.
  -depth DEPTH, -d DEPTH
                        Depth offset for solidification. Type float. Default: 0.0. The lowest existing z-value will always override this.
  -flat, -f             Solidify the mesh with a flat back.
  -mirror, -m           Mirror the front of the mesh to the back. (Written for depth-map generated meshes.)
  --rotate ROTATE, -r ROTATE
                        Rotate the mesh by the given angle in degrees. Specify the axis as 'x', 'y', or 'z'. E.g., -r x:-90
  -fix, -x              Fix the mesh by removing unreferenced and duplicate vertices and duplicate faces and closing holes.  
  --normals, -n         Fix normals. Must use with -fix to get this. (It slows down the process.)
  --show, -s            Show each generated mesh in the 3D viewer.
  --verbose, -v         Enable verbose mode
  -h, --help            show this help message and exit
---

## General Description

The **Mesh Tools** script provides functionalities to manipulate and process 3D meshes, including operations such as rotation, solidification, mirroring, flipping, and fixing. It is accessible through a Python command-line interface and allows users to run specific mesh processing tasks with relevant parameters.

---

## Prerequisites

To run the script, make sure you have:
1. **Python 3.x** installed. Optionally, conda may provide faster runtime. YMMV.
2. Run `pip install -r requirements.txt` to install the necessary dependencies.
3. Your 3D mesh files ready for processing.
---

## Notes

- The file paths and other arguments should be valid for appropriate operation.
- The tool works with commonly used 3D file formats such as `.obj`, `.ply` and `.stl`. Ensure your input files are in the correct format.
- If mesh has colors, output will also.
- The script will generate new mesh files based on the operations performed, with the default naming convention being `<input>_<suffix>.<ext>`, where`<suffix>` is the operation. E.g., "_flat_back" for solidification with a flat back.
- The `--show` option opens a 3D viewer to display the generated meshes. This uses the included viewer script, vieport_3d.py.
- This is a standalone script that takes a single file name, a directory name or wildcard inputs. It is not a library, though you're welcome to use it in your own scripts. Usage is as simple as `python viewport_3d.py G:\Downloads\*.ply`.
- Press <Esc> to close the current viewer window. 
- Hold down <Esc> to close it *and* exit the program, when using multiple filenames or wildcards. (Stops processing additional files.) 

---

## Real-World Example

Below is a complete example for fixing and solidifying a mesh (`example.obj`) while enabling verbose mode:

```shell script
# Fix a mesh with verbose mode:
python mesh_tools.py ./models/example.obj -x -v
# Make a flat back for all models in the models directory with a Z depth of 0.5 (or minimum existing z-value, if lower):
python mesh_tools.py ./models/*.ply -f -d 0.5 -v
# Solidify all models in the models directory to a Z depth of -0.3 (or minimum existing z-value, if lower):
# Create a mirror mesh, mirror it, fix it and rotate it by -90 degrees around the x-axis:
python mesh_tools.py ./models/*.ply -f -d -0.3 -m -x -r x:-90 -v
```

---
Feel free to reach out if you have issues or need more advanced usage! See mesh_tools.py for my contact info.

############################################################################################################
## Develeper Documentation of Features
The module is centered around the `MeshTools` class, along with supporting attributes and functions. Here are the key features you can leverage:
1. **Rotation of meshes** – Rotate a mesh object to achieve desired orientations.
2. **Solidification of meshes** – Convert a thin mesh into a solid object, including options for flat backing.
3. **Flipping meshes** – Flip entire mesh objects for modifications or corrections.
4. **Mirroring** – Add mirrored versions of the mesh for symmetric designs.
5. **Mesh fixing** – Correct issues in mesh geometry with systematic cleanup procedures.
6. **Main Method** – A standalone `main` function typically serving as an entry point to execute various functionalities.

---

## Classes and Methods

### **1. Attributes**
The module uses the following attributes:
- **`np`** – A key attribute that likely refers to the NumPy library.
- **`R`** – A generic attribute representing some constant or helper function.
- **Instance Attributes (Inside `MeshTools`)**
  - **`mesh`** – The core 3D mesh object being manipulated and processed.
  - **`verbose`** – A boolean or integer indicating whether detailed logs or outputs should be displayed (`True` = detailed processing steps).
  - **`spinner`** – A status utility for tracking progress during operations.

---

### **2. `MeshTools` Class**

The `MeshTools` class is the core of the module, encapsulating various mesh-related operations. All methods operate on the mesh instance stored within the class.

#### **`__init__(self, mesh, verbose=False)`**
- **Purpose**: Initialize the `MeshTools` object with a mesh instance and an optional verbosity setting.
- **Parameters**:
  - `mesh`: The 3D mesh object to work with.
  - `verbose`: (Optional) A flag to toggle detailed output for debugging or logging.

---

#### **Key Methods**
Below are the essential methods provided by the `MeshTools` class:

1. **`rotate_mesh(self, axis, angle)`**
   - **Purpose**: Rotates the mesh around a defined axis (e.g., X, Y, Z) by a specified angle.
   - **Parameters**:
     - `axis`: The axis around which the rotation should occur.
     - `angle`: The angle (in degrees or radians) to rotate the mesh.

2. **`solidify_mesh(self, thickness)`**
   - **Purpose**: Solidifies a mesh by adding thickness to it. The result is a solid 3D object derived from the original thin geometry.
   - **Parameters**:
     - `thickness`: The amount to thicken the mesh.

3. **`solidify_mesh_with_flat_back(self, thickness)`**
   - **Purpose**: Similar to `solidify_mesh`, but adds a flat back to the solidified mesh. This is often used for objects that need a flat base or "backside."
   - **Parameters**:
     - `thickness`: The amount to thicken the mesh.

4. **`flip_mesh(self)`**
   - **Purpose**: Flips the mesh (e.g., inverting geometry, flipping the normals), typically for adjustment or correction purposes.

5. **`add_mirror_mesh(self, axis)`**
   - **Purpose**: Creates a mirrored copy of the mesh and adds it to the object for symmetry along a given axis.
   - **Parameters**:
     - `axis`: Axis along which the mirror should occur (e.g., X, Y, Z).

6. **`fix_mesh(self)`**
   - **Purpose**: Performs corrective operations to resolve issues within the mesh, such as fixing broken geometry or ensuring consistency in structure.
   - **Usage**: This is often an automated process without additional parameters.

---

### **3. Main Function**
The `main` function serves as the module's entry point, enabling execution as a standalone script.

- **Purpose**: Executes predefined or dynamic mesh-processing operations by calling various tool methods from the `MeshTools` class.
- **Usage**: This is typically invoked when the script is run directly (e.g., `python mesh_tools.py`). Custom commands and logic may be integrated within `main`.

---

## Usage Instructions

### **Importing the Module**
To start using the module, import it into your script as shown below:
```python
from mesh_tools import MeshTools
```

### **Example Workflow**
Here’s an illustrative example of how to use `MeshTools` to manipulate a 3D mesh:

```python
# Import MeshTools
from mesh_tools import MeshTools

# Example mesh object (replace with an actual 3D mesh instance)
example_mesh = ...

# Initialize the tool
mesh_tools = MeshTools(mesh=example_mesh, verbose=True)

# Rotate the mesh
mesh_tools.rotate_mesh(axis='X', angle=90)

# Add a mirrored version of the mesh
mesh_tools.add_mirror_mesh(axis='Y')

# Fix the mesh
mesh_tools.fix_mesh()
```

---

## Common Use Cases
1. **3D Printing Preparation**: Create watertight and solid meshes suitable for 3D printing.
2. **Artwork Mirroring**: Add symmetry to 3D objects for designs.
3. **Game Development**: Fix and optimize meshes for use in engines like Unity or Unreal.
4. **Geometry Repair**: Use `fix_mesh` to correct errors in downloaded or scanned meshes.

---

## Conclusion
The `mesh_tools.py` module is an essential utility for anyone working with 3D meshes. By leveraging features like rotation, solidification, flipping, and mirroring, you can simplify complex geometry operations and achieve professional results in your workflows.

For further assistance, feel free to refer to the codebase or consult the relevant function and class documentation.
