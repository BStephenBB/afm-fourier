from scipy.fft import fft2
from typing import Any
from re import sub, MULTILINE


def parse_text_blob(blob):
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

import sys
import os
from scipy.fft import ifft2
import matplotlib.pyplot as plt
import numpy as np

user_input = input("Enter path to fiducial file: ")
 
assert os.path.exists(user_input), "File count not be found at: "+str(user_input)
file = open(user_input,'r+')

text = file.read()
matrix = parse_text_blob(text)

file.close()

figure, (axis1, axis2, axis3, axis4,) = plt.subplots(4, 1)

axis1.set_title('Original Data')
axis1.imshow(matrix)

transform = fft2(matrix)
axis2.set_title('Fourier Transform')
axis2.imshow(np.real(transform))

transform_without_peaks = transform

# defaultMaxValue = 1e3;

userMaxValue = input("Max value threshold: ")

assert float(userMaxValue)

maxValue = float(userMaxValue)

for row in range(len(transform_without_peaks)):
    for col in range(len(transform_without_peaks[row])):
        if abs(np.real(transform_without_peaks[row][col])) > maxValue:
            transform_without_peaks[row][col] = 0

axis3.set_title('Remove "Dots"')
axis3.imshow(np.real(transform_without_peaks))

reverse = ifft2(transform_without_peaks)
axis4.set_title('Invert Transform')

axis4.imshow(np.real(reverse))
# axis.imshow(np.real(transform), cmap=cm.gray)

plt.show()

import csv  

with open('no-peaks.csv', 'w', encoding='UTF8') as f:
    writer = csv.writer(f)

    # write the data
    for row in np.real(reverse):
        writer.writerow(row)


# N = 30
# f, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3, sharex='col', sharey='row')
# xf = np.zeros((N,N))
# xf[0, 5] = 1
# xf[0, N-5] = 1
# Z = ifftn(xf)
# ax1.imshow(xf, cmap=cm.Reds)
# ax4.imshow(np.real(Z), cmap=cm.gray)
# xf = np.zeros((N, N))
# xf[5, 0] = 1
# xf[N-5, 0] = 1
# Z = ifftn(xf)
# ax2.imshow(xf, cmap=cm.Reds)
# ax5.imshow(np.real(Z), cmap=cm.gray)
# xf = np.zeros((N, N))
# xf[5, 10] = 1
# xf[N-5, N-10] = 1
# Z = ifftn(xf)
# ax3.imshow(xf, cmap=cm.Reds)
# ax6.imshow(np.real(Z), cmap=cm.gray)
# plt.show()
