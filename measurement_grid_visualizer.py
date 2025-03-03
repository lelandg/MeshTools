"""!@file measurement_grid_visualizer.py
@brief Measurement grid visualizer module for creating a grid overlay on a 3D mesh.
@details This module provides functionality to create a measurement grid overlay on a 3D mesh. The grid consists of
horizontal and vertical lines with text labels indicating the percentage of the grid spacing. The grid is useful for
measuring distances and aligning objects in the 3D space.
@version 0.1.0
@date_created 2025-02-26
@date_modified 2025-02-26
@author Leland Green
@license MIT
"""
import traceback

import numpy as np
import open3d as o3d

import text_3d

from color_transition_gradient_generator import ColorTransition

rainbow_colors = ["red", "orange", "yellow", "green", "blue", "indigo", "violet"]

class MeasurementGrid:
    """!
    @brief A class for creating and visualizing a 3D measurement grid overlay.
    @details This class provides functionality to create a set of grid lines with percentage labels and render them on
             a 3D scene using the Open3D library. It is primarily designed for measurement and alignment purposes.

    @note Requires the Open3D and NumPy libraries.
    """
    def __init__(self, trimesh, colors=None):
        """!
        @brief Initializes the MeasurementGrid instance.
        @details Constructs the MeasurementGrid object and initializes its parameters.
        @param trimesh The 3D mesh object to overlay the grid on.
        @param colors [Optional] A list of colors to use for the grid lines (default: None).
        """
        self.mesh = trimesh
        if not colors:
            colors = rainbow_colors
        self.colors = ColorTransition(*colors).generate_gradient(21)

    def create_grid_with_labels_from_values(self, values : np.ndarray):
        """! @
        """
        # Ensure the
        if not isinstance(values, np.ndarray):
            try:
                values = np.array(values)
            except Exception as e:
                raise ValueError(f"Invalid depth map format. Expected ndarray, got {type(values)}. Error: {e}")

        # Flatten values to 1D and get min, max values
        depth_values = values.flatten()
        min_depth, max_depth = depth_values.min(), depth_values.max()

        # Create 21 evenly spaced intervals
        intervals = np.linspace(min_depth, max_depth, 21)

        # Format the intervals as text
        text_values = [f"{value:.2f}" for value in intervals]

        return self.create_measurement_grid(text_values) # returns vertices, edges, line_colors, labels


        # from color_transition_gradient_generator import ColorTransition
        # self.colors = ColorTransition(*rainbow_colors).generate_gradient(21)


    def _create_grid_with_labels(self, custom_labels=None):
        """!
        @brief Create the grid lines with associated labels positioned at the endpoints.

        @param custom_labels Optional list of 21 labels to use instead of the default percentage labels.
        @return vertices, edges, line_colors, labels, all as Open3D geometries.
        """
        if self.mesh is None:
            print("No mesh loaded to create a measurement grid.")
            return None

        try:
            # Get the bounding box of the mesh
            bounding_box = self.mesh.get_axis_aligned_bounding_box()
            min_bound = bounding_box.get_min_bound()
            max_bound = bounding_box.get_max_bound()

            # Dimensions of the mesh
            width = max_bound[0] - min_bound[0]  # x-axis
            height = max_bound[1] - min_bound[1]  # y-axis
            depth = max_bound[2] - min_bound[2]  # z-axis

            # Define grid spacing (step size)
            spacing = depth * 0.05  # 5% of the depth

            # Grid vertices, edges, line colors, and labels container
            vertices = []
            edges = []
            line_colors = []  # To store colors for each line
            labels = []  # Store label geometries (text objects)

            # Use custom labels if provided, otherwise generate default percentage labels
            if custom_labels:
                if len(custom_labels) != 21:
                    raise ValueError("custom_labels must be a list of exactly 21 elements.")
                if not isinstance(custom_labels[0], str):
                    if type(custom_labels[0]) in [int, float]:
                        custom_labels = [f"{int(label)}" for label in custom_labels]
                    else:
                        raise ValueError("custom_labels must be a list of strings or numbers. Got list of: ", type(custom_labels[0]))
                label_texts = custom_labels
            else:
                label_texts = [f"{i * 5}%" for i in range(21)]  # Default labels (0, 5, 10, ..., 100)

            # Generate grid lines and labels
            num_intervals = 21  # 21 intervals for 5% steps (0 to 100%)
            for i, label_text in enumerate(label_texts):
                z = min_bound[2] + i * spacing  # Calculate z-level

                # Horizontal line along the x-axis, at fixed y and z
                start_x = [min_bound[0], min_bound[1], z]
                end_x = [max_bound[0], min_bound[1], z]
                vertices.extend([start_x, end_x])
                edges.append([len(vertices) - 2, len(vertices) - 1])  # Connect start and end
                line_colors.append(self.colors[i])  # Assign corresponding color

                # Add text label at the end of the horizontal line
                text_label_x = text_3d.create_text_3d(label_text, position=end_x, color=self.colors[i], height=20, depth=2)
                labels.append(text_label_x)

                # Vertical line along the y-axis, at fixed x and z
                start_y = [min_bound[0], min_bound[1], z]
                end_y = [min_bound[0], max_bound[1], z]
                vertices.extend([start_y, end_y])
                edges.append([len(vertices) - 2, len(vertices) - 1])  # Connect start and end
                line_colors.append(self.colors[i])  # Assign corresponding color

                # Add text label at the end of the vertical line
                text_label_y = text_3d.create_text_3d(label_text, position=end_y, color=self.colors[i], height=20, depth=2)
                labels.append(text_label_y)

            # Convert vertices and edges to numpy arrays
            vertices = np.array(vertices, dtype=np.float64)
            edges = np.array(edges, dtype=np.int32)

            return vertices, edges, line_colors, labels
        except Exception as e:
            print(f"Error in creating the measurement grid: {traceback.format_exc()}")
            return None

    def create_measurement_grid(self, labels=None):
        """!
        @brief Create a list of Open3D geometries (LineSet and text labels)
        to be used for the measurement grid.

        @return A list of Open3D geometries, including the grid lines and text labels.
        """
        if self.mesh is None:
            print("No mesh loaded to create a measurement grid.")
            return []

        # Generate grid components
        vertices, edges, line_colors, labels = self._create_grid_with_labels(labels)

        # Create and configure LineSet for the grid
        grid_lines = o3d.geometry.LineSet()
        grid_lines.points = o3d.utility.Vector3dVector(vertices)
        grid_lines.lines = o3d.utility.Vector2iVector(edges)
        grid_lines.colors = o3d.utility.Vector3dVector(line_colors)

        # Collect all geometries (LineSet + text labels) into a list
        geometries = [grid_lines]  # Start with the grid lines
        geometries.extend(labels)  # Add all the text labels

        return geometries
