"""Color Generator.

Food waste is usually has colors ranging red to green. This includes yellows
and browns. A usual categorical color selection would thus be unsuitable, as it
aims to provide colors that are as distinct from each other as possible. Since
most food waste is similarly colored, a custom randomization script to choose
colors was necessary. This is the result.

Author:
    Yvan Satyawan <y_satyawan@hotmail.com>

"""
from random import uniform
from colorsys import hsv_to_rgb, rgb_to_hsv
from PIL import Image, ImageDraw, ImageColor, ImageFont


def import_colors(fp: str):
    """Imports colors in a CSV file. This is essentially a file opener.

    The CSV file should have the header ["color"] and colors simply listed
    below it.

    :param fp: File path to the colors csv.
    :returns: A list of hex strings.
    :rtype: list[str]
    """
    with open(fp) as colors_file:
        next(colors_file)  # Skip header
        colors = [line.rstrip("\n") for line in colors_file]

    return colors

def rgb_to_hex(rgb: tuple) -> str:
    """Generates hex string from RGB tuple"""
    hex_values = []
    for v in rgb:
        hex_val = hex(int(255 * v))[2:]
        if len(hex_val) == 0:
            hex_values.append('00')
        elif len(hex_val) == 1:
            hex_values.append(f'0{hex_val}')
        else:
            hex_values.append(hex_val)

    return f'#{hex_values[0]}{hex_values[1]}{hex_values[2]}'


def generate_colors(n: int) -> list:
    """Generates n colors ranging from red to green."""
    colors = set()
    while len(colors) < n:
        color = (uniform(0, 0.25), uniform(.2, 1.), uniform(.3, .8))
        color = rgb_to_hex(hsv_to_rgb(*color))
        if color not in colors:
            colors.add(color)

    colors = list(colors)
    return colors


def sort_hex_by_hue(hex_str: list) -> list:
    """Sorts a list of hex strings by hue value."""
    rgb_colors = [ImageColor.getrgb(i) for i in hex_str]
    hsv_colors = [rgb_to_hsv(*i) for i in rgb_colors]
    hsv_colors.sort(key=lambda x: x[0])
    rgb_colors = [hsv_to_rgb(*i) for i in hsv_colors]
    rgb_colors = [(int(r), int(g), int(b)) for r, g, b in rgb_colors]
    return ["#%02x%02x%02x" % (r, g, b) for r, g, b in rgb_colors]


def visualize_palette(colors: list, save_fp: str = None):
    """Visualizes a given color palette. Assumes 40 colors.

    :param colors: List of the colors in hex to visualize.
    :param save_fp: If save_fp is given, then saves the palette to the specified
        path. Must also contain the filename.
    """
    box_size = 100
    box_h = 5
    box_w = 8
    palette = Image.new('RGB',
                        (box_size * box_w, box_size * box_h),
                        color='#ffffff')
    p_draw = ImageDraw.Draw(palette)
    arial_font = ImageFont.truetype("arial", 36)

    for i in range(8):
        for j in range(5):
            idx = 5 * i + j
            xy_box = (i * box_size,
                      j * box_size,
                      (i + 1) * box_size,
                      (j + 1) * box_size)
            p_draw.rectangle(xy_box, fill=colors[idx])

            # Then draw the index at the center of the box
            text_box_size = arial_font.getsize(str(idx))
            box_center = ((box_size / 2) + xy_box[0],
                          (box_size / 2) + xy_box[1])
            text_box_anchor = (box_center[0] - (text_box_size[0] / 2),
                               box_center[1] - (text_box_size[1] / 2))
            p_draw.text(text_box_anchor, str(idx), "#ffffff", arial_font,
                        stroke_width=1, stroke_fill="#000000")

    palette.show()
    palette.save(save_fp)


if __name__ == '__main__':
    # colors = generate_colors(40)
    colors = import_colors("E:\Offline Docs\Git\\trash-generator\src\\"
                           "colors.csv")
    print(colors)
    visualize_palette(colors, "E:\\Offline Docs\\Git\\trash-generator\\media\\"
                              "colorscheme.png")
