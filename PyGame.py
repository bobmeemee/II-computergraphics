import numpy as np
import pygame
import sys

from Camera import Camera
from Line import Point, Vector
from Objects import ObjectList, Sphere, Cube, GenericSquare, LightList, Light

# Initialize Pygame
pygame.init()

# Set up display
width, height = 800, 600
blocksize = 4
x_blocksize = width // blocksize
y_blocksize = height // blocksize

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Ray Tracer")

camera = Camera()
camera.set(eye=Point(0, 0, 0), look=Point(0, 0, -1), up=Vector(0, 1, 0))

obj_list = ObjectList()
lightList = LightList()

# Create a clock object to control the frame rate
clock = pygame.time.Clock()

# Initialize variables
render_progress = 0
image = None


def main():
    #test_transparency()
    #test_reflection()
    test_reflection_inCube()
    update_color = None
    update_rect = None
    render_progress = 0
    x = 0
    y = 0
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if y < height:
            update_color = camera.raytrace(width, height, x, y)  # Function to get the color
            # cast np array to tuple
            update_color = tuple(update_color)
            update_rect = pygame.Rect(x, y, blocksize, blocksize)

            if x < width:
                x += blocksize
            else:
                x = 0
                y += blocksize
                render_progress = y / height * 100
                print("Part of image rendered: " + str(render_progress) + "%")

            # Draw the rendered part of the image
            if update_rect is not None:
                pygame.draw.rect(screen, update_color, update_rect)
                pygame.display.update(update_rect)

    pygame.quit()
    sys.exit()


# This routine only works when the shadows are turned off
def test_reflection():
    # Create lights
    light_1 = Light(Point(0, 0, 1), np.array([100, 100, 100]) * .0)
    lightList.addLight(light_1)
    light_2 = Light(Point(3, 0, -3), np.array([255, 255, 255]) * .0)
    lightList.addLight(light_2)
    light_3 = Light(Point(0, -2, -3), np.array([255, 255, 255]) * .3)
    lightList.addLight(light_3)

    # Create a cube
    cube = Cube()
    cube.scale(0.3, 0.3, 0.3)
    cube.rotate(45, 1, 0, 0)
    cube.rotate(45, 0, 1, 0)
    cube.translate(0, 0, -3)

    cube.material.emissive = np.array([100., 100, 100]) * 0
    cube.material.eta = np.array([.800, .2, .989])  # BGR
    cube.material.ka = 0.5  # ambient
    cube.material.kd = 0.3  # diffuse
    cube.material.ks = 0.4  # specular
    cube.material.m = 0.3  # roughness

    cube.material.shininess = 0  # reflection
    cube.material.transparency = 0.0  # refraction
    cube.material.relativeLightspeed = 1

    # create a cube and place yourself inside
    square = GenericSquare()
    square.scale(2, 2)
    square.translate(0, .2, -4)
    square.rotate(30, 1, 0, 0)
    square.priority = 1

    square.material.emissive = np.array([100., 100, 100]) * 0
    square.material.eta = np.array([.8, .8, .8])  # BGR
    square.material.ka = 0.2  # ambient
    square.material.kd = 0.4  # diffuse
    square.material.ks = 0.2  # specular
    square.material.m = 0.1  # roughness CANT BE 0

    square.material.shininess = 1.  # reflection

    square.material.transparency = 0  # refraction
    square.material.relativeLightspeed = 1

    # Add the objects to the list of objects
    obj_list.addObject(square)
    obj_list.addObject(cube)


def test_reflection_inCube():
    # Create lights
    light_1 = Light(Point(0, 0, 1), np.array([100, 100, 100]) * .8)
    lightList.addLight(light_1)
    light_2 = Light(Point(3, 0, -3), np.array([255, 255, 255]) * .0)
    lightList.addLight(light_2)
    light_3 = Light(Point(0, -2, -3), np.array([255, 255, 255]) * .0)
    lightList.addLight(light_3)

    # Create a cube
    cube = Cube()
    cube.scale(5, 5, 5)
    cube.translate(0, 0, 0)

    cube.material.emissive = np.array([100., 100, 100]) * 0
    cube.material.eta = np.array([.4, .4, .4])  # BGR
    cube.material.ka = 0.2  # ambient
    cube.material.kd = 0.3  # diffuse
    cube.material.ks = 0.4  # specular
    cube.material.m = 0.3  # roughness

    cube.material.shininess = 1  # reflection
    cube.material.transparency = 0.0  # refraction
    cube.material.relativeLightspeed = 1

    # create a cube and place yourself inside
    sphere = Sphere()
    sphere.scale(0.5, 0.5, 0.5)
    sphere.translate(0, 0, -3)
    sphere.priority = 1

    sphere.material.emissive = np.array([100., 100, 100]) * 0
    sphere.material.eta = np.array([.8, .8, .8])  # BGR
    sphere.material.ka = 0.2  # ambient
    sphere.material.kd = 0.4  # diffuse
    sphere.material.ks = 0.6  # specular
    sphere.material.m = 0.1  # roughness CANT BE 0

    sphere.material.shininess = 0.  # reflection

    sphere.material.transparency = 0  # refraction
    sphere.material.relativeLightspeed = 1

    # Add the objects to the list of objects
    obj_list.addObject(sphere)
    obj_list.addObject(cube)


def test_transparency():
    # Create lights
    light_1 = Light(Point(0, 0, 4), np.array([100, 100, 100]))
    lightList.addLight(light_1)
    light_2 = Light(Point(2, 2, -3), np.array([255, 255, 255]))
    #lightList.addLight(light_2)

    # Create a sphere
    sphere = Sphere()
    sphere.scale(0.5, 0.8, 0.5)
    sphere.translate(0, 0, -3)

    sphere.material.emissive = np.array([100., 100, 100]) * 0
    sphere.material.eta = np.array([.800, .876, .989])  # BGR
    sphere.material.ka = 0.1  # ambient
    sphere.material.kd = 0.2  # diffuse
    sphere.material.ks = 0.1  # specular
    sphere.material.m = 0.1  # roughness

    sphere.material.shininess = 0.01  # reflection

    sphere.material.transparency = 1  # refraction
    sphere.material.relativeLightspeed = .9
    sphere.priority = 1

    # create a transparent square
    cube = Cube()
    cube.scale(1, 1, 1)
    cube.rotate(45, 1, 0, 0)
    cube.rotate(45, 0, 1, 0)
    cube.translate(0, 0, -9)
    cube.priority = 0

    cube.material.emissive = np.array([100., 100, 100]) * 0
    cube.material.eta = np.array([.6, .5, .3])  # BGR
    cube.material.ka = 0.2  # ambient
    cube.material.kd = 0.2  # diffuse
    cube.material.ks = 0.4  # specular
    cube.material.m = 0.01  # roughness CANT BE 0

    cube.material.shininess = 0.01  # reflection

    cube.material.transparency = 0  # refraction
    cube.material.relativeLightspeed = 1

    # Add the objects to the list of objects
    obj_list.addObject(sphere)
    obj_list.addObject(cube)


if __name__ == "__main__":
    main()
