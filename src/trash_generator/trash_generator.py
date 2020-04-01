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
from trash_generator.shape_generator import Shapes
from random import random, randint


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

        :param np.ndarray polygon: The polygon to be transformed.
        :returns: The transformed polygon.
        :rtype: np.ndarray
        """
        pass

    @staticmethod
    def _apply_slice(polygon):
        """Applies a slice transfomration on a polygon.

        :param np.ndarray polygon: The polygon to be transformed.
        :returns: The transformed polygon.
        :rtype: np.ndarray
        """

    @staticmethod
    def _apply_rotation(polygon):
        """Applies a random rotation to a polygon.

        :param np.ndarray polygon: The polygon to be transformed.
        :returns: The transformed polygon.
        :rtype: np.ndarray
        """
        pass

    @staticmethod
    def _apply_scale(polygon):
        """Applies a random scaling (including stretching) to a polygon.

        :param np.ndarray polygon: The polygon to be transformed.
        :returns: The transformed polygon.
        :rtype: np.ndarray
        """

    def generate_trash(self, class_label):
        """Generate the trash based on a class_label.

        :param int class_label: Class label to generate trash for.
        :returns: A list of np.ndarrays representing polygons of the trash
            object which fit within a 1 x 1 unit area.
        :rtype: list[np.ndarray]
        """
        class_props = self.class_properties[class_label]

        if class_props['shape'] == 'banana':
            shape = self.shapes.get_banana()
        elif class_props['shape'] == 'semicircle':
            shape = self.shapes.get_semicircle()
        elif class_props['shape'] == 'circle':
            shape = self.shapes.get_circle()
        else:
            shape = self.shapes.get_blob()

        if random() > class_props['p_warp_deform']:
            shape = self._apply_warp(shape)
        if random() > class_props['p_slice_deform']:
            shape = self._apply_slice(shape)

        shape = self._apply_scale(shape)
        shape = self._apply_rotation(shape)

        return shape
