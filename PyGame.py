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
light = Light(Point(0, 0.1, 2), np.array([2, 2, 2]))
lightList.addLight(light)


# Create a sphere
sphere = Sphere()
# sphere.scale(1, 2, 2)
sphere.translate(-2, -2, -6)
# black plastic
sphere.material.diffuse = np.array([0.00, 0.00, 0.00])
sphere.material.specular = np.array([0.1, 0.1, 0.3])
sphere.material.specularExponent = 10
# Add the sphere to the list of objects
obj_list.addObject(sphere)

# Create a clock object to control the frame rate
clock = pygame.time.Clock()

# Initialize variables
render_progress = 0
image = None


def render_next_chunk(render_progress_x: int, render_progress_y, x_blocksize: int, y_blocksize: int):
    """Render the next chunk of the image"""
    # append the next chunk of the image to the list of rects to update
    rect = pygame.Rect(render_progress_x * x_blocksize, render_progress_y * y_blocksize, x_blocksize, y_blocksize)
    color = (255, 0, 0)

    # return the rect as an image
    return rect, color


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
