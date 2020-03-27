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


def interpolate_smoothly(xs, n):
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


def generate_random_shape(num_points, smoothness):
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

    :Example to make a blob and show it using matplotlib:

    >>> import matplotlib.pyplot as plt
    >>> polygon = generate_random_shape(10, 25)
    >>> plt.fill(polygon[0], polygon[1])
    >>> plt.show()
    """
    assert num_points >= 3, 'num_points must be greater than 3.'
    assert smoothness >= 0, 'smoothness_ cannot be negative.'

    points = np.random.rand(num_points, 2)
    hull = ConvexHull(points)
    hull_points = hull.points[hull.vertices]
    x_vals = hull_points[:, 0]
    y_vals = hull_points[:, 1]
    x_vals = interpolate_smoothly(x_vals, smoothness)
    y_vals = interpolate_smoothly(y_vals, smoothness)

    return np.stack((x_vals, y_vals))


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    polygon = generate_random_shape(10, 25)
    plt.fill(polygon[0], polygon[1])
    plt.show()
