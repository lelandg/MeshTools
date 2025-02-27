"""!
@file color_transition_gradient_generator.py
@brief Generate a color gradient transition between two or more colors.
@details This script generates a color gradient transition between two or more colors. The gradient is created by
interpolating between the specified colors and generating a list of distinct RGB tuples. The gradient can be used for

@author Leland Green
@version 0.1.0
@date_created 2025-02-26
@email lelandgreenproductions@gmail.com
@license MIT
"""

import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb, LinearSegmentedColormap
import numpy as np


class ColorTransition:
    """!@brief Handles the creation of a smooth gradient from a set of given color names.

    @details This class provides functionality to define a gradient between specified named
    colors and generates a list of distinct RGB tuples representing the transition.
    It ensures even distribution of colors across a specified number of steps, while
    handling edge cases where fewer unique colors might be calculated.

    param colors (tuple) A tuple of color names provided during initialization. Used for gradient generation.
    """
    def __init__(self, *colors):
        """!
        Represents a container for multiple colors.

        This class is initialized with a variable number of color values.
        The colors are stored as a tuple, preserving the order they are
        provided. It can hold any number of color values.

        @param colors (tuple) A variable number of colors to be managed.
        """
        self.colors = colors

    def generate_gradient(self, num_steps):
        """!
        Generates a gradient with specified number of color steps based on the colors
        available in the object. The method ensures that at least two colors are used
        to construct the gradient and interpolates colors evenly to fill the
        specified number of steps. Duplicate colors are removed, and if the number of
        unique colors falls short of the requested steps, the colors are evenly
        redistributed to maintain the required number of steps.

        @param num_steps (int) The number of color steps to generate in the gradient.
        @retval list[List[int, int, int]] A list of RGB tuples representing the gradient colors.
        """
        if len(self.colors) < 2:
            raise ValueError("At least two colors are required for a gradient.")

        # Convert named colors to RGB format
        rgb_colors = [to_rgb(color) for color in self.colors]

        # Create a colormap using the given colors
        cmap = LinearSegmentedColormap.from_list("custom_cmap", rgb_colors)

        # Generate evenly spaced color steps
        gradient_colors = [tuple(cmap(i / (num_steps - 1))[:3]) for i in range(num_steps)]

        # Remove duplicate colors (if any are calculated due to input constraints)
        unique_colors = []
        seen = set()
        for color in gradient_colors:
            if color not in seen:
                seen.add(color)
                unique_colors.append(color)

        # Check if the number of unique colors satisfies the required steps
        if len(unique_colors) < num_steps:
            print(
                f"Info: Fewer unique colors than requested ({len(unique_colors)} < {num_steps}). "
                f"Evenly spreading the colors to fill the steps."
            )
            indices = np.linspace(0, len(unique_colors) - 1, num_steps)
            unique_colors = [unique_colors[int(round(i))] for i in indices]

        return unique_colors


def main():
    """!
    This script demonstrates the creation of a color gradient from three distinct
    colors using the `ColorTransition` class. The gradient involves generating
    a specified number of distinct color transitions and visualizing it.

    @exception ValueError If inputs for gradient generation or color visualization are invalid.
    """
    # Create the ColorTransition object with distinct colors
    transition = ColorTransition("red", "orange", "yellow")

    n = 25
    # Generate a set of distinct colors
    gradient = transition.generate_gradient(n)

    # Output the distinct gradient
    print("Generated Colors:", gradient)

    # Visualize the gradient
    gradient_array = np.linspace(0, 1, n).reshape(1, -1)
    gradient_image = np.zeros((n, n, 3))
    for idx, color in enumerate(gradient):
        gradient_image[:, idx, :] = color

    plt.imshow(gradient_image, aspect='auto')
    plt.axis("off")
    plt.show()

# Example usage
if __name__ == "__main__":
    main()