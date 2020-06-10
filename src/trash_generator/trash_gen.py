"""Trash Generator.

Generates trash using random or predefined shapes. Loads class values from a
file called "classes.csv". The core idea for blog generation was found on
stack overflow at the following link: <https://stackoverflow.com/questions/
3587704/good-way-to-procedurally-generate-a-blob-graphic-in-2d>. It was then
heavily modified for efficiency and to avoid rewriting code that already exists
in numpy and scipy.

Author:
    Yvan Satyawan <y_satyawan@hotmail.com>

References:
    Evgeni Sergeev <https://stackoverflow.com/users/1143274/evgeni-sergeev>
    NinjaFart <https://stackoverflow.com/users/1772200/ninjafart>

Created On:
    April 1, 2020.
"""
from csv import DictReader
import numpy as np
from random import random, randint, uniform
from math import pi
from scipy.spatial import ConvexHull
from skimage.draw import ellipse_perimeter


class TrashGenerator:
    def __init__(self, csv_fp):
        """Initialize the trash generator.

        This csv file should contain the following headers:
            - super_category: str
            - category: str
            - avoidable: bool
            - shape: [semicircle, ellipse, banana, None]
            - p_warp_deform: Optional[float]
            - p_slice_deform: Optional[float]
            - max_items: Optional[int]

        :param str csv_fp: Path to the CSV file containing the classes.
        """
        self.class_properties = self._import_csv_file(csv_fp)

        # Shape definitions are stored in shapes
        self.banana_polygon = self._interpolate_2dim(
            np.array(
                [[0.790, 0.120], [0.734, 0.273], [0.672, 0.448], [0.393, 0.694],
                 [0.123, 0.743], [0.027, 0.801], [0.020, 0.852], [0.054, 0.893],
                 [0.222, 0.933], [0.433, 0.924], [0.638, 0.835], [0.811, 0.672],
                 [0.896, 0.537], [0.954, 0.374], [0.956, 0.307], [0.925, 0.232],
                 [0.893, 0.187], [0.856, 0.131], [0.818, 0.104]]),
            n=10)

    @staticmethod
    def _import_csv_file(csv_fp):
        """Imports the CSV file with the required additional post processing"""
        classes = []
        with open(csv_fp, 'r') as file:
            reader = DictReader(file)
            for line in reader:
                d_line = dict()
                for k, v in line.items():
                    if v == "":
                        v = None
                    elif v == "FALSE":
                        v = False
                    elif v == "TRUE":
                        v = True
                    d_line[k] = v
                classes.append(d_line)
        return classes

    @staticmethod
    def _apply_warp(polygon):
        """Applies warp transformation on a polygon.

        The warp transformation is based on using a wave distortion filter.
        A wave distortion filter works by applying a series of sine wave
        generators to an image in pairs; one for the x-axis and one for the
        y-axis. This distortion is then applied using a simple addition to the
        coordinates of the polygon. A random number (between 1 and 11) of
        generators are applied to the image, with a wavelength between 0.3 and
        0.6 and an amplitude between 0.001 and 0.03. This is to keep the same
        basic shape to the image without too much distortion.

        :param np.ndarray polygon: The polygon to be transformed with shape
            [2, n]
        :returns: The transformed polygon with shape [2, n].
        :rtype: np.ndarray
        """
        # First choose number of generators
        num_generators = randint(1, 11)
        steps = np.flip(polygon, 0)
        for _ in range(num_generators):
            for i in range(2):  # X and Y axis have same operations
                wavelength = uniform(0.3, 0.6)
                amplitude = uniform(0.001, 0.02)
                polygon[i] += amplitude * np.sin(steps[i] / wavelength * 2 * pi)

        return polygon

    @staticmethod
    def _apply_slice(polygon):
        """Applies a slice transfomration on a polygon.

        Slices by drawing a random vertical line and taking the left half.

        :param np.ndarray polygon: The polygon to be transformed with shape
            [2, n]
        :returns: The transformed polygon with shape [2, n]
        :rtype: np.ndarray
        """
        line_xs = np.random.uniform(0.3, 0.7, [2])
        line_ys = np.array([0., 1.])
        a = line_xs[1] - line_xs[0]
        b = polygon[1] - line_ys[0]
        c = polygon[0] - line_xs[0]
        d = line_ys[1] - line_ys[0]

        left_of_line = a * b - c * d > 0

        return polygon.T[left_of_line].T

    @staticmethod
    def _apply_rotation(polygon):
        """Applies a random rotation to a polygon.

        :param np.ndarray polygon: The polygon to be transformed with shape
            [2, n]
        :returns: The transformed polygon with shape [2, n]
        :rtype: np.ndarray
        """
        angle = random() * pi * 2
        center = np.array([0.5, 0.5])
        polygon = polygon.T
        rot_matrix = np.array([[np.cos(angle), np.sin(angle)],
                              [-np.sin(angle), np.cos(angle)]])
        return (np.dot(polygon - center, rot_matrix) + center).T

    @staticmethod
    def _apply_scale(polygon):
        """Applies a random scaling (including stretching) to a polygon.

        Note that flipping is also possible.

        :param np.ndarray polygon: The polygon to be transformed with shape
            [2, n]
        :returns: The transformed polygon with shape [2, n]
        :rtype: np.ndarray
        """
        scale = np.random.uniform(0.1, 1., [2])
        scale *= np.random.choice([-1, 1], [2])
        return (polygon.T * scale).T

    @staticmethod
    def _interpolate_1dim(xs, n):
        """For each point, add N points.

            Interpolates n values between each value in xs. This is a
            one-dimensional
            interpolation so must be run per dimension.

            :param xs: The one-dimensional array of values to interpolate
            shape [m]
            :param n: Number of values to interpolate between each value
            :type xs: np.ndarray
            :type n: int

            :returns: The one-dimensional array with n interpolated values
            between
                each value in xs.
            :rtype: np.ndarray
            """
        fs = np.fft.fft(xs)
        half = (len(xs) + 1) // 2
        fs2 = np.insert(fs, half, [0] * (len(fs) * n))

        return np.fft.fft(fs2).real[::-1] / len(xs)

    def _interpolate_2dim(self, values, n):
        """Interpolates points smoothly from a 2-dimensional array.

        :param np.ndarray values: Points to be interpolated. Shape is [n, 2].
        :param int n: Number of points to interpolate between each value.
        :returns: The two-dimensional array with n interpolated values between
            each value in values with shape [2, n]
        :rtype: np.ndarray
        """
        return np.stack(
            (self._interpolate_1dim(values[:, 0], n),
             self._interpolate_1dim(values[:, 1], n))
        )

    @staticmethod
    def _get_convex_hull(points):
        """Gets the points that make up the convex hull.

        :param np.ndarray points: Points to get the convex hull of. Must be in
            the shape [n, 2]
        :returns: Points in the convex hull in the shape [n, 2].
        :rtype: np.ndarray
        """
        hull = ConvexHull(points)
        return hull.points[hull.vertices]

    def _generate_random_shape(self, num_points, smoothness):
        """Generates random blob shape.

        Generates a random blob shape from a given number of points, and smooths
        it using interpolation. This function works by first randomly generating
        the given number of points. It then calculates the convex hull around
        those points, creating a random polygon shape. Points are then
        interpolated between the vertices of the convex hull to generate a
        smooth, enclosed blob. This function interpolates n points between each
        of the vertices of the convex hull, where n is the smoothness parameter.

        The output is then a blob whose perimeter all fit within a (1, 1)
        square.

        :param int num_points: The number of points to initially use. Value
            must be greater than 3.
        :param int smoothness: The number of points to interpolate between each
            vertex of the convex hull. Value cannot be negative.
        :returns: The coordinates of points that make up the perimeter of the
            blob with the shape [2, n]
        :rtype: np.ndarray
        """
        assert num_points >= 3, 'num_points must be greater than 3.'
        assert smoothness >= 0, 'smoothness_ cannot be negative.'

        points = np.random.rand(num_points, 2)

        return self._interpolate_2dim(self._get_convex_hull(points),
                                      smoothness)

    def _banana(self):
        """Generates the perimeter of a banana shaped object.

        :returns: perimeter of a banana shaped object in the shape [2, n].
        :rtype: np.ndarray
        """
        return self.banana_polygon

    def _blob(self, num_points=10, smoothness=25):
        """Generates the perimeter of a blob shaped object.

        :returns: Perimeter of the blob in the shape [2, n].
        :rtype: np.ndarray
        """
        return self._generate_random_shape(num_points, smoothness)

    def _semi_ellipse(self):
        """Generates the perimeter of a sliced ellipse.

        :returns: Perimeter of the semi-ellipse with shape [2, n].
        :rtype: np.ndarray
        """
        return self._ellipse((50, 100))

    def _ellipse(self, shape=None):
        """Generates the perimeter of a random ellipse.

        :param tuple[int, int] shape: shape to restrict ellipse to as a tuple
            representing (max rows, max columns).
        :returns: Perimeter of the ellipse with shape [2, n].
        :rtype: np.ndarray
        """
        minor_axis = randint(15, 50)
        major_axis = randint(15, 50)
        orientation = uniform(0, pi)
        points = ellipse_perimeter(50, 50, minor_axis, major_axis,
                                   orientation, shape)
        points = np.array(points, dtype=float) / 100.

        # Make points into shape [n, 2] and get the convex hull, then transpose
        # back to [2, n]
        perimeter = self._get_convex_hull(points.T).T
        return perimeter

    def generate_trash(self, class_label: int):
        """Generate the trash based on a class_label.

        :param class_label: Class label to generate trash for.
        :returns: A tuple. The first element is a list of np.ndarrays
            representing polygons of the trash object which fit within a
            1 x 1 unit area. Each polygon has shape [2, n].
            The second element is a single int value which represents the index
            of the color that should be used.
        :rtype: tuple[list[np.ndarray], int]
        """
        class_props = self.class_properties[class_label]
        shapes = []

        # Generate a random number number of items up to and including max_items
        if class_props['max_items'] is None:
            num_items = 1
        else:
            num_items = randint(1, int(class_props['max_items']))

        for _ in range(num_items):
            # Only banana needs a scale and rotation deform
            if class_props['shape'] == 'semicircle':
                shape = self._semi_ellipse()
            elif class_props['shape'] == 'circle':
                shape = self._ellipse()
            elif class_props['shape'] == 'banana':
                shape = self._banana()
                shape = self._apply_rotation(shape)
                shape = self._apply_scale(shape)
            else:
                shape = self._blob()

            if class_props['p_warp_deform'] is not None:
                if random() > float(class_props['p_warp_deform']):
                    shape = self._apply_warp(shape)

            if class_props['p_slice_deform'] is not None:
                if random() > float(class_props['p_slice_deform']):
                    shape = self._apply_slice(shape)
                    # Rotates again after slicing so it's not always a vertical
                    # slice and not always the left side that's kept
                    shape = self._apply_rotation(shape)
                    shape = self._apply_scale(shape)

            shapes.append(shape)
        if class_props['color'] is not None:
            color = class_props['color']
        else:
            color = randint(0, 39)

        return shapes, color
