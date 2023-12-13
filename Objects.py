# create an abstract object class
# object should consist of 4x4 matrix
from abc import abstractmethod, ABC
import numpy as np
import Line
import utils


# a class that provides information about a hit

class Object(ABC):
    @abstractmethod
    def hit(self, line: Line):
        pass


class Intersection:
    def __init__(self):
        self.numberOfHits = 0
        self.hit = []

    def getFirst(self):
        if self.numberOfHits == 0:
            return None
        else:
            return self.hit[0]


class HitInfo:
    def __init__(self, isEntering: bool, intersectionPoint: Line.Point, normal: Line.Vector, obj: Object, time: float,
                 surface: int):
        self.time = time
        self.object = obj
        self.isEntering = isEntering
        self.surface = surface
        self.intersectionPoint = intersectionPoint
        self.normal = normal


# make a color class???

class Light:
    def __init__(self, position: Line.Point, color: np.array):
        self.point = position
        self.color = color

    def getPosition(self):
        return self.point

    def getColor(self):
        return self.color

    # print method
    def __str__(self):
        return f'({self.point}, {self.color})'


class Material:
    def __init__(self):
        self.emissive = np.array([0., 0., 0.])
        self.ambient = np.array([0, 0, 0])
        self.diffuse = np.array([0, 0, 0])
        self.specular = np.array([0.9, 0.9, 0.9])
        self.specularExponent = 40  # shininess 1-200 for phong
        self.eta = np.array([1., 1., 1.])
        self.ka = 0.5
        self.kd = 0.5
        self.ks = 0.5
        self.m = 0.1  # roughness

        self.shininess = 0.5
        self.transparency = 0.5
        self.relativeLightspeed = 1.0

    def setKd(self, kd):
        self.kd = kd
        self.ks = 1 - kd

    def setKs(self, ks):
        self.ks = ks
        self.kd = 1 - ks

    def setEta(self, eta):
        self.eta = eta

    def setEmissive(self, emissive):
        self.emissive = emissive

    def setAmbient(self, ambient):
        self.ambient = ambient

    def setDiffuse(self, diffuse):
        self.diffuse = diffuse

    def setSpecular(self, specular):
        self.specular = specular

    def setSpecularExponent(self, specularExponent):
        self.specularExponent = specularExponent


class Sphere(Object):
    def __init__(self):
        self.transform = np.identity(4)
        self.inverseTransform = np.identity(4)
        self.radius = (1, 1, 1)
        self.material = Material()
        self.priority = 0

    def setMaterial(self, material):
        self.material = material

    def scale(self, sx, sy, sz):
        self.transform = np.dot(np.array([[sx, 0, 0, 0],
                                          [0, sy, 0, 0],
                                          [0, 0, sz, 0],
                                          [0, 0, 0, 1]]), self.transform)

        self.radius = (self.radius[0] * sx, self.radius[1] * sy, self.radius[2] * sz)

        self.inverseTransform = np.dot(self.inverseTransform, np.array([[1 / sx, 0, 0, 0],
                                                                        [0, 1 / sy, 0, 0],
                                                                        [0, 0, 1 / sz, 0],
                                                                        [0, 0, 0, 1]]))

    def translate(self, tx, ty, tz):
        self.transform = np.dot(np.array([[1, 0, 0, tx],
                                          [0, 1, 0, ty],
                                          [0, 0, 1, tz],
                                          [0, 0, 0, 1]]), self.transform)

        self.inverseTransform = np.dot(self.inverseTransform, np.array([[1, 0, 0, -tx],
                                                                        [0, 1, 0, -ty],
                                                                        [0, 0, 1, -tz],
                                                                        [0, 0, 0, 1]]))

    def rotate(self, angle, ux, uy, uz):
        pass


    # returns the intersection point and the color of the object
    def hit(self, line: Line):
        # transform the line
        transformedLineVector = np.dot(self.inverseTransform,
                                       np.array([line.vector.x, line.vector.y, line.vector.z, 0]))
        transformedLinePoint = np.dot(self.inverseTransform, np.array([line.point.x, line.point.y, line.point.z, 1]))

        # calculate the intersection point
        a = transformedLineVector[0] ** 2 + transformedLineVector[1] ** 2 + transformedLineVector[2] ** 2
        b = (transformedLineVector[0] * transformedLinePoint[0] + transformedLineVector[1] * transformedLinePoint[1]
             + transformedLineVector[2] * transformedLinePoint[2])
        c = transformedLinePoint[0] ** 2 + transformedLinePoint[1] ** 2 + transformedLinePoint[2] ** 2 - 1

        discriminant = b ** 2 - (a * c)
        if discriminant < 0:
            return False, None

        inter = Intersection()
        t1 = (-b - np.sqrt(discriminant)) / a
        if t1 > 0:
            inter.numberOfHits = 1
            intersectionPoint1 = line.getPosition(t1)

            normal = self.getNormal(intersectionPoint1)
            info = HitInfo(isEntering=True, obj=self, surface=0, time=t1, intersectionPoint=intersectionPoint1,
                           normal=normal)
            inter.hit.append(info)

        t2 = (-b + np.sqrt(discriminant)) / a
        if t2 > 0:
            inter.numberOfHits += 1
            intersectionPoint2 = line.getPosition(t2)
            normal = self.getNormal(intersectionPoint2)
            # mirror the normal if the ray is exiting the sphere
            normal *= -1
            """
            intersectionPoint2 = np.dot(self.transform,
                                        np.array([transformedLinePoint[0] + t2 * transformedLineVector[0],
                                                  transformedLinePoint[1] + t2 * transformedLineVector[1],
                                                  transformedLinePoint[2] + t2 * transformedLineVector[2],
                                                  1]))
                                                  """

            info = HitInfo(isEntering=False, obj=self, surface=0, time=t1, intersectionPoint=intersectionPoint2,
                           normal=normal)
            inter.hit.append(info)
        if inter.numberOfHits == 0:
            return False, None
        return True, inter

    def getNormal(self, point: Line.Point):
        point.transform(self.inverseTransform)
        normal = (point.x * 2 / self.radius[0] ** 2, point.y * 2 / self.radius[1] ** 2,
                  point.z * 2 / self.radius[2] ** 2)
        v = Line.Vector(normal[0], normal[1], normal[2])
        v.normalize()
        return v

    def getTransform(self):
        return self.transform

    def getInverseTransform(self):
        return self.inverseTransform


class GenericSquare(Object):
    def __init__(self):
        self.transform = np.identity(4)
        self.inverseTransform = np.identity(4)

        self.size_x = 1
        self.size_y = 1
        self.material = Material()

        self.priority = 0

    def scale(self, sx, sy):
        self.size_x *= sx
        self.size_y *= sy

    def translate(self, tx, ty, tz):
        self.transform = np.dot(np.array([[1, 0, 0, tx],
                                          [0, 1, 0, ty],
                                          [0, 0, 1, tz],
                                          [0, 0, 0, 1]]), self.transform)

        self.inverseTransform = np.dot(self.inverseTransform, np.array([[1, 0, 0, -tx],
                                                                        [0, 1, 0, -ty],
                                                                        [0, 0, 1, -tz],
                                                                        [0, 0, 0, 1]]))

    def rotate(self, angle, ux, uy, uz):
        # rotate the object with the Maillot algorithm
        theta = utils.degreeToRadian(angle)
        c = np.cos(theta)
        s = np.sin(theta)
        self.transform = np.dot(np.array(
            [[c + ux ** 2 * (1 - c), uy * ux * (1 - c) - uz * s, uz * ux * (1 - c) + uy * s, 0],
             [ux * uy * (1 - c) + uz * s, c + uy ** 2 * (1 - c), uz * uy * (1 - c) - ux * s, 0],
             [ux * uz * (1 - c) - uy * s, uy * uz * (1 - c) + ux * s, c + uz ** 2 * (1 - c), 0],
             [0, 0, 0, 1]]), self.transform)

        self.inverseTransform = np.dot(self.inverseTransform, np.array(
            [[c + ux ** 2 * (1 - c), uy * ux * (1 - c) + uz * s, uz * ux * (1 - c) - uy * s, 0],
             [ux * uy * (1 - c) - uz * s, c + uy ** 2 * (1 - c), uz * uy * (1 - c) + ux * s, 0],
             [ux * uz * (1 - c) + uy * s, uy * uz * (1 - c) - ux * s, c + uz ** 2 * (1 - c), 0],
             [0, 0, 0, 1]]))

    def hit(self, line: Line):
        # transform the line
        transformedLine = np.dot(self.inverseTransform,
                                 np.array([line.vector.x, line.vector.y, line.vector.z, line.vector.type]))
        transformedPoint = np.dot(self.inverseTransform,
                                  np.array([line.point.x, line.point.y, line.point.z, line.point.type]))

        # check if the line is parallel to the plane
        if abs(transformedLine[2]) < 0.00001:
            return False, None

        # calculate the intersection time
        t = -transformedPoint[2] / transformedLine[2]
        if t <= 0:
            return False, None
        hx = transformedPoint[0] + t * transformedLine[0]
        hy = transformedPoint[1] + t * transformedLine[1]

        # Check if the hit point is within the square boundaries
        if not (-self.size_x <= hx <= self.size_x and -self.size_y <= hy <= self.size_y):
            return False, None

        inter = Intersection()
        inter.numberOfHits = 1
        normal = Line.Vector(0, 0, 1)
        normal.transform(self.transform)

        info = HitInfo(isEntering=True, obj=self, surface=0, time=t, intersectionPoint=line.getPosition(t),
                       normal=normal)
        inter.hit.append(info)

        if inter.numberOfHits == 0:
            return False, None
        return True, inter


class Cube(Object):
    def __init__(self):
        self.transform = np.identity(4)
        self.inverseTransform = np.identity(4)

        self.size_x = 1
        self.size_y = 1
        self.size_z = 1

        self.material = Material()

        self.priority = 0

    def scale(self, sx, sy, sz):
        self.size_x *= sx
        self.size_y *= sy
        self.size_z *= sz

    def translate(self, tx, ty, tz):
        self.transform = np.dot(np.array([[1, 0, 0, tx],
                                          [0, 1, 0, ty],
                                          [0, 0, 1, tz],
                                          [0, 0, 0, 1]]), self.transform)

        self.inverseTransform = np.dot(self.inverseTransform, np.array([[1, 0, 0, -tx],
                                                                        [0, 1, 0, -ty],
                                                                        [0, 0, 1, -tz],
                                                                        [0, 0, 0, 1]]))

    def rotate(self, angle, ux, uy, uz):
        theta = utils.degreeToRadian(angle)
        c = np.cos(theta)
        s = np.sin(theta)
        self.transform = np.dot(np.array(
            [[c + ux ** 2 * (1 - c), uy * ux * (1 - c) - uz * s, uz * ux * (1 - c) + uy * s, 0],
             [ux * uy * (1 - c) + uz * s, c + uy ** 2 * (1 - c), uz * uy * (1 - c) - ux * s, 0],
             [ux * uz * (1 - c) - uy * s, uy * uz * (1 - c) + ux * s, c + uz ** 2 * (1 - c), 0],
             [0, 0, 0, 1]]), self.transform)

        self.inverseTransform = np.dot(self.inverseTransform, np.array(
            [[c + ux ** 2 * (1 - c), uy * ux * (1 - c) + uz * s, uz * ux * (1 - c) - uy * s, 0],
             [ux * uy * (1 - c) - uz * s, c + uy ** 2 * (1 - c), uz * uy * (1 - c) + ux * s, 0],
             [ux * uz * (1 - c) + uy * s, uy * uz * (1 - c) - ux * s, c + uz ** 2 * (1 - c), 0],
             [0, 0, 0, 1]]))

    def hit(self, r: Line):
        tIn = -10000000
        tOut = 10000000
        inSurface = -1
        outSurface = -1

        ray = r.transformReturn(self.inverseTransform)

        for i in range(0, 6):
            if i == 0:
                numer = self.size_y - ray.point.y
                denom = ray.vector.y
            elif i == 1:
                numer = self.size_y + ray.point.y
                denom = - ray.vector.y
            elif i == 2:
                numer = self.size_x - ray.point.x
                denom = ray.vector.x
            elif i == 3:
                numer = self.size_x + ray.point.x
                denom = - ray.vector.x
            elif i == 4:
                numer = self.size_z - ray.point.z
                denom = ray.vector.z
            elif i == 5:
                numer = self.size_z + ray.point.z
                denom = - ray.vector.z
            else:
                print("Error: Invalid case")

            if abs(denom) < 0.00001:  # parallel
                if numer < 0:  # ray is wholly outside, no chance at hit
                    return False, None
                else:  # ray is wholly inside, no chance at hit
                    continue
            else:  # not parallel and not wholly outside or inside
                tHit = numer / denom
                if denom > 0:  # exiting
                    if tHit < tOut:
                        tOut = tHit
                        outSurface = i
                else:  # entering
                    if tHit > tIn:
                        tIn = tHit
                        inSurface = i

            if tIn >= tOut:
                return False, None

        inter = Intersection()
        if tIn > 0.00001:
            inter.numberOfHits += 1
            hitNormal = utils.vectorFromArray(self.getCubeNormal(inSurface))
            hitNormal.transform(self.transform)
            inter.hit.append(
                HitInfo(isEntering=True, obj=self, surface=inSurface, time=tIn, intersectionPoint=r.getPosition(tIn),
                        normal=hitNormal))

        if tOut > 0.00001:
            inter.numberOfHits += 1
            hitNormal = utils.vectorFromArray(self.getCubeNormal(outSurface))
            #hitNormal *= -1
            hitNormal.transform(self.transform)

            inter.hit.append(HitInfo(isEntering=False, obj=self, surface=outSurface, time=tOut,
                                     intersectionPoint=r.getPosition(tOut), normal=hitNormal))

        if inter.numberOfHits == 0:
            return False, None
        return True, inter

    def getTransform(self):
        return self.transform

    def getInverseTransform(self):
        return self.inverseTransform

    @staticmethod
    def getCubeNormal(surface):
        if surface == 0:  # top
            return np.array([0, 1, 0])
        elif surface == 1:  # bottom
            return np.array([0, -1, 0])
        elif surface == 2:  # right
            return np.array([1, 0, 0])
        elif surface == 3:  # left
            return np.array([-1, 0, 0])
        elif surface == 4:  # front
            return np.array([0, 0, 1])
        elif surface == 5:  # back
            return np.array([0, 0, -1])
        else:
            print("Error: Invalid case, no hit normal for this surface ", surface)


# singleton class that stores all the objects
class ObjectList:
    __instance = None

    @staticmethod
    def getInstance():
        if ObjectList.__instance is None:
            ObjectList()
        return ObjectList.__instance

    def __init__(self):
        if ObjectList.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            ObjectList.__instance = self
            self.objects = []

    def addObject(self, obj: Object):
        self.objects.append(obj)

    def getObjects(self):
        return self.objects


# singleton class that stores all the lights
class LightList:
    __instance = None

    @staticmethod
    def getInstance():
        if LightList.__instance is None:
            LightList()
        return LightList.__instance

    def __init__(self):
        if LightList.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            LightList.__instance = self
            self.lights = []

    def addLight(self, light: Light):
        self.lights.append(light)

    def getLights(self):
        return self.lights


def isInShadow(feeler: Line):
    for obj in ObjectList.getInstance().getObjects():
        isHit, inter = obj.hit(feeler)
        if isHit:
            if inter.hit[0].time > 0.00001:
                return True
    return False
