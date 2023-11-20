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
