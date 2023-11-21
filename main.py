# This is a sample Python script.
import numpy as np

from Line import Point
from Objects import Sphere, Light, isInShadow, ObjectList, LightList

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    obj = Sphere()
    obj.translate(0, 0, -6)
    objlist = ObjectList()
    objlist.addObject(obj)
    point = Point(0, 0, -10)

    light = Light(Point(0, 0, 0), np.array([100, 100, 100]))

    isInShadow = isInShadow(light, point)
    print(isInShadow)
