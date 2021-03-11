import pygame, json, sys
from pygame.locals import *

cfg_string = open('../assets/cfg.json', encoding='utf_8-sig').read()  # 读取配置文件
cfg = json.loads(cfg_string)

pygame.init()
screen = pygame.display.set_mode((1920,1080),FULLSCREEN | HWSURFACE)

prompt_text_size = cfg['gui']['prompt_text']['size']
prompt_text_font = pygame.font.Font(cfg['gui']['prompt_text']['font'], prompt_text_size)
prompt_text_string = None

font = pygame.font.Font(cfg['gui']['menu_assets']['font'], cfg['gui']['menu_assets']['font_size'])

global_event = []

default_adj_callback = None

class Settings:
    def __init__(self):
        self.sound_volume = 100 #音效的音量，百分之
        self.double_click_ms = 500 #判定鼠标双击的时长，当两次点击相隔时长小于此数值时判定为双击

settings = Settings()

def show_prompt_text(text = None, display = False, pos = None):#显示提示文字，event == 1表示开始显示，event == 0表示停止显示，event == 其他数表示继续显示
    global prompt_text_string
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

class Text:
    def __init__(self, surface, pos, text, size=cfg['gui']['menu_assets']['font_size'], color=cfg['gui']['menu_assets']['text_color']['text']['default'], font=cfg['gui']['menu_assets']['font'], antialias=True):
        self.font = pygame.font.Font(font, size)
        self.surface = surface
        self.pos = pos
        self.text = text
        self.antialias = antialias
        self.color = color
        self.text_surface = self.font.render(self.text, self.antialias, self.color)
    def rerender(self):
        self.text_surface = self.font.render(self.text, self.antialias, self.color)
    def display(self):
        self.surface.blit(self.text_surface, self.pos)

class Button:
    def __init__(self, surface, pos, width=None, name=None, enable=True, mouse_on_callback=None, press_callback=None, text=None, prompt_text=None,
                 im_release=cfg['gui']['menu_assets']['image']['button']['release'],
                 im_mouse_on=cfg['gui']['menu_assets']['image']['button']['mouse_on'],
                 im_press=cfg['gui']['menu_assets']['image']['button']['press'],
                 im_unenable=cfg['gui']['menu_assets']['image']['button']['unenable'],
                 sound=cfg['gui']['menu_assets']['sound']['button']):
        """
        :param pos: topleft
        :param width: 按钮的长度
        :param mouse_on_callback: 鼠标位于按钮上方时被调用的回调，此回调函数会被多次调用
        :param press_callback: 按钮被点击时被调用的回调
        :param text: 按钮上显示的字符串
        :param prompt_text: 提示文字
        :param im_release: 按钮被释放时的贴图
        :param im_mouse_on: 鼠标放在按钮上时的贴图
        :param im_press: 按钮被按下时的贴图
        :param im_unenable: 按钮被禁用时的贴图
        :param sound: 按钮被按下时的音效
        :param enable: 是否激活按钮
        """
        if width == None:
            self.im_release = pygame.image.load(im_release).convert_alpha()
            self.im_mouse_on = pygame.image.load(im_mouse_on).convert_alpha()
            self.im_press = pygame.image.load(im_press).convert_alpha()
            self.im_unenable = pygame.image.load(im_unenable).convert_alpha()
        else:
            self.im_release = pygame.image.load(im_release).convert_alpha()
            image_width = self.im_release.get_width()
            image_height = self.im_release.get_height()
            self.im_release = pygame.transform.chop(self.im_release, (5, image_height, image_width - width, image_height))
            self.im_mouse_on = pygame.image.load(im_mouse_on).convert_alpha()
            self.im_mouse_on = pygame.transform.chop(self.im_mouse_on, (5, image_height, image_width - width, image_height))
            self.im_press = pygame.image.load(im_press).convert_alpha()
            self.im_press = pygame.transform.chop(self.im_press, (5, image_height, image_width - width, image_height))
            self.im_unenable = pygame.image.load(im_unenable).convert_alpha()
            self.im_unenable = pygame.transform.chop(self.im_unenable, (5, image_height, image_width - width, image_height))

        self.rect = self.im_release.get_rect(topleft=pos)

        self.sound = pygame.mixer.Sound(sound)

        self.enable = enable
        self.text = text
        self.prompt_text = prompt_text

        self.name = name

        self.mouse_on_callback = mouse_on_callback
        self.press_callback = press_callback

        self.surface = surface

    def update(self, mouse_pos=None):
        """
        更新并显示按钮
        """
        if mouse_pos == None:
            mouse_pos = pygame.mouse.get_pos()
        if self.enable:
            for event in global_event:
                if event.type == MOUSEBUTTONUP and event.button == 1 and self.rect.collidepoint(mouse_pos) and self.im_press.get_at((mouse_pos[0] - self.rect.topleft[0], mouse_pos[1] - self.rect.topleft[1]))[3] != 0:
                    self.play_sound()
                    if self.press_callback != None:
                        self.press_callback(self.name)
                    self.display(self.im_release, cfg['gui']['menu_assets']['text_color']['button']['mouse_on'])
                    return True
            if self.rect.collidepoint(mouse_pos) and self.im_release.get_at((mouse_pos[0] - self.rect.topleft[0], mouse_pos[1] - self.rect.topleft[1]))[3] != 0:
                if pygame.mouse.get_pressed()[0]:
                    self.display(self.im_press, cfg['gui']['menu_assets']['text_color']['button']['mouse_on'])
                else:
                    self.display(self.im_mouse_on, cfg['gui']['menu_assets']['text_color']['button']['mouse_on'])
                    if self.mouse_on_callback != None:
                        self.mouse_on_callback(self.name)

                if self.prompt_text != None:
                    show_prompt_text(self.prompt_text)
                return
            self.display(self.im_release, cfg['gui']['menu_assets']['text_color']['button']['enable'])
        else:
            self.display(self.im_unenable, cfg['gui']['menu_assets']['text_color']['button']['unenable'])

    def display(self, image, text_color):
        self.surface.blit(image, self.rect)
        if self.text != None:
            sur = font.render(self.text, True, text_color)
            rect = sur.get_rect()
            rect.center = self.rect.center
            self.surface.blit(sur, rect)

    def play_sound(self):
        self.sound.set_volume(settings.sound_volume / 100)
        self.sound.play()

class Scale:
    def __init__(self, surface, pos, points, width, enable=True, direction='x', start_point=0, name=None, cross=False, parts=None, mouse_on_callback=None, adj_callback=None, text=None, prompt_text=None,
                 text_color=cfg['gui']['menu_assets']['text_color']['scale']['default'],
                 im_slider=cfg['gui']['menu_assets']['image']['scale']['slider'],
                 im_slider_mouse_on=cfg['gui']['menu_assets']['image']['scale']['slider_mouse_on'],
                 im_slider_unenable=cfg['gui']['menu_assets']['image']['scale']['slider_unenable'],
                 im_track=cfg['gui']['menu_assets']['image']['scale']['track'],
                 im_track_mouse_on=cfg['gui']['menu_assets']['image']['scale']['track_mouse_on'],
                 im_track_unenable=cfg['gui']['menu_assets']['image']['scale']['track_unenable'],
                 sound=cfg['gui']['menu_assets']['sound']['scale']):
        """
        :param surface: 将渲染至此平面
        :param pos: topleft
        :param points: 滑动到每一个位置时的字符串，如果非字符串，会被自动转换，可以用range()生成
        :param start_point: 滑块的初始位置
        :param width: 轨道的长度
        :param enable: 是否激活滑块
        :param direction: 方向，'x'：横向，'y'：竖向
        :param cross: 是否允许滑块穿越循环（用来设置较大的数值）
        :param parts: 滑块滑动一次有多少点
        :param mouse_on_callback: 鼠标在轨道上时调用的回调
        :param adj_callback: 改变滑块位置时调用的回调
        :param text: 轨道上显示的文字
        :param prompt_text: 提示文字
        :param im_slider: 滑块的贴图
        :param im_slider_mouse_on: 鼠标在滑块上时滑块的贴图
        :param im_slider_unenable: 未激活时滑块的贴图
        :param im_track: 轨道的贴图
        :param im_track_mouse_on: 鼠标在轨道上时轨道的贴图
        :param im_track_unenable: 未激活时轨道的贴图
        :param sound: 拖动完毕时播放的音效
        :param text_color: 没有触发时字体的颜色
        """
        self.points = []
        for p in points:
            self.points.append(str(p))
            self.pt = start_point
        self.enable = enable
        self.mouse_on_callback = mouse_on_callback
        if adj_callback == None:
            self.adj_callback = default_adj_callback
        else:
            self.adj_callback = adj_callback
        self.text = text
        self.prompt_text = prompt_text
        self.direction = direction
        self.cross = cross
        self.parts = parts
        if parts == None:
            self.parts = len(self.points)
        self.im_slider = pygame.image.load(im_slider).convert()
        self.im_slider_mouse_on = pygame.image.load(im_slider_mouse_on).convert()
        self.im_slider_unenable = pygame.image.load(im_slider_unenable).convert()
        self.im_track = pygame.image.load(im_track).convert()
        image_width = self.im_track.get_width()
        image_height = self.im_track.get_height()
        self.im_track = pygame.transform.chop(self.im_track, (5, image_height, image_width - width, image_height))
        self.im_track_mouse_on = pygame.image.load(im_track_mouse_on).convert()
        self.im_track_mouse_on = pygame.transform.chop(self.im_track_mouse_on, (5, image_height, image_width - width, image_height))
        self.im_track_unenable = pygame.image.load(im_track_unenable).convert()
        self.im_track_unenable = pygame.transform.chop(self.im_track_unenable, (5, image_height, image_width - width, image_height))
        if direction == 'y':
            self.im_slider = pygame.transform.rotate(self.im_slider, 90)
            self.im_slider_mouse_on = pygame.transform.rotate(self.im_slider_mouse_on, 90)
            self.im_slider_unenable = pygame.transform.rotate(self.im_slider_unenable, 90)
            self.im_track = pygame.transform.rotate(self.im_track, 90)
            self.im_track_mouse_on = pygame.transform.rotate(self.im_track_mouse_on, 90)
            self.im_track_unenable = pygame.transform.rotate(self.im_track_unenable, 90)
        self.track_rect = self.im_track.get_rect(topleft=pos)
        self.slider_rect = self.im_slider.get_rect(topleft=pos)
        self.sound = pygame.mixer.Sound(sound)
        if self.direction == 'x':
            self.part_width = (self.track_rect.width - self.slider_rect.width) / (self.parts - 1)
        else:
            self.part_width = (self.track_rect.height - self.slider_rect.height) / (self.parts - 1)
        self.mode = 0
        self.move_distance = 0
        self.text_color = text_color

        self.name = name

        self.surface = surface
    def update(self, mouse_button=None):
        if self.enable:
            if mouse_button == None:
                mouse_button = pygame.mouse.get_pos()
            for event in global_event:
                call = False
                if event.type == MOUSEBUTTONDOWN and self.track_rect.collidepoint(mouse_button):
                    if self.mode == 0:
                        self.mode = 1
                        p = mouse_button
                        if self.direction == 'x':
                            p = p[0]
                            p -= self.track_rect.left
                        else:
                            p = p[1]
                            p -= self.track_rect.top
                        ps = False
                        if self.cross == False:
                            if self.pt != int(p / self.part_width):
                                self.pt = int(p / self.part_width)
                                ps = True
                        else:
                            if int(p / self.part_width) - self.pt % self.parts != 0:
                                self.pt += int(p / self.part_width) - self.pt % self.parts
                                ps = True
                        if self.pt < 0:
                            self.pt = 0
                        elif self.pt >= len(self.points):
                            self.pt = len(self.points) - 1
                        elif ps:
                            self.play_sound()
                            call = True
                if event.type == MOUSEBUTTONUP:
                    if self.mode == 1:
                        self.mode = 0
                if event.type == MOUSEMOTION:
                    if self.mode == 1:
                        call = False
                        if self.direction == 'x':
                            self.move_distance += event.rel[0]
                        else:
                            self.move_distance += event.rel[1]
                        if self.move_distance >= self.part_width:
                            self.pt += int(self.move_distance / self.part_width)
                            self.move_distance = 0
                            call = True
                            if self.pt >= len(self.points):
                                self.pt = len(self.points) - 1
                            else:
                                self.play_sound()
                        elif -self.move_distance >= self.part_width:
                            self.pt -= int(-self.move_distance / self.part_width)
                            self.move_distance = 0
                            call = True
                            if self.pt < 0:
                                self.pt = 0
                            else:
                                self.play_sound()
                if self.adj_callback != None and call:
                    self.adj_callback(self.name, self.pt, self.points[self.pt])
                """
                if self.pt < 0:
                    self.pt = 0
                elif self.pt >= len(self.points):
                    self.pt = len(self.points) - 1
                """
        if self.enable == False:
            self.display(self.im_slider_unenable, self.im_track_unenable, cfg['gui']['menu_assets']['text_color']['scale']['unenable'])
        elif self.mode == 1:
            self.display(self.im_slider_mouse_on, self.im_track_unenable, cfg['gui']['menu_assets']['text_color']['scale']['mouse_on'])
        elif self.track_rect.collidepoint(mouse_button):
            self.display(self.im_slider_mouse_on, self.im_track_mouse_on, cfg['gui']['menu_assets']['text_color']['scale']['mouse_on'])
            if self.mouse_on_callback != None:
                self.mouse_on_callback(self.name, self.pt, self.points[self.pt])
        else:
            self.display(self.im_slider, self.im_track, self.text_color)
    def display(self, s_image, t_image, text_color):
        self.surface.blit(t_image, self.track_rect)

        if self.cross:
            pt = self.pt % self.parts
        else:
            pt = self.pt

        if self.direction == 'x':
            s_x = int(self.part_width * pt + self.track_rect.left)
            self.surface.blit(s_image, (s_x, self.slider_rect.top))
        elif self.direction == 'y':
            s_y = int(self.part_width * pt + self.track_rect.top)
            self.surface.blit(s_image, (self.slider_rect.left, s_y))

        if self.text != None:
            sur = font.render(self.text + ':' + self.points[self.pt], True, text_color)
        else:
            sur = font.render(self.points[self.pt], True, text_color)
        rect = sur.get_rect()
        rect.center = self.track_rect.center
        self.surface.blit(sur, rect)
    def play_sound(self):
        self.sound.set_volume(settings.sound_volume / 100)
        self.sound.play()

class Toolbar:#工具栏
    def __init__(self, surface, bar_image, selected_image, topleft, check_topleft_list, tool_list, prompt_text, name, adj_callback=None,
                 sound=cfg['gui']['menu_assets']['sound']['toolbar']):
        """
        :param bar_image: 工具栏的贴图
        :param selected_image: 被选中的选项上显示的贴图
        :param topleft: 位置
        :param check_topleft_list: 每一个选项的左上角位置
        :param tool_list: 每个选项的名字
        :param prompt_text: 每个选项的提示文字
        :param adj_callback: 改变选中的项时调用的回调
        """
        self.bar_image = pygame.image.load(bar_image).convert_alpha()
        self.selected_image = pygame.image.load(selected_image).convert_alpha()

        self.bar_rect = self.bar_image.get_rect(topleft=topleft)

        self.rect_list = []
        for pos in check_topleft_list:
            self.rect_list.append(self.selected_image.get_rect(topleft=(pos[0] + self.bar_rect.topleft[0], pos[1] + self.bar_rect.topleft[1])))

        self.tool_list = tool_list
        self.prompt_text = prompt_text

        self.selected = None

        self.surface = surface

        self.adj_callback = adj_callback

        self.sound = pygame.mixer.Sound(sound)

        self.name = name
    def update(self,mode=False, mouse_button=None):#更新工具栏
        if mode:#当执行完用户选择的内容后，重置选项
            self.selected = None
        else:
            if mouse_button == None:
                mouse_button = pygame.mouse.get_pos()
            m_pos = mouse_button
            m_button = pygame.mouse.get_pressed()[0]

            for i in range(len(self.rect_list)):#判断用户选择了那个选项
                rect = self.rect_list[i]
                if rect.collidepoint(m_pos):
                    if m_button:
                        if self.selected != i:
                            self.selected = i
                            self.play_sound()
                            self.adj_callback(self.name, i, self.tool_list[i])
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
        self.surface.blit(self.bar_image, self.bar_rect)

        if self.selected != None:
            self.surface.blit(self.selected_image, self.rect_list[self.selected])
    def play_sound(self):
        self.sound.set_volume(settings.sound_volume / 100)
        self.sound.play()

class Menu:
    def __init__(self, surface, menu_cfg, close_callback=None):
        self.surface = surface.subsurface(menu_cfg['rect'])

        self.pos = menu_cfg['rect'][:2]

        self.cfg = menu_cfg
        if menu_cfg.get('background') != None:
            background = menu_cfg['background']
        else:
            background = cfg['gui']['menu_assets']['image']['menu']['background']
        self.im_bg = pygame.image.load(background).convert()
        self.im_bg = pygame.transform.chop(self.im_bg, (5, 0, self.im_bg.get_width() - self.surface.get_width(), 0))
        self.im_bg = pygame.transform.chop(self.im_bg, (0, 5, 0, self.im_bg.get_height() - self.surface.get_height()))
        if menu_cfg.get('alpha') != None:
            self.alpha = menu_cfg['alpha']
        else:
            self.alpha = 150
        self.im_bg.set_alpha(self.alpha)
        self.old_bg = self.im_bg.copy()

        if menu_cfg.get('close_button') != None:
            p = (self.im_bg.get_width() - pygame.image.load(menu_cfg['close_button']['im_release']).get_width(), 0)
            self.close_button = Button(**menu_cfg['close_button'], surface=self.im_bg, press_callback=self.close, pos=p)
        else:
            p = (self.im_bg.get_width() - pygame.image.load(cfg['gui']['menu_assets']['button']['menu']['close']['im_release']).get_width(), 0)
            self.close_button = Button(**cfg['gui']['menu_assets']['button']['menu']['close'], surface=self.im_bg, press_callback=self.close, pos=p)

        self.text_list = []
        if menu_cfg.get('texts') != None:
            for b_cfg in menu_cfg['texts']:
                b_cfg['surface'] = self.im_bg
                self.text_list.append(Text(**b_cfg))

        self.button_list = []
        if menu_cfg.get('buttons') != None:
            for b_cfg in menu_cfg['buttons']:
                """
                if type(b_cfg.get('mouse_on_callback')) is str:
                    b_cfg['mouse_on_callback'] = eval(b_cfg['mouse_on_callback'])
                if type(b_cfg.get('press_callback')) is str:
                    b_cfg['press_callback'] = eval(b_cfg['press_callback'])
                """
                for e in b_cfg:
                    b_cfg[e] = eval(str(b_cfg[e]))
                b_cfg['surface'] = self.im_bg

                self.button_list.append(Button(**b_cfg))

        self.scale_list = []
        if menu_cfg.get('scales') != None:
            for s_cfg in menu_cfg['scales']:
                """
                if type(s_cfg.get('mouse_on_callback')) is str:
                    s_cfg['mouse_on_callback'] = eval(s_cfg['mouse_on_callback'])
                if type(s_cfg.get('adj_callback')) is str:
                    s_cfg['adj_callback'] = eval(s_cfg['adj_callback'])
                """
                if type(s_cfg['points']) is str:
                    s_cfg['points'] = eval(s_cfg['points'])

                s_cfg['surface'] = self.im_bg

                self.scale_list.append(Scale(**s_cfg))

        self.bar_list = []
        if menu_cfg.get('bars') != None:
            for b_cfg in menu_cfg['bars']:
                """
                if type(b_cfg.get('adj_callback')) is str:
                    b_cfg['adj_callback'] = eval(b_cfg['adj_callback'])
                """
                for e in b_cfg:
                    b_cfg[e] = eval(str(b_cfg[e]))
                b_cfg['surface'] = self.im_bg

                self.bar_list.append(Toolbar(**b_cfg))

        self.close_callback = close_callback

    def offset_mouse_pos(self):
        return pygame.mouse.get_pos()[0] - self.pos[0], pygame.mouse.get_pos()[1] - self.pos[1]

    def update(self):
        if self.close_button.update(self.offset_mouse_pos()):
            return True

        for t in self.text_list:
            t.display()
        for b in self.button_list:
            b.update(self.offset_mouse_pos())
        for s in self.scale_list:
            s.update(self.offset_mouse_pos())
        for b in self.bar_list:
            b.update(self.offset_mouse_pos())

        self.display()

        return False

    def display(self):
        self.surface.blit(self.im_bg, (0, 0))
        self.im_bg.blit(self.old_bg, (0, 0))

    def close(self, name):
        if self.close_callback != None:
            self.close_callback()
        print('close')

def adj(a, b):
    print(a, b)

if __name__ == '__main__':
    screen = pygame.display.set_mode((1000,400))
    clock = pygame.time.Clock()

    l = list(range(20))
    l[0] = '小'
    l[19] = '大'

    #s = Scale(screen, (50,50), l, 0, 300, True, text='abc')
    m = Menu(screen.subsurface((100, 100, 100, 100)), {})
    b = Button(screen, (200, 300), 100)

    while True:
        screen.fill((255, 0, 255))

        global_event = pygame.event.get()
        for event in global_event:
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        #s.update()
        m.update()
        b.update()

        show_prompt_text(display=True)

        pygame.display.flip()

        clock.tick(60)