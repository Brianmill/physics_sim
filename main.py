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

for i in range(400):
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
frame_count = 1
collision_checks_per_frame = 10
average_collision_time_setup = []
average_collision_time_calculation = []
average_move_time = []
average_draw_time = []
average_fps = []
fps_start_time = time.perf_counter()

while running:

    start_time_total = time.time()

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

        if event.type == pg.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pg.mouse.get_pos()
            if event.button == 1:  # left click
                object_list.append(Object(screen, mouse_x, mouse_y, 15, 1, 3, 0))
            else:
                object_list.append(Object(screen, mouse_x, mouse_y, 15, 1, -3, 0))

    start_time_collision_setup = time.time()
    object_list = sorted(object_list, key=lambda obj: obj.x)
    pairs = []

    for i in range(len(object_list)):
        near_objects = object_collision.find_near_object(i, object_list)

        for obj2 in near_objects:
            pairs.append((object_list[i], obj2))
    
    end_time_collision_setup = time.time()
    start_time_collision_calculation = time.time()

    for _ in range(collision_checks_per_frame):
        for obj1, obj2 in pairs:
            object_collision.handle_object_collision(obj1, obj2, energy_loss, friction)

    end_time_collision_calculation = time.time()
    start_time_move = time.time()

    for obj in object_list:
        # remove if if out of bounds
        if 0 < obj.y < WIN_HEIGHT and 0 < obj.x < WIN_WIDTH:
            object_collision.simulate_move(obj, boundries, energy_loss, friction)
        else:
            object_list.remove(obj)

    end_time_move = time.time()
    start_time_draw = time.time()

    #NOTE# Anything drawn before this line will be covered by the white background
    screen.fill((255, 255, 255))

    for obj in object_list:
        obj.draw(screen)

    for boundry in boundries:
        boundry.draw(screen)

    end_time_draw = time.time()

    clock.tick(FPS)

    end_time_total = time.time()
    average_fps.append(end_time_total - start_time_total)
    average_collision_time_setup.append(end_time_collision_setup - start_time_collision_setup)
    average_collision_time_calculation.append(end_time_collision_calculation - start_time_collision_calculation)
    average_move_time.append(end_time_move - start_time_move)
    average_draw_time.append(end_time_draw - start_time_draw)
    frame_count += 1

    if time.perf_counter() - fps_start_time >= 1:
        pg.display.set_caption(f"FPS: {frame_count:.0f}")
        average_fps = sum(average_fps) / len(average_fps)
        average_collision_time_setup = sum(average_collision_time_setup) / len(average_collision_time_setup)
        average_collision_time_calculation = sum(average_collision_time_calculation) / len(average_collision_time_calculation)
        average_move_time = sum(average_move_time) / len(average_move_time)
        average_draw_time = sum(average_draw_time) / len(average_draw_time)
        print("--- Performance Metrics ---")
        print(f"Average collison time setup: {(average_collision_time_setup / average_fps):.4f}%")
        print(f"Average collison time calculation: {(average_collision_time_calculation / average_fps):.4f}%")
        print(f"Average move time: {(average_move_time / average_fps):.4f}%")
        print(f"Average draw time: {(average_draw_time / average_fps):.4f}%")
        print("---------------------------")
        frame_count = 1
        average_fps = []
        average_collision_time_setup = []
        average_collision_time_calculation = []
        average_move_time = []
        average_draw_time = []
        fps_start_time = time.perf_counter()

    pg.display.update()