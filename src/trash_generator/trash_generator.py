"""Trash Generator.

Generates trash using random or predefined shapes. Loads class values from a
file called "classes.csv".

Author:
    Yvan Satyawan <y_satyawan@hotmail.com>

Created On:
    April 1, 2020.
"""
from csv import DictReader
import numpy as np
from trash_generator import Shapes
from random import random, randint, uniform
from math import pi


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
        self.shapes = Shapes()

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
                amplitude = uniform(0.001, 0.03)
                polygon[i] += amplitude * np.sin(steps[i] / wavelength * 2 * pi)

        return polygon

    @staticmethod
    def _apply_slice(polygon):
        """Applies a slice transfomration on a polygon.

        :param np.ndarray polygon: The polygon to be transformed with shape
            [2, n]
        :returns: The transformed polygon with shape [2, n]
        :rtype: np.ndarray
        """

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

        :param np.ndarray polygon: The polygon to be transformed.
        :returns: The transformed polygon.
        :rtype: np.ndarray
        """
        pass

    def generate_trash(self, class_label, h, w):
        """Generate the trash based on a class_label.

        :param int class_label: Class label to generate trash for.
        :param int h: Height of the image to produce
        :param int w: Width of the image to produce
        :returns: A list of np.ndarrays representing polygons of the trash
            object which fit within a 1 x 1 unit area.
        :rtype: list[np.ndarray]
        """
        class_props = self.class_properties[class_label]

        # Only banana needs a scale and rotation deform
        if class_props['shape'] == 'semicircle':
            shape = self.shapes.semi_ellipse()
        elif class_props['shape'] == 'circle':
            shape = self.shapes.ellipse()
        elif class_props['shape'] == 'banana':
            shape = self.shapes.banana()
            shape = self._apply_rotation(shape)
            shape = self._apply_scale(shape)
        else:
            shape = self.shapes.blob()

        if class_props['p_warp_deform'] is not None:
            if random() > class_props['p_warp_deform']:
                shape = self._apply_warp(shape)

        if class_props['p_slice_deform'] is not None:
            if random() > class_props['p_slice_deform']:
                shape = self._apply_slice(shape)

        return shape
