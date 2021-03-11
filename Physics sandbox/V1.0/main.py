import pygame, math, sys
from pygame.locals import *

import pymunk
import pymunk.pygame_util
from pymunk import Vec2d

mode = None
add_mode = None

global_event = []

def quit():
    pygame.quit()
    sys.exit()

class Space:
    def __init__(self):
        self.space = pymunk.Space()
        self.space.gravity = (0,-1000)

        self.add_mode = 0

        self.c_center = []
        self.c_edge = []
        self.c_radius = []

        self.do = pymunk.pygame_util.DrawOptions(screen)

    def add_circle_draw(self,center,edge,radius):
        pygame.draw.circle(screen,(0,0,255),center,int(radius),0)
        pygame.draw.aaline(screen,(0,255,0),center,edge,1)

    def add_circle(self):#向space添加圆形刚体
        for event in global_event:
            if event.type == QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
                quit()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 3:
                    if mode == 0:
                        return True
                    self.add_mode = 0
                if event.button == 1:
                    self.add_mode += 1

        if self.add_mode == 1:
            self.c_center = pygame.mouse.get_pos()
            self.add_mode += 1
        elif self.add_mode == 2:
            self.c_edge = pygame.mouse.get_pos()
            self.c_radius = pygame.math.Vector2(self.c_center).distance_to(self.c_edge)
            self.add_circle_draw(self.c_center,self.c_edge,self.c_radius)
        elif self.add_mode == 3:
            self.add_mode = 0

            pos = pymunk.pygame_util.to_pygame(self.c_center, screen)
            inertia = pymunk.moment_for_circle(10, 0, self.c_radius, (0, 0))
            body = pymunk.Body(10, inertia)
            body.position = pos
            shape = pymunk.Circle(body, self.c_radius, (0, 0))
            shape.elasticity = 0.9
            shape.friction = 0.5
            self.space.add(body, shape)
            body.angle += pygame.math.Vector2((self.c_edge[0] - self.c_center[0], self.c_edge[1] - self.c_center[1])).angle_to((1, 0)) * math.pi / 180
            self.space.reindex_shapes_for_body(body)

        return False

    def update(self):
        self.space.step(1.0 / 60.0)

        for shape in self.space.shapes:
            if shape.bb.top < -10:
                self.space._remove_shape(shape)

        self.space.debug_draw(self.do)

def main():
    global global_event

    space = Space()
    main_clock = pygame.time.Clock()

    while True:
        screen.fill((255, 255, 255))

        global_event = pygame.event.get()

        space.add_circle()
        space.update()

        pygame.display.flip()

        main_clock.tick_busy_loop(60)

if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((1920,1080),FULLSCREEN | HWSURFACE)

    main()