__author__ = "Leland Green"
from _version import version
__version__ = version
__date_created__ = "2025-01-28"
__email__ = "lelandgreenproductions@gmail.com"
__license__ = "Open Source CC0 v1.09" # License of this script is free for all purposes.

"""
Version 0.1.0: Initial release.
"""

import argparse
import os
import sys
import traceback

import numpy as np
import trimesh
from trimesh import Trimesh
from scipy.spatial.transform import Rotation as R

from spinner import Spinner


class MeshTools:
    def __init__(self, mesh_file_name="", verbose=True):
        """
        Initialize the depth estimation and mesh generation pipeline.
        :param model_type: "midas" (default) or "dense_depth". Specifies the depth estimation model.
        """
        self.mesh = None
        self.verbose = verbose

        if mesh_file_name and os.path.exists(mesh_file_name):
            self.mesh = trimesh.load(mesh_file_name)
            if self.mesh.triangles is None:
                self.mesh.trianglulate()

        if verbose: self.spinner = Spinner(f"{{time}} ")
        if self.verbose:
            if self.mesh is not None:
                print(f"Loaded mesh with {len(self.mesh.vertices)} vertices and {len(self.mesh.faces)} faces.")
            else:
                print("No mesh loaded.")


    def rotate_mesh(self, mesh: Trimesh=None, axis: str='y', angle: float=90.0) -> Trimesh:
        """
        Rotate a Trimesh object around the specified axis by the given angle.

        :param mesh: A Trimesh object to rotate.
        :param axis: The axis of rotation ('x', 'y', or 'z').
        :param angle: The rotation angle in degrees. Negative values rotate downward or counter-clockwise.
        :return: A new Trimesh object with rotated vertices.
        """
        if mesh is None and self.mesh is not None:
            mesh = self.mesh
        if mesh is None:
            raise ValueError("No mesh provided for solidification.")
        if axis not in {'x', 'y', 'z'}:
            raise ValueError("Invalid axis specified. Please choose from 'x', 'y', or 'z'.")
        if not isinstance(mesh, Trimesh):
            raise TypeError("The mesh parameter must be a Trimesh object.")

        # Map axis to a unit vector
        axis_map = {
            'x': [1, 0, 0],
            'y': [0, 1, 0],
            'z': [0, 0, 1]
        }
        rotation_vector = np.radians(angle) * np.array(axis_map[axis])  # Convert to radians

        # Create the rotation matrix using scipy's Rotation module
        rotation_matrix = R.from_rotvec(rotation_vector).as_matrix()

        # Apply the rotation to the vertices
        rotated_vertices = mesh.vertices @ rotation_matrix.T

        # Return a new mesh with rotated vertices
        rotated_mesh = Trimesh(
            vertices=rotated_vertices,
            faces=mesh.faces,
            process=False  # Prevent automatic modification of the geometry
        )

        # Preserve vertex colors, if available
        if hasattr(mesh.visual, 'vertex_colors') and mesh.visual.vertex_colors is not None:
            rotated_mesh.visual.vertex_colors = mesh.visual.vertex_colors

        return rotated_mesh

    def solidify_mesh_with_flat_back(self, mesh: Trimesh = None, flat_back_depth: float = -1.0) -> Trimesh:
        """
        Solidify the mesh by making the back side flat while preserving vertex colors.
        All added faces will face backward (toward -z).

        :param mesh: Existing 3D trimesh object with vertex colors.
        :param flat_back_depth: The depth value for the flat back surface.
        :return: A new solidified trimesh object with vertex colors preserved.
        """
        if mesh is None and self.mesh is not None:
            mesh = self.mesh
        if mesh is None:
            raise ValueError("No mesh provided for solidification.")

        # from trimesh.smoothing import filter_laplacian
        # mesh = filter_laplacian(mesh)  # Ensure the mesh is clean
        # Extract the original vertices, faces, and vertex colors
        original_vertices = mesh.vertices
        original_faces = mesh.faces
        original_colors = mesh.visual.vertex_colors if hasattr(mesh.visual, 'vertex_colors') else None

        # Assign default colors if none exist
        if original_colors is None:
            original_colors = np.ones((len(original_vertices), 3))  # Default white color

        z_values = mesh.vertices[:, 2]
        # pnt(i) = 0.5 * pnt(i) + 0.25 * pnt(i - 1) + 0.25 * pnt(i + 1)

        # Calculate the minimum and maximum z values
        min_z = z_values.min()
        max_z = z_values.max()

        if min_z < flat_back_depth:
            if self.verbose: print(f"Overriding depth of {flat_back_depth}. Existing Z values are, min: {min_z}, max: {max_z}. Using min.")
            flat_back_depth = min_z

        # Create the "flat back" vertices by setting all z values to flat_back_depth
        flat_back_vertices = original_vertices.copy()
        flat_back_vertices[:, 2] = flat_back_depth

        # Combine original vertices and flat back vertices
        combined_vertices = np.vstack([original_vertices, flat_back_vertices])

        # Duplicate vertex colors for the flat back vertices
        combined_colors = np.vstack([original_colors, original_colors])

        # Create faces for the flat back surface, ensure reversed order for facing backward
        num_vertices = len(original_vertices)
        flat_back_faces = np.fliplr(original_faces + num_vertices)  # Reverse face winding

        # Create side faces to connect the front and flat back vertices
        side_faces = []
        for face in original_faces:
            for i in range(3):
                # Get the current edge (start, end)
                start = face[i]
                end = face[(i + 1) % 3]
                side_faces.append([start, end, end + num_vertices])
                side_faces.append([start, end + num_vertices, start + num_vertices])
                # Create two faces to cover each side, ensure they face backward
                side_faces.append([start, end + num_vertices, end])
                side_faces.append([start, start + num_vertices, end + num_vertices])

        side_faces = np.array(side_faces)

        # Combine all faces: front, flat back, and side
        combined_faces = np.vstack([original_faces, flat_back_faces, side_faces])

        # Create a new mesh with the combined vertices, faces, and preserved colors
        solid_mesh = trimesh.Trimesh(
            vertices=combined_vertices,
            faces=combined_faces,
            vertex_colors=combined_colors
        )

        return solid_mesh

    # Assuming 'mesh' is your created Trimesh object
    def flip_mesh(self, mesh: Trimesh = None) -> Trimesh:
        """
        Flip the mesh geometry horizontally (flipping the y-axis).
        Adjust the vertex colors accordingly if vertex colors are present.

        :param mesh: Trimesh object to be flipped.
        :return: Transformed Trimesh object with flipped geometry and adjusted colors.
        """
        if mesh is None and self.mesh is not None:
            mesh = self.mesh
        if mesh is None:
            raise ValueError("No mesh provided for solidification.")
        # Define the transformation matrix for flipping along the y-axis
        flip_matrix = np.array([
            [1, 0, 0, 0],  # No change to x-axis
            [0, -1, 0, 0],  # Flip y-axis
            [0, 0, 1, 0],  # No change to z-axis
            [0, 0, 0, 1],  # Homogeneous coordinate
        ])

        # Apply the transformation to the mesh
        mesh.apply_transform(flip_matrix)

        # # Check if the mesh has vertex colors
        # if hasattr(mesh.visual, 'vertex_colors') and mesh.visual.vertex_colors is not None:
        #     # Optionally adjust the vertex colors during flipping
        #     # Example: If flipping affects orientation-dependent effects, handle it here
        #     # For instance, flipping colors (if mirrored) can be implemented, but often the color remains unchanged
        #     flipped_colors = mesh.visual.vertex_colors.copy()  # Currently colors are unchanged
        #
        #     # Update flipped colors (if needed) - placeholder for any operation on colors.
        #     mesh.visual.vertex_colors = flipped_colors

        return mesh

    def add_mirror_mesh(self, mesh: Trimesh) -> Trimesh:
        """
        Add a mirrored backside to the provided 3D mesh and stitch the halves together.
        This creates a water-tight mesh by connecting the edges of the original
        mesh and the mirrored counterpart.

        :param mesh: A Trimesh object representing the front-facing mesh.
        :return: A new Trimesh object with a water-tight mirrored back side.
        """
        if self.verbose: print("Adding mirrored backside to the mesh...")

        # Optionally combine vertex colors if provided
        if hasattr(mesh.visual, 'vertex_colors') and mesh.visual.vertex_colors is not None:
            original_colors = mesh.visual.vertex_colors
            combined_colors = np.vstack([original_colors, original_colors])
        else:
            combined_colors = None

        # Original mesh vertices and faces
        original_vertices = mesh.vertices
        original_faces = mesh.faces

        # Create mirrored vertices by negating the z-axis
        mirrored_vertices = original_vertices.copy()
        mirrored_vertices[:, 2] = -mirrored_vertices[:, 2]

        # Adjust face indices for mirrored vertices
        num_original_vertices = len(original_vertices)
        mirrored_faces = original_faces.copy() + num_original_vertices

        # Reverse the face winding for the mirrored side
        mirrored_faces = mirrored_faces[:, ::-1]

        # Combine original and mirrored vertices and faces
        combined_vertices = np.vstack([original_vertices, mirrored_vertices])
        combined_faces = np.vstack([original_faces, mirrored_faces])

        if self.verbose: print("Finding boundary edges...")
        original_edges = mesh.edges_sorted
        mirrored_edges = np.roll(original_edges, shift=1, axis=1) + num_original_vertices

        original_edges_set = set(map(tuple, original_edges))
        mirrored_edges_set = set(map(tuple, mirrored_edges))

        # shared_edges = original_edges_set.intersection(mirrored_edges_set)
        # boundary_edges = original_edges_set.symmetric_difference(shared_edges)
        boundary_edges = original_edges_set - mirrored_edges_set

        if len(boundary_edges) == 0 and self.verbose:
            print("Warning: No boundary edges detected! Mesh may already be watertight.")

        if self.verbose: print("Stitching boundary edges...")
        stitching_faces = []
        for edge in boundary_edges:
            # Validate that the edge has exactly two elements
            if len(edge) != 2:
                raise ValueError(f"Edge must contain exactly 2 vertices, but found {len(edge)}: {edge}")

            v1, v2 = edge
            mv1, mv2 = v1 + num_original_vertices, v2 + num_original_vertices

            stitching_faces.append([v1, v2, mv1])
            stitching_faces.append([v2, mv2, mv1])

            # Ensure proper vertex relationships before adding additional faces
            if mv2 != v1 and mv1 != v2:
                stitching_faces.append([mv2, v2, v1])
                stitching_faces.append([mv1, mv2, v1])

        stitching_faces = np.array(stitching_faces)

        if self.verbose: print("Combining faces, applying colors, creating watertight mesh...")
        # Combine stitching faces with others
        watertight_faces = np.vstack([combined_faces, stitching_faces])

        # Create the watertight Trimesh object
        watertight_mesh = Trimesh(
            vertices=combined_vertices,
            faces=watertight_faces,
            vertex_colors=combined_colors,
            process=False
        )
        if self.verbose: print(f"Finished creating mesh with {len(watertight_mesh.vertices)} vertices and {len(watertight_mesh.faces)} faces.")
        watertight_mesh.remove_unreferenced_vertices()
        if self.verbose: print(f"After remove_unreferenced_vertices() {len(watertight_mesh.vertices)} vertices and {len(watertight_mesh.faces)} faces.")
        if self.verbose: print(f"Finished creating mesh with {len(watertight_mesh.faces)} faces.")
        return watertight_mesh

    def fix_mesh(self, mesh: Trimesh = None, fix_normals : bool = False) -> {Trimesh}:
        """
        Fix the mesh by removing any duplicate vertices and faces.
        :param mesh: Trimesh object to be fixed.
        :return: Trimesh object with duplicate vertices and faces removed.
        """
        if mesh is None and self.mesh is not None:
            mesh = self.mesh
        if mesh is None:
            raise ValueError("No mesh provided for solidification.")

        # Remove duplicate vertices and faces
        if self.verbose: print(f"Removing unreferenced vertices...")
        mesh.remove_unreferenced_vertices()

        if len(mesh.faces) != len(mesh.unique_faces()):
            if self.verbose: print(f"Removing {len(mesh.faces) - len(mesh.unique_faces())} duplicate faces of {len(mesh.faces)} faces")
            mesh.update_faces(mesh.unique_faces())

        if not mesh.is_watertight:
            if self.verbose: print("Mesh is not watertight! Filling holes...")
            # Fill holes
            mesh.fill_holes()

        if fix_normals:
            if self.verbose: print("Fixing normals...")
            mesh.fix_normals()  # Ensure outward normals

        return mesh

def main():
    parser = argparse.ArgumentParser(description="Mesh Tools",
                                     epilog='Example usage: "python mesh_tools.py mesh.obj -f -depth -0.3 -mirror -fix" '
                                            "Produces three meshes: solid, mirror, and fixed in the same folder as the original.")
    parser.add_argument("input", type=str, help="Input mesh file path.")
    parser.add_argument("--output", "-o", type=str,
                        help="Optional output mesh file name. Default: <input>_<suffix>.<ext> where suffix is 'solid', 'mirror', or 'fixed'.\r\n"
                        "If you provide a different file extension, you specify STL, OBJ, PLY, etc. as the output format.")
    parser.add_argument("-depth", "-d", type=float, default=0.0, help="Depth offset for solidification. Type float. Default: 0.0.\r\nThe lowest existing z-value will always override this.")
    parser.add_argument("-flat", "-f", action="store_true", help="Solidify the mesh with a flat back.")
    parser.add_argument("-mirror", "-m", action="store_true",
                        help="Mirror the front of the mesh to the back. (Written for depth-map generated meshes.)")
    parser.add_argument("--rotate", "-r", type=str, help="Rotate the mesh by the given angle in degrees. Specify the axis as 'x', 'y', or 'z'. E.g., -r x:90")
    parser.add_argument("-fix", "-x", action="store_true",
                        help="Fix the mesh by removing unreferenced and duplicate vertices and duplicate faces and closing holes.")
    parser.add_argument("--normals", "-n", action="store_true", help="Fix normals. Must use with -fix to get this. (It slows down the process.)")
    parser.add_argument("--show", "-s", action="store_true", help="Show each generated mesh in the 3D viewer.")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose mode")

    if len(sys.argv) == 1:
        parser.print_help()
        exit(1)

    args = parser.parse_args()
    input_name = args.input

    if not os.path.exists(input_name):
        print(f"Error: Input file not found: {input_name}")
        parser.print_help()
        exit(1)

    if not (args.flat or args.mirror or args.fix or args.rotate):
        print(
            "Error: No operation selected. Use -flat, -mirror, or -fix to specify an operation.\r\n(I.e., a minimum of -f, -m or -x. Use -h for help)")
        parser.print_help()
        exit(1)

    output_name = args.output
    if not output_name:
        output_name = input_name

    basename, ext = os.path.splitext(output_name)
    if args.flat:
        flat_name = basename + "_flat_back" + ext
    if args.mirror:
        mirror_name = basename + "_mirror" + ext
    if args.fix:
        fix_name = basename + "_fixed" + ext
    if args.rotate:
        axis, angle = args.rotate.split(":")
        rotate_name = basename + f"_rotate_{axis}{angle}" + ext
    verbose = args.verbose

    mesh_tools = MeshTools(input_name, verbose)
    outnames = []
    try:
        if args.rotate:
            axis, angle = args.rotate.split(":")
            angle = float(angle)
            print(f"Rotating mesh by {angle} degrees along the {axis}-axis...")
            rotated_mesh = mesh_tools.rotate_mesh(axis=axis, angle=angle)
            rotated_mesh.export(rotate_name)
            print(f"Saved rotated mesh to: {rotate_name}")
            outnames.append(rotate_name)

        if args.flat:
            print("Solidifying mesh with flat back...")
            solid_mesh = mesh_tools.solidify_mesh_with_flat_back(flat_back_depth=args.depth)
            solid_mesh.export(flat_name)
            print(f"Saved solid mesh with flat back to: {flat_name}")
            outnames.append(flat_name)

        if args.mirror:
            print("Adding mirrored backside to the mesh...")
            mirrored_mesh = mesh_tools.add_mirror_mesh(mesh_tools.mesh)
            mirrored_mesh.export(mirror_name)
            print(f"Saved mirrored mesh to: {mirror_name}")
            outnames.append(mirror_name)

        if args.fix:
            print("Fixing mesh...")
            fixed_mesh = mesh_tools.fix_mesh(mesh_tools.mesh, args.normals)
            fixed_mesh.export(fix_name)
            print(f"Saved fixed mesh to: {fix_name}")
            outnames.append(fix_name)

    except Exception as e:
        print(f"Error: {traceback.format_exc()}")
        exit(1)

    if args.show:
        print("Showing the generated meshes in the 3D viewer...")
        for name in outnames:
            import viewport_3d
            viewport = viewport_3d.ThreeDViewport(name)
            viewport.run()
        print("Done.")
    print("Done.")

if __name__ == "__main__":
    main()