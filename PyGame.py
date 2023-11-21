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
blocksize = 1
x_blocksize = width // blocksize
y_blocksize = height // blocksize

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Ray Tracer")

camera = Camera()
camera.set(eye=Point(0, 0, 0), look=Point(0, 0, -1), up=Vector(0, 1, 0))

obj_list = ObjectList()
lightList = LightList()

# Create a light
light = Light(Point(-1, -1, 3), np.array([100, 100, 100]))
lightList.addLight(light)


# Create a sphere
sphere = Cube()
sphere.rotate(45, 0, 1, 0)
sphere.rotate(45, 1, 0, 0)

sphere.translate(1, 1, -6)
# black plastic
sphere.material.ambient = np.array([0.0, 0.0, 0.0])
sphere.material.diffuse = np.array([0.01, 0.01, 0.01])
sphere.material.specular = np.array([0.8, 0.8, 0.8])
sphere.material.specularExponent = 1

# gold

sphere.material.eta = np.array([.800, .876, .989])  # BGR
sphere.material.ka = 0.1
sphere.material.kd = 0.6
sphere.material.ks = 0.4
sphere.material.m = 0.3

# Add the sphere to the list of objects
obj_list.addObject(sphere)

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
