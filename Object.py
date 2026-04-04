import pygame as pg
import numpy as np

class Object:

    gravity = 0.05

    def __init__(self, screen, x, y, radius, mass, velocityX=0, velocityY=0):
        self.x = x
        self.y = y
        self.screen = screen
        self.radius = radius
        self.color = (0, 0, 0)
        self.velocity = np.array([velocityX, velocityY], dtype=float)
        self.mass = mass

    def draw(self, surface):
        pg.draw.circle(surface, self.color, (self.x, self.y), self.radius)
        pg.draw.circle(surface, (72, 182, 215), (self.x, self.y), self.radius - 2)

    def move(self):
        self.velocity[1] += self.gravity
 
        self.y += self.velocity[1]
        self.x += self.velocity[0]