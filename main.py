# This is a sample Python script.
import numpy as np
import random as rd

from Line import Point, Line, Vector
from Objects import Sphere, Light, isInShadow, ObjectList, LightList
from utils import radianToDegree, degreeToRadian, vectorFromArray, pointFromArray, fresnel, fresnelZero, \
    Beckmann63Distribution, Gm, Gs, microfacet_distribution, fresnel_term, calculate_transparency_vector

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    ray = Line(Vector(4, 2, 2), Point(0, 0, -1))
    ray.vector.normalize()
    print(ray.vector)
    for i in range(0, 10):
        i /=10
        j = rd.random()
        normal = Vector(i, j, -1)
        normal.normalize()
        vect = calculate_transparency_vector(ray.vector, normal, 1, 1)
        print(vect)
