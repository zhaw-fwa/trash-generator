"""Bin Sequence.

Fills the waste bin with trash. This script takes the bin generated by
bin_generator.py and adds shapes from trash_gen.py sequentially into the
bin, creating image sequences along with their annotations.

Author:
    Yvan Satyawan <y_satyawan@hotmail.com>

Created on:
    March 30, 2020
"""
from PIL import Image, ImageDraw, ImageColor, ImageFilter
from os.path import join, abspath, split
import numpy as np
from math import ceil, sin, cos, radians, sqrt
from random import randint, choice, uniform
from colorsys import rgb_to_hls, hls_to_rgb
from trash_generator import TrashGenerator, generate_bin
from utils import import_colors
import noise


class BinSequence:
    def __init__(self, class_csv: str, color_csv: str,
                 h: int = 800, w: int =1024):
        """Class that can generate sequences of h, w bin images.

        Generates an image with 40 classes, of which only the first 20 classes
        should be classified.

        :param class_csv: Path to a CSV file containing class definitions.
        :param color_csv: Path to a CSV file containing color definitions.
        :param h: Height of image.
        :param w: Width of image

        """
        self.h = h
        self.w = w
        self.class_colors = import_colors(color_csv)

        self.bin_bg = None
        self.bin_mask = None
        self.inside_pos = None
        self.inside_dim = None
        self.color_bg, self.color_out, self.color_in = None, None, None
        self._randomize_bin()
        self.trash_generator = TrashGenerator(class_csv)
        self.pattern_dir = join(split(split(abspath(__file__))[0])[0],
                                'patterns')

        # Calculate how much to scale the light gradient
        # The gradient is a circle, so finding the distance to the corner of the
        # generated bin and resizing the gradient's diameter will ensure the
        # the entire generated bin is covered.
        d = ceil(sqrt(((h / 2) ** 2) + ((w / 2) ** 2)) * 2)
        self.light_gradient = Image.open(join(self.pattern_dir, 'gradient.png'))
        self.light_gradient = self.light_gradient.convert('L')
        self.light_gradient = self.light_gradient.resize(
            (d, d), resample=Image.BICUBIC
        )

        self.white = None
        self.black = None

    @staticmethod
    def _largest_enclosed_rect(w, h, angle):
        """Calculates maximum area rectangle inside a rotated rectangle.

        :param int w: Width of the original rectangle.
        :param int h: Height of the original rectangle.
        :param int angle: Angle of the rotation in degrees
        :returns: The largest area rectangle enclosed by the original rotated
            rectangle as an (x0, y0, x1, y1) tuple representing the new crop
            box.
        :rtype: tuple[int, int, int, int]
        """
        longer_width = w >= h
        side_long, side_short = (w, h) if longer_width else (h, w)
        rad_ang = radians(angle)

        # Search only through the first quadrant
        sin_a = abs(sin(rad_ang))
        cos_a = abs(cos(rad_ang))

        if (side_short <= 2. * sin_a * cos_a * side_long
            or abs(sin_a - cos_a) < 1e-10):
            # Case 1: Half constrained where two crop corners touch the longer side
            # and the other two corners are on the mid-line parallel to the longer
            # line
            x = 0.5 * side_short
            if longer_width:
                lw = int(x / sin_a)  # lw = largest width
                lh = int(x / cos_a)  # lh = largest height
            else:
                lw = x / cos_a
                lh = x / sin_a
        else:
            # Fully constrained case where crop touches all 4 sides
            cos_2a = (cos_a * cos_a) - (sin_a * sin_a)
            lw = (w * cos_a - h * sin_a) / cos_2a
            lh = (h * cos_a - w * sin_a) / cos_2a

        x0 = (w / 2) - (lw / 2)
        y0 = (h / 2) - (lh / 2)
        x1 = (w / 2) + (lw / 2)
        y1 = (w / 2) + (lh / 2)

        return [int(x0), int(y0), int(x1), int(y1)]

    def _generate_pattern(self, label, color):
        """Generates a pattern blended with the colors representing each class.

        :param int label: The class label. Used to get the pattern to use for
            the class.
        :param int color: The color index that should be used for the class.
        :returns: A list of tiled versions of each pattern as large as the
            main image size.
        :rtype: PIL.Image.Image
        """

        img = Image.open(join(self.pattern_dir, f'pattern__{label:04}.png'))

        # Rotate image
        rot_ang = randint(0, 360)
        img = img.rotate(rot_ang)
        img = img.crop(self._largest_enclosed_rect(200, 200, rot_ang))
        # Translate image
        im_size = img.size
        translation = [randint(0, im_size[0]), randint(0, im_size[0])]
        img = np.array(img)
        img = np.roll(img, np.array(translation), axis=0)
        img = Image.fromarray(img)
        # scale
        resize_to = int(uniform(.3, 2) * im_size[0])
        img = img.resize((resize_to, resize_to))

        # Tile the image and crop it to the main size
        reps = [ceil(self.h * 3 / img.size[0]), ceil(self.w * 3 / img.size[1])]
        img_array = np.array(img)
        tiled = np.tile(img_array, reps)
        img_tiled = Image.fromarray(tiled).crop((0, 0, self.w, self.h))

        # Generate perlin noise
        z_val = randint(0, 255)
        w = ceil(img.size[0] / 8)
        h = ceil(img.size[1]/ 8)
        noise_texture = np.zeros((w, h))
        for x in range(w):
            for y in range(h):
                noise_texture[x, y] = noise.snoise3(x, y, z_val, octaves=2)
        noise_texture *= 127.0
        noise_texture += 128.0
        noise_texture = Image.fromarray(noise_texture.astype(np.uint8))
        noise_texture = noise_texture.resize((self.w, self.h)).convert('L')
        img_tiled = Image.blend(img_tiled, noise_texture, .5).convert('RGB')

        # Randomly shift the color hue by 2% of a full circle
        color = [float(i) / 255.
                 for i in ImageColor.getrgb(self.class_colors[color])]
        color = np.array(rgb_to_hls(*color))
        shifts = np.random.uniform(-0.1, 0.1, [3]) * color
        color += shifts
        color = color.clip(0, 1)
        color = [int(x * 255) for x in hls_to_rgb(*color.tolist())]

        # Add color
        color_layer = Image.new('RGB', (self.w, self.h),
                                color='#{:02x}{:02x}{:02x}'.format(*color))
        pattern = Image.blend(img_tiled, color_layer, .5)

        return pattern.convert('RGBA')

    @staticmethod
    def _choose_colors():
        """Chooses a random selection of colors from the predifined color lists.

        :returns: A tuple with colors for background, bin exterior, and bin
            interior.
        :rtype: tuple
        """
        bg_colors = ['#D9D9D9', '#CBD8CD', '#B6B4D4', '#FFFFFF', '#90A2C3',
                     '#848588', '#FFF7BC']
        outside_colors = ['#ED1C24', '#F68E56', '#363636', '#00A651', '#0054A6']
        inside_colors = ['#252525', '#DFDFDF']

        return choice(bg_colors), choice(outside_colors), choice(inside_colors)

    def _randomize_bin(self):
        self.color_bg, self.color_out, self.color_in = self._choose_colors()

        self.bin_bg, self.bin_mask, self.inside_pos = generate_bin(
            self.color_bg, self.color_out, self.color_in, self.h, self.w
        )

        self.inside_dim = (self.inside_pos[2] - self.inside_pos[0],
                           self.inside_pos[3] - self.inside_pos[1])

        # Create light and shadow
        bin_mask_array = np.array(self.bin_mask)
        self.white = np.full((self.h, self.w, 4), 255, dtype=np.uint8)
        self.white[bin_mask_array] = np.array([0, 0, 0, 0])
        self.white = Image.fromarray(self.white)
        self.black = np.full((self.h, self.w, 4), (0, 0, 0, 255),
                             dtype=np.uint8)
        self.black[np.invert(bin_mask_array)] = np.array([0, 0, 0, 0])
        self.black = Image.fromarray(self.black)

    def _place_trash(self, polygons):
        """Places the trash somewhere in the bin.

        :param list[np.ndarray] polygons: List of [2, n] arrays representing the
            trash items to be placed. Each array is a polygon representation.
        :returns: Transformed [2, n] arrays of the trash placed somewhere in
            the bin.
        :rtype: list[np.ndarray]
        """
        # If there are more objects, they have to be made smaller.
        min_size = 0.1 / len(polygons)
        max_size = 0.8 / len(polygons)

        out_list = []

        for polygon in polygons:
            factor = np.random.uniform(min_size, max_size, [2])
            scale = self.inside_dim * factor
            polygon = (polygon.T * scale)
            translate = [randint(0, self.inside_dim[0]) + self.inside_pos[0],
                         randint(0, self.inside_dim[1]) + self.inside_pos[1]]
            polygon += np.array(translate)
            out_list.append(polygon.T)

        return out_list

    def _rasterize_trash(self, polygon, label, color):
        """Rasterizes the polygon by filling it with a pattern.

        Places the class pattern, adds a color, and adds Perlin noise to the
        polygon.
        Places a pattern fill over an object with random rotation, scaling, and
        translation. Also randomly shift the color value of the given label
        slightly and

        :param np.ndarray polygon: The polygon to be filled with shape [2, n]
        :param int label: The label the polygon has.
        :param int color: The color index the polygon should have.
        :returns: An image of the polygon filled with a colorized pattern.
        :rtype: PIL.Image
        """
        # Convert the polygon into the right shape
        polygon = [(x, y) for x, y in polygon.T.tolist()]
        # Place the pattern somewhere
        pattern = self._generate_pattern(label, color)
        tmask = Image.new('1', (self.w, self.h), 0)
        t_draw = ImageDraw.Draw(tmask)
        t_draw.polygon(polygon, fill=1)
        trash = Image.new('RGBA', (self.w, self.h), '#00000000')
        trash.paste(pattern, mask=tmask)

        return trash

    def _render(self, trash_layers, p_bar):
        """Renders the entire bin as one image.

        :param list[list[dict]] trash_layers: All the trash layers, with each
            sublist being a layer and the dictionaries in that list being
            individual objects.
        :param tqdm.tqdm p_bar: A tqdm p_bar so that the sequence generation can
            be updated per image generated. This is optional.
        :return: The rendered sequence as a list of dictionaries where the keys
            are "rendered_img", "new_object_gt", "top_20_gt". Each layer is
            returned as a separate dict.
        :rtype: list[dict]
        """
        rendered_sequence = []
        shifts = np.zeros([len(trash_layers), 2], dtype=int)
        for i in range(len(trash_layers)):
            composed_layer = self.bin_bg.copy().convert('RGBA')
            new_object_gt = Image.new('L', (self.w, self.h), color=0)
            top_20_gt = Image.new('L', (self.w, self.h), color=255)
            for j in range(i):
                # Loop to previous layers and shift and add them to the current
                # layer
                # Generate a shift for the layer
                shift = np.random.uniform(-0.1, 0.1, [2])
                shift *= np.array([self.w, self.h])
                # Apply a factor to the shift based on distance to current
                # layer
                shift /= max(i - j, 1) * 2  # clip to 1 just in case
                # Save the shift so the shift is remembered over iterations
                shifts[j] += shift.astype(int)

                # Now render that layer here
                layer_shift = tuple(shifts[j].tolist())
                for poly in trash_layers[j]:
                    a = Image.new('RGBA', (self.w, self.h), color='#00000000')
                    a.paste(poly['image'], layer_shift, self.bin_mask)
                    # Add the blur to the layer here
                    a = a.filter(ImageFilter.GaussianBlur(randint(0, 2)))

                    # Crop out the area of the layer that is not inside the bin
                    b = Image.new('RGBA', (self.w, self.h))
                    b.paste(a, mask=self.bin_mask)

                    # Put it on the composed layer
                    composed_layer.paste(b, (0, 0), b)

            for poly in trash_layers[i]:
                # Render the top layer
                a = Image.new('RGBA', (self.w, self.h), color='#00000000')
                a.paste(poly['image'], (0, 0), self.bin_mask)
                a = a.filter(ImageFilter.GaussianBlur(randint(0, 2)))

                # Crop out area not inside the bin
                b = Image.new('RGBA', (self.w, self.h))
                b.paste(a, mask=self.bin_mask)

                # Put it on the composed layer
                composed_layer.paste(b, (0, 0), b)

                new_object_gt.paste(255, mask=a)
                # Add poly to new_object_gt
                if poly['label'] < 20:
                    top_20_gt.paste(poly['label'] + 1, mask=a)

            # Apply overall lighting effect for the current shot
            # First calculate where and how to place lighting effects
            light_angle = randint(0, 360)
            light_strength = uniform(0.3, 1.0)
            light_mask = self.light_gradient.copy()
            light_mask = light_mask.rotate(light_angle)
            centered_box = [(light_mask.width / 2) - (self.w / 2),
                            (light_mask.height / 2) - (self.h / 2),
                            (light_mask.width / 2) + (self.w / 2),
                            (light_mask.height / 2) + (self.h / 2)]
            light_mask = light_mask.crop(centered_box)

            # Then apply it to the image
            # First create the shadow
            shadow = Image.new('RGBA', (self.w, self.h), '#00000000')
            shadow.paste(self.black, mask=light_mask)
            shadow = Image.blend(Image.new('RGBA', (self.w, self.h),
                                           '#00000000'),
                                 shadow, light_strength)

            # Then the highlight
            highlight = Image.new('RGBA', (self.w, self.h), '#00000000')
            highlight.paste(self.white, mask=light_mask)
            highlight = Image.blend(Image.new('RGBA', (self.w, self.h),
                                              '#00000000'),
                                    highlight, light_strength * .67)
            composed_layer.paste(highlight, mask=highlight)
            composed_layer.paste(shadow, mask=shadow)

            rendered_sequence.append({
                'rendered_img': composed_layer.convert('RGB'),
                'new_object_gt': new_object_gt,
                'top_20_gt': top_20_gt
            })
            p_bar.update(1)
        return rendered_sequence

    def generate_sequence(self, n, p_bar=None):
        """Generates the image sequence.

        The top 20 classes are classes [0, 19]

        :param int n: Length of the image sequence to generate.
        :param tqdm.tqdm p_bar: A tqdm p_bar so that the sequence generation can
            be updated per image generated. This is optional.
        :returns: The generated image sequence as a list of PIL Image files and
            their corresponding ground truth masks. The first GT mask is the
            binary new object mask and the second is the segmentation of the
            top 20 classes. The final dictionary is a mapping where the keys are
            the colors used in the top_20_gt image and the values are their
            actual labels.
        :rtype: list[dict]
        """
        self._randomize_bin()  # So the same bin isn't used twice.

        # obj_sequence is a list of lists of dicts. Each sublist represents
        # a layer of trash so we can move them around over time. Each dict
        # contains the rasterized trash image as well as its label.
        obj_sequence = [[] for _ in range(n)]

        # This just generates the trash inside the bin.
        for i in range(n):
            # Randomly choose how many instances and their classes will appear
            # in the image and generate the trash for it.
            instances = [randint(0, 39) for _ in range(randint(1, 5))]
            for label in instances:
                # For each thing we have to make, generate a list of the trash
                # objects it should be made up of.
                polygons, color = self.trash_generator.generate_trash(label)
                polygons = self._place_trash(polygons)
                for polygon in polygons:
                    obj_sequence[i].append(
                        {'image': self._rasterize_trash(polygon, label, color),
                         'label': label}
                    )

        return self._render(obj_sequence, p_bar)


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    def showim(img):
        plt.imshow(img)
        plt.axis('off')
        plt.show()
    b = BinSequence('E:\\Offline Docs\\Git\\trash-generator\\src\\classes.csv',
                    'E:\\Offline Docs\\Git\\trash-generator\\src\\colors.csv',
                    300, 400)
    for i, img in enumerate(b.generate_sequence(10)):
        plt.imshow(img['rendered_img'])
        plt.axis('off')
        plt.show()
        input('Next?')
