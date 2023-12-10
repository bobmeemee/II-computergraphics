import numpy as np
import sys as sys
import ctypes

from Objects import ObjectList, Intersection, GenericSquare, Sphere, Cube, Object, LightList, isInShadow

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
        x_dir = screen_width + 2 * -x
        y_dir = screen_height + 2 * -y
        self.ray.setDirection(x_dir, y_dir, self.farDist)
        clr = self.shadeCookTorrance(self.ray)
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
        normal = h.normal
        normal.normalize()  # vector
        for light in LightList.getInstance().getLights():
            # TODO: if light in shadow, don't add diffuse and specular
            s = light.position - hitPoint  # vector
            s.normalize()
            mDotS = s.dot(normal)  # point * vector = scalar
            if mDotS > 0:  # if the light is in front of the object
                # TODO: diffuse is the same for one surface, this has potential for optimization
                diffuseColor = mDotS * obj.material.diffuse * light.color  # scalar *color * color = color
                color += diffuseColor  # color + color = color
                half = s + v  # vector
                half.normalize()
                mDotH = half.dot(normal)  # scalar
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

    def shadeNew(self, ray: Line):
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

        ambient = np.array([0.1, 0.1, 0.1]) * obj.material.ka * utils.fresnelZero(obj.material.eta)
        color += ambient

        normal = h.normal
        normal.normalize()  # vector

        for light in LightList.getInstance().getLights():
            s = light.position - hitPoint  # vector
            s.normalize()
            lambert = s.dot(normal)  # lambert term
            if lambert > 0:  # if the light is in front of the object
                diffuse = light.color * 0.0001 * obj.material.kd * utils.fresnelZero(obj.material.eta) * lambert
                color += diffuse

                half = s + v  # half vector
                half.normalize()
                mDotV = normal.dot(v)  # denominator of the geometric term
                if mDotV > 0:
                    phi = np.arccos(half.dot(normal))
                    theta = np.arccos(s.dot(normal))
                    delta = (phi - theta) / 2
                    D = utils.Beckmann63Distribution(delta, obj.material.m)
                    F = utils.fresnel(phi, obj.material.eta)
                    Gm = utils.Gm(normal, half, s)
                    Gs = utils.Gs(normal, half, s, v)
                    G = min(1, Gm, Gs)
                    geometric = G * F * D / mDotV
                    specular = light.color * obj.material.ks * 0.0001 * geometric
                    color += specular
                print(color)

        # if one of the color components is greater than 255, set it to 255
        for i in range(3):
            if color[i] > 255:
                color[i] = 255
        return color

    def shadeCookTorrance(self, ray: Line):
        bestIntersection = self.getFistHit(ray)
        if bestIntersection.numberOfHits == 0:
            return np.array([0, 0, 0])
        # if ray.recuseLevel == 1 and bestIntersection.numberOfHits == 1:
        #     print("recursed hit object", bestIntersection.hit[0].object)
        #     print("isEntering" if bestIntersection.hit[0].isEntering else "isExiting")
        h = bestIntersection.hit[0]
        hitPoint = h.intersectionPoint
        ray.vector.normalize()
        v = ray.vector * -1  # viewer vector
        obj = h.object

        # emissive component
        color = np.array([0., 0., 0.])
        color += obj.material.emissive

        # ambient component
        ambient = np.array([255., 255.0, 255.0]) * obj.material.ka * utils.fresnelZero(obj.material.eta)
        color += ambient

        normal = h.normal
        normal.normalize()

        domega = 200  # honestly, I don't know what value this should be

        # create a ray to find the shadows
        epsilon = 0.002
        hitPoint_shade = hitPoint - ray.vector * epsilon
        feeler = Line(Vector(0, 0, 0), hitPoint_shade)
        feeler.recuseLevel = 1

        for light in LightList.getInstance().getLights():

            # if the light is in shadow, skip it
            feeler.setDirection(light.point.x - hitPoint.x, light.point.y - hitPoint.y, light.point.z - hitPoint.z)
            feeler.vector.normalize()
            # TODO: if blocking objects are transparent, don't skip it
            if isInShadow(feeler):
                continue

            s = light.point - hitPoint  # vector to light source
            s.normalize()

            # diffuse component
            lambert = s.dot(normal)  # lambert term
            if lambert > 0:  # if the light is in front of the object
                diffuse = light.color * domega * obj.material.kd * utils.fresnelZero(obj.material.eta) * lambert
                color += diffuse

                # specular component
                half = s + v  # half vector between viewer and light source
                half.normalize()
                mDotV = normal.dot(v)  # check if the viewer is in front of the object
                if mDotV > 0:
                    thetha_in = np.arccos(s.dot(normal))  # phi
                    v.normalize()
                    thetha_out = np.arccos(v.dot(normal))  # theta
                    spec = utils.specular_value(thetha_in, thetha_out, obj.material.m, obj.material.eta)
                    specular = light.color * obj.material.ks * spec * domega
                    color += specular
                    # if ray.recuseLevel == 1:
                    #     print("recursed color: ", color)

            # if the ray has been recused too many times, skip the reflection & refraction
        if ray.recuseLevel == 3:
            return color
        # TODO: refraction from other objects
        # reflection component
        if obj.material.shininess > 0.51:
            # create a ray to find the reflection
            reflection = Line(Vector(0, 0, 0), hitPoint)
            r = 2 * ray.vector.dot(normal)
            reflection.vector = ray.vector - normal * r
            reflection.vector.normalize()
            reflection.recuseLevel = ray.recuseLevel + 1
            color += self.shadeCookTorrance(reflection) * obj.material.shininess

        # refraction component
        if obj.material.transparency > 0.51:
            # create a ray to find the refraction
            # move the hitpoint a little bit to prevent the ray from hitting the same object again
            epsilon = 0.005
            hitPoint_refraction = hitPoint + ray.vector * epsilon
            transparancyRay = Line(Vector(0, 0, 0), hitPoint)
            if h.isEntering:
                if ray.recuseLevel == 0:  # the first object it enters
                    c1 = 1
                    c2 = obj.material.relativeLightspeed
                elif len(ray.objects) != 0:
                    highestPriorityObject = utils.getHighestPriorityObject(ray.objects)
                    c1 = highestPriorityObject.material.relativeLightspeed
                    if obj.priority > highestPriorityObject.priority:  # if the new object has a higher priority,
                        # use it for c2
                        c2 = obj.material.relativeLightspeed
                    else:
                        c2 = highestPriorityObject.material.relativeLightspeed
                # copy the objects from the previous ray in the new ray
                transparancyRay.objects = ray.objects.copy()
                # add the current object to the new ray
                transparancyRay.objects.append(obj)
            else:
                c1 = utils.getHigestPriorityLightSpeed(ray.objects)
                ray.objects.remove(obj)
                c2 = utils.getHigestPriorityLightSpeed(ray.objects)
                transparancyRay.objects = ray.objects.copy()
            # calculate the new direction of the ray
            transparancyRay.vector = utils.calculate_transparency_vector(ray.vector, normal, c1, c2)
            transparancyRay.recuseLevel = ray.recuseLevel + 1
            print("recursed refraction: ", transparancyRay)
            color += self.shadeCookTorrance(transparancyRay) * obj.material.transparency

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
            if isHit:
                # if there is no hit yet or the current hit is closer than the previous hit
                if bestIntersection.numberOfHits == 0 or inter.hit[0].time < bestIntersection.hit[0].time:
                    bestIntersection.hit = inter.hit
                    bestIntersection.numberOfHits = inter.numberOfHits
        return bestIntersection
