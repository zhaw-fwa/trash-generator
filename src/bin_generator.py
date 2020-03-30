"""Bin Generator

Generates a waste bin background with a transparency mask where the contents of
the bin should be.

Author:
    Yvan Satyawan <y_satyawan@hotmail.com>

Created on:
    March 30, 2020
"""
from PIL import Image, ImageDraw
import numpy as np
import random





def choose_colors():
    """Chooses a random selection of colors from the color lists above.

    :returns A tuple with colors for background, bin exterior, and bin
        interior.
    :rtype: tuple
    """
    bg_colors = ['#D9D9D9', '#CBD8CD', '#B6B4D4', '#FFFFFF', '#90A2C3',
                 '#848588', '#FFF7BC']
    outside_colors = ['#ED1C24', '#F68E56', '#363636', '#00A651', '#0054A6']
    inside_colors = ['#111111', '#F4F4F4']

    return (random.choice(bg_colors), random.choice(outside_colors),
            random.choice(inside_colors))


def generate_bin(h=800, w=1024):
    """Generates a waste bin based on the given image dimensions.

    This function generates a waste bin somewhere in the middle of an image with
    the given dimensions. The waste bin makes up most of the center of the image
    but maybe offset randomly.

    :param h: Height of the resulting image.
    :param w: Width of the resulting image.
    :type h: int
    :type w: int

    :returns A waste bin image with mode 'RGB' and a binary mask with values 1
        where the inside of the bin is. This np.ndarray has shape (h, w)
    :rtype: tuple(Image, np.ndarray)
    """
    # First pick the necessary colors
    bg, outside_color, inside_color = choose_colors()

    img = Image.new('RGB', (w, h), bg)
    draw = ImageDraw.Draw(img)

    # Figure out dimensions of waste bin. It is based on the minor axis of
    # the image and is always squared or circular.
    bin_radius = random.uniform(0.75, 1.0) * min(h, w) / 2
    bin_lip = min(h, w) / 20
    inside_width = bin_radius - bin_lip

    # Choose where to place the bin as an x, y translation from the image center
    max_shift = min(h, w) / 20
    bin_center = (random.uniform(-max_shift, max_shift) + w / 2,
                  random.uniform(-max_shift, max_shift) + h / 2)

    # Calculate bin bounding box
    outside_dim = [bin_center[0] - bin_radius,
                   bin_center[1] - bin_radius,
                   bin_center[0] + bin_radius,
                   bin_center[1] + bin_radius]

    inside_dim = [bin_center[0] - inside_width,
                  bin_center[1] - inside_width,
                  bin_center[0] + inside_width,
                  bin_center[1] + inside_width]

    outside_dim = [int(i) for i in outside_dim]
    inside_dim = [int(i) for i in inside_dim]

    # Create mask
    mask = Image.new('1', (w, h), color=0)
    mask_draw = ImageDraw.Draw(mask)

    # Choose bin shape
    bin_shape = random.choice(['circular', 'square'])
    if bin_shape == 'circular':
        draw.ellipse(outside_dim, fill=outside_color)
        draw.ellipse(inside_dim, fill=inside_color)
        mask_draw.ellipse(inside_dim, fill=1)
    else:
        draw.rectangle(outside_dim, fill=outside_color)
        draw.rectangle(inside_dim, fill=inside_color)
        mask_draw.rectangle(inside_dim, fill=1)

    # Generate inside binary mask
    mask = np.array(mask)

    return img, mask


if __name__ == '__main__':
    # Testing Code
    generate_bin()
