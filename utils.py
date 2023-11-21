import numpy as np
import Line


def radianToDegree(radian):
    return radian * 180 / np.pi


def degreeToRadian(degree):
    return degree * np.pi / 180


# transforms a np array into a vector
def vectorFromArray(array):
    return Line.Vector(array[0], array[1], array[2])


def pointFromArray(array):
    return Line.Point(array[0], array[1], array[2])


# calculate the fresnel factor
def fresnel(psi, eta):
    c = np.cos(psi)
    g = np.sqrt(eta ** 2 + c ** 2 - 1)
    F = 0.5 * ((g - c) / (g + c)) ** 2 * (1 + ((c * (g + c) - 1) / (c * (g - c) + 1)) ** 2)
    return F

def fresnelZero(eta):
    c = 1.
    g = np.sqrt(eta ** 2 + c ** 2 - 1)
    F = 0.5 * ((g - c) / (g + c)) ** 2 * (1 + ((c * (g + c) - 1) / (c * (g - c) + 1)) ** 2)
    return F


def Beckmann63Distribution(delta, m):
    D = np.exp(-np.tan(delta) ** 2 / m ** 2) / (4 * m ** 2 * np.cos(delta) ** 4)
    return D


def Gm(m, h, s):
    Gm = 2 * m.dot(h) * m.dot(s) / h.dot(s)
    return Gm


def Gs(m, h, s, v):
    Gs = 2 * m.dot(h) * m.dot(v) / h.dot(s)
    return Gs
