## Fourier Transforms and Filters

Given a file containing AFM data, this program will:

1. Parse and perform a fourier transform on an inputted file
2. Expose a GUI which allows the user to "zero out" any points on the transformed data
3. Perform an inverse fourier transform on the transform
4. Output the results to a `.csv` file

## Setup

Before the transform program can be run:

```bash
pip3 install scipy matplotlib numpy
```

to install scipy, matplotlib, and numpy.

### To run the program, first we need to be in the correct directory. This can be done by using the `fourier` alias:

```bash
fourier
```

Now that's we're in the correct directory, we can run the program like so:

```bash
python transform.py [path_to_file]
```

Where `[path_to_file]` is the path to the file containing the AFM data, ie:

```bash
python transform.py Scan.124.txt
```

One the program starts, double click on any points in the FFT graph to remove them. When you're satisfied with what you see, close the graphs and the resulting inverse fourier transfrom will be written to a file. The file path will have all the points that were removed encoded into it's name.

If you want to write the current results of the program to a CSV file before closing the graphs, you can click the "export" button and the current state of everything will be writen.
