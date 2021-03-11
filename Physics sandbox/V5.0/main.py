import pygame, time, math, json, sys
from pygame.locals import *

import pymunk
import pymunk.pygame_util

import gui

mode = None#决定正在放置什么刚体

global_event = []#pygame产生的event

def quit():#退出程序
    pygame.quit()
    sys.exit()

def inverted_color(color):#反色
    output_color = []
    for i in color:
        output_color.append(255 - i)
    return tuple(output_color)
"""
class Propeller:
    def __init__(self, length, angle, shape):
        self.length = length
        self.angle = angle
"""
class Moving_Distance_Record():
    def __init__(self, shape, step):
        self.shape = shape
        self.start_point = pymunk.pygame_util.to_pygame(shape.body.position, screen)
        self.now_point = []
        self.run = True
        self.step = step
    def disable(self):
        self.run = False
    def update(self):
        if self.run:
            self.now_point = pymunk.pygame_util.to_pygame(self.shape.body.position, screen)
        self.draw()
    def draw(self):
        sp = list(self.start_point)
        sp[1] -= self.step * 30
        np = list(self.now_point)
        np[1] -= self.step * 30
        pygame.draw.circle(screen, (0, 255, 0), sp, 10)
        pygame.draw.circle(screen, (255, 0, 0), np, 10)
        pygame.draw.aaline(screen, (0, 0, 0), sp, np)
        length = pygame.Vector2(sp).distance_to(np)
        prompt = '%.3fcm' % length
        pos = []
        pos.append((np[0] - sp[0]) / 2 + sp[0])
        pos.append((np[1] - sp[1]) / 2 + sp[1])
        gui.show_prompt_text(prompt, pos)
class Space:#最重要的类，虚拟物理环境
    def __init__(self):
        self.space = pymunk.Space()
        self.space.gravity = (0,-1000)

        self.run_simulation = False#决定是否更新虚拟环境（是否进行仿真）

        self.shape_internal_number = 0#下一个被创建的形状的内部编码（用来记录被选中的形状等）

        self.close_button = gui.Button(**cfg['gui']['menu_assets']['button']['menu']['close'], surface=screen, press_callback=quit, pos=(350, 10), prompt_text='退出程序')

        #self.propeller_list = []
        self.moving_distance_record_list = []

        self.give_force_image = pygame.image.load(cfg['gui']['maps']['give_force']).convert_alpha()
        self.give_force_sound = pygame.mixer.Sound(cfg['sounds']['give_force'])
        self.give_force_sound.set_volume(1)

        self.chosen_prompt = None#在鼠标上的形状
        self.chosen_shape = []#被选中的形状列表
        self.chosen_draw_width = 5#在被选中的形状上渲染的提示框的宽度
        self.chosen_mode = 0#用来记录用户的选中动作进行到那步
        self.drag_mode = 0#用来记录用户的拖动动作进行到那步
        self.chosen_start = []#开始选中时的鼠标位置
        self.chosen_end = []#结束选中时的鼠标位置
        self.chosen_rect = None#选中的区域
        self.continue_to_choose = False#是否继续选择
        self.temporary_chosen_shape = []#继续选中时的临时选中列表

        self.add_mode = 0#用来记录用户动作进行到那步

        self.c_center = []#添加圆形时用来记录圆心的坐标
        self.c_edge = []#添加圆形时用来记录圆的边缘（鼠标）的坐标
        self.c_radius = []#添加圆形时用来记录半径

        self.b_a = []#添加方形时用来记录起始点的坐标
        self.b_offset = []#添加方形时用来记录与起始点的偏移距离
        self.b_rect = pygame.Rect(0,0,0,0)#添加方形时用来记录当前的形状及位置

        self.s_a = []#添加线段时用来记录起始点的坐标
        self.s_b = []#添加线段时用来记录当前点的坐标
        self.s_radius = 1#添加线段时用来记录线段的宽度

        self.p_vertices = []#添加多边形时用来记录每个顶点的坐标

        self.c_p_a = []
        self.c_p_b = []

        self.u_gf_a = []
        self.u_gf_b = []
        self.u_gf_angle = 0
        self.u_gf_length = 0
        self.u_gf_shape_num = 0

        #self.default_shape_color = (0,0,255)#默认的形状颜色

        self.adj = False
        self.shape_in_adj = None
        self.adj_shape_menu = None

        self.do = pymunk.pygame_util.DrawOptions(screen)



        #self.start_time = 0
        #self.stop_time = 5
        #self.record_time = False
    def add_circle_draw(self,center,edge,radius):#添加圆形刚体时用来实时绘制提示形状
        pygame.draw.circle(screen,(0,0,255),center,int(radius),0)
        pygame.draw.aaline(screen,(0,255,0),center,edge,1)
    def add_circle(self, static):#添加圆形刚体
        pygame.mouse.set_cursor(*pygame.cursors.broken_x)

        for event in global_event:#遍历事件列表以确定用户的操作进度
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    if self.add_mode == 0:
                        pygame.mouse.set_cursor(*pygame.cursors.arrow)
                        return True
                    self.add_mode = 0
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.add_mode == 0:
                        self.add_mode = 1
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    if self.add_mode == 2:
                        self.add_mode = 3

        if self.add_mode == 1:#确定圆心
            self.c_center = pygame.mouse.get_pos()
            self.add_mode += 1
        elif self.add_mode == 2:#确定半径
            self.c_edge = pygame.mouse.get_pos()
            self.c_radius = pygame.math.Vector2(self.c_center).distance_to(self.c_edge)
            self.add_circle_draw(self.c_center,self.c_edge,self.c_radius)
        elif self.add_mode == 3:#创建刚体
            self.add_mode = 0

            if self.c_center != self.c_edge:
                if static:
                    pos = pymunk.pygame_util.to_pygame(self.c_center, screen)
                    body = self.space.static_body
                    body.position = pos
                    shape = pymunk.Circle(body, self.c_radius, (0, 0))
                    shape.elasticity = 0.5
                    shape.friction = 0.5
                    setattr(shape,'num',self.shape_internal_number)
                    setattr(shape, 'color', (0, 255, 0))
                    self.shape_internal_number += 1
                    self.space.add(shape)
                    body.angle += pygame.math.Vector2((self.c_edge[0] - self.c_center[0], self.c_edge[1] - self.c_center[1])).angle_to((1, 0)) * math.pi / 180
                    self.space.reindex_shapes_for_body(body)
                else:
                    pos = pymunk.pygame_util.to_pygame(self.c_center, screen)
                    inertia = pymunk.moment_for_circle(10, 0, self.c_radius, (0, 0))
                    print(inertia)
                    body = pymunk.Body(10, inertia)
                    body.position = pos
                    shape = pymunk.Circle(body, self.c_radius, (0, 0))
                    shape.elasticity = 0.5
                    shape.friction = 0.5
                    setattr(shape, 'num', self.shape_internal_number)
                    setattr(shape, 'color', (0, 0, 255))
                    self.shape_internal_number += 1
                    self.space.add(body, shape)
                    body.angle += pygame.math.Vector2((self.c_edge[0] - self.c_center[0], self.c_edge[1] - self.c_center[1])).angle_to((1, 0)) * math.pi / 180
                    self.space.reindex_shapes_for_body(body)

        return False
    def add_box_draw(self, rect):#添加方形刚体时用来实时绘制提示形状
        pygame.draw.rect(screen, (0,0,255), rect, 0)
    def add_box(self, static):#添加方形刚体
        pygame.mouse.set_cursor(*pygame.cursors.broken_x)

        for event in global_event:#遍历事件列表以确定用户的操作进度
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    if self.add_mode == 0:
                        pygame.mouse.set_cursor(*pygame.cursors.arrow)
                        return True
                    self.add_mode = 0
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.add_mode == 0:
                        self.add_mode = 1
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    if self.add_mode == 2:
                        self.add_mode = 3

        if self.add_mode == 1:#确定第一个点
            self.b_a = pygame.mouse.get_pos()
            self.b_rect.topleft = self.b_a
            self.add_mode += 1
        elif self.add_mode == 2:#确定第二个点
            self.b_offset = [pygame.mouse.get_pos()[0] - self.b_a[0], pygame.mouse.get_pos()[1] - self.b_a[1]]
            self.b_rect.size = self.b_offset
            self.add_box_draw(pygame.Rect(*self.b_a, *self.b_offset))
        elif self.add_mode == 3:#创建刚体
            self.add_mode = 0

            if self.b_offset != [0, 0]:
                if static:
                    pos = pymunk.pygame_util.from_pygame(self.b_rect.center, screen)
                    body = self.space.static_body
                    body.position = pos
                    shape = pymunk.Poly.create_box(body, self.b_offset, 0)
                    shape.elasticity = 0.5
                    shape.friction = 0.5
                    setattr(shape, 'num', self.shape_internal_number)
                    setattr(shape, 'box', True)
                    setattr(shape, 'color', (0, 255, 0))
                    self.shape_internal_number += 1
                    self.space.add(shape)
                else:
                    pos = pymunk.pygame_util.from_pygame(self.b_rect.center, screen)
                    inertia = pymunk.moment_for_box(10, self.b_offset)
                    body = pymunk.Body(10, inertia)
                    body.position = pos
                    shape = pymunk.Poly.create_box(body, self.b_offset, 0)
                    shape.elasticity = 0.5
                    shape.friction = 0.5
                    setattr(shape, 'num', self.shape_internal_number)
                    setattr(shape, 'box', True)
                    setattr(shape, 'box_size', self.b_offset)
                    setattr(shape, 'color', (0, 0, 255))
                    self.shape_internal_number += 1
                    self.space.add(body, shape)

        return False
    def add_segment_draw(self,a,b,r):#添加线段刚体时用来实时绘制提示形状
        rr = int(r) * 2
        if rr == 0:
            rr += 1
        pygame.draw.line(screen,(0,0,255),a,b,rr)
        pygame.draw.circle(screen, (0, 0, 255), a, r - 1)
        pygame.draw.circle(screen, (0, 0, 255), b, r - 1)
    def add_segment(self, static):#添加线段刚体
        pygame.mouse.set_cursor(*pygame.cursors.broken_x)

        for event in global_event:#遍历事件列表以确定用户的操作进度
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    if self.add_mode == 0:
                        pygame.mouse.set_cursor(*pygame.cursors.arrow)
                        return True
                    self.add_mode = 0
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.add_mode == 0:
                        self.add_mode = 1
                if event.button == 4:
                    self.s_radius += 1
                if event.button == 5:
                    if self.s_radius > 1:
                        self.s_radius -= 1
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    if self.add_mode == 2:
                        self.add_mode = 3

        if self.add_mode == 1:#确定起始点
            self.s_a = pygame.mouse.get_pos()
            self.add_mode += 1
        elif self.add_mode == 2:#确定结束点
            self.s_b = pygame.mouse.get_pos()
            self.add_segment_draw(self.s_a, self.s_b, self.s_radius)
        elif self.add_mode == 3:#创建刚体
            self.add_mode = 0

            if static:
                body = self.space.static_body
                shape = pymunk.Segment(body, pymunk.pygame_util.from_pygame(self.s_a, screen), pymunk.pygame_util.from_pygame(self.s_b, screen), self.s_radius)
                shape.elasticity = 0.95
                shape.friction = 0.9
                setattr(shape, 'num', self.shape_internal_number)
                setattr(shape, 'color', (0, 255, 0))
                self.shape_internal_number += 1
                self.space.add(shape)
            else:
                inertia = pymunk.moment_for_segment(10, pymunk.pygame_util.from_pygame(self.s_a, screen), pymunk.pygame_util.from_pygame(self.s_b, screen), self.s_radius)
                body = pymunk.Body(10, inertia)
                pos = ((max(self.s_a[0], self.s_b[0]) - min(self.s_a[0], self.s_b[0])) / 2 + min(self.s_a[0], self.s_b[0]),
                     (max(self.s_a[1], self.s_b[1]) - min(self.s_a[1], self.s_b[1])) / 2 + min(self.s_a[1], self.s_b[1]))
                shape = pymunk.Segment(body, pymunk.pygame_util.from_pygame(self.s_a, screen), pymunk.pygame_util.from_pygame(self.s_b, screen), self.s_radius)
                shape.elasticity = 0.5
                shape.friction = 0.5
                angle = pygame.math.Vector2(100, 0).angle_to((self.s_b[0] - self.s_a[0], self.s_b[1] - self.s_a[1])) * math.pi / 180
                setattr(shape, 'num', self.shape_internal_number)
                setattr(shape, 'angle', angle)
                setattr(shape, 'length', pygame.math.Vector2(self.s_a).distance_to(self.s_b))
                setattr(shape, 'pos', pos)
                setattr(shape, 'color', (0, 255, 0))
                self.shape_internal_number += 1
                self.space.add(body, shape)
        return False
    def add_poly_draw(self, vertices_in):#添加平滑多边形刚体时用来实时绘制提示形状
        vertices = vertices_in.copy()
        if len(vertices) == 0:
            return
        elif len(vertices) == 1:
            vertices.append(pygame.mouse.get_pos())
            pygame.draw.aaline(screen, (0, 0, 255), vertices[0], vertices[1], 1)
        else:
            vertices.append(pygame.mouse.get_pos())
            pygame.draw.polygon(screen, (0, 0, 255), vertices, 0)
    def add_poly(self, static):#添加多边形
        pygame.mouse.set_cursor(*pygame.cursors.broken_x)

        for event in global_event:#遍历事件列表以确定用户的操作进度
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    if self.add_mode == 0:
                        pygame.mouse.set_cursor(*pygame.cursors.arrow)
                        return True
                    self.add_mode = 0
                    self.p_vertices = []
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.add_mode == 0:
                        self.add_mode += 1
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    if self.add_mode == 1:
                        self.add_mode = 2

        self.add_poly_draw(self.p_vertices)

        if self.add_mode == 1 and pygame.key.get_pressed()[K_LSHIFT] == False:#添加顶点
            self.p_vertices.append(pygame.mouse.get_pos())
        elif self.add_mode == 2:#创建刚体
            self.add_mode = 0

            vertices = []

            for p in self.p_vertices:
                if p not in vertices:
                    vertices.append(p)

            if len(vertices) <= 2:
                self.add_mode = 0
                return False

            for i in range(len(vertices)):
                vertices[i] = pymunk.pygame_util.from_pygame(vertices[i], screen)

            if static:
                body = self.space.static_body
                shape = pymunk.Poly(body, vertices, None, 0)
                shape.elasticity = 0.5
                shape.friction = 0.5
                setattr(shape, 'num', self.shape_internal_number)
                setattr(shape, 'color', (0, 255, 0))
                self.shape_internal_number += 1
                self.space.add(shape)
            else:
                inertia = pymunk.moment_for_poly(10, vertices,(0,0), 0)
                body = pymunk.Body(10, inertia)
                shape = pymunk.Poly(body, vertices, None, 0)
                shape.elasticity = 0.5
                shape.friction = 0.5
                setattr(shape, 'num', self.shape_internal_number)
                setattr(shape, 'color', (0, 0, 255))
                self.shape_internal_number += 1
                self.space.add(body, shape)

            self.p_vertices = []

        return False
    def add_pin_joint_draw(self, a, b):
        pygame.draw.aaline(screen, (0, 0, 255), a, b)
    def add_pin_joint(self):
        pygame.mouse.set_cursor(*pygame.cursors.broken_x)

        for event in global_event:  # 遍历事件列表以确定用户的操作进度
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 3:
                    if self.add_mode == 0:
                        pygame.mouse.set_cursor(*pygame.cursors.arrow)
                        return True
                    self.add_mode = 0
                if event.button == 1:
                    if self.add_mode == 0:
                        self.add_mode = 1
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    if self.add_mode == 2:
                        self.add_mode = 3

        if self.add_mode == 1:  # 确定起始点
            self.c_p_a = pygame.mouse.get_pos()
            self.add_mode = 2
        elif self.add_mode == 2:  # 确定结束点
            self.c_p_b = pygame.mouse.get_pos()
            self.add_pin_joint_draw(self.c_p_a, self.c_p_b)
        elif self.add_mode == 3:  # 创建刚体
            self.add_mode = 0

            '''
            inertia = pymunk.moment_for_segment(10, pymunk.pygame_util.from_pygame(self.s_a, screen),
                                                pymunk.pygame_util.from_pygame(self.s_b, screen), self.s_radius)
            body = pymunk.Body(10, inertia)
            pos = (
            (max(self.s_a[0], self.s_b[0]) - min(self.s_a[0], self.s_b[0])) / 2 + min(self.s_a[0], self.s_b[0]),
            (max(self.s_a[1], self.s_b[1]) - min(self.s_a[1], self.s_b[1])) / 2 + min(self.s_a[1], self.s_b[1]))
            shape = pymunk.Segment(body, pymunk.pygame_util.from_pygame(self.s_a, screen),
                                   pymunk.pygame_util.from_pygame(self.s_b, screen), self.s_radius)
            shape.elasticity = 0.5
            shape.friction = 0.5
            angle = pygame.math.Vector2(100, 0).angle_to(
                (self.s_b[0] - self.s_a[0], self.s_b[1] - self.s_a[1])) * math.pi / 180
            setattr(shape, 'num', self.shape_internal_number)
            setattr(shape, 'angle', angle)
            setattr(shape, 'length', pygame.math.Vector2(self.s_a).distance_to(self.s_b))
            setattr(shape, 'pos', pos)
            setattr(shape, 'color', (0, 255, 0))
            self.shape_internal_number += 1
            self.space.add(body, shape)
            '''

        return False
    def add_slide_joint(self):
        return True
    def add_pivot_joint(self):
        return True
    def add_groove_joint(self):
        return True
    def add_damped_spring(self):
        return True
    def add_damped_rotary_spring(self):
        return True
    def add_rotary_limit_joint(self):
        return True
    def add_ratchet_joint(self):
        return True
    def add_gear_joint(self):
        return True
    def add_simple_motor(self):
        return True
    def give_force_draw(self, a, b, angle, length):
        prompt_str = '%.2fN %.2f°' % (length, angle)
        gui.show_prompt_text(prompt_str)

        image = pygame.transform.scale(self.give_force_image, (self.give_force_image.get_width(), int(length)))
        image = pygame.transform.rotate(image, angle)

        center = [0, 0]
        center[0] = (b[0] - a[0]) / 2 + a[0]
        center[1] = (b[1] - a[1]) / 2 + a[1]
        rect = image.get_rect()
        rect.center = center

        screen.blit(image, rect)
    def give_force(self):#给刚体一个力
        pygame.mouse.set_cursor(*pygame.cursors.broken_x)

        for event in global_event:  # 遍历事件列表以确定用户的操作进度
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    if self.add_mode == 0:
                        pygame.mouse.set_cursor(*pygame.cursors.arrow)
                        return True
                    self.add_mode = 0
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    for shape in self.space.shapes:
                        if shape.point_query(pymunk.pygame_util.from_pygame(pygame.mouse.get_pos(), screen))[0] <= 0:
                            self.u_gf_shape_num = shape.num
                            self.add_mode = 1
                            break
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    if self.add_mode == 2:
                        self.add_mode = 3

        if self.add_mode == 1:  # 确定起始点
            self.u_gf_a = pygame.mouse.get_pos()
            self.add_mode += 1
        elif self.add_mode == 2:  # 确定结束点
            self.u_gf_b = list(pygame.mouse.get_pos())
            if abs(self.u_gf_b[0] - self.u_gf_a[0]) < 10:
                self.u_gf_b[0] = self.u_gf_a[0]
            if abs(self.u_gf_b[1] - self.u_gf_a[1]) < 10:
                self.u_gf_b[1] = self.u_gf_a[1]
            pos = list(self.u_gf_b)
            pos[0] -= self.u_gf_a[0]
            pos[1] -= self.u_gf_a[1]
            angle = pygame.Vector2(pos).angle_to((0, -10))
            self.u_gf_angle = angle
            length = pygame.Vector2(self.u_gf_a).distance_to(self.u_gf_b)
            self.u_gf_length = length
            self.give_force_draw(self.u_gf_a, self.u_gf_b, angle, length)
        elif self.add_mode == 3:
            self.add_mode = 0

            self.give_force_sound.play()

            for shape in self.space.shapes:
                if shape.num == self.u_gf_shape_num:
                    pos = pymunk.pygame_util.from_pygame(self.u_gf_a, screen)
                    length = self.u_gf_length * 1000
                    force = [0, 0]
                    force[0] = -math.sin(math.radians(self.u_gf_angle)) * length
                    force[1] = math.cos(math.radians(self.u_gf_angle)) * length
                    print(force)
                    #self.start_time = time.clock()
                    #self.record_time = True
                    shape.body.apply_force_at_world_point(force, pos)
                    break
    def start_moving_distance_recording(self, name):
        step = 0
        for r in self.moving_distance_record_list:
            if r.shape.num == self.shape_in_adj.num:
                r.disable()
                step += 1
        self.moving_distance_record_list.append(Moving_Distance_Record(self.shape_in_adj, step))
    def draw_shape(self,shape_list):#渲染刚体
        for order in range(3):#order == 0：未选中，order == 1：提示，order == 2：已选中
            for shape in shape_list:
                shape.color = list(shape.color)
                if hasattr(shape, 'color_r'):
                    shape.color[0] = int(shape.color_r)
                if hasattr(shape, 'color_g'):
                    shape.color[1] = int(shape.color_g)
                if hasattr(shape, 'color_b'):
                    shape.color[2] = int(shape.color_b)
                color = shape.color

                if isinstance(shape, pymunk.Circle):#绘制圆形刚体
                    pos = list(pymunk.pygame_util.to_pygame(shape.body.position, screen))
                    pos[0] = int(pos[0])
                    pos[1] = int(pos[1])

                    edge = pygame.math.Vector2(shape.radius, 0).rotate_rad(-shape.body.angle)
                    edge[0] += pos[0]
                    edge[1] += pos[1]

                    if order == 0:
                        pygame.draw.circle(screen, color, pos, int(shape.radius), 0)
                        pygame.draw.aaline(screen, inverted_color(color), pos, edge, 1)
                    elif order == 1 and shape.num == self.chosen_prompt:
                        pygame.draw.circle(screen, inverted_color(color), pos, int(shape.radius) + self.chosen_draw_width, 0)
                        pygame.draw.circle(screen, color, pos, int(shape.radius), 0)
                        pygame.draw.aaline(screen, inverted_color(color), pos, edge, 1)
                    elif order == 2 and shape.num in list(set(self.chosen_shape + self.temporary_chosen_shape)):
                        pygame.draw.circle(screen, (0, 0, 0), pos, int(shape.radius) + self.chosen_draw_width, 0)
                        pygame.draw.circle(screen, color, pos, int(shape.radius), 0)
                        pygame.draw.aaline(screen, inverted_color(color), pos, edge, 1)

                elif isinstance(shape, pymunk.Segment):#绘制线段刚体
                    if hasattr(shape, 'angle'):
                        angle = shape.angle - shape.body.angle
                        length = shape.length / 2
                        pos = list(shape.body.position)
                        pos[1] = -pos[1]
                        pos[1] -= screen.get_height()
                        pos[0] += shape.pos[0]
                        pos[1] += shape.pos[1]
                        a = pygame.math.Vector2(length, 0).rotate_rad(angle)
                        b = pygame.math.Vector2(-length, 0).rotate_rad(angle)
                        a[0] += pos[0]
                        a[1] += pos[1]
                        b[0] += pos[0]
                        b[1] += pos[1]
                        a[1] = -a[1]
                        b[1] = -b[1]
                        a = list(pymunk.pygame_util.to_pygame(a, screen))
                        b = list(pymunk.pygame_util.to_pygame(b, screen))
                    else:
                        a = pymunk.pygame_util.to_pygame(shape.a, screen)
                        b = pymunk.pygame_util.to_pygame(shape.b, screen)
                    if order == 0:
                        pygame.draw.line(screen, color, a, b, int(shape.radius * 2))
                    elif order == 1 and shape.num == self.chosen_prompt:
                        pygame.draw.line(screen, inverted_color(color), a, b, int(shape.radius * 2) + self.chosen_draw_width * 2)
                        pygame.draw.line(screen, color, a, b, int(shape.radius * 2))
                    elif order == 2 and shape.num in list(set(self.chosen_shape + self.temporary_chosen_shape)):
                        pygame.draw.line(screen, (0, 0, 0), a, b, int(shape.radius * 2) + self.chosen_draw_width * 2)
                        pygame.draw.line(screen, color, a, b, int(shape.radius * 2))

                elif isinstance(shape, pymunk.Poly):#绘制多边形刚体（方形、平滑多边形、普通多边形都属于多边形，绘制方式也一样）
                    vertices = []
                    for v in shape.get_vertices():
                        vertices.append(pymunk.pygame_util.to_pygame(v.rotated(shape.body.angle) + shape.body.position, screen))
                    if order == 0:
                        pygame.draw.polygon(screen, color, vertices)
                    elif order == 1 and shape.num == self.chosen_prompt:
                        pygame.draw.polygon(screen, color, vertices)
                        pygame.draw.lines(screen, inverted_color(color), True, vertices, self.chosen_draw_width * 2)
                    elif order == 2 and shape.num in list(set(self.chosen_shape + self.temporary_chosen_shape)):
                        pygame.draw.polygon(screen, color, vertices)
                        pygame.draw.lines(screen, (0, 0, 0), True, vertices, self.chosen_draw_width * 2)
    def draw_other(self):#渲染其他东西
        for record in self.moving_distance_record_list:
            record.update()
    def adj_parameters_of_shape(self, name, a, value):
        shape_copy = self.shape_in_adj.copy()
        self.space.remove(self.shape_in_adj)
        setattr(shape_copy, name, float(value))
        self.space.add(shape_copy.body, shape_copy)
        self.space.reindex_shapes_for_body(shape_copy.body)
        self.shape_in_adj = shape_copy
    def adj_mass(self, name, a, value):
        shape_copy = self.shape_in_adj.copy()
        self.space.remove(self.shape_in_adj)
        if isinstance(shape_copy, pymunk.Circle):
            inertia = pymunk.moment_for_circle(float(value), 0, shape_copy.radius, (0, 0))
        elif isinstance(shape_copy, pymunk.Poly):
            if hasattr(shape_copy, 'box'):
                inertia = pymunk.moment_for_box(float(value), shape_copy.box_size)
            else:
                pass
        elif isinstance(shape_copy, pymunk.Segment):
            pass
        #shape_copy.body = pymunk.Body(float(value), inertia)
        shape_copy.body.moment = inertia
        self.space.add(shape_copy.body, shape_copy)
        self.space.reindex_shapes_for_body(shape_copy.body)
        self.shape_in_adj = shape_copy
    def create_scale_points_1(self):
        r = []
        for i in range(100):
            r.append(i / 100)
        for i in range(10, 100):
            r.append(i / 10)
        for i in range(10, 101):
            r.append(i)
        return r
    def close_adj_menu(self):
        self.adj = False
        self.adj_shape_menu = None
    def adj_shape(self, shape):
        if self.adj_shape_menu == None:
            self.shape_in_adj = shape

            if shape.body.body_type == pymunk.Body.STATIC:
                menu_cfg = 'adj_static_'
            else:
                menu_cfg = 'adj_'
            if isinstance(shape, pymunk.Circle):
                menu_cfg += 'circle'
            elif isinstance(shape, pymunk.Segment):
                menu_cfg += 'segment'
            elif isinstance(shape, pymunk.Poly):
                if hasattr(shape, 'box'):
                    menu_cfg += 'box'
                else:
                    menu_cfg += 'poly'

            self.adj_shape_menu = gui.Menu(screen, cfg['gui']['menus'][menu_cfg].copy(), self.close_adj_menu)
        else:
            self.adj_shape_menu.update()
    def update_chosen(self):#更新选择模式（选择单个物体也可以通过这种方式判断）
        self.chosen_prompt = None

        for shape in self.space.shapes:
            if shape.point_query(pymunk.pygame_util.from_pygame(pygame.mouse.get_pos(), screen))[0] <= 0:
                self.chosen_prompt = shape.num

        if self.chosen_rect != None:
            pygame.draw.rect(screen, (0, 0, 0), self.chosen_rect, 1)

        for event in global_event:
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.drag_mode == 0 and not self.run_simulation and len(self.chosen_shape) != 0 and self.chosen_mode == 0 and not(pygame.key.get_pressed()[K_LCTRL] or pygame.key.get_pressed()[K_RCTRL] or pygame.key.get_pressed()[K_LSHIFT] or pygame.key.get_pressed()[K_RSHIFT]):
                        for shape in self.space.shapes:
                            if shape.num in self.chosen_shape and shape.point_query(pymunk.pygame_util.from_pygame(pygame.mouse.get_pos(), screen))[0] <= 0:
                                self.drag_mode = 1
                                break
                    if self.chosen_mode == 0 and self.drag_mode == 0:
                        if pygame.key.get_pressed()[K_LCTRL] or pygame.key.get_pressed()[K_RCTRL] or pygame.key.get_pressed()[K_LSHIFT] or pygame.key.get_pressed()[K_RSHIFT]:
                            self.continue_to_choose = True
                        self.chosen_start = pygame.mouse.get_pos()
                        rect_date = list(self.chosen_start)
                        rect_date.append(0)
                        rect_date.append(0)
                        self.chosen_rect = pygame.Rect(*rect_date)
                        pygame.mouse.set_cursor(*pygame.cursors.broken_x)
                        self.chosen_mode = 1
                if event.button == 3:
                    if self.chosen_mode != 2:
                        self.chosen_mode = 0
                        pygame.mouse.set_cursor(*pygame.cursors.arrow)
                        self.chosen_shape = []
                        self.chosen_start = []
                        self.chosen_end = []
                        self.chosen_rect = None
                        self.continue_to_choose = False
                        self.temporary_chosen_shape = []
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    if self.drag_mode == 1:
                        self.drag_mode = 0
                    elif self.chosen_mode == 1:
                        self.chosen_mode = 2
            if event.type == MOUSEDOUBLECLICK:
                for shape in self.space.shapes:
                    if shape.point_query(pymunk.pygame_util.from_pygame(event.pos0, screen))[0] <= 0 and shape.point_query(pymunk.pygame_util.from_pygame(event.pos1, screen))[0] <= 0:
                        self.adj = True
                        print('adj')
                        self.shape_in_adj = shape
                        break

        if self.run_simulation:
            self.drag_mode = 0

        if self.drag_mode == 1:
            pygame.mouse.set_cursor(cfg['mouse']['move']['size'], cfg['mouse']['move']['hotspot'], *pygame.cursors.compile(cfg['mouse']['move']['string']))
            move = (0, 0)
            for event in global_event:
                if event.type == MOUSEMOTION:
                    move = event.rel
            if move != (0, 0):
                s_list = []
                for shape in self.space.shapes:
                    if shape.num in self.chosen_shape:
                        s_list.append(shape)
                for shape in s_list:
                    temporary_shape = shape.copy()
                    temporary_shape.body.position += (move[0], -move[1])
                    self.space.remove(shape)
                    self.space.add(temporary_shape.body, temporary_shape)

        if self.drag_mode == 0:
            pygame.mouse.set_cursor(*pygame.cursors.arrow)

        if self.chosen_mode == 1:
            self.chosen_end = pygame.mouse.get_pos()
            self.chosen_rect.size = (self.chosen_end[0] - self.chosen_start[0], self.chosen_end[1] - self.chosen_start[1])
            left, top = self.chosen_rect.topleft
            right, bottom = self.chosen_rect.bottomright
            left, top = pymunk.pygame_util.from_pygame((left,top), screen)
            right, bottom = pymunk.pygame_util.from_pygame((right, bottom), screen)
            bb = pymunk.BB(left, bottom, right, top)
            if self.continue_to_choose and len(self.temporary_chosen_shape) == 0:
                self.temporary_chosen_shape = self.chosen_shape.copy()
            self.chosen_shape = []
            for shape in self.space.shapes:
                if bb.intersects(shape.bb):
                    self.chosen_shape.append(shape.num)

        elif self.chosen_mode == 2:
            self.chosen_mode = 0
            if self.continue_to_choose:
                self.chosen_shape += self.temporary_chosen_shape
                self.temporary_chosen_shape = []
                self.chosen_shape = list(set(self.chosen_shape))
                self.continue_to_choose = False
            self.chosen_start = []
            self.chosen_end = []
            self.chosen_rect = None
            pygame.mouse.set_cursor(*pygame.cursors.arrow)

        if self.adj:
            self.adj_shape(self.shape_in_adj)
    def update(self):#更新并绘制刚体
        self.close_button.update()

        if self.run_simulation:
            self.space.step(1.0 / 60.0)

        for event in global_event:
            if event.type == KEYDOWN:
                if event.key == K_DELETE:
                    for shape in self.space.shapes:
                        if shape.num in self.chosen_shape:
                            self.chosen_shape.remove(shape.num)
                            self.space.remove(shape)

        for shape in self.space.shapes:
            if shape.bb.top < -10:
                self.space.remove(shape)

        self.space.debug_draw(self.do)
        self.draw_shape(self.space.shapes)
        self.draw_other()
        """
        t = time.clock() - self.start_time
        if t >= self.stop_time and self.record_time:
            self.run_simulation = False
            self.record_time = False
        ts = '%.2f' % t
        screen.blit(gui.font.render(ts, True, (0, 0, 0)), (1700, 10))
        """
def change_mode(name, a, b):
    global mode
    if mode == None:
        mode = b
def main():
    global global_event, mode, prompt_text_size

    place_shape_tool = gui.Toolbar(surface=screen,
                                   bar_image=cfg['gui']['place_shape_toolbar']['image']['bar'],
                                   selected_image=cfg['gui']['place_shape_toolbar']['image']['selected'],
                                   topleft=cfg['gui']['place_shape_toolbar']['bar_pos'],
                                   check_topleft_list=cfg['gui']['place_shape_toolbar']['check_topleft_list'],
                                   tool_list=cfg['gui']['place_shape_toolbar']['tools'],
                                   prompt_text=cfg['gui']['place_shape_toolbar']['prompt_text'],
                                   name='place_shape',
                                   adj_callback=change_mode)
    place_constraint_tool = gui.Toolbar(surface=screen,
                                        bar_image=cfg['gui']['place_constraint_toolbar']['image']['bar'],
                                        selected_image=cfg['gui']['place_constraint_toolbar']['image']['selected'],
                                        topleft=cfg['gui']['place_constraint_toolbar']['bar_pos'],
                                        check_topleft_list=cfg['gui']['place_constraint_toolbar']['check_topleft_list'],
                                        tool_list=cfg['gui']['place_constraint_toolbar']['tools'],
                                        prompt_text=cfg['gui']['place_constraint_toolbar']['prompt_text'],
                                        name='place_constraint',
                                        adj_callback=change_mode)
    utilities_tool = gui.Toolbar(surface=screen,
                                bar_image=cfg['gui']['utilities_toolbar']['image']['bar'],
                                selected_image=cfg['gui']['utilities_toolbar']['image']['selected'],
                                topleft=cfg['gui']['utilities_toolbar']['bar_pos'],
                                check_topleft_list=cfg['gui']['utilities_toolbar']['check_topleft_list'],
                                tool_list=cfg['gui']['utilities_toolbar']['tools'],
                                prompt_text=cfg['gui']['utilities_toolbar']['prompt_text'],
                                name='utilities_tool',
                                adj_callback=change_mode)

    main_clock = pygame.time.Clock()
    mouse_clock = pygame.time.Clock()
    mouse_mode = 0
    m_pos_0 = []

    while True:
        screen.fill((255, 255, 255))

        global_event = pygame.event.get()
        gui.global_event = global_event.copy()

        for event in global_event:
            if event.type == QUIT:
                quit()
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    space.run_simulation = not space.run_simulation
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    ms = mouse_clock.tick()
                    if mouse_mode == 0:
                        mouse_mode = 1
                        m_pos_0 = pygame.mouse.get_pos()
                    elif mouse_mode == 1:
                        if ms <= gui.settings.double_click_ms:
                            pygame.event.post(pygame.event.Event(MOUSEDOUBLECLICK, {'pos0': m_pos_0, 'pos1': pygame.mouse.get_pos()}))
                        mouse_mode = 0

        place_shape_tool.display()
        place_constraint_tool.display()
        utilities_tool.display()

        if mode == 'circle':
            if space.add_circle(False):
                mode = None
                place_shape_tool.update(True)
        elif mode == 'box':
            if space.add_box(False):
                mode = None
                place_shape_tool.update(True)
        elif mode == 'segment':
            if space.add_segment(False):
                mode = None
                place_shape_tool.update(True)
        elif mode == 'poly':
            if space.add_poly(False):
                mode = None
                place_shape_tool.update(True)
        elif mode == 'static_circle':
            if space.add_circle(True):
                mode = None
                place_shape_tool.update(True)
        elif mode == 'static_box':
            if space.add_box(True):
                mode = None
                place_shape_tool.update(True)
        elif mode == 'static_segment':
            if space.add_segment(True):
                mode = None
                place_shape_tool.update(True)
        elif mode == 'static_poly':
            if space.add_poly(True):
                mode = None
                place_shape_tool.update(True)
        elif mode == 'pin_joint':
            if space.add_pin_joint():
                mode = None
                place_constraint_tool.update(True)
        elif mode == 'slide_joint':
            if space.add_slide_joint():
                mode = None
                place_constraint_tool.update(True)
        elif mode == 'pivot_joint':
            if space.add_pivot_joint():
                mode = None
                place_constraint_tool.update(True)
        elif mode == 'groove_joint':
            if space.add_groove_joint():
                mode = None
                place_constraint_tool.update(True)
        elif mode == 'damped_spring':
            if space.add_damped_spring():
                mode = None
                place_constraint_tool.update(True)
        elif mode == 'damped_rotary_spring':
            if space.add_damped_rotary_spring():
                mode = None
                place_constraint_tool.update(True)
        elif mode == 'rotary_limit_joint':
            if space.add_rotary_limit_joint():
                mode = None
                place_constraint_tool.update(True)
        elif mode == 'ratchet_joint':
            if space.add_ratchet_joint():
                mode = None
                place_constraint_tool.update(True)
        elif mode == 'gear_joint':
            if space.add_gear_joint():
                mode = None
                place_constraint_tool.update(True)
        elif mode == 'simple_motor':
            if space.add_simple_motor():
                mode = None
                place_constraint_tool.update(True)
        elif mode == 'give_force':
            if space.give_force():
                mode = None
                utilities_tool.update(True)
        else:
            place_shape_tool.update()
            place_constraint_tool.update()
            utilities_tool.update()

        space.update()
        if mode == None:
            space.update_chosen()

        gui.show_prompt_text(show=True)

        pygame.display.flip()

        main_clock.tick_busy_loop(60)
def start_menu():
    start_button = gui.Button(screen, (823, 550), im_release='../assets/textures/gui/start_menu/start.png', im_mouse_on='../assets/textures/gui/start_menu/start_1.png', im_press='../assets/textures/gui/start_menu/start_1.png')
    about_button = gui.Button(screen, (823, 650), im_release='../assets/textures/gui/start_menu/about.png',
                              im_mouse_on='../assets/textures/gui/start_menu/about_1.png',
                              im_press='../assets/textures/gui/start_menu/about_1.png')
    background = pygame.image.load('../assets/textures/gui/start_menu/background.png')

    about_menu = gui.Menu(screen, cfg['gui']['menus']['about_software'].copy())

    show_about = False

    while True:
        screen.blit(background, (0, 0))

        global_event = pygame.event.get()
        gui.global_event = global_event.copy()

        if show_about:
            show_about = not about_menu.update()
        else:
            for event in global_event:
                if event.type == QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
                    quit()
            if start_button.update():
                break
            if about_button.update():
                show_about = True

        pygame.display.flip()

if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((1920,1080),FULLSCREEN | HWSURFACE)

    MOUSEDOUBLECLICK = USEREVENT

    cfg_string = open('../assets/cfg.json', encoding='utf_8-sig').read()  # 读取配置文件
    cfg = json.loads(cfg_string)

    space = Space()
    gui.space = space

    start_menu()
    main()#主程序