from scipy.fft import fft2
from copy import deepcopy
from typing import Any
from re import sub, MULTILINE
import os
from scipy.fft import ifft2
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import numpy as np
import argparse
import csv

# TODOs
# show the imaginary number graph (and allow for those numbers to be blanked out too)
# make the graphs bigger
# higher contrast in graphs, maybe use a log scale for the FFT graph


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
# transform_without_peaks = deepcopy(transform)
# max_value = args.threshold
# for row in range(len(transform_without_peaks)):
#     for col in range(len(transform_without_peaks[row])):
#         if abs(np.real(transform_without_peaks[row][col])) > max_value:
#             transform_without_peaks[row][col] = 0
# reverse = ifft2(transform_without_peaks)

transformed_data = deepcopy(transform)
transformed_back_data = ifft2(transformed_data)
final_data = None

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
    # plot everything
    figure, (axis1, axis2, axis3, axis4) = plt.subplots(4, 1)
    axis1.set_title("Original Data")
    axis1.imshow(matrix)
    axis2.set_title("Fourier Transform - Real")
    axis2.imshow(np.real(transformed_data))
    axis3.set_title("Fourier Transform - Imaginary")
    axis3.imshow(np.imag(transformed_data))
    axis4.set_title("Invert Transform")
    axis4.imshow(np.real(transformed_back_data))

    LEFT_CLICK = 1

    def on_click(event):
        # only toggle point for left clicks, on the correct axis, and for double clicks
        if event.button == LEFT_CLICK and event.inaxes == axis2 and event.dblclick:
            x = round(event.xdata)
            y = round(event.ydata)
            formatted_point = f"[{x},{y}]"

            if points_removed.get(formatted_point):
                value_to_restore = points_removed.pop(formatted_point)
                transformed_data[y][x] = value_to_restore
            else:
                points_removed[formatted_point] = transformed_data[y][x]
                transformed_data[y][x] = 0

            # recaculate transforms and re-draw graphs:
            axis2.imshow(np.real(transformed_data))
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
