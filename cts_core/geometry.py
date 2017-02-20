import numpy as np


def createPixel(x, y, d=23.6, rotation=0., shift=None):
    """
    Create lists of x and y positions of the vertices of a pixel around a given center
    """
    r = d / np.sqrt(3.)
    if rotation == 240.:
        x = [x - d / 2, x - d / 2, x, x + d / 2, x + d / 2, x, x - d / 2]
        y = [
            y + r / 2,
            y - r / 2,
            y - r,
            y - r / 2,
            y + r / 2,
            y + r,
            y + r / 2]
    elif rotation == 120.:
        x = [x + d / 2, x, x - d / 2, x - d / 2, x, x + d / 2, x + d / 2]
        y = [
            y + r / 2,
            y + r,
            y + r / 2,
            y - r / 2,
            y - r,
            y - r / 2,
            y + r / 2]
    else:
        x = [x, x + d / 2, x + d / 2, x, x - d / 2, x - d / 2, x]
        y = [y - r, y - r / 2, y + r / 2, y + r, y + r / 2, y - r / 2, y - r]
    if shift:
        x = [i + shift[0] * d for i in x]
        y = [i + shift[1] * d for i in y]
    return np.array(x), np.array(y)


def createPatch(pix):
    """
    Create list of of x and y positions of the vertices of a
    patch out of its pixel vertices

    """
    x = np.array([pix[0][0][0],
                  pix[0][0][1],
                  pix[0][0][2],
                  pix[2][0][1],
                  pix[2][0][2],
                  pix[2][0][3],
                  pix[2][0][4],
                  pix[1][0][3],
                  pix[1][0][4],
                  pix[1][0][5],
                  pix[0][0][4],
                  pix[0][0][5],
                  pix[0][0][0]])
    y = np.array([pix[0][1][0],
                  pix[0][1][1],
                  pix[0][1][2],
                  pix[2][1][1],
                  pix[2][1][2],
                  pix[2][1][3],
                  pix[2][1][4],
                  pix[1][1][3],
                  pix[1][1][4],
                  pix[1][1][5],
                  pix[0][1][4],
                  pix[0][1][5],
                  pix[0][1][0]])
    return x, y


def createModule(pix):
    """
    Create list of of x and y positions of the vertices
    of a module out of its pixel vertices

    """
    x = np.array([pix[8][0][3],
                  pix[8][0][4],
                  pix[9][0][3],
                  pix[10][0][2],
                  pix[10][0][3],
                  pix[10][0][4],
                  pix[11][0][3],
                  pix[11][0][4],
                  pix[11][0][5],
                  pix[7][0][4],
                  pix[7][0][5],
                  pix[3][0][4],
                  pix[3][0][5],
                  pix[2][0][4],
                  pix[2][0][5],
                  pix[2][0][0],
                  pix[1][0][5],
                  pix[0][0][4],
                  pix[0][0][5],
                  pix[0][0][0],
                  pix[0][0][1],
                  pix[0][0][2],
                  pix[4][0][1],
                  pix[4][0][2],
                  pix[4][0][3],
                  pix[5][0][2],
                  pix[8][0][1],
                  pix[8][0][2],
                  pix[8][0][3]])
    y = np.array([pix[8][1][3],
                  pix[8][1][4],
                  pix[9][1][3],
                  pix[10][1][2],
                  pix[10][1][3],
                  pix[10][1][4],
                  pix[11][1][3],
                  pix[11][1][4],
                  pix[11][1][5],
                  pix[7][1][4],
                  pix[7][1][5],
                  pix[3][1][4],
                  pix[3][1][5],
                  pix[2][1][4],
                  pix[2][1][5],
                  pix[2][1][0],
                  pix[1][1][5],
                  pix[0][1][4],
                  pix[0][1][5],
                  pix[0][1][0],
                  pix[0][1][1],
                  pix[0][1][2],
                  pix[4][1][1],
                  pix[4][1][2],
                  pix[4][1][3],
                  pix[5][1][2],
                  pix[8][1][1],
                  pix[8][1][2],
                  pix[8][1][3]])
    return x, y


def createPatches(pixels, pixelsList):
    """
    Create a list of patches out of a list of vertices

    """
    patches = []
    for pixes in pixelsList:
        patches.append(createPatch([pixels[p] for p in pixes]))
    return patches
