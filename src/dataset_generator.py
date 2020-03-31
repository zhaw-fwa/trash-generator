"""Dataset Generator.

Generates the dataset. This uses fill_bin.py to generate multiple image
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
from os.path import join
from random import randint
from tqdm import tqdm

from trash_generator.fill_bin import BinSequence


TOP_20_CLASSES = [
    {'super_category': 'fruit', 'category': 'lemon', 'avoidable': False},
    {'super_category': 'menu', 'category': 'pasta', 'avoidable': True},
    {'super_category': 'vegetable', 'category': 'sweet potato',
     'avoidable': True},
    {'super_category': 'menu', 'category': 'fries', 'avoidable': True},
    {'super_category': 'menu', 'category': 'plate waste', 'avoidable': False},
    {'super_category': 'menu', 'category': 'sandwich', 'avoidable': True},
    {'super_category': 'vegetable', 'category': 'salad', 'avoidable': True},
    {'super_category': 'menu', 'category': 'white sauce', 'avoidable': False},
    {'super_category': 'fruit', 'category': 'banana', 'avoidable': True},
    {'super_category': 'starch', 'category': 'bread roll', 'avoidable': True},
    {'super_category': 'starch', 'category': 'bread', 'avoidable': True},
    {'super_category': 'fruit', 'category': 'apple', 'avoidable': True},
    {'super_category': 'fruit', 'category': 'mango', 'avoidable': True},
    {'super_category': 'starch', 'category': 'rice', 'avoidable': True},
    {'super_category': 'vegetable', 'category': 'cuttings', 'avoidable': False},
    {'super_category': 'vegetable', 'category': 'carrots', 'avoidable': False},
    {'super_category': 'menu', 'category': 'fried rice', 'avoidable': True},
    {'super_category': 'menu', 'category': 'fish', 'avoidable': True},
    {'super_category': 'meat', 'category': 'beef', 'avoidable': True},
    {'super_category': 'vegetable', 'category': 'garlic', 'avoidable': False}
]


def parse_args():
    parser = ArgumentParser('generates trash dataset')
    parser.add_argument('DIR', type=str,
                        help='where to output the dataset')
    parser.add_argument('N', type=int,
                        help='number of image sequences to generate')
    parser.add_argument('LENGTH', type=int, nargs='?',
                        help='length of each image sequence')
    parser.add_argument('-v', action='store_true',
                        help='make the top_20_masks more visible by making the '
                             'background white')

    return parser.parse_args()


def make_dir_structure(dir_path):
    """Creates the directory structure as described in the readme.

    :param str dir_path: Where the directory structure should be generated.
    :returns: the root path, the images path, the new_object_masks path, and the
        top_20_masks path.
    :rtype: tuple[str, str, str, str]
    """
    root_path = join(dir_path, 'trash_dataset')
    img_path = join(root_path, 'images')
    new_path = join(root_path, 'new_object_masks')
    t20_path = join(root_path, 'top_20_masks')

    mkdir(root_path)
    mkdir(img_path)
    mkdir(new_path)
    mkdir(t20_path)

    return root_path, img_path, new_path, t20_path


def generate_dataset(output_dir, num_sequences, length_per_seq, top_20_white):
    """Generates the dataset itself using the schema described in the readme.

    This generates the dataset immediately in the output_dir.

    :param str output_dir: Directory where the dataset will be generated in.
        The dataset itself will be generated in a subfolder named
        "trash_dataset" within output_dir.
    :param int num_sequences: Number of sequences to generate.
    :param int or None length_per_seq: Length of each sequence in the
        dataset. If None is given, then a random value between 5 and 50 will be
        chosen.
    :param bool top_20_white: Whether or not to make the background of the
        top 20 masks white for visibility.
    """
    anns = {"images": dict()}
    root_path, img_path, new_path, t20_path = make_dir_structure(output_dir)
    if length_per_seq is None:
        length_per_seq = [randint(5, 50) for _ in range(num_sequences)]
    else:
        length_per_seq = [length_per_seq] * num_sequences

    total = sum(length_per_seq)
    p_bar = tqdm(total=total, unit='img')

    for i in range(num_sequences):
        b = BinSequence()

        sequence = b.generate_sequence(length_per_seq[i],
                                       top_20_white=top_20_white)

        for j, (img, new_mask, t20_mask, labels) in enumerate(sequence):
            img_name = f'{i:04}-{j:04}'

            # Save the files
            img.save(join(img_path, img_name + '.jpg'))
            new_mask.save(join(new_path, img_name + '.png'))
            t20_mask.save(join(t20_path, img_name + '.png'))

            # Add the annotation to the annotations dict
            prev_img = None if j == 0 else f'{i:04}-{j - 1:04}'
            next_img = None if j == length_per_seq[i] - 1 \
                else f'{i:04}-{j + 1:04}'

            categories = {k: TOP_20_CLASSES[v] for k, v in labels.items()}

            anns['images'][img_name + '.jpg'] = {
                'new_obj_mask': join('new_object_masks', img_name + '.png'),
                'top_20_mask': join('top_20_masks', img_name + '.png'),
                'prev_img': prev_img,
                'next_img': next_img,
                'categories': categories
            }
            p_bar.update(1)

    with open(join(root_path, 'annotations.json'), mode='w') as fp:
        json.dump(anns, fp, indent=2)


if __name__ == '__main__':
    args = parse_args()
    generate_dataset(args.DIR, args.N, args.LENGTH, args.v)
