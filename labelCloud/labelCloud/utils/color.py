import colorsys
from typing import Any, List
from nptyping import NDArray, Float32, Shape
import numpy as np
import numpy.typing as npt
import pkg_resources
import sys 
from pathlib import Path
from ..definitions.types import Color3f


def get_distinct_colors(n: int) -> List[str]:
    """generate visualy distinct colors
    Args:
        n (int): number of colors
    Returns:
        npt.NDArray[np.float32]: n x 3 (rgb) values between 0 and 1
    """
    hue_partition = 1.0 / (n + 1)
    colors = np.vstack(
        [
            np.array(
                colorsys.hsv_to_rgb(
                    hue_partition * value,
                    1.0 - (value % 2) * 0.5,
                    1.0 - (value % 3) * 0.1,
                )
            )
            for value in range(0, n)
        ]
    ).astype(np.float32)

    return [rgb_to_hex(color) for color in colors]


def colorize_points_with_height(
    points: NDArray[Any, Float32], z_min: float, z_max: float
) -> NDArray[Any, Float32]:
  #  palette = np.loadtxt(
  #      pkg_resources.resource_filename("labelCloud.resources", "rocket-palette.txt")
  #  )
    palette = np.loadtxt(
    get_palette_path("rocket-palette.txt")
    )
    palette_len = len(palette) - 1

    colors = np.zeros(points.shape)
    for ind, height in enumerate(points[:, 2]):
        colors[ind] = palette[round((height - z_min) / (z_max - z_min) * palette_len)]
    return colors.astype(np.float32)

def get_palette_path(filename):
    """Get the path to the icon file, considering whether running in PyInstaller bundle or not."""
    if getattr(sys, 'frozen', False):
        # Running in a PyInstaller bundle
        base_path = Path(sys._MEIPASS)
        return base_path / "resources" / filename
    else:
        # Running in a development environment
        base_path = Path(__file__).resolve().parent.parent.parent
        return base_path / "labelCloud" / "resources" / filename
    
    

def hex_to_rgb(hex: str) -> Color3f:
    """Converts a hex color to a list of RGBA values.

    Args:
        hex (str): The hex color to convert.

    Returns:
        List[float]: The RGB values.
    """
    hex = hex.lstrip("#")
    return tuple(  # type: ignore
        [int(hex[i : i + 2], 16) / 255 for i in range(0, 6, 2)]
    )


def rgb_to_hex(color: Color3f) -> str:
    """Converts a list of RGBA values to a hex color.

    Args:
        color (ColorRGB): The RGB values.

    Returns:
        str: The hex color.
    """
    return "#%02x%02x%02x" % tuple([int(c * 255) for c in color])
