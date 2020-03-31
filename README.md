# Trash Generator
Generates randomized toy examples of food waste 🗑.

As a stop-gap measure so that we can work on development even before any real data has arrived, we have decided to make a trash generation program.
The goal is to randomly generate images of trash cans with food waste in them, along with the required annotations.
The images themselves will be very simple, consisting mostly of solid colors and lines as well as simple patterns representing different foodstuff.

This generates an arbitrary number of image sequences, with each image sequence having arbitrary length as defined by the user or chosen randomly.

A simple command line interface is available to run the program.

## Examples
Here are some examples of the results of this tool for image sequences of length 9

![Example of sequence of 9 images with square bins](media/sample.png)
![Example of sequence of 9 images with round bins](media/sample2.png)
## To Dos
- [x] Create background trash cans
- [x] Crate/find food patterns
- [x] Implement random blob generator
- [x] Implement image sequence generator
- [ ] Implement dataset generator
- [ ] Implement command line interface
