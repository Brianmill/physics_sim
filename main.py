import pygame as pg
import object_collision
import time
from Object import Object
from Floor import Floor
import math

WIN_WIDTH = 800
WIN_HEIGHT = 600

FPS = 60
clock = pg.time.Clock()

pg.init()
screen = pg.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

running = True

object_list = []

for i in range(500):
    if i % 2 == 0:
        object_list.append(Object(screen, WIN_WIDTH * 0.5, WIN_HEIGHT * 0.5, 15, 1, 0, 0))
    else:
        object_list.append(Object(screen, WIN_WIDTH * 0.5, WIN_HEIGHT * 0.5, 15, 1, 0, 0))

boundries = []
#boundries.append(Floor(WIN_WIDTH, WIN_HEIGHT).angled_floor(WIN_WIDTH, WIN_HEIGHT, 50, 100, 300, 1, 1))
#boundries.append(Floor(WIN_WIDTH, WIN_HEIGHT).angled_floor(WIN_WIDTH, WIN_HEIGHT, 50, 100, 500, 1, -1))
#boundries.append(Floor(WIN_WIDTH, WIN_HEIGHT).straight_floor((WIN_WIDTH // 2, 100), (WIN_WIDTH // 2, 300)))
#boundries.append(Floor(WIN_WIDTH, WIN_HEIGHT).straight_floor((100, WIN_HEIGHT // 2), (700, WIN_HEIGHT // 2)))
#boundries.append(Floor(WIN_WIDTH, WIN_HEIGHT).straight_floor((300, 400), (500, 400)))
boundries.append(Floor(WIN_WIDTH, WIN_HEIGHT).straight_floor((0, 0), (0, WIN_HEIGHT)))
boundries.append(Floor(WIN_WIDTH, WIN_HEIGHT).straight_floor((WIN_WIDTH, 0), (WIN_WIDTH, WIN_HEIGHT)))
boundries.append(Floor(WIN_WIDTH, WIN_HEIGHT).straight_floor((0, WIN_HEIGHT), (WIN_WIDTH, WIN_HEIGHT)))
boundries.append(Floor(WIN_WIDTH, WIN_HEIGHT).straight_floor((0, 500), (100, 600)))
boundries.append(Floor(WIN_WIDTH, WIN_HEIGHT).straight_floor((700, 600), (800, 500)))

energy_loss = 0.7
friction = 0.99
average_fps = 0
frame_count = 1
collision_checks_per_frame = 1

while running:

    start_time = time.time()

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

        if event.type == pg.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pg.mouse.get_pos()
            if event.button == 1:  # left click
                object_list.append(Object(screen, mouse_x, mouse_y, 15, 1, 3, 0))
            else:
                object_list.append(Object(screen, mouse_x, mouse_y, 15, 1, -3, 0))

    object_list = sorted(object_list, key=lambda obj: obj.x)

    for i in range(collision_checks_per_frame):
        for i in range(len(object_list)):
            near_objects = object_collision.find_near_object(i, object_list)
            for obj2 in near_objects:
                object_collision.handle_object_collision(object_list[i], obj2, energy_loss, friction)

    for obj in object_list:
        # remove if if out of bounds
        if 0 < obj.y < WIN_HEIGHT and 0 < obj.x < WIN_WIDTH:
            object_collision.simulate_move(obj, boundries, energy_loss, friction)
        else:
            object_list.remove(obj)

    #NOTE# Anything drawn before this line will be covered by the white background
    screen.fill((255, 255, 255))

    for obj in object_list:
        obj.draw(screen)

    for boundry in boundries:
        boundry.draw(screen)

    clock.tick(FPS)

    current_time = time.time()
    average_fps = (1 / (current_time - start_time)) + average_fps / frame_count
    frame_count += 1

    if frame_count == 60:
        pg.display.set_caption(f"FPS: {average_fps:.0f}")
        frame_count = 1
        average_fps = 0

    pg.display.update()