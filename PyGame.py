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

# Create lights
light_1 = Light(Point(0, 0, 4), np.array([100, 100, 100]))
lightList.addLight(light_1)
light_2 = Light(Point(2, 2, -1.5), np.array([255, 255, 255]))
lightList.addLight(light_2)


# Create a sphere
sphere = Cube()
sphere.scale(0.5, 0.5, 0.5)
sphere.rotate(45, 1, 0, 0)
sphere.rotate(45, 0, 1, 0)
sphere.translate(0, 0, -5)

sphere.material.emissive = np.array([100., 100, 100]) * 1
sphere.material.eta = np.array([.800, .876, .989])  # BGR
sphere.material.ka = 0.5  # ambient
sphere.material.kd = 0.4  # diffuse
sphere.material.ks = 0.4  # specular
sphere.material.m = 0.3  # roughness

sphere.material.shininess = 0.01  # reflection
sphere.material.transparency = 0.01  # refraction

# create a transparent square
square = GenericSquare()
square.translate(0, 0, -2)
square.priority = 1

square.material.emissive = np.array([100., 100, 100]) * 0
square.material.eta = np.array([.4, .876, .4])  # BGR
square.material.ka = 0.1  # ambient
square.material.kd = 0.2  # diffuse
square.material.ks = 0.1  # specular
square.material.m = 0.01  # roughness CANT BE 0

square.material.shininess = 0.01  # reflection

square.material.transparency = .99  # refraction
square.material.relativeLightspeed = 0.8



# Create a cube
cube = Cube()
cube.translate(0, 0, 0)

cube.material.emissive = np.array([100., 100, 100]) * 0.1
cube.material.eta = np.array([.800, .876, .989])  # BGR
cube.material.ka = 0.1  # ambient
cube.material.kd = 0.2  # diffuse
cube.material.ks = 0.2  # specular
cube.material.m = 0.3  # roughness

cube.material.shininess = 0  # reflection
cube.material.transparency = 0.0  # refraction


# Add the objects to the list of objects
obj_list.addObject(sphere)
# obj_list.addObject(cube)
obj_list.addObject(square)

# Create a clock object to control the frame rate
clock = pygame.time.Clock()

# Initialize variables
render_progress = 0
image = None


def main():
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


if __name__ == "__main__":
    main()
