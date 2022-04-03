from scipy.fft import fft2
from copy import deepcopy
from typing import Any
from re import sub, MULTILINE
import os
from scipy.fft import ifft2
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from matplotlib.colors import LogNorm
import numpy as np
import argparse
import csv


def parse_text_blob(blob):
    """
    parse a text file into a 2d array (a matrix)
    """
    lines = blob.split("\n")
    matrix: list[list[Any]] = [
        sub(r" +", " ", line.strip(), flags=MULTILINE).split(" ") for line in lines
    ]

    # remove empty lines
    i = len(matrix) - 1
    while True:
        if i < 0:
            break
        if len(matrix[i]) == 1:
            matrix.pop()
        else:
            break
        i = i - 1

    for row in range(len(matrix)):
        for col in range(len(matrix[row])):
            matrix[row][col] = float(matrix[row][col])

    return matrix


# accept and parse cli input
parser = argparse.ArgumentParser(
    description="Perform a fourier transform and filter on a file"
)
parser.add_argument(
    "file_path",
    metavar="file",
    help="a path to the file to run the fourier transform on",
)
parser.add_argument("-n", "--no-graph", action="store_true")
args = parser.parse_args()
file_path = args.file_path
no_graph = args.no_graph


# parse file
assert os.path.exists(file_path), "File count not be found at: " + str(file_path)
file = open(file_path, "r+")
text = file.read()
matrix = parse_text_blob(text)
file.close()


# perform calculations
transform = fft2(matrix)
transformed_data = deepcopy(transform)
transformed_back_data = ifft2(transformed_data)
final_data = None

# determine min and max values
min_max = {"real": {"min": 0, "max": 0,}, "imaginary": {"min": 0, "max": 0,}}

for row in np.real(transformed_data):
    for value in row:
        if value > min_max["real"]["max"]:
            min_max["real"]["max"] = value
        if value < min_max["real"]["min"]:
            min_max["real"]["min"] = value

# determine min and max values
for row in np.imag(transformed_data):
    for value in row:
        if value > min_max["imaginary"]["max"]:
            min_max["imaginary"]["max"] = value
        if value < min_max["imaginary"]["min"]:
            min_max["imaginary"]["min"] = value


# store "removed" points in an object here for restoring and building output file path
points_removed = {}


class Writer:
    def __init__(self, data):
        self.data = data

    def update_data(self, data):
        self.data = data

    def write(self):
        # write data to output file
        with open(
            f"{'.'.join(file_path.split('.')[:-1])}_sans{'_'.join(points_removed.keys())}.csv",
            "w",
            encoding="UTF8",
        ) as f:
            writer = csv.writer(f)
            # write the data
            for row in np.real(self.data):
                writer.writerow(row)

    def write_handler(self, _event):
        # need to define this method since the on_clicked callback accepts self and event as args (even though we don't use the event)
        self.write()


writer = Writer(transformed_back_data)

# only plot if the no_graph option hasn't been specified
if not no_graph:
    log_norm = LogNorm()
    # plot everything
    figure, (axis1, axis2, axis3, axis4) = plt.subplots(4, 1)
    axis1.set_title("Original Data")
    axis1.imshow(matrix)
    axis2.set_title("Fourier Transform - Real")
    # axis2.imshow(np.real(transformed_data), norm=log_norm, cmap="bwr")
    axis2.imshow(
        np.real(transformed_data),
        vmin=min_max["real"]["min"] * 0.1,
        vmax=min_max["real"]["max"] * 0.1,
    )
    axis3.set_title("Fourier Transform - Imaginary")
    # axis3.imshow(np.imag(transformed_data), norm=log_norm, cmap="bwr")
    axis3.imshow(
        np.imag(transformed_data),
        vmin=min_max["imaginary"]["min"] * 0.1,
        vmax=min_max["imaginary"]["max"] * 0.1,
    )
    axis4.set_title("Invert Transform")
    axis4.imshow(np.real(transformed_back_data))

    LEFT_CLICK = 1

    def on_click(event):
        # only toggle point for left clicks, on the correct axis, and for double clicks
        is_left_double_click = event.button == LEFT_CLICK and event.dblclick
        if event.button == is_left_double_click and (
            event.inaxes == axis2 or event.inaxes == axis3
        ):
            x = round(event.xdata)
            y = round(event.ydata)
            formatted_point = f"[{x},{y}]"

            # For now, clicking on either the imaginary or real axis will remove the point completely.
            # The same is true for restoring the points. In the future we might want to be more sophisticated and eliminate _only_ the real or imaginary part based on the graph clicked on.
            if points_removed.get(formatted_point):
                value_to_restore = points_removed.pop(formatted_point)
                transformed_data[y][x] = value_to_restore
            else:
                points_removed[formatted_point] = transformed_data[y][x]
                transformed_data[y][x] = 0

            # recaculate transforms and re-draw graphs:
            axis2.imshow(
                np.real(transformed_data),
                vmin=min_max["real"]["min"] * 0.1,
                vmax=min_max["real"]["max"] * 0.1,
            )
            axis3.imshow(
                np.imag(transformed_data),
                vmin=min_max["imaginary"]["min"] * 0.1,
                vmax=min_max["imaginary"]["max"] * 0.1,
            )
            transformed_back_data = ifft2(transformed_data)
            writer.update_data(transformed_back_data)
            axis4.imshow(np.real(transformed_back_data))
            plt.gcf().canvas.draw_idle()

    connection_id = figure.canvas.mpl_connect("button_press_event", on_click)

    plt.get_current_fig_manager().full_screen_toggle()  # toggle fullscreen mode

    button_axis = plt.axes([0.89, 0.05, 0.1, 0.07])
    export_button = Button(button_axis, "Export")
    export_button.on_clicked(writer.write_handler)

    plt.show()
    figure.canvas.mpl_disconnect(connection_id)


writer.write()
