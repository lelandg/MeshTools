"""!
@file viewport_3d.py
@brief A script for visualizing 3D meshes in a 3D viewport using Open3D.
@details This script provides a class for creating a 3D viewport for visualizing and interacting with 3D meshes.
It supports loading, manipulating, and exporting 3D mesh data, as well as customizing viewport appearance and behavior.
The viewport includes user interaction features via keyboard and controllers like a space mouse. However, you need
to change use_space_mouse to True to enable space mouse support.

@note This script requires Open3D and NumPy to be installed.
@version 0.1.1
@date_created 2025-02-26
@date_modified 2025-02-26
@author Leland Green
@email lelandgreenproductions@gmail.com
@license MIT
"""
import configparser
import os
import sys
import traceback

import keyboard
import numpy as np
import open3d
import pygetwindow as gw

if os.getcwd().endswith("MeshTools") or __name__ == "__main__":
    import mesh_manipulation as mesh_manipulation
    from color_transition_gradient_generator import ColorTransition
    from measurement_grid_visualizer import MeasurementGrid
    from mesh_gradient_colorizer import MeshColorizer
else:
    import MeshTools.mesh_manipulation as mesh_manipulation
    from MeshTools.color_transition_gradient_generator import ColorTransition
    from MeshTools.measurement_grid_visualizer import MeasurementGrid
    from MeshTools.mesh_gradient_colorizer import MeshColorizer

verbose = True
use_space_mouse = False
def print_viewport_3d_help():
    """!
    @brief Print the help message for the 3D viewport.
    @details This function prints a help message with instructions for using the 3D viewport to the console.
    (That's the primary reason it's outside the class definition.)
    """
    print("Press 'C' to toggle the rainbow-colored mesh.")
    print("Press 'G' to toggle the measurement grid.")
    print("Press 'D' to toggle the grid between percentage and depth values.")
    print("Press '+' or '-' to zoom in or out.")
    print("Press '<Ctrl>-D' to delete the current mesh.")
    print("Use mouse to navigate the viewport.")
    print("Press 'Esc' to exit the current viewport.")
    print("Press and hold 'Esc' to exit the program.")

"""
 @var SUPPORTED_EXTENSIONS
 @brief Specifies file extensions supported for mesh processing.
 @type: List[str]
 """
SUPPORTED_EXTENSIONS = [".obj", ".ply", ".stl", ".off", ".gltf", ".glb"]

if use_space_mouse:
    from space_mouse_controller import SpaceMouseController


class ThreeDViewport:
    """!
    @brief A class representing a 3D viewport for visualizing and interacting with 3D meshes.

    @details The `ThreeDViewport` class provides tools for loading, manipulating, and exporting 3D mesh data.
    It includes user interaction features via keyboard and controllers like a space mouse,
    as well as the ability to customize viewport appearance and behavior.

    @note This class supports loading mesh files and exporting them in OBJ and STL formats.

    @section Attributes
    - mesh_file (str): The file path of the currently loaded 3D mesh.
    - custom_labels (dict): Custom labels associated with mesh elements.
    - viewer (Any): The underlying 3D visualization instance.
    - prev_show_depth_values (bool): Stores the previous state of depth values visibility.
    - show_depth_values (bool): Determines whether depth values are displayed.
    - display_grid (bool): Indicates whether the grid is displayed.
    - measurement_grid (list): A measurement grid used for 3D overlay representation.
    - show_rainbow_mesh (bool): Flag to apply rainbow colors to the mesh.
    - rainbow_colors (list): Predefined color scheme for the rainbow mesh rendering.
    - rainbow_mesh (Any): The currently rendered mesh with a rainbow colormap.
    - mesh (Any): The active 3D mesh object in the viewport.
    - pan_x (float): Horizontal panning offset of the viewport.
    - pan_y (float): Vertical panning offset of the viewport.
    - zoom_factor (float): The current zoom level.
    - background_color (tuple): The viewport background color, represented as RGB values.
    - mesh_manipulator (Any): A helper for performing transformations and operations on the mesh.
    - space_mouse_controller (Any): Handler for space mouse controller input.
    """

    def __init__(self, initial_mesh_file=None, background_color=None):
        """!@brief Initializes the 3DViewport instance.

        @param initial_mesh_file
            The path to the initial 3D mesh file to load into the viewport.
        @param background_color
            The background color for the viewport in RGB format.
        """
        self.viewer = None  # Replace with the actual viewer instance initialization
        self.window_size = (800, 600)  # Default size (width, height)
        self.window_position = (100, 100)  # Default position (x, y)

        self.mesh_file = None
        self.custom_labels = None
        self.prev_show_depth_values = True
        self.show_depth_values = False
        self.viewer = open3d.visualization.VisualizerWithKeyCallback()
        if initial_mesh_file:
            fname = os.path.split(initial_mesh_file)[-1]
        else:
            fname = ""
        self.title = f"3D Viewport - Open3D v{open3d.__version__} - Press 'H' for help - {fname}"
        if verbose: print (f"Creating window with title: {self.title}")

        # Load the viewport settings if the .ini file exists
        self.ini_file = "config.ini"
        self.load_viewport_settings()
        print (f"Loaded window size: {self.window_size[0]} {self.window_size[1]}. Position: {self.window_position[0]} {self.window_position[1]}")
        self.viewer.create_window(window_name=self.title,
                                  width=self.window_size[0], height=self.window_size[1],
                                  left=self.window_position[0], top=self.window_position[1])

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

    def _setup_key_callbacks(self):
        """!@brief Configures key bindings and input callbacks.

        Sets up the necessary key bindings for user interaction, allowing
        actions like panning, zooming, rotating, and toggling features.
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
        self.viewer.register_key_callback(ord("U"), lambda _: self.zoom(10))  # Zoom in
        self.viewer.register_key_callback(ord("J"), lambda _: self.zoom(-10))  # Zoom out
        self.viewer.register_key_callback(ord("G"), lambda _: self.toggle_grid())  # Zoom out
        self.viewer.register_key_callback(ord("C"), lambda _: self.toggle_rainbow_mesh())
        self.viewer.register_key_callback(ord("D"), lambda _: self.toggle_depth_values())
        self.viewer.register_key_callback(263, lambda _: self.rotate_left(15))
        self.viewer.register_key_callback(262, lambda _: self.rotate_right(15))

    def load_viewport_settings(self):
        """Load the viewport size and position from the .ini file."""
        if os.path.exists(self.ini_file):
            self.config = configparser.ConfigParser()
            self.config.read(self.ini_file)

            if 'Viewport' in self.config:
                self.window_size = (
                    max(300, int(self.config['Viewport'].get('width', '800'))),
                    max(200, int(self.config['Viewport'].get('height', '600'))),
                )
                self.window_position = (
                    max(0, int(self.config['Viewport'].get('x', '100'))),
                    max(0, int(self.config['Viewport'].get('y', '100'))),
                )
                print(f"Loaded window size: {self.window_size}. Position: {self.window_position}")

    def save_viewport_settings(self):
        """Save the current viewport size and position to the .ini file."""
        self.config = configparser.ConfigParser()
        self.config.read(self.ini_file)
        self.config['Viewport'] = {
            'width': self.window_size[0],
            'height': self.window_size[1],
            'x': self.window_position[0],
            'y': self.window_position[1],
        }

        with open(self.ini_file, 'w') as configfile:
            self.config.write(configfile)

    def poll_space_mouse(self, frame):
        """!
        Poll the SpaceMouse for input and process the data for 3D manipulation.
        @param frame
            The current frame number. Unused in this method. Required for the callback.
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


    def rotate_left(self, degrees: float = 10.0):
        """!
        @brief Rotates the mesh or viewport to the left by a specified angle.

        @details This method rotates either the active 3D mesh or the camera viewport
        to the left by the specified number of degrees. The rotation is clockwise
        relative to the viewport.

        @param degrees
            The number of degrees to rotate the view or object. Defaults to 10.

        @note The rotation affects all visible geometries in the scene.
        @return None
        """
        self.mesh_manipulator.rotate_object(degrees, counter_clockwise=False)

    def rotate_right(self, degrees=10):
        """!
        @brief Rotates the mesh or viewport to the right.
        @param degrees The number of degrees to rotate right.
        """
        self.mesh_manipulator.rotate_object(degrees, counter_clockwise=True)

    def toggle_depth_values(self):
        """!
        @brief Toggles the visibility of depth values in the viewport.
        Provides a way to enable or disable visualization of depth values for the loaded mesh.
        """
        self.show_depth_values = not self.show_depth_values
        print(f"Depth values {'visible' if self.show_depth_values else 'hidden'}.")
        self.show_grid()

    def toggle_rainbow_mesh(self):
        """!
        @brief Toggle the visibility of the rainbow-colored mesh in the viewport.
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
        """!
        @brief Ensures the active mesh is visible in the viewport.

        This method re-renders the current mesh in the viewport if it is not already visible.
        """
        self.viewer.clear_geometries()
        if self.show_rainbow_mesh:
            self.viewer.add_geometry(self.rainbow_mesh)
        else:
            self.viewer.add_geometry(self.mesh)

    def toggle_grid(self):
        """!
        @brief Toggles the visibility of the measurement grid overlay.

        Turns the measurement grid on or off in the 3D viewport.
        """
        self.display_grid = not self.display_grid
        if verbose: print(f"Measurement grid {'enabled' if self.display_grid else 'disabled'}.")
        self.show_grid()

    def show_grid(self):
        """!
        @brief Displays the measurement grid overlay in the viewport.

        Visually renders a measurement grid to assist with spatial alignment.
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
        """!
        @brief Clear all geometries currently loaded in the 3D viewer.
        This allows loading a new mesh without accumulating old geometries.
        """
        self.viewer.clear_geometries()
        if verbose: print("Existing geometries cleared from the viewport.")

    def update_custom_labels_from_mesh(self, mesh_instance):
        """!
        @brief Updates self.custom_labels with 21 values based on the range of z values in a given
        open3d.geometry.TriangleMesh instance.

        @param mesh_instance (open3d.geometry.TriangleMesh): An Open3D TriangleMesh instance to extract the z-range from.
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

    def load_mesh(self, mesh: open3d.geometry.TriangleMesh, depth_labels: [str] = None):
        """!
        @brief Loads a new 3D mesh into the viewport.

        @param filepath (str) The path to the mesh file to be loaded.
        @param depth_labels (list) Custom depth labels for the measurement grid.
        """
        try:
            self.custom_labels = depth_labels
            # Clear existing geometry before loading a new mesh
            self.clear_geometries()

            if (isinstance(mesh, str)):
                self.mesh_file = mesh
                # Check if this is an .obj file and if a corresponding .mtl file exists
                if mesh.lower().endswith('.obj'):
                    mtl_file = os.path.splitext(mesh)[0] + '.mtl'
                    if os.path.exists(mtl_file):
                        print(f"Found corresponding material file: {mtl_file}")
                        # Open3D will automatically load the .mtl file if it's in the same directory with the same name

                self.mesh = open3d.io.read_triangle_mesh(mesh)
                if self.mesh.is_empty():
                    raise ValueError(f"Could not load mesh from {mesh}.")
                if self.mesh.has_vertex_colors():
                    self.mesh.compute_vertex_normals()
                    print(f"Loaded mesh from {mesh} with vertex colors.")
                else:
                    print(f"Loaded mesh from {mesh} without vertex colors.")

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
        """!
        @brief Generates a measurement grid in 3D space.

        Creates and overlays a measurement grid that aids in visualizing distances and scales.

        @retval An Open3D LineSet object representing the measurement grid.
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
        """!
        @brief Pans the viewport in a specified direction.

        @param dx The horizontal offset for translation in X plane.
        @param dy The vertical offset for translation in Y plane.
        """
        self.pan_x += dx
        self.pan_y += dy
        ctr = self.viewer.get_view_control()
        ctr.translate(dx, dy, 0.0)  # Translation in the x, y plane

    def zoom(self, delta):
        """!
        @brief Changes the zoom level in the viewport.

        @param delta The zoom multiplier. Positive values zoom in; negative values zoom out.
        """
        self.zoom_factor += delta
        self.zoom_factor = max(0.1, min(self.zoom_factor, 10.0))  # Clamp zoom factor between 0.1 and 10.0
        ctr = self.viewer.get_view_control()
        ctr.set_zoom(1.0 / self.zoom_factor)  # Adjust zoom level

    def run(self):
        """!
        @brief Starts the rendering and interaction loop.

        This method begins the main rendering process for the viewport, enabling user interaction.
        """
        if isinstance(self.mesh, str):
            if verbose: print(f"3D viewport is running for {self.mesh_file}")
        self.viewer.run()
        for w in gw.getWindowsWithTitle(self.title):
            if not w.isMaximized:
                self.window_size = ( w.width - 16, w.height - 39) # Adjust for window borders
                self.window_position = (w.left + 8, w.top + 31) # Adjust for window borders
                print(f"Saving values for window size: {self.window_size}. Position: {self.window_position}")
                self.save_viewport_settings()
        self.viewer.destroy_window()

    def export_mesh_as_obj(self, output_path):
        """!
        @brief Exports the current mesh as an OBJ file.

        @param output_path The file path to save the OBJ mesh.
        """
        if self.mesh is None:
            print("No mesh loaded to export.")
            return
        try:
            open3d.io.write_triangle_mesh(output_path, self.mesh)
            print(f"Successfully exported the mesh to {output_path}")
        except Exception as e:
            print(f"Error exporting mesh to OBJ: {traceback.format_exc()}")

    def export_mesh_as_stl(self, output_path):
        """!
        @brief Exports the current mesh as an STL file.

        @param output_path The file path to save the STL mesh.
        """
        if self.mesh is None:
            print("No mesh loaded to export.")
            return
        try:
            open3d.io.write_triangle_mesh(output_path, self.mesh, write_ascii=True)
            print(f"Successfully exported the mesh to {output_path}")
        except Exception as e:
            print(f"Error exporting mesh to STL: {traceback.format_exc()}")



from file_tools import find_newest_file_in_directory, get_matching_files

def main():
    """!
    Main entry point for processing and visualizing 3D mesh files. This script can take paths to
    mesh files as arguments, collect files using wildcards, or optionally identify the newest file
    in a specified folder or the current directory. It filters the files by supported extensions
    and opens 3D viewports for visualization of valid mesh files.

    This functionality is particularly useful when dealing with meshes in various formats, providing
    support for wildcards and directories. Features include selecting the newest file, keyboard
    interrupt handling, and error-resistant mesh visualization.

    Raises an exception if an error occurs during loading or visualizing a mesh file.
    """
    # Check if there are any arguments passed to the script
    if len(sys.argv) > 1:
        # Collect files using wildcards and filter by extensions
        input_patterns = sys.argv[1:]  # Exclude the script name
        if os.path.exists(input_patterns[0]) and os.path.isdir(input_patterns[0]):
            valid_files = [find_newest_file_in_directory(input_patterns[0], SUPPORTED_EXTENSIONS)]
        else:
            valid_files = get_matching_files(input_patterns, SUPPORTED_EXTENSIONS)

        if not valid_files:
            print("No valid mesh files were provided.")
        else:
            if len(valid_files) > 1:
                print(f"Opening viewports for {len(valid_files)} valid files...")
                print_viewport_3d_help()
            # Open a separate viewport for each valid file
            for mesh_file in valid_files:
                # Check if Esc is pressed
                if keyboard.is_pressed('esc'):
                    key = keyboard.read_event()
                    if keyboard.is_pressed('esc'):
                        print("Esc key held down. Exiting...")
                        break  # Exit the loop and quit the program
                try:
                    print(f"Opening viewport for: {mesh_file}")
                    viewport = ThreeDViewport(initial_mesh_file=mesh_file)
                    viewport.run()
                except Exception as e:
                    print(f"Error while loading or visualizing {mesh_file}: {traceback.format_exc()}")
    else:
        # E.g. fname = "g:/Downloads/lelandgreen_Technical_perspective_Illustration_of_many_rectan_e4408041-480c-40bb-96b6-f415b199dc70_0*2025*.ply"
        fname = find_newest_file_in_directory("./", SUPPORTED_EXTENSIONS)

        print(f"Usage: python {os.path.basename(__file__)} [path_to_mesh1] [path_to_mesh2] ...")
        print(f"If [path_to_mesh1] is a folder name, the newest mesh file in the folder will be used.")
        print(f"If no arguments are provided, the newest mesh file in the current directory will be used.")
        print(f"Wildcards are supported for matching multiple files.")
        print("`*.obj`: Matches all `.obj` files in the current directory.")
        print("`models/**/*.stl`: Matches all `.stl` files recursively in the `models` directory.\r\n"
                "Supported mesh formats: ", ", ".join(SUPPORTED_EXTENSIONS))
        print(f"Example: python {os.path.basename(__file__)} *.obj *.ply sample.stl")
        print(f"Using newest matching file in Downloads for demonstration: {fname}\r\n")

        if fname:
            print_viewport_3d_help()
            viewport = ThreeDViewport(initial_mesh_file=fname)
            viewport.run()
        else:
            print(f"No valid mesh files found in the current directory.")


if __name__ == "__main__":
    main()
