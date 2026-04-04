import pygame
import sys
import math
import numpy as np

class Floor:

    def __init__(self, screen_width, screen_height, color=(200, 200, 200), thickness=3):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.color = color
        self.thickness = thickness

    """A floor represented as a line segment between two points."""
    def straight_floor(self, start_cords, end_cords):
        self.start = start_cords
        self.end = end_cords

        dx = self.end[0] - self.start[0]
        dy = self.end[1] - self.start[1]

        length = max(abs(dx), abs(dy))

        if length == 0:
            raise ValueError("Start and end points cannot be the same")

        # Normalize direction vector
        dx /= length
        dy /= length

        self.dx = dx
        self.dy = dy

        self.calculate_normal()
        return self

    def angled_floor(self, screen_width, screen_height, angle_deg, y_start, x_end, tilt_dir=1, dir=1):
        """
        screen_width, screen_height: dimensions of the window
        angle_deg: angle of the floor in degrees (e.g., 10 for a slight tilt)
        x_start: how far from the bottom the floor starts (e.g., 50)
        tilt_dir: 1 for tilting down left to right, -1 for tilting up left to right
        dir: 1 for left-to-right floor, -1 for flipped right-to-left floor
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.angle_deg = angle_deg
        self.y_start = y_start
        self.x_end = x_end
        self.tilt_dir = tilt_dir
        self.dir = dir

        # Anchor the line near the bottom-left of the screen.
        # At 45° (slope = 1): y = y_start + x
        if self.dir == 1:
            self.start = (0, self.y_start)
        else:
            self.start = (self.screen_width, self.y_start)

        dx = math.cos(math.radians(angle_deg)) * self.dir
        dy = math.sin(math.radians(angle_deg))

        self.dx = dx
        self.dy = dy

        if self.dir == 1:
            length = math.sqrt((self.screen_height - self.y_start)**2 + x_end**2)  # how far the line goes
        else:
            length = math.sqrt((self.screen_height - self.y_start)**2 + (self.screen_width - x_end)**2)

        end_x = int(self.start[0] + dx * length)
        end_y = int(self.start[1] + dy * length)

        self.end = (end_x, end_y)

        self.calculate_normal()
        return self

    def draw(self, surface):
        pygame.draw.line(surface, self.color, self.start, self.end, self.thickness)

    def calculate_normal(self):
        # Normal vector is perpendicular to the floor's direction vector (dx, dy)
        normal = np.array([-self.dy, self.dx])

        # Ensure the normal points upwards (away from the floor). If the y-component is positive, flip it.
        if normal[1] > 0:
            normal = -normal

        # if I didnt use numpy, I would need to normalize the normal vector like this:
        #length = math.sqrt(normal[0]**2 + normal[1]**2)
        #self.normal = (normal[0] / length, normal[1] / length)

        normal = normal / np.linalg.norm(normal)
        self.normal = normal

        mid_x = (self.start[0] + self.end[0]) // 2
        mid_y = (self.start[1] + self.end[1]) // 2

        scale = 50  # makes the normal visible

        end_x = int(mid_x + normal[0] * scale)
        end_y = int(mid_y + normal[1] * scale)



def main():
    pygame.init()
    WIDTH, HEIGHT = 800, 600
    angle_deg = 10
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("45° Tilted Floor")
    clock = pygame.time.Clock()

    floor = Floor(WIDTH, HEIGHT, angle_deg)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

        screen.fill((30, 30, 40))

        mid_x = (floor.start[0] + floor.end[0]) // 2
        mid_y = (floor.start[1] + floor.end[1]) // 2

        scale = 50  # makes the normal visible

        end_x = int(mid_x + floor.normal[0] * scale)
        end_y = int(mid_y + floor.normal[1] * scale)

        #pygame.draw.line(screen, (255, 255, 255), (mid_x, mid_y), (end_x, end_y), 2)

        #pygame.draw.line(screen, (255, 0, 0), normal[0], normal[1], 1)  # draw normal for visualization   
        floor.draw(screen)
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()