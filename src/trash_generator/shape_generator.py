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


class Shapes:
    def __init__(self):
        """Calculates the shape polygons.

        :Example to make a blob and show it using matplotlib:

        >>> import matplotlib.pyplot as plt
        >>> s = Shapes()
        >>> polygon = s.get_blob(10, 25)
        >>> plt.fill(polygon[0], polygon[1])
        >>> plt.show()
        """
        self.banana = self._interpolate_smoothly_2dim(np.array(
            [[0.790, 0.120], [0.734, 0.273], [0.672, 0.448], [0.393, 0.694],
             [0.123, 0.743], [0.027, 0.801], [0.020, 0.852], [0.054, 0.893],
             [0.222, 0.933], [0.433, 0.924], [0.638, 0.835], [0.811, 0.672],
             [0.896, 0.537], [0.954, 0.374], [0.956, 0.307], [0.925, 0.232],
             [0.893, 0.187], [0.856, 0.131], [0.818, 0.104]]
            ),
            10)

        # Base polygon for semicircle
        x = np.arange(0., 1.01, 0.01)
        y = np.sqrt(np.clip((0.25 - ((x - 0.5) ** 2)), 0., None)) + 0.5

        self.semicircle = np.stack((x, y))

        # Base polygon for circle
        x = np.concatenate((x, np.flip(x)))
        y = np.concatenate((y, ((y - 0.5) * -1) + 0.5))
        self.circle = np.stack((x, y))

    def get_banana(self):
        return self.banana

    def get_semicircle(self):
        return self.semicircle

    def get_circle(self):
        return self.circle

    def get_blob(self, num_points=10, smoothness=25):
        return self._generate_random_shape(num_points, smoothness)

    @staticmethod
    def _interpolate_smoothly_1dim(xs, n):
        """For each point, add N points.

        Interpolates n values between each value in xs. This is a one-dimensional
        interpolation so must be run per dimension.

        :param xs: The one-dimensional array of values to interpolate
        :param n: Number of values to interpolate between each value
        :type xs: np.ndarray
        :type n: int

        :returns: The one-dimensional array with n interpolated values between each
            value in xs.
        :rtype: np.ndarray
        """
        fs = np.fft.fft(xs)
        half = (len(xs) + 1) // 2
        fs2 = np.insert(fs, half, [0] * (len(fs) * n))

        return np.fft.fft(fs2).real[::-1] / len(xs)

    def _interpolate_smoothly_2dim(self, values, n):
        """Interpolates points smoothly from a 2-dimensional array.

        :param np.ndarray values: Points to be interpolated. Shape is [n, 2].
        :param int n: Number of points to interpolate between each value.
        :returns: The two-dimensional array with n interpolated values between each
            value in values.
        :rtype: np.ndarray
        """
        return np.stack(
            (self._interpolate_smoothly_1dim(values[:, 0], n),
             self._interpolate_smoothly_1dim(values[:, 1], n))
        )

    def _generate_random_shape(self, num_points, smoothness):
        """Generates random blob shape.

        Generates a random blob shape from a given number of points, and smooths it
        using interpolation. This function works by first randomly generating the
        given number of points. It then calculates the convex hull around those
        points, creating a random polygon shape. Points are then interpolated
        between the vertices of the convex hull to generate a smooth, enclosed blob.
        This function interpolates n points between each of the vertices of the
        convex hull, where n is the smoothness parameter.

        The output is then a blob whose perimeter all fit within a (1, 1) square.

        :param num_points: The number of points to initially use. Value must be
            greater than 3.
        :param smoothness: The number of points to interpolate between each vertex
            of the convex hull. Value cannot be negative.
        :type num_points: int
        :type smoothness: int
        :returns: The coordinates of points that make up the perimeter of the blob
            with the shape [2, n]
        :rtype: np.ndarray
        """
        assert num_points >= 3, 'num_points must be greater than 3.'
        assert smoothness >= 0, 'smoothness_ cannot be negative.'

        points = np.random.rand(num_points, 2)
        hull = ConvexHull(points)
        hull_points = hull.points[hull.vertices]

        return self._interpolate_smoothly_2dim(hull_points, smoothness)


if __name__ == '__main__':
    # Testing code
    import matplotlib.pyplot as plt
    # polygon = generate_random_shape(10, 25)
    # plt.fill(polygon[0], polygon[1])
    x = np.arange(0., 1.01, 0.01)
    y = np.sqrt(np.clip((0.25 - ((x - 0.5) ** 2)), 0., None)) + 0.5
    x = np.concatenate((x, np.flip(x)))
    y = np.concatenate((y, ((y - 0.5) * -1) + 0.5))
    circle = np.stack((x, y))
    plt.plot(circle[0], circle[1])
    plt.fill(circle[0], circle[1])

    # plt.plot(semicircle_arc[0], semicircle_arc[1])
    plt.show()
