"""Color Generator."""
from random import uniform
from colorsys import hsv_to_rgb
from PIL import Image, ImageDraw


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


def visualize_palette(colors: list):
    """Visualizes a given color palette. Assumes 40 colors."""
    palette = Image.new('RGB', (800, 400), color='#ffffff')
    p_draw = ImageDraw.Draw(palette)

    for i in range(8):
        for j in range(5):
            idx = 5 * i + j
            xy_box = (i * 100,
                      j * 100,
                      (i + 1) * 100,
                      (j + 1) * 100)
            p_draw.rectangle(xy_box, fill=colors[idx])
    palette.show()


if __name__ == '__main__':
    colors = generate_colors(40)
    print(colors)
    visualize_palette(colors)
