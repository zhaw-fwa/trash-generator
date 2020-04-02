"""Shape Generator.

Generates random organic blob-like shapes. The core idea was found on
stack overflow at the following link: <https://stackoverflow.com/questions/
3587704/good-way-to-procedurally-generate-a-blob-graphic-in-2d>. It was then
heavily modified for efficiency and to avoid rewriting code that already exists
in numpy and scipy.

Authors:
    Yvan Satyawan <y_satyawan@hotmail.com>
    Evgeni Sergeev <https://stackoverflow.com/users/1143274/evgeni-sergeev>
    NinjaFart <https://stackoverflow.com/users/1772200/ninjafart>

Created on:
    March 27, 2020
"""
import numpy as np
from scipy.spatial import ConvexHull
from skimage.draw import ellipse_perimeter
from random import randint, uniform
from math import pi


class Shapes:
    def __init__(self):
        """Contains code to generate shapes."""
        self.banana_polygon = self._interpolate_2dim(
            np.array(
                [[0.790, 0.120], [0.734, 0.273], [0.672, 0.448], [0.393, 0.694],
                 [0.123, 0.743], [0.027, 0.801], [0.020, 0.852], [0.054, 0.893],
                 [0.222, 0.933], [0.433, 0.924], [0.638, 0.835], [0.811, 0.672],
                 [0.896, 0.537], [0.954, 0.374], [0.956, 0.307], [0.925, 0.232],
                 [0.893, 0.187], [0.856, 0.131], [0.818, 0.104]]),
            n=10)

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

    def banana(self):
        """Generates the perimeter of a banana shaped object.

        :returns: perimeter of a banana shaped object in the shape [2, n].
        :rtype: np.ndarray
        """
        return self.banana_polygon

    def blob(self, num_points=10, smoothness=25):
        """Generates the perimeter of a blob shaped object.

        :returns: Perimeter of the blob in the shape [2, n].
        :rtype: np.ndarray
        """
        return self._generate_random_shape(num_points, smoothness)

    def semi_ellipse(self):
        """Generates the perimeter of a sliced ellipse.

        :returns: Perimeter of the semi-ellipse with shape [2, n].
        :rtype: np.ndarray
        """
        return self.ellipse((50, 100))

    def ellipse(self, shape=None):
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
