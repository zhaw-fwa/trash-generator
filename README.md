# Trash Generator
Generates randomized toy examples of food waste 🗑.

As a temporary measure so that we can work on development even before any real data has arrived, we have decided to make a trash generation program.
The goal is to randomly generate images of trash cans with food waste in them, along with the required annotations.
The images themselves will be relatively simple, consisting mostly of patterns and lines representing different foodstuff.

This generates an arbitrary number of image sequences, with each image sequence having arbitrary length as defined by the user or chosen randomly.

## Running the generator
The generator can be run from the command line.

```bash
python3 dataset_generator.py DIR CSV N [LENGTH] [--height val] [--width val]
```

- `DIR` is the where the dataset should be output to. If it is not empty, its contents will be overwritten.
- `CSV` is the classes csv file. A default version is included in this repo under `src/classes.csv`.
- `N` is the number of image sequences to generate.
- `LENGTH` is the length of each image sequence. If none is given, then a random length between 0 and 50 will be chosen
  e.g. if `val` is 20, `N` is 6, and `LENGTH` is 8, then the 3rd image sequence will only have 4 images. 
- `--height` is an optional height argument. This specifies the height of the generated image. Defaults to 800. 
- `--width` is an optional width argument. This specifies the width of the generated image. Defaults to 1024.

 
## Annotation Schema
This dataset uses a custom annotation style.

### Directory Structure Example
```
dataset/
├── annotations.json
│
├── images/
│   ├── 2020-09-18-10-34-29.jpg
│   ...
│   └── 2020-12-21-13-32-32.jpg
│
├── new_object_masks/
│   ├── 2020-09-18-10-34-29.png
│   ...
│   └── 2020-12-21-13-32-32.png
│
└── top_20_masks/
    ├── 2020-09-18-10-34-29_.png
    ...
    └── 2020-12-21-13-32-32.png
```

### `annotations.json` Example
```json
{
  "categories": 
  {
    "1": {"super_category": "fruit", "category": "banana", "avoidable": false}
  },
  "images": 
  {
    "2019-09-18-10-34-29.jpg": 
    {
      "new_obj_mask": "new_object_masks/2020-09-18-10-34-29.png",
      "top_20_mask": "top_20_masks/2020-09-18-10-34-29.png",
      "prev_image": null,
      "next_image": "2019-09-18-10-34-43.jpg"
    }
  }
}
```

The category keys here corresponds with the luminosity value in the corresponding 8-bit top_20 segmentation mask. 


## Examples
Here are some examples of the results of this tool for image sequences of length 9

![Example of sequence of 9 images with round bins](media/sample_1.jpg)
![Example of sequence of 9 images with square bins](media/sample_2.jpg)

## Color scheme
A hand-picked color scheme was chosen for the color of the objects inside the bin to make them have colors that are more analogous to items that may be found in trash bins.
For example, the colors are more muted and more similar to each other.
The final chosen color scheme uses the following colors.

![Chosen color scheme](media/colorscheme.png)
