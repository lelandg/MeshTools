import glob
import sys
import traceback
import os

import keyboard
import numpy as np
import open3d

import mesh_manipulation
from color_transition_gradient_generator import ColorTransition
from measurement_grid_visualizer import MeasurementGrid
from mesh_gradient_colorizer import MeshColorizer
from spinner import Spinner

verbose = False
use_space_mouse = False

if use_space_mouse:
    from space_mouse_controller import SpaceMouseController


class ThreeDViewport:
    custom_labels: object

    def __init__(self, initial_mesh_file=None, background_color=None):
        """
        Initialize the 3D viewport using Open3D with default parameters
        for camera movement, rotation, and mesh rendering.
        :param initial_mesh_file: Optional initial mesh file to load and display.
        :param background_color: Background color for the viewport as a list [R, G, B].
                                 Uses dark gray [0.2, 0.2, 0.2] if None.
        """
        self.mesh_file = None
        self.custom_labels = None
        self.prev_show_depth_values = True
        self.show_depth_values = False
        self.viewer = open3d.visualization.VisualizerWithKeyCallback()
        if initial_mesh_file:
            fname = os.path.split(initial_mesh_file)[-1]
        else:
            fname = ""
        title = f"3D Viewport - Open3D v{open3d.__version__} - Press 'H' for help - {fname}"
        if verbose: print (f"Creating window with title: {title}")
        self.viewer.create_window(window_name=title, width=1024, height=768, left=800, top=50)

        rainbow_colors = ["red", "orange", "yellow", "green", "blue", "indigo", "violet"]
        self.rainbow_colors = ColorTransition(*rainbow_colors).generate_gradient(255)
        self.rainbow_mesh = None
        self.show_rainbow_mesh = False
        self.mesh = None  # Placeholder for the loaded 3D mesh
        self.measurement_grid = None  # Placeholder for the measurement grid
        self.display_grid = False  # Flag to toggle the measurement grid visibility
        self.zoom_factor = 1.0  # Default zoom factor
        self.pan_x = 0.0  # Pan translation on x-axis
        self.pan_y = 0.0  # Pan translation on y-axis

        # Default background color (dark gray if None)
        if background_color is None:
            background_color = [0.2, 0.2, 0.2]
        else:
            # Check if background_color needs scaling (assume >1.0 implies [0, 255] range)
            if max(background_color) > 1.0:
                background_color = [x / 255.0 for x in background_color]

        self.background_color = background_color

        self.viewer.get_render_option().background_color = self.background_color
        print(f"Background color set to: {self.background_color}")

        # Register interaction callbacks
        self._setup_key_callbacks()
        if initial_mesh_file:
            self.load_mesh(initial_mesh_file)
            self.show_grid()
        self.mesh_manipulator = mesh_manipulation.MeshManipulation(self.viewer, self.mesh)
        self.space_mouse_controller = None
        if use_space_mouse:
            self.space_mouse_controller = SpaceMouseController()
            if self.space_mouse_controller.sm_device is not None:
                self.viewer.register_animation_callback(self.poll_space_mouse)

    def poll_space_mouse(self, frame):
        """
        Poll the SpaceMouse for input and process the data for 3D manipulation.
        """
        try:
            data = self.space_mouse_controller.read_data()
            if data is not None:
                if data["t"] == self.space_mouse_controller.SMP_MOVE_CHANNEL:
                    flip = data["f"] == 255
                    pan_x = data["x"]
                    pan_y = data["y"]
                    if flip:
                        pan_x = -pan_x
                        pan_y = -pan_y
                    depth_movement = data["z"]

                    if pan_x != 0 or pan_y != 0 or depth_movement != 1.0:
                        self.mesh_manipulator.move_object(pan_x, pan_y, 0)

                    rot_amount = data["rot"] / 255 * 10
                    counter_clockwise = data["cc"] == 255
                    if rot_amount != 0:
                        self.mesh_manipulator.rotate_object(rot_amount, counter_clockwise)
                elif data["t"] == self.space_mouse_controller.SMP_BUTTON_CHANNEL:
                    # Handle button press events if necessary
                    pass
                elif data["t"] == self.space_mouse_controller.SMP_ROTATE_CHANNEL:
                    # Handle rotation channel events if necessary
                    pass

        except KeyboardInterrupt:
            print("Polling interrupted by user. Cleaning up...")
        # finally:
        #     print("SpaceMouse controller disconnected.")
        #     self.space_mouse_controller = SpaceMouseController()


    def _setup_key_callbacks(self):
        """
        Set up key callbacks for panning, zooming, and navigation in the viewport.
        """
        # Panning with arrow keys (WASD for directions)
        # self.viewer.register_key_callback(ord("W"), lambda _: self.pan(0, 10))  # Pan up
        # self.viewer.register_key_callback(ord("S"), lambda _: self.pan(0, -10))  # Pan down
        # self.viewer.register_key_callback(ord("A"), lambda _: self.pan(-10, 0))  # Pan left
        # self.viewer.register_key_callback(ord("D"), lambda _: self.pan(10, 0))  # Pan right
        #
        # # Zooming with '+' and '-' keys
        # self.viewer.register_key_callback(ord("+"), lambda _: self.zoom(10))  # Zoom in
        # self.viewer.register_key_callback(ord("-"), lambda _: self.zoom(-10))  # Zoom out
        self.viewer.register_key_callback(ord("="), lambda _: self.zoom(10))  # Zoom in
        self.viewer.register_key_callback(ord("-"), lambda _: self.zoom(-10))  # Zoom out

        # Support for Shift + Arrow Keys for zoom
        self.viewer.register_key_callback(ord("U"), lambda _: self.zoom(0.1))  # Zoom in
        self.viewer.register_key_callback(ord("J"), lambda _: self.zoom(-0.1))  # Zoom out
        self.viewer.register_key_callback(ord("g"), lambda _: self.toggle_grid())  # Zoom out
        self.viewer.register_key_callback(ord("G"), lambda _: self.toggle_grid())  # Zoom out
        self.viewer.register_key_callback(ord("c"), lambda _: self.toggle_rainbow_mesh())
        self.viewer.register_key_callback(ord("C"), lambda _: self.toggle_rainbow_mesh())
        self.viewer.register_key_callback(ord("D"), lambda _: self.toggle_depth_values())
        self.viewer.register_key_callback(263, lambda _: self.rotate_left())
        self.viewer.register_key_callback(262, lambda _: self.rotate_right())

    def rotate_left(self):
        self.mesh_manipulator.rotate_object(10, counter_clockwise=False)

    def rotate_right(self):
        self.mesh_manipulator.rotate_object(10, counter_clockwise=True)

    def toggle_depth_values(self):

        self.show_depth_values = not self.show_depth_values
        print(f"Depth values {'visible' if self.show_depth_values else 'hidden'}.")
        self.show_grid()

    def toggle_rainbow_mesh(self):
        """
        Toggle the visibility of the rainbow-colored mesh in the viewport.
        """
        self.viewer.clear_geometries()
        self.show_rainbow_mesh = not self.show_rainbow_mesh
        print(f"Rainbow-colored mesh {'visible' if self.show_rainbow_mesh else 'hidden'}.")
        self.show_mesh()
        if self.rainbow_mesh is None:
            # Create a rainbow-colored mesh for the current mesh
            if verbose: print ("Creating rainbow mesh...")
            self.rainbow_mesh = MeshColorizer().apply_gradient_to_mesh(self.mesh, self.rainbow_colors)
            self.viewer.add_geometry(self.rainbow_mesh)
            if verbose: print ("Rainbow-colored mesh added to the viewport.")
        else:
            # Toggle the visibility of the rainbow-colored mesh
            if verbose: print(f"Rainbow-colored mesh {'visible' if self.show_rainbow_mesh else 'hidden'}.")
        self.show_grid()

    def show_mesh(self):
        self.viewer.clear_geometries()
        if self.show_rainbow_mesh:
            self.viewer.add_geometry(self.rainbow_mesh)
        else:
            self.viewer.add_geometry(self.mesh)

    def toggle_grid(self):
        """
        Toggle the visibility of the measurement grid in the viewport.
        """
        self.display_grid = not self.display_grid
        if verbose: print(f"Measurement grid {'enabled' if self.display_grid else 'disabled'}.")
        self.show_grid()

    def show_grid(self):
        """
        Show or hide the measurement grid in the viewport based on the display_grid flag.
        """
        try:
            self.show_mesh()
            if self.display_grid:
                if self.show_depth_values != self.prev_show_depth_values or self.measurement_grid is None:
                    self.prev_show_depth_values = self.show_depth_values
                    if self.show_depth_values and self.custom_labels:
                        self.measurement_grid = MeasurementGrid(self.mesh).create_measurement_grid(labels=self.custom_labels)
                    else:
                        self.measurement_grid = MeasurementGrid(self.mesh).create_measurement_grid()

                # Add each grid component separately to the viewer
                for geometry in self.measurement_grid:
                    self.viewer.add_geometry(geometry)
            else:
                # Remove each grid component separately from the viewer
                if self.measurement_grid:
                    for geometry in self.measurement_grid:
                        self.viewer.remove_geometry(geometry)
        except Exception as e:
            print(f"Error showing grid: {traceback.format_exc()}")

    def clear_geometries(self):
        """
        Clear all geometries currently loaded in the 3D viewer.
        This allows loading a new mesh without accumulating old geometries.
        """
        self.viewer.clear_geometries()
        if verbose: print("Existing geometries cleared from the viewport.")

    def update_custom_labels_from_mesh(self, mesh_instance):
        """
        Updates self.custom_labels with 21 values based on the range of z values in a given
        open3d.geometry.TriangleMesh instance.

        Args:
            mesh_instance (open3d.geometry.TriangleMesh): An Open3D TriangleMesh instance to extract the z-range from.
        """
        if not isinstance(mesh_instance, open3d.geometry.TriangleMesh):
            raise ValueError(f"The provided mesh_instance is not a valid open3d.geometry.TriangleMesh instance. Got {type(mesh_instance)}.")

        # Extract vertex positions (numpy array)
        vertices = np.asarray(mesh_instance.vertices)

        if vertices.size == 0:
            raise ValueError("The provided mesh_instance does not contain any vertices.")

        # Extract z-values from the vertex positions
        z_values = vertices[:, 2]

        # Compute the minimum and maximum z-values
        z_min, z_max = np.min(z_values), np.max(z_values)

        # Generate 21 equally spaced values within the range
        self.custom_labels = np.linspace(z_min, z_max, num=21).tolist()

    def load_mesh(self, mesh: open3d.geometry.TriangleMesh, depth_labels: [str] = None) -> None:
        """
        Load a new 3D triangular mesh file into the viewport.
        Clears any existing geometry to ensure no duplicates.

        :param mesh: Path to the new mesh file (.obj, .stl, .ply, etc.).
        :param depth_labels: Optional custom depth labels for the measurement grid.
        """
        try:
            self.custom_labels = depth_labels
            # Clear existing geometry before loading a new mesh
            self.clear_geometries()

            if (isinstance(mesh, str)):
                self.mesh_file = mesh
                self.mesh = open3d.io.read_triangle_mesh(mesh)
                if self.mesh.is_empty():
                    raise ValueError(f"Could not load mesh from {mesh}.")
            elif (isinstance(mesh, open3d.geometry.TriangleMesh)):
                self.mesh = mesh
                self.mesh_file = "(Trimesh)"
            else:
                if verbose: print(f"Unsupported mesh type: {type(mesh)}")

            self.update_custom_labels_from_mesh(self.mesh)

            self.mesh.compute_vertex_normals()

            # Add the new mesh for rendering
            self.viewer.add_geometry(self.mesh)
            # self._center_mesh_in_view()
            self.viewer.get_render_option().background_color = self.background_color

            self.measurement_grid = MeasurementGrid(self.mesh).create_measurement_grid()
            if verbose: print(f"Mesh loaded: {mesh}")
        except Exception as e:
            print(f"Error loading mesh: {traceback.format_exc()}")

    def create_measurement_grid(self, custom_labels=None):
        """
        Create a measurement grid using Open3D's LineSet to overlay on the viewport.

        :return: An Open3D LineSet object representing the measurement grid.
        """
        if self.mesh is None:
            print("No mesh loaded to create a measurement grid.")
            return None

        if self.custom_labels is not None:
            self.custom_labels = custom_labels
        else:
            self.update_custom_labels_from_mesh(self.mesh)

        # Create a measurement grid based on the bounding box of the mesh
        grid = MeasurementGrid(self.mesh).create_measurement_grid(custom_labels)

        # # Set the grid color to light gray
        # grid.paint_uniform_color([0.7, 0.7, 0.7])

        return grid

    def pan(self, dx, dy):
        """
        Pan the camera by translating it in the x and y directions.

        :param dx: Translation along the x-axis.
        :param dy: Translation along the y-axis.
        """
        self.pan_x += dx
        self.pan_y += dy
        ctr = self.viewer.get_view_control()
        ctr.translate(dx, dy, 0.0)  # Translation in the x, y plane

    def zoom(self, delta):
        """
        Zoom the camera in or out based on a delta factor.

        :param delta: Positive for zoom in, negative for zoom out.
        """
        self.zoom_factor += delta
        self.zoom_factor = max(0.1, min(self.zoom_factor, 10.0))  # Clamp zoom factor between 0.1 and 10.0
        ctr = self.viewer.get_view_control()
        ctr.set_zoom(1.0 / self.zoom_factor)  # Adjust zoom level

    def run(self):
        """
        Start the Open3D visualization window.
        """
        if isinstance(self.mesh, str):
            if verbose: print(f"3D viewport is running for {self.mesh_file}")
        self.viewer.run()
        self.viewer.destroy_window()

    def export_mesh_as_obj(self, output_file):
        """
        Export the current mesh to a Wavefront OBJ file.

        :param output_file: The path to save the OBJ file.
        """
        if self.mesh is None:
            print("No mesh loaded to export.")
            return
        try:
            open3d.io.write_triangle_mesh(output_file, self.mesh)
            print(f"Successfully exported the mesh to {output_file}")
        except Exception as e:
            print(f"Error exporting mesh to OBJ: {traceback.format_exc()}")

    def export_mesh_as_stl(self, output_file):
        """
        Export the current mesh to an STL file.

        :param output_file: The path to save the STL file.
        """
        if self.mesh is None:
            print("No mesh loaded to export.")
            return
        try:
            open3d.io.write_triangle_mesh(output_file, self.mesh, write_ascii=True)
            print(f"Successfully exported the mesh to {output_file}")
        except Exception as e:
            print(f"Error exporting mesh to STL: {traceback.format_exc()}")


def find_newest_file_in_directory(directory_path):
    # Define the list of allowed file extensions
    allowed_extensions = [".obj", ".ply", ".stl", ".off", ".gltf", ".glb"]

    spinner = Spinner("{time} Scanning files...")
    # Scan the directory and collect files with allowed extensions
    files_with_timestamps = []
    for root, dirs, files in os.walk(directory_path):
        if root.startswith(".") or len(files) == 0:
            continue  # Skip hidden directories
        spinner.spin(f"Scanning {len(files)} files in {root}...")
        for file in files:
            # Check file extension
            if any(file.lower().endswith(ext) for ext in allowed_extensions):
                spinner.spin()
                file_path = os.path.join(root, file)
                modified_time = os.path.getmtime(file_path)  # Get the last modified timestamp
                files_with_timestamps.append((file_path, modified_time))

    # Check if any files are collected
    if not files_with_timestamps:
        return None  # Return None if no valid files are found

    spinner.spin(f"Found {len(files_with_timestamps)} matching files.")
    # Find the newest file
    newest_file = max(files_with_timestamps, key=lambda x: x[1])
    return newest_file[0]  # Return the file name of the newest file


    # # Example usage
    # directory_to_scan = "C:/example_directory"  # Replace with your directory path
    # newest_file = find_newest_file_in_directory(directory_to_scan)
    # if newest_file:
    #     print(f"The newest file is: {newest_file}")
    # else:
    #     print("No valid files found in the directory.")


def print_help():
    print("Press 'C' to toggle the rainbow-colored mesh.")
    print("Press 'G' to toggle the measurement grid.")
    print("Press 'D' to toggle the grid between percentage and depth values.")
    print("Use mouse to navigate the viewport.")
    print("Press 'Esc' to exit the current viewport.")
    print("Press and hold 'Esc' to exit the program.")


if __name__ == "__main__":
    # Supported mesh formats
    SUPPORTED_EXTENSIONS = [".obj", ".ply", ".stl", ".off", ".gltf", ".glb"]

    def get_matching_files(patterns, supported_extensions):
        """Expand wildcard patterns and return a list of matching files with supported extensions."""

        matched_files = []
        for pattern in patterns:
            spinner = Spinner(f"Matching files for: {pattern}. Searching...")
            spinner.spin()
            # Resolve wildcard patterns
            for file in glob.glob(pattern, recursive=True):
                if os.path.isfile(file) and os.path.splitext(file)[1].lower() in supported_extensions:
                    matched_files.append(file)
                    spinner.spin("{time} Matched: " + file)

        spinner.spin(f"Found {len(matched_files)} matching files.")
        return matched_files


    # Check if there are any arguments passed to the script
    if len(sys.argv) > 1:
        # Collect files using wildcards and filter by extensions
        input_patterns = sys.argv[1:]  # Exclude the script name
        if os.path.exists(input_patterns[0]) and os.path.isdir(input_patterns[0]):
            valid_files = [find_newest_file_in_directory(input_patterns[0])]
        else:
            valid_files = get_matching_files(input_patterns, SUPPORTED_EXTENSIONS)

        if not valid_files:
            print("No valid mesh files were provided.")
        else:
            if len(valid_files) > 1:
                print(f"Opening viewports for {len(valid_files)} valid files...")
                print_help()
            # Open a separate viewport for each valid file
            for mesh_file in valid_files:
                # Check if Esc is pressed
                if keyboard.is_pressed('esc'):
                    key = keyboard.read_event()
                    if keyboard.is_pressed('esc'):
                        print("Esc key held down. Exiting...")
                        break  # Exit the loop and quit the program
                print(f"Opening viewport for: {mesh_file}")
                try:
                    viewport = ThreeDViewport(initial_mesh_file=mesh_file)
                    viewport.run()
                except Exception as e:
                    print(f"Error while loading or visualizing {mesh_file}: {traceback.format_exc()}")
    else:
        # E.g. fname = "g:/Downloads/lelandgreen_Technical_perspective_Illustration_of_many_rectan_e4408041-480c-40bb-96b6-f415b199dc70_0*2025*.ply"
        fname = find_newest_file_in_directory("./")

        print(f"Usage: python {os.path.basename(__file__)} [path_to_mesh1] [path_to_mesh2] ...")
        print(f"If [path_to_mesh1] is is a folder name, the newest mesh file in the folder will be used.")
        print(f"If no arguments are provided, the newest mesh file in G:/Downloads will be used.")
        print(f"Wildcards are supported for matching multiple files.")
        print("`*.obj`: Matches all `.obj` files in the current directory.")
        print("`models/**/*.stl`: Matches all `.stl` files recursively in the `models` directory.\r\n"
                "Supported mesh formats: ", ", ".join(SUPPORTED_EXTENSIONS))
        print(f"Example: python {os.path.basename(__file__)} *.obj *.ply sample.stl")
        print(f"Using newest matching file in Downloads for demonstration: {fname}\r\n")

        if fname:
            print_help()
            viewport = ThreeDViewport(initial_mesh_file=fname)
            viewport.run()
        else:
            print(f"No valid mesh files found in the current directory.")
