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


def microfacet_distribution(theta_h, k):
    cos_theta_h = np.maximum(0.001, np.cos(theta_h))  # To prevent division by zero or negative values
    tan_theta_h = np.tan(theta_h)
    return (k ** 2) / (np.pi * cos_theta_h ** 4) * np.exp(-tan_theta_h ** 2 / (k ** 2 * cos_theta_h ** 2))


# we are going to replace eta with F0
def fresnel_term(theta_i, F0):
    return F0 + (1 - F0) * (1 - np.cos(theta_i)) ** 5


def geometry_attenuation(theta_i, theta_r, theta_h):
    cos_theta_i = np.maximum(0.001, np.cos(theta_i))  # To prevent division by zero or negative values
    cos_theta_r = np.maximum(0.001, np.cos(theta_r))  # To prevent division by zero or negative values
    cos_theta_h = np.maximum(0.001, np.cos(theta_h))  # To prevent division by zero or negative values

    G1 = 2 * cos_theta_h * cos_theta_i / np.maximum(cos_theta_i, cos_theta_r)
    G2 = 2 * cos_theta_h * cos_theta_r / cos_theta_i
    return np.minimum(np.minimum(1, G1), G2)


def specular_value(theta_i, theta_r, k, F0):
    theta_h = (theta_i + theta_r) / 2  # Calculate the half-angle

    D = microfacet_distribution(theta_h, k)
    F = fresnel_term(theta_i, F0)
    G = geometry_attenuation(theta_i, theta_r, theta_h)

    specular = (D * F * G) / (4 * np.cos(theta_i) * np.cos(theta_r))
    return specular
