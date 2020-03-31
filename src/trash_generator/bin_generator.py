"""Bin Generator

Generates a waste bin background with a transparency mask where the contents of
the bin should be.

Author:
    Yvan Satyawan <y_satyawan@hotmail.com>

Created on:
    March 30, 2020
"""
from PIL import Image, ImageDraw
import random


def generate_bin(bg, outside_color, inside_color, h=800, w=1024):
    """Generates a waste bin based on the given image dimensions.

    This function generates a waste bin somewhere in the middle of an image with
    the given dimensions. The waste bin makes up most of the center of the image
    but maybe offset randomly.

    :param h: Height of the resulting image.
    :param w: Width of the resulting image.
    :type h: int
    :type w: int

    :returns: A waste bin image with mode 'RGB', a binary mask with values
        1 where the inside of the bin is as an PIL Image with mode '0' and
        shape (h, w), and a list with the [x0, y0, x1, y1] coordinates of the
        inside of the bin.
    :rtype: tuple
    """
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
    mask = Image.new('1', (w, h), color=1)
    mask_draw = ImageDraw.Draw(mask)

    # Choose bin shape
    bin_shape = random.choice(['circular', 'square'])
    if bin_shape == 'circular':
        draw.ellipse(outside_dim, fill=outside_color)
        draw.ellipse(inside_dim, fill=inside_color)
        mask_draw.ellipse(inside_dim, fill=0)
    else:
        draw.rectangle(outside_dim, fill=outside_color)
        draw.rectangle(inside_dim, fill=inside_color)
        mask_draw.rectangle(inside_dim, fill=0)

    return img, mask, inside_dim


if __name__ == '__main__':
    # Testing Code
    generate_bin()
