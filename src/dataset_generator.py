"""Dataset Generator.

Generates the dataset. This uses bin_sequence.py to generate multiple image
sequences of a bin being filled. It then generates images that can be saved
along with annotations in the format specified in README.md

Author:
    Yvan Satyawan <y_satyawan@hotmail.com>

Created on:
    March 30, 2020
"""
import json
from argparse import ArgumentParser
from os import mkdir
from os.path import join, exists
from random import randint
from csv import DictReader
from tqdm import tqdm

from trash_generator import BinSequence


def parse_args():
    parser = ArgumentParser('generates trash dataset')
    parser.add_argument('DIR', type=str,
                        help='where to output the dataset')
    parser.add_argument('CSV', type=str,
                        help='path to the classes csv file')
    parser.add_argument('N', type=int,
                        help='number of image sequences to generate')
    parser.add_argument('LENGTH', type=int, nargs='?',
                        help='length of each image sequence')
    parser.add_argument('--height', type=int, nargs='?',
                        help='specifies the height of the generated image. '
                             'Defaults to 800')
    parser.add_argument('--width', type=int, nargs='?',
                        help='specifies the width of the generated image. '
                             'Defaults to 1024')

    return parser.parse_args()


def make_dir_structure(dir_path):
    """Creates the directory structure as described in the readme.

    :param str dir_path: Where the directory structure should be generated.
    :returns: the root path, the images path, the new_object_masks path, and the
        top_20_masks path.
    :rtype: list[str, str, str, str]
    """
    root_path = join(dir_path, 'trash_dataset')
    paths = [dir_path,
             root_path,
             join(root_path, 'images'),
             join(root_path, 'new_object_masks'),
             join(root_path, 'top_20_masks')]

    for p in paths:
        if not exists(p):
            mkdir(p)

    return paths[1:]


def generate_dataset(output_dir, num_sequences, length_per_seq, csv_fp, h, w):
    """Generates the dataset itself using the schema described in the readme.

    This generates the dataset immediately in the output_dir.

    :param str output_dir: Directory where the dataset will be generated in.
        The dataset itself will be generated in a subfolder named
        "trash_dataset" within output_dir.
    :param int num_sequences: Number of sequences to generate.
    :param int or None length_per_seq: Length of each sequence in the
        dataset. If None is given, then a random value between 5 and 50 will be
        chosen.
    :param str csv_fp: Path to the classes CSV file.
    :param int h: Height of the generated images. Defaults to 800.
    :param int w: Width of the generated images. Defaults to 1024.
    """
    h = 800 if h is None else h
    w = 1024 if w is None else w
    # First make dir structure
    root_path, img_path, new_path, t20_path = make_dir_structure(output_dir)
    if length_per_seq is None:
        length_per_seq = [randint(5, 50) for _ in range(num_sequences)]
    else:
        length_per_seq = [length_per_seq] * num_sequences

    # Load classes csv file and read categories
    cat_counter = 1
    cats = dict()
    with open(csv_fp) as csv_file:
        reader = DictReader(csv_file)
        for line in reader:
            cats[str(cat_counter)] = {
                'super_category': line['super_category'],
                'category': line['category'],
                'avoidable': line['avoidable']
            }
            cat_counter += 1

    # Initialize an empty dictionary for image annotations
    imgs = dict()
    total = sum(length_per_seq)
    p_bar = tqdm(total=total, unit='img')

    for i in range(num_sequences):
        b = BinSequence(csv_fp, h, w)

        sequence = b.generate_sequence(length_per_seq[i], p_bar)

        for j, out in enumerate(sequence):
            img_name = f'{i:04}-{j:04}'

            # Save the files
            out['rendered_img'].save(join(img_path, img_name + '.jpg'))
            out['new_object_gt'].save(join(new_path, img_name + '.png'))
            out['top_20_gt'].save(join(t20_path, img_name + '.png'))

            # Add the annotation to the annotations dict
            prev_img = None if j == 0 else f'{i:04}-{j - 1:04}.jpg'
            next_img = None if j == length_per_seq[i] - 1 \
                else f'{i:04}-{j + 1:04}.jpg'

            imgs[img_name + '.jpg'] = {
                'new_obj_mask': join('new_object_masks', img_name + '.png'),
                'top_20_mask': join('top_20_masks', img_name + '.png'),
                'prev_img': prev_img,
                'next_img': next_img,
            }

    anns = {'categories': cats, 'images': imgs}

    with open(join(root_path, 'annotations.json'), mode='w') as fp:
        json.dump(anns, fp, indent=2)


if __name__ == '__main__':
    args = parse_args()
    generate_dataset(args.DIR, args.N, args.LENGTH, args.CSV, args.height,
                     args.width)
