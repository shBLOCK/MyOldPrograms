import pygame, math, json, sys
from pygame.locals import *

import pymunk
import pymunk.pygame_util
from pymunk import Vec2d

place_mode = None#决定正在放置什么刚体

prompt_text_size = 0
prompt_text_font = None
prompt_text_string = None

global_event = []#pygame产生的event

cfg_string = open('../assets/cfg.json', encoding='utf_8-sig').read()#读取配置文件
cfg = json.loads(cfg_string)

def quit():#退出程序
    pygame.quit()
    sys.exit()

def inverted_color(color):#反色
    output_color = []
    for i in color:
        output_color.append(255 - i)
    return tuple(output_color)

def show_prompt_text(text = None, display = False, pos = None):#显示提示文字，event == 1表示开始显示，event == 0表示停止显示，event == 其他数表示继续显示
    global  prompt_text_string
    if display and prompt_text_string != None:
        if pos == None:
            pos = pygame.mouse.get_pos()
        rect = pygame.rect.Rect((0,0), prompt_text_font.size(prompt_text_string))
        rect.bottomleft = pos
        rect2 = rect.copy()
        rect2.top -= 3
        rect2.left -= 3
        rect2.width += 4
        rect2.height += 4
        sur = pygame.Surface(rect2.size)
        sur.fill((0, 0, 0))
        sur.blit(prompt_text_font.render(prompt_text_string, True, (0, 0, 0), (255, 255, 255)), (2,2))
        screen.blit(sur, rect2.topleft)
        prompt_text_string = None
    else:
        if text != None:
            prompt_text_string = text

class Toolbar:#工具栏
    def __init__(self, bar_image, selected_image, topleft, check_topleft_list, tool_list, prompt_text):
        self.bar_image = pygame.image.load(bar_image)
        self.selected_image = pygame.image.load(selected_image)

        self.bar_rect = self.bar_image.get_rect(topleft=topleft)

        self.rect_list = []
        for pos in check_topleft_list:
            self.rect_list.append(self.selected_image.get_rect(topleft=(pos[0] + self.bar_rect.topleft[0], pos[1] + self.bar_rect.topleft[1])))

        self.tool_list = tool_list
        self.prompt_text = prompt_text

        self.selected = None

    def update(self,mode = False):#更新工具栏
        if mode:#当执行完用户选择的内容后，重置选项
            self.selected = None
        else:
            m_pos = pygame.mouse.get_pos()
            m_button = pygame.mouse.get_pressed()[0]

            for i in range(len(self.rect_list)):#判断用户选择了那个选项
                rect = self.rect_list[i]
                if rect.collidepoint(m_pos):
                    if m_button:
                        self.selected = i
                        return self.tool_list[i]
                    else:
                        show_prompt_text(self.prompt_text[i])

            """
            if m_button:#如果鼠标左键被按下，判断用户选择了那个选项
                for i in range(len(self.rect_list)):
                    rect = self.rect_list[i]
                    if rect.collidepoint(m_pos):
                        self.selected = i
                        self.display()
                        return self.tool_list[i]
            else:
                self.display()
            """

            return False

    def display(self):#绘制工具栏
        screen.blit(self.bar_image, self.bar_rect)

        if self.selected != None:
            screen.blit(self.selected_image, self.rect_list[self.selected])

class Space:#最重要的类，虚拟物理环境
    def __init__(self):
        self.space = pymunk.Space()
        self.space.gravity = (0,-1000)

        self.run_simulation = False#决定是否更新虚拟环境（是否进行仿真）

        self.shape_internal_number = 0#下一个被创建的形状的内部编码（用来记录被选中的形状等）

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

        self.pc_vertices = []#添加平滑的多边形时用来记录每个顶点的坐标

        self.pp_vertices = []#添加普通的多边形时用来记录每个顶点的坐标

        self.default_shape_color = (0,0,255)#默认的形状颜色

        self.do = self.do = pymunk.pygame_util.DrawOptions(screen)

    def add_circle_draw(self,center,edge,radius):#添加圆形刚体时用来实时绘制提示形状
        pygame.draw.circle(screen,(0,0,255),center,int(radius),0)
        pygame.draw.aaline(screen,(0,255,0),center,edge,1)

    def add_circle(self, static):#添加圆形刚体
        pygame.mouse.set_cursor(*pygame.cursors.broken_x)

        for event in global_event:#遍历事件列表以确定用户的操作进度
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 3:
                    if self.add_mode == 0:
                        pygame.mouse.set_cursor(*pygame.cursors.arrow)
                        return True
                    self.add_mode = 0
                if event.button == 1:
                    self.add_mode += 1

        if self.add_mode == 1:#确定圆心
            self.c_center = pygame.mouse.get_pos()
            self.add_mode += 1
        elif self.add_mode == 2:#确定半径
            self.c_edge = pygame.mouse.get_pos()
            self.c_radius = pygame.math.Vector2(self.c_center).distance_to(self.c_edge)
            self.add_circle_draw(self.c_center,self.c_edge,self.c_radius)
        elif self.add_mode == 3:#创建刚体
            self.add_mode = 0

            if static:
                pos = pymunk.pygame_util.to_pygame(self.c_center, screen)
                body = self.space.static_body
                body.position = pos
                shape = pymunk.Circle(body, self.c_radius, (0, 0))
                shape.elasticity = 0.5
                shape.friction = 0.5
                setattr(shape,'num',self.shape_internal_number)
                self.shape_internal_number += 1
                self.space.add(shape)
                body.angle += pygame.math.Vector2((self.c_edge[0] - self.c_center[0], self.c_edge[1] - self.c_center[1])).angle_to((1, 0)) * math.pi / 180
                self.space.reindex_shapes_for_body(body)
            else:
                pos = pymunk.pygame_util.to_pygame(self.c_center, screen)
                inertia = pymunk.moment_for_circle(10, 0, self.c_radius, (0, 0))
                body = pymunk.Body(10, inertia)
                body.position = pos
                shape = pymunk.Circle(body, self.c_radius, (0, 0))
                shape.elasticity = 0.5
                shape.friction = 0.5
                setattr(shape, 'num', self.shape_internal_number)
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
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 3:
                    if self.add_mode == 0:
                        pygame.mouse.set_cursor(*pygame.cursors.arrow)
                        return True
                    self.add_mode = 0
                if event.button == 1:
                    self.add_mode += 1

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

            if static:
                pos = pymunk.pygame_util.from_pygame(self.b_rect.center, screen)
                body = self.space.static_body
                body.position = pos
                shape = pymunk.Poly.create_box(body, self.b_offset, 0)
                shape.elasticity = 0.5
                shape.friction = 0.5
                setattr(shape, 'num', self.shape_internal_number)
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
                self.shape_internal_number += 1
                self.space.add(body, shape)

        return False

    def add_segment_draw(self,a,b,r):#添加线段刚体时用来实时绘制提示形状
        rr = int(r) * 2
        if rr == 0:
            rr += 1
        pygame.draw.line(screen,(0,0,255),a,b,rr)

    def add_segment(self, static):#添加线段刚体
        pygame.mouse.set_cursor(*pygame.cursors.broken_x)

        for event in global_event:#遍历事件列表以确定用户的操作进度
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
                    if self.s_radius > 1:
                        self.s_radius -= 1

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
                self.shape_internal_number += 1
                self.space.add(body, shape)

        return False

    def add_poly_curve_draw(self, vertices):#添加平滑多边形刚体时用来实时绘制提示形状
        if len(vertices) <= 2:
            return
        pygame.draw.polygon(screen, (0,0,255), vertices, 0)

    def add_poly_curve(self, static):#添加平滑的多边形
        pygame.mouse.set_cursor(*pygame.cursors.broken_x)

        append = False
        for event in global_event:#遍历事件列表以确定用户的操作进度
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 3:
                    if self.add_mode == 0:
                        pygame.mouse.set_cursor(*pygame.cursors.arrow)
                        self.pc_vertices = []
                        return True
                    self.add_mode = 0
                    self.pc_vertices = []
                if event.button == 1:
                    self.add_mode += 1
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    if self.add_mode == 1:
                        self.add_mode = 2
            if event.type == MOUSEMOTION:#如果鼠标移动，便添加顶点
                append = True

        self.add_poly_curve_draw(self.pc_vertices)

        if self.add_mode == 1 and append:#添加顶点
            self.pc_vertices.append(pygame.mouse.get_pos())
        elif self.add_mode == 2:#创建刚体
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
                setattr(shape, 'num', self.shape_internal_number)
                self.shape_internal_number += 1
                self.space.add(shape)
            else:
                inertia = pymunk.moment_for_poly(10, self.pc_vertices,(0,0), 0)
                body = pymunk.Body(10, inertia)
                shape = pymunk.Poly(body, self.pc_vertices, None, 0)
                shape.elasticity = 0.5
                shape.friction = 0.5
                setattr(shape, 'num', self.shape_internal_number)
                self.shape_internal_number += 1
                self.space.add(body, shape)

            self.pc_vertices = []

        return False

    def add_poly_point_draw(self, vertices_in):#添加普通多边形刚体时用来实时绘制提示形状
        vertices = vertices_in.copy()
        if len(vertices) == 0:
            return
        elif len(vertices) == 1:
            vertices.append(pygame.mouse.get_pos())
            pygame.draw.aaline(screen, (0, 0, 255), vertices[0], vertices[1], 1)
        else:
            vertices.append(pygame.mouse.get_pos())
            pygame.draw.polygon(screen, (0, 0, 255), vertices, 0)

    def add_poly_point(self, static):#添加普通多边形刚体
        pygame.mouse.set_cursor(*pygame.cursors.broken_x)

        for event in global_event:#遍历事件列表以确定用户的操作进度
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 3:
                    if self.add_mode == 0:
                        pygame.mouse.set_cursor(*pygame.cursors.arrow)
                        self.pp_vertices = []
                        return True
                    self.add_mode = 0
                    self.pp_vertices = []
                if event.button == 1:
                    if self.add_mode == 0:
                        self.add_mode = 1
                    self.pp_vertices.append(pygame.mouse.get_pos())#添加顶点
                if event.button == 2:
                    if self.add_mode == 1:
                        self.add_mode = 2

        self.add_poly_point_draw(self.pp_vertices)

        if self.add_mode == 2:#创建刚体
            if len(self.pp_vertices) <= 2:
                self.add_mode = 1
                return False

            self.add_mode = 0

            for i in range(len(self.pp_vertices)):
                self.pp_vertices[i] = pymunk.pygame_util.from_pygame(self.pp_vertices[i], screen)

            if static:
                body = self.space.static_body
                shape = pymunk.Poly(body, self.pp_vertices, None, 0)
                shape.elasticity = 0.5
                shape.friction = 0.5
                setattr(shape, 'num', self.shape_internal_number)
                self.shape_internal_number += 1
                self.space.add(shape)
            else:
                inertia = pymunk.moment_for_poly(10, self.pp_vertices, (0, 0), 0)
                body = pymunk.Body(10, inertia)
                shape = pymunk.Poly(body, self.pp_vertices, None, 0)
                shape.elasticity = 0.5
                shape.friction = 0.5
                setattr(shape, 'num', self.shape_internal_number)
                self.shape_internal_number += 1
                self.space.add(body, shape)

            self.pp_vertices = []

        return False

    def draw_shape(self,shape_list):#渲染刚体
        for order in range(3):#order == 0：未选中，order == 1：提示，order == 2：已选中
            for shape in shape_list:
                if hasattr(shape, 'color'):
                    color = shape.color
                else:
                    color = self.default_shape_color

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
                    print(a, b)
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
                        self.chosen_rect = pygame.Rect(*self.chosen_start,0,0)
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
            #print(bb)
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

    def update(self):#更新并绘制刚体
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
                self.space._remove_shape(shape)

        self.draw_shape(self.space.shapes)
        self.space.debug_draw(self.do)

def main():
    global global_event, place_mode, prompt_text_size

    space = Space()
    place_tool = Toolbar(cfg['gui']['place_toolbar']['image']['bar'],
                         cfg['gui']['place_toolbar']['image']['selected'],
                         cfg['gui']['place_toolbar']['bar_pos'],
                         cfg['gui']['place_toolbar']['check_topleft_list'],
                         cfg['gui']['place_toolbar']['tools'],
                         cfg['gui']['place_toolbar']['prompt_text'])
    main_clock = pygame.time.Clock()

    while True:
        screen.fill((255, 255, 255))

        global_event = pygame.event.get()

        for event in global_event:
            if event.type == QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
                quit()
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    space.run_simulation = not space.run_simulation

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

            space.update_chosen()

        space.update()

        show_prompt_text(display=True)

        pygame.display.flip()

        main_clock.tick_busy_loop(60)

if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((1920,1080),FULLSCREEN | HWSURFACE)
    prompt_text_size = cfg['gui']['prompt_text']['size']
    prompt_text_font = pygame.font.Font(cfg['gui']['prompt_text']['font'], prompt_text_size)

    main()#主程序