## Overview

This documentation provides a guide to the command-line usage of a Python toolset called **Mesh Tools**. It also covers use in your own Python projects. The tool is designed for performing various operations on 3D meshes, including solidification, mirroring, rotation, and fixing. By following the instructions outlined here, you can effectively utilize the tool to process and manipulate 3D mesh objects.

The `mesh_tools.py` module is designed to simplify and enhance the processing of 3D mesh objects in Python. It provides a variety of tools to manipulate and adjust meshes, making it useful for designers, developers, or anyone working on 3D geometry tasks such as rotation, solidification, mirroring, and more.

---

# Command Line Usage for mesh_tools.py

```shell
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
```

---

# Command Line Usage for viewport_3d.py

Basic usage:
```shell
python viewport_3d.py [path_to_mesh1] [path_to_mesh2] ...
```
If [path_to_mesh1] is a folder name, the newest mesh file in the folder will be used.
If no arguments are provided, the newest mesh file in the current directory will be used.
Wildcards are supported for matching multiple files.
`*.obj`: Matches all `.obj` files in the current directory.
`models/**/*.stl`: Matches all `.stl` files recursively in the `models` directory.
Supported mesh formats:  .obj, .ply, .stl, .off, .gltf, .glb

More examples:
```shell
python viewport_3d.py *.obj *.ply sample.stl
python viewport_3d.py -v d:\Downloads\ 
python viewport_3d.py d:\Downloads\mesh_for_today*.ply
```

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
- The `--show` option opens a 3D viewer to display the generated meshes. This uses the included viewer script, **vieport_3d.py**.
- This is a standalone script that takes a single file name, a directory name or wildcard inputs. It is not a library, though you're welcome to use it in your own scripts. Usage is as simple as **`python viewport_3d.py G:\Downloads\*.ply`**.
- Press <Esc> to close the current viewer window. 
- Hold down <Esc> to close it *and* exit the program, when using multiple filenames or wildcards. (Stops processing additional files.) 

---

## Real-World Example

Below is a complete example for fixing and solidifying a mesh (`./models/example.obj`) with verbose mode enabled (`-v`).
The third example demonstrates solidifying, mirroring, fixing, and rotating a mesh by -90 degrees around the x-axis. Basically, all the options in one command.
```shell
# Fix a mesh:
python mesh_tools.py ./models/example.obj -x -v

# Make a flat back for all models in the models directory with a Z depth of 0.5 (or minimum existing z-value, if lower):
python mesh_tools.py ./models/*.ply -f -d 0.5 -v

# Solidify all models in the models directory to a Z depth of -0.3 (or minimum existing z-value, if lower), then
# create a mirror mesh, mirror it, fix it and rotate it by -90 degrees around the x-axis:
python mesh_tools.py ./models/*.ply -f -d -0.3 -m -x -r x:-90 -v
```

---
Feel free to reach out if you have issues or need more advanced usage! See mesh_tools.py for my contact info.

---

## Developer Usage Instructions

If you'd like more thorough documentation, just use Doxygen to generate it. The Doxyfile is included in the repository.
Just go to the folder you downloaded this and run "doxygen". Results will be in the "docs/html" folder.

### **Importing the Module**
To start using the module, import it into your script as shown below:
```
from mesh_tools import MeshTools
```

### **Example Workflow**
Here’s an illustrative example of how to use `MeshTools` to manipulate a 3D mesh from your Python code:

```
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

## Conclusion
The `mesh_tools.py` module is an essential utility for anyone working with 3D meshes. By leveraging features like rotation, solidification, flipping, and mirroring, you can simplify complex geometry operations and achieve professional results in your workflows.

For further assistance, feel free to refer to the codebase or consult the relevant function and class documentation.
