import pygame, math, json, sys
from pygame.locals import *

import pymunk
import pymunk.pygame_util
from pymunk import Vec2d

mode = None
place_mode = None

global_event = []

cfg_string = open('../assets/cfg.json').read()
cfg = json.loads(cfg_string)

def quit():
    pygame.quit()
    sys.exit()

class Toolbar:
    def __init__(self,bar_image,selected_image,topleft,check_topleft_list,tool_list):
        self.bar_image = pygame.image.load(bar_image)
        self.selected_image = pygame.image.load(selected_image)

        self.bar_rect = self.bar_image.get_rect(topleft=topleft)

        self.rect_list = []
        for pos in check_topleft_list:
            self.rect_list.append(self.selected_image.get_rect(topleft=(pos[0] + self.bar_rect.topleft[0], pos[1] + self.bar_rect.topleft[1])))

        self.tool_list = tool_list

        self.selected = None

    def update(self,mode = False):
        if mode:
            self.selected = None
        else:
            m_pos = pygame.mouse.get_pos()
            m_button = pygame.mouse.get_pressed()[0]

            if m_button:
                for i in range(len(self.rect_list)):
                    rect = self.rect_list[i]
                    if rect.collidepoint(m_pos):
                        self.selected = i
                        self.display()
                        return self.tool_list[i]
            else:
                self.display()

            return False

    def display(self):
        screen.blit(self.bar_image, self.bar_rect)

        if self.selected != None:
            screen.blit(self.selected_image, self.rect_list[self.selected])

class Space:
    def __init__(self):
        self.space = pymunk.Space()
        self.space.gravity = (0,-1000)

        self.add_mode = 0

        self.c_center = []
        self.c_edge = []
        self.c_radius = []

        self.b_a = []
        self.b_offset = []
        self.b_rect = pygame.Rect(0,0,0,0)

        self.s_a = []
        self.s_b = []
        self.s_radius = 0

        self.pc_vertices = []

        self.pp_vertices = []

        self.do = pymunk.pygame_util.DrawOptions(screen)

    def add_circle_draw(self,center,edge,radius):
        pygame.draw.circle(screen,(0,0,255),center,int(radius),0)
        pygame.draw.aaline(screen,(0,255,0),center,edge,1)

    def add_circle(self, static):#向space添加圆形刚体
        #pygame.mouse.set_cursor(cfg['mouse']['circle']['size'],cfg['mouse']['circle']['hotspot'],*pygame.cursors.compile(cfg['mouse']['circle']['string']))
        pygame.mouse.set_cursor(*pygame.cursors.broken_x)

        for event in global_event:
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 3:
                    if self.add_mode == 0:
                        pygame.mouse.set_cursor(*pygame.cursors.arrow)
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

            if static:
                pos = pymunk.pygame_util.to_pygame(self.c_center, screen)
                body = self.space.static_body
                body.position = pos
                body.angle += pygame.math.Vector2((self.c_edge[0] - self.c_center[0], self.c_edge[1] - self.c_center[1])).angle_to((1, 0)) * math.pi / 180
                shape = pymunk.Circle(body, self.c_radius, (0, 0))
                shape.elasticity = 0.5
                shape.friction = 0.5
                self.space.add(shape)
            else:
                pos = pymunk.pygame_util.to_pygame(self.c_center, screen)
                inertia = pymunk.moment_for_circle(10, 0, self.c_radius, (0, 0))
                body = pymunk.Body(10, inertia)
                body.position = pos
                shape = pymunk.Circle(body, self.c_radius, (0, 0))
                shape.elasticity = 0.5
                shape.friction = 0.5
                self.space.add(body, shape)
                body.angle += pygame.math.Vector2((self.c_edge[0] - self.c_center[0], self.c_edge[1] - self.c_center[1])).angle_to((1, 0)) * math.pi / 180
                self.space.reindex_shapes_for_body(body)

        return False

    def add_box_draw(self, rect):
        pygame.draw.rect(screen, (0,0,255), rect, 0)

    def add_box(self, static):
        pygame.mouse.set_cursor(*pygame.cursors.broken_x)

        for event in global_event:
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 3:
                    if self.add_mode == 0:
                        pygame.mouse.set_cursor(*pygame.cursors.arrow)
                        return True
                    self.add_mode = 0
                if event.button == 1:
                    self.add_mode += 1

        if self.add_mode == 1:
            self.b_a = pygame.mouse.get_pos()
            self.b_rect.topleft = self.b_a
            self.add_mode += 1
        elif self.add_mode == 2:
            self.b_offset = [pygame.mouse.get_pos()[0] - self.b_a[0], pygame.mouse.get_pos()[1] - self.b_a[1]]
            self.b_rect.size = self.b_offset
            self.add_box_draw(pygame.Rect(*self.b_a, *self.b_offset))
        elif self.add_mode == 3:
            self.add_mode = 0

            if static:
                pos = pymunk.pygame_util.from_pygame(self.b_rect.center, screen)
                body = self.space.static_body
                body.position = pos
                shape = pymunk.Poly.create_box(body, self.b_offset, 0)
                shape.elasticity = 0.5
                shape.friction = 0.5
                self.space.add(shape)
            else:
                pos = pymunk.pygame_util.from_pygame(self.b_rect.center, screen)
                inertia = pymunk.moment_for_box(10, self.b_offset)
                body = pymunk.Body(10, inertia)
                body.position = pos
                shape = pymunk.Poly.create_box(body, self.b_offset, 0)
                shape.elasticity = 0.5
                shape.friction = 0.5
                self.space.add(body, shape)

        return False

    def add_segment_draw(self,a,b,r):
        rr = int(r) * 2
        if rr == 0:
            rr += 1
        pygame.draw.line(screen,(0,0,255),a,b,rr)

    def add_segment(self, static):
        pygame.mouse.set_cursor(*pygame.cursors.broken_x)

        for event in global_event:
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 3:
                    if self.add_mode == 0:
                        pygame.mouse.set_cursor(*pygame.cursors.arrow)
                        return True
                    self.add_mode = 0
                if event.button == 1:
                    self.add_mode += 1
                if event.button == 4:
                    self.s_radius += 1
                if event.button == 5:
                    if self.s_radius > 0:
                        self.s_radius -= 1

        if self.add_mode == 1:
            self.s_a = pygame.mouse.get_pos()
            self.add_mode += 1
        elif self.add_mode == 2:
            self.s_b = pygame.mouse.get_pos()
            self.add_segment_draw(self.s_a, self.s_b, self.s_radius)
        elif self.add_mode == 3:
            self.add_mode = 0

            if static:
                body = self.space.static_body
                shape = pymunk.Segment(body, pymunk.pygame_util.from_pygame(self.s_a, screen), pymunk.pygame_util.from_pygame(self.s_b, screen), self.s_radius)
                shape.elasticity = 0.95
                shape.friction = 0.9
                self.space.add(shape)
            else:
                inertia = pymunk.moment_for_segment(10, self.s_a, self.s_b, self.s_radius)
                body = pymunk.Body(10, inertia)
                shape = pymunk.Segment(body, pymunk.pygame_util.from_pygame(self.s_a, screen), pymunk.pygame_util.from_pygame(self.s_b, screen), self.s_radius)
                shape.elasticity = 0.5
                shape.friction = 0.5
                self.space.add(body, shape)

        return False

    def add_poly_curve_draw(self, vertices):
        if len(vertices) <= 2:
            return
        pygame.draw.polygon(screen, (0,0,255), vertices, 0)

    def add_poly_curve(self, static):
        pygame.mouse.set_cursor(*pygame.cursors.broken_x)

        append = False
        for event in global_event:
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 3:
                    if self.add_mode == 0:
                        pygame.mouse.set_cursor(*pygame.cursors.arrow)
                        return True
                    self.add_mode = 0
                    self.pc_vertices = []
                if event.button == 1:
                    self.add_mode += 1
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    if self.add_mode == 1:
                        self.add_mode = 2
            if event.type == MOUSEMOTION:
                append = True

        self.add_poly_curve_draw(self.pc_vertices)

        if self.add_mode == 1 and append:
            self.pc_vertices.append(pygame.mouse.get_pos())
        elif self.add_mode == 2:
            self.add_mode = 0

            if len(self.pc_vertices) <= 2:
                self.add_mode = 0
                return False

            for i in range(len(self.pc_vertices)):
                self.pc_vertices[i] = pymunk.pygame_util.from_pygame(self.pc_vertices[i], screen)

            if static:
                body = self.space.static_body
                shape = pymunk.Poly(body, self.pc_vertices, None, 0)
                shape.elasticity = 0.5
                shape.friction = 0.5
                self.space.add(shape)
            else:
                inertia = pymunk.moment_for_poly(10, self.pc_vertices,(0,0), 0)
                body = pymunk.Body(10, inertia)
                shape = pymunk.Poly(body, self.pc_vertices, None, 0)
                shape.elasticity = 0.5
                shape.friction = 0.5
                self.space.add(body, shape)

            self.pc_vertices = []

        return False

    def add_poly_point_draw(self, vertices_in):
        vertices = vertices_in.copy()
        if len(vertices) == 0:
            return
        elif len(vertices) == 1:
            vertices.append(pygame.mouse.get_pos())
            pygame.draw.aaline(screen, (0, 0, 255), vertices[0], vertices[1], 1)
        else:
            vertices.append(pygame.mouse.get_pos())
            pygame.draw.polygon(screen, (0, 0, 255), vertices, 0)

    def add_poly_point(self, static):
        pygame.mouse.set_cursor(*pygame.cursors.broken_x)

        for event in global_event:
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 3:
                    if self.add_mode == 0:
                        pygame.mouse.set_cursor(*pygame.cursors.arrow)
                        return True
                    self.add_mode = 0
                    self.pp_vertices = []
                if event.button == 1:
                    self.pp_vertices.append(pygame.mouse.get_pos())
                if event.button == 2:
                    if self.add_mode == 0:
                        self.add_mode = 1

        self.add_poly_point_draw(self.pp_vertices)

        if self.add_mode == 1:
            self.add_mode = 0

            if len(self.pp_vertices) <= 2:
                return False

            for i in range(len(self.pp_vertices)):
                self.pp_vertices[i] = pymunk.pygame_util.from_pygame(self.pp_vertices[i], screen)

            if static:
                body = self.space.static_body
                shape = pymunk.Poly(body, self.pp_vertices, None, 0)
                shape.elasticity = 0.5
                shape.friction = 0.5
                self.space.add(shape)
            else:
                inertia = pymunk.moment_for_poly(10, self.pp_vertices, (0, 0), 0)
                body = pymunk.Body(10, inertia)
                shape = pymunk.Poly(body, self.pp_vertices, None, 0)
                shape.elasticity = 0.5
                shape.friction = 0.5
                self.space.add(body, shape)

            self.pp_vertices = []

        return False

    def update(self):
        self.space.step(1.0 / 60.0)

        for shape in self.space.shapes:
            if shape.bb.top < -10:
                self.space._remove_shape(shape)

        self.space.debug_draw(self.do)

def main():
    global global_event, place_mode

    space = Space()
    place_tool = Toolbar(cfg['gui']['toolbar']['image']['bar'],
                         cfg['gui']['toolbar']['image']['selected'],
                         cfg['gui']['toolbar']['bar_pos'],
                         cfg['gui']['toolbar']['check_topleft_list'],
                         cfg['gui']['toolbar']['tools'])

    main_clock = pygame.time.Clock()

    while True:
        screen.fill((255, 255, 255))

        global_event = pygame.event.get()

        for event in global_event:
            if event.type == QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
                quit()

        place_tool.display()

        if place_mode == 'circle':
            if space.add_circle(False):
                place_mode = None
                place_tool.update(True)
        elif place_mode == 'box':
            if space.add_box(False):
                place_mode = None
                place_tool.update(True)
        elif place_mode == 'segment':
            if space.add_segment(False):
                place_mode = None
                place_tool.update(True)
        elif place_mode == 'poly_curve':
            if space.add_poly_curve(False):
                place_mode = None
                place_tool.update(True)
        elif place_mode == 'poly_point':
            if space.add_poly_point(False):
                place_mode = None
                place_tool.update(True)
        elif place_mode == 'static_circle':
            if space.add_circle(True):
                place_mode = None
                place_tool.update(True)
        elif place_mode == 'static_box':
            if space.add_box(True):
                place_mode = None
                place_tool.update(True)
        elif place_mode == 'static_segment':
            if space.add_segment(True):
                place_mode = None
                place_tool.update(True)
        elif place_mode == 'static_poly_curve':
            if space.add_poly_curve(True):
                place_mode = None
                place_tool.update(True)
        elif place_mode == 'static_poly_point':
            if space.add_poly_point(True):
                place_mode = None
                place_tool.update(True)

        else:
            place_mode_next = place_tool.update()
            if place_mode_next:
                place_mode = place_mode_next

        space.update()

        pygame.display.flip()

        main_clock.tick_busy_loop(60)

if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((1920,1080),FULLSCREEN | HWSURFACE)

    main()