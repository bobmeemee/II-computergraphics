import numpy as np
import utils


# create a point class
class Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.type = 1

    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def getZ(self):
        return self.z

    def rotate(self, angle, ux, uy, uz):
        theta = utils.degreeToRadian(angle)
        c = np.cos(theta)
        s = np.sin(theta)

        rotationMatrix = np.array([[c + ux ** 2 * (1 - c), ux * uy * (1 - c) - uz * s, ux * uz * (1 - c) + uy * s, 0],
                                   [uy * ux * (1 - c) + uz * s, c + uy ** 2 * (1 - c), uy * uz * (1 - c) - ux * s, 0],
                                   [uz * ux * (1 - c) - uy * s, uz * uy * (1 - c) + ux * s, c + uz ** 2 * (1 - c), 0],
                                   [0, 0, 0, 1]])

        newPoint = np.dot(rotationMatrix, np.array([self.x, self.y, self.z, self.type]))
        self.x = newPoint[0]
        self.y = newPoint[1]
        self.z = newPoint[2]

    def translate(self, tx, ty, tz):
        translationMatrix = np.array([[1, 0, 0, tx],
                                      [0, 1, 0, ty],
                                      [0, 0, 1, tz],
                                      [0, 0, 0, 1]])

        newPoint = np.dot(translationMatrix, np.array([self.x, self.y, self.z, self.type]))
        self.x = newPoint[0]
        self.y = newPoint[1]
        self.z = newPoint[2]

    def scale(self, sx, sy, sz):
        scalingMatrix = np.array([[sx, 0, 0, (1 - sx) * self.x],
                                  [0, sy, 0, (1 - sy) * self.y],
                                  [0, 0, sz, (1 - sz) * self.z],
                                  [0, 0, 0, 1]])

        newPoint = np.dot(scalingMatrix, np.array([self.x, self.y, self.z, self.type]))
        self.x = newPoint[0]
        self.y = newPoint[1]
        self.z = newPoint[2]

    def transform(self, m: np.array):
        point = np.dot(m, np.array([self.x, self.y, self.z, 1]))
        self.x = point[0]
        self.y = point[1]
        self.z = point[2]

    def toVector(self):
        return Vector(self.x, self.y, self.z)

    # define subtraction
    def __sub__(self, p):
        return Vector(self.x - p.x, self.y - p.y, self.z - p.z)

    # define addition
    def __add__(self, v):
        return Point(self.x + v.x, self.y + v.y, self.z + v.z)

    def __mul__(self, s):
        return Point(self.x * s, self.y * s, self.z * s)

    # define print method
    def __str__(self):
        return f'({self.x}, {self.y}, {self.z})'


class Vector:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.type = 0

    def rotate(self, thx, thy, thz):
        thx = utils.degreeToRadian(thx)
        thy = utils.degreeToRadian(thy)
        thz = utils.degreeToRadian(thz)
        # x-axis rotation
        x1 = self.x
        y1 = self.y * np.cos(thx) - self.z * np.sin(thx)
        z1 = self.y * np.sin(thx) + self.z * np.cos(thx)

        # y-axis rotation
        x2 = x1 * np.cos(thy) + z1 * np.sin(thy)
        y2 = y1
        z2 = -x1 * np.sin(thy) + z1 * np.cos(thy)

        # z-axis rotation
        x3 = x2 * np.cos(thz) - y2 * np.sin(thz)
        y3 = x2 * np.sin(thz) + y2 * np.cos(thz)
        z3 = z2

        self.x = x3
        self.y = y3
        self.z = z3

    def scale(self, sx, sy, sz):
        self.x *= sx
        self.y *= sy
        self.z *= sz

    def normalize(self):
        magnitude = np.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)
        self.x /= magnitude
        self.y /= magnitude
        self.z /= magnitude

    def transform(self, m: np.array):
        vector = np.dot(m, np.array([self.x, self.y, self.z, 0]))
        self.x = vector[0]
        self.y = vector[1]
        self.z = vector[2]

    def dot(self, v):
        return self.x * v.x + self.y * v.y + self.z * v.z

    # define cross product
    def cross(self, v):
        return Vector(self.y * v.z - self.z * v.y,
                      self.z * v.x - self.x * v.z,
                      self.x * v.y - self.y * v.x)

    # define scalar multiplication in the form v * s
    def __mul__(self, s):
        return Vector(self.x * s, self.y * s, self.z * s)

    def __rmul__(self, s):
        return Vector(self.x * s, self.y * s, self.z * s)

    # define subtraction
    def __sub__(self, v):
        return Vector(self.x - v.x, self.y - v.y, self.z - v.z)

    # define addition
    def __add__(self, v):
        return Vector(self.x + v.x, self.y + v.y, self.z + v.z)

    # define print method
    def __str__(self):
        return f'({self.x}, {self.y}, {self.z})'


# create a line class
# a line is defined by a point and a vector
class Line:
    def __init__(self, v: Vector, p: Point):
        self.vector = v
        self.point = p
        self.recuseLevel = 0
        self.objects = []

    def setDirection(self, x, y, z):
        self.vector = Vector(x, y, z)

    def setOrigin(self, x, y, z):
        self.point = Point(x, y, z)

    def getPosition(self, t):
        return self.point + self.vector.__mul__(t)

    def transform(self, m: np.array):
        self.vector.transform(m)
        self.point.transform(m)

    def transformReturn(self, m: np.array):
        v = np.dot(m, np.array([self.vector.x, self.vector.y, self.vector.z, 0]))
        p = np.dot(m, np.array([self.point.x, self.point.y, self.point.z, 1]))
        return Line(Vector(v[0], v[1], v[2]), Point(p[0], p[1], p[2]))

    # define print method
    def __str__(self):
        return f'({self.vector}, {self.point})'
