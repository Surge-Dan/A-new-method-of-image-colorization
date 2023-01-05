# -*- coding: utf-8 -*-
import numpy as np
import cv2 as cv
import colorsys
import matplotlib.pyplot as plt
import scipy.sparse as sparse
from scipy.sparse.linalg import spsolve


padding = 2  # window size

'''
    BGR -> RGB -> YUV
'''
src = cv.imread('glass.bmp')  # cv reads BGR format
src = src[:, :, ::-1]  # the first and third channels are interchanged for BGR to RGB conversion (reverse channel order)
_src = src.astype(float) / 255  # convert the image data from 8-bit integers to floating-point numbers
marked = cv.imread('glass_marked.bmp')
marked = marked[:, :, ::-1]
_marked = marked.astype(float) / 255
Y, _, _ = colorsys.rgb_to_yiq(_src[:, :, 0], _src[:, :, 1], _src[:, :, 2])  # Y channel for the original grayscale image
_, U, V = colorsys.rgb_to_yiq(_marked[:, :, 0], _marked[:, :, 1], _marked[:, :, 2])  # U&V channel for the marked image
yuv = colorsys.rgb_to_yiq(_marked[:, :, 0], _marked[:, :, 1], _marked[:, :, 2])
yuv = np.stack(yuv, axis=2)
y = yuv[:, :, 0]


'''
    Set the matrix used for graph cutting optimization
'''
rows = _src.shape[0]
cols = _src.shape[1]
size = rows * cols  # the total number of pixels in the image
hhash = abs(_src - _marked).sum(2) > 0.01  # U&V of the grayscale image are 0. >0 if it's colored
W = sparse.lil_matrix((size, size))

YY = np.zeros((Y.shape[0]+2*padding, Y.shape[1]+2*padding))
for i in range(YY.shape[0]):
    for j in range(YY.shape[1]):
        YY[i, j] = -10  # avoid crossing the line
for i in range(Y.shape[0]):
    for j in range(Y.shape[1]):
        YY[i+padding, j+padding] = Y[i, j]


def best(center):

    r = center[0] + 1 * padding
    c = center[1] + 1 * padding
    y = center[2]
    r_min = r - padding
    r_max = r + padding + 1
    c_min = c - padding
    c_max = c + padding + 1

    LL = YY[r_min:r_max, c_min:c + 1].mean()
    RR = YY[r_min:r_max, c:c_max].mean()
    UP = YY[r_min:r + 1, c_min:c_max].mean()
    DOWN = YY[r:r_max, c_min:c_max].mean()

    if (center[0] < padding or center[0] > Y.shape[0] - padding - 1) and (
            center[1] < padding or center[1] > Y.shape[1] - padding - 1):
        NW = YY[r_min:r + 1, c_min:c + 1].mean()
        NE = YY[r_min:r + 1, c:c_max].mean()
        SW = YY[r:r_max, c_min:c + 1].mean()
        SE = YY[r:r_max, c:c_max].mean()
    else:
        SE = 100.0
        SW = 100.0
        NE = 100.0
        NW = 100.0
    res = abs(np.array([NE, NW, UP, LL, RR, SW, SE, DOWN]) - y)
    rr_min = r_min
    rr_max = r_max
    cc_min = c_min
    cc_max = c_max
    MIN = res.argmin()
    for i in range(8):
        if i == MIN:
            if i == 0:
                rr_min = r_min
                rr_max = r + 1
                cc_min = c
                cc_max = c_max
                break
            elif i == 1:
                rr_min = r_min
                rr_max = r + 1
                cc_min = c_min
                cc_max = c+1
                break
            elif i == 2:
                rr_min = r_min
                rr_max = r + 1
                cc_min = c_min
                cc_max = c_max
                break
            elif i == 3:
                rr_min = r_min
                rr_max = r_max
                cc_min = c_min
                cc_max = c+1
                break
            elif i == 4:
                rr_min = r_min
                rr_max = r_max
                cc_min = c
                cc_max = c_max
                break
            elif i == 5:
                rr_min = r
                rr_max = r_max
                cc_min = c_min
                cc_max = c+1
                break
            elif i == 6:
                rr_min = r
                rr_max = r_max
                cc_min = c
                cc_max = c_max
                break
            else:
                rr_min = r
                rr_max = r_max
                cc_min = c_min
                cc_max = c_max
                break
        else:
            continue
    rr_min -= 1*padding
    rr_max -= 1*padding
    cc_min -= 1*padding
    cc_max -= 1*padding
    return (rr_min, rr_max, cc_min, cc_max)


def find_neighbors(center):
    neighbors = []
    # find the neighbor traversal range of the pixel, taking into account the pixel at the boundary
    # select the optimal window
    r_min, r_max, c_min, c_max = best(center)
    # traverse all neighbor pixels
    for r in range(r_min, r_max):
        for c in range(c_min, c_max):
            # ignore itself
            if r == center[0] and c == center[1]:
                continue
            # store the xy position of neighbor pixels and the intensity of neighbor pixels
            neighbors.append([r, c, Y[r, c]])
    return neighbors


def affinity_a(neighbors, center):
    # store weights while retaining information about neighbor pixels
    nbs = np.array(neighbors)
    r = center[0]  # row index
    c = center[1]  # column index
    sY = nbs[:, 2]  # intensity of neighbor pixels
    cY = center[2]  # intensity of central pixels

    diff = sY - cY
    sig = np.var(np.append(sY, cY))
    if sig < 1e-6:
        sig = 1e-6

    wrs1 = np.exp(- np.power(diff, 2) / (sig))
    rd = nbs[:, 0] - r
    cd = nbs[:, 1] - c
    wrs = np.power((np.power(rd, 2)+np.power(cd, 2)), -3) * wrs1
    wrs = - wrs / np.sum(wrs)
    nbs[:, 2] = wrs
    return nbs


# create index
def to_seq(r, c, cols):
    return r*cols + c


for r in range(rows):
    for c in range(cols):
        if r == 5 and c == 5:
            print("666")
        # store the position of the pixel and its intensity and calculate the index
        center = [r, c, Y[r, c]]  # yuv[(r, c)][0]
        c_idx = int(to_seq(r, c, cols))
        # if the pixel has not been colored
        if not hhash[r, c]:
            # find the neighbor pixel of the pixel
            neighbors = find_neighbors(center)
            # calculate the weight
            weights = affinity_a(neighbors, center)

            for e in weights:
                # calculate the indexes of the central pixel and the neighbor pixel
                n_idx = int(to_seq(e[0], e[1], cols))
                # put into matrix
                W[c_idx, n_idx] = e[2]
        # 3. if the pixel is colored, it contributes its own value with a weight of 1.0
        W[c_idx, c_idx] = 1.0
matA = W.tocsr()

b_u = np.zeros(size)
b_v = np.zeros(size)
idx_colored = np.nonzero(hhash.reshape(size))
u = yuv[:, :, 1].reshape(size)
b_u[idx_colored] = u[idx_colored]
v = yuv[:, :, 2].reshape(size)
b_v[idx_colored] = v[idx_colored]

ansU = spsolve(matA, b_u).reshape(marked.shape[0],marked.shape[1])
ansV = spsolve(matA, b_v).reshape(marked.shape[0],marked.shape[1])

# YUV -> RGB
r = Y + 0.9468822170900693*ansU + 0.6235565819861433*ansV
r = np.clip(r, 0.0, 1.0)
g = Y - 0.27478764629897834*ansU - 0.6356910791873801*ansV
g = np.clip(g, 0.0, 1.0)
b = Y - 1.1085450346420322*ansU + 1.7090069284064666*ansV
b = np.clip(b, 0.0, 1.0)
Ans = np.stack((r, g, b), axis=2)

plt.imshow(Ans)
plt.title("Colorized_With_SWF")
plt.show()
plt.imsave('result.bmp', Ans)