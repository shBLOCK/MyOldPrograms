import pygame,json,sys
from pygame.locals import *

class Button:
    def __init__(self,image,image_on,coordinate,screen,sound,execute,text = None,volume = 1):
        self.screen = screen
        self.image = pygame.image.load(image).convert_alpha()
        self.image_on = None
        if image_on != None:
            self.image_on = pygame.image.load(image_on).convert_alpha()
        self.rect = self.image.get_rect()
        self.sound = pygame.mixer.Sound(sound)
        self.sound.set_volume(volume)
        self.text = text
        self.coordinate = coordinate
        self.mouse_on = False
        self.execute = execute

    def play_sound(self):
        self.sound.play()

    def adj_pos(self,screen_rect):
        self.rect.center = int(screen_rect.width * self.coordinate[0] + screen_rect.left),int(screen_rect.height * self.coordinate[1] + screen_rect.top)
        #self.rect.center = int(screen_size[0] * self.coordinate[0]), int(screen_size[1] * self.coordinate[1])

    def mouse_on_effect(self):
        if self.mouse_on != None:
            self.display(self.image_on)
        else:
            self.display(self.image)

    def check_mouse_on(self,mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.mouse_on_effect()
            return True
        self.display(self.image)
        return False

    def check_click(self,mouse_pos):
        if self.rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
            self.play_sound()
            return self.execute
        return False

    def check_click_buttonup(self,mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.play_sound()
            return True
        return False

    def display(self,surface):
        self.screen.blit(surface,self.rect)

class Album:
    def __init__(self,file,read_part):
        self.cfg = json.loads(open(file,encoding = 'utf-8-sig').read())
        self.cfg = self.cfg[read_part]
        self.screen = pygame.display.set_mode(self.cfg['window_size'])
        self.image_list = []
        lsl = []
        for a in self.cfg['images']:
            b = a.copy()
            b['image'] = pygame.image.load(b['image']).convert_alpha()
            lsl.append(b)
        self.image_list = lsl

        self.button_list = []
        for a in self.cfg['buttons']:
            lsb = Button(a['image'],a['image_on'],a['coordinate'],self.screen,a['sound'],a['execute'])
            lsb.adj_pos(self.screen.get_rect())
            self.button_list.append(lsb)

        self.text_image_list = []
        for a in self.cfg['texts']:
            lsf = pygame.font.Font(a['font'],a['size'])
            self.text_image_list.append({
                'image': lsf.render(a['text'], False, a['color'], a['bg_color']),
                'pos':a['pos']
            })

    def update(self):
        for im in self.image_list:
            self.screen.blit(im['image'],im['pos'])

        mp = pygame.mouse.get_pos()
        for b in self.button_list:
            b.check_mouse_on(mp)

        for t in self.text_image_list:
            self.screen.blit(t['image'],t['pos'])

    def main(self):
        while True:
            self.screen.fill((255,255,255))
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYUP:
                    if event.key == K_ESCAPE:
                        return None

            self.update()

            mp = pygame.mouse.get_pos()
            for b in self.button_list:
                click_return = b.check_click(mp)
                if click_return:
                    print(click_return)
                    parameter = click_return[1]
                    exe = click_return[0]
                    if exe == 'quit':
                        return None
                    if exe == 'jump':
                        return parameter
                    else:
                        print('execute run error!')

            pygame.display.update()