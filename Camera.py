import numpy as np
import sys as sys
import ctypes

from Objects import ObjectList, Intersection, GenericSquare, Sphere, Cube, Object, LightList

'''
from Objects import Intersection, ObjectList
from pyopengl.OpenGL.raw.GLUT import *
from pyopengl.OpenGL.GLUT.special import glutInit
from pyopengl.OpenGL.raw.GL.VERSION.GL_1_0 import *
'''
import utils
from Line import Point, Vector, Line


class Camera:
    def __init__(self):
        self.eye = Point(0, 0, 0)
        self.look = Point(0, 0, -1)
        self.up = Vector(0, 1, 0)

        self.u = Vector(1, 0, 0)
        self.v = Vector(0, 1, 0)
        self.n = Vector(0, 0, 1)

        self.viewAngle = 45
        self.aspect = 1
        self.nearDist = 1
        self.farDist = -1000

        self.ray = Line(Vector(0, 0, 0), self.eye)

    def setModelviewMatrix(self):
        eVec = Vector(self.eye.x, self.eye.y, self.eye.z)
        m = [self.u.x, self.v.x, self.n.x, -eVec.dot(self.u),
             self.u.y, self.v.y, self.n.y, -eVec.dot(self.v),
             self.u.z, self.v.z, self.n.z, -eVec.dot(self.n),
             0, 0, 0, 1]

    def set(self, eye, look, up):
        self.eye = eye
        self.look = look
        self.up = up
        self.n = self.eye - self.look
        self.u = self.up.cross(self.n)
        self.n.normalize(), self.u.normalize()
        self.v = self.n.cross(self.u)

    def slide(self, delU, delV, delN):
        self.eye.x += delU * self.u.x + delV * self.v.x + delN * self.n.x
        self.eye.y += delU * self.u.y + delV * self.v.y + delN * self.n.y
        self.eye.z += delU * self.u.z + delV * self.v.z + delN * self.n.z

    def roll(self, angle):
        cs = np.cos(utils.degreeToRadian(angle))
        sn = np.sin(utils.degreeToRadian(angle))
        t = self.u
        self.u = cs * t + sn * self.v
        self.v = -sn * t + cs * self.v

    def raytrace(self, screen_width: int, screen_height: int, x: int, y: int):
        """Raytrace the scene

        ray = Line(Vector(0, 0, 0), self.eye)
        ray.setOrigin(0, 0, 0)
        nCols = screen_width / blocksize
        nRows = screen_height / blocksize
        for x in range(0, screen_width, blocksize):
            for y in range(0, screen_height, blocksize):
                x_dir = -screen_width + 2*x
                y_dir = -screen_height + 2*y
                print(x_dir, y_dir)
                ray.setDirection(x_dir, y_dir, self.farDist)
                clr = self.shade(ray)
                """
        x_dir = screen_width + 2 * -x
        y_dir = screen_height + 2 * -y
        self.ray.setDirection(x_dir, y_dir, self.farDist)
        clr = self.shade(self.ray)
        return clr

    def shade(self, ray: Line):
        """Shade the ray
        """
        bestIntersection = self.getFistHit(ray)
        if bestIntersection.numberOfHits == 0:
            return np.array([0, 0, 0])
        h = bestIntersection.hit[0]
        hitPoint = h.intersectionPoint
        v = ray.vector * -1
        obj = h.object
        color = np.array([0., 0., 0.])
        color += obj.material.emissive
        print("obj material emissive: ", obj.material.emissive)
        normal = h.normal
        normal.normalize()  # vector
        for light in LightList.getInstance().getLights():
            # TODO: if light in shadow, don't add diffuse and specular
            s = light.position - hitPoint  # vector
            s.normalize()
            mDotS = s.dot(normal)  # point * vector = scalar
            if mDotS > 0:  # if the light is in front of the object
                print("surface: ", h.surface)
                # TODO: diffuse is the same for one surface, this has potential for optimization
                diffuseColor = mDotS * obj.material.diffuse * light.color  # scalar *color * color = color
                color += diffuseColor  # color + color = color
                h = s + v  # vector
                h.normalize()
                mDotH = h.dot(normal)  # scalar
                if mDotH > 0:
                    phong = np.power(mDotH, obj.material.specularExponent)
                    specularColor = phong * obj.material.specular * light.color
                    color += specularColor
        print(color)

        # if one of the color components is greater than 255, set it to 255
        for i in range(3):
            if color[i] > 255:
                color[i] = 255
        return color

    def getFistHit(self, ray: Line):
        """Get the first hit"""

        bestIntersection = Intersection()
        bestIntersection.numberOfHits = 0

        for obj in ObjectList.getInstance().getObjects():
            isHit, inter = obj.hit(ray)
            # TODO: fix the hit return value
            if isHit:
                if bestIntersection.numberOfHits == 0 or inter.hit[0].time < bestIntersection.hit[0].time:
                    bestIntersection.hit = inter.hit
                    bestIntersection.numberOfHits = inter.numberOfHits
        return bestIntersection
