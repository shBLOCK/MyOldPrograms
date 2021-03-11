import pygame,json,sys
from pygame.locals import *
import album

class Button:
    def __init__(self,image,image_on,coordinate,screen,sound,text = None,volume = 1):
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
            return True
        return False

    def check_click_buttonup(self,mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.play_sound()
            return True
        return False

    def display(self,surface):
        self.screen.blit(surface,self.rect)

def main():
    pygame.init()
    pygame.mixer.init()

    screen = pygame.display.set_mode((1440,960),RESIZABLE)
    pygame.display.set_caption('六.1班班级纪念册')

    main_cfg = json.loads(open('../assets/cfg/interface.json',encoding='utf-8-sig').read())
    print(main_cfg)

    student_list = main_cfg['student']['student_list']
    student_button = []
    one_cfg_list = []

    for x in range(len(student_list)):
        student_button.append([])
        one_cfg_list.append([])
        for y in range(len(student_list[x])):
            if student_list[x][y] != None:
                one_cfg = json.loads(open(main_cfg['student']['album_file'] % student_list[x][y],encoding='utf-8-sig').read())
                print(one_cfg)
                student_button[x].append(Button(one_cfg['button']['image'],one_cfg['button']['image_on'],one_cfg['button']['coordinate'],screen,one_cfg['button']['sound']))
                one_cfg_list[x].append(one_cfg)
            else:
                student_button[x].append(None)
                one_cfg_list[x].append(None)

    while True:
        screen.fill((255,255,255))
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == VIDEORESIZE:
                screen = pygame.display.set_mode(event.size,RESIZABLE)
                for b0 in student_button:
                    for b1 in b0:
                        if b1 != None:
                            b1.adj_pos(screen.get_rect())
            if event.type == KEYUP:
                if event.key == K_F3:
                    print('')


        m_pos = pygame.mouse.get_pos()

        for b0 in range(len(student_button)):
            for b1 in range(len(student_button[b0])):
                ls_b = student_button[b0][b1]
                if ls_b != None:
                    ls_b.check_mouse_on(m_pos)
                    if ls_b.check_click(m_pos):
                        print(student_list[b0][b1])
                        now_stu = album.Album(one_cfg_list[b0][b1]['file'],'main')
                        r = now_stu.main()
                        while True:
                            del now_stu
                            if r != None:
                                now_stu = album.Album(one_cfg_list[b0][b1]['file'],r)
                                r = now_stu.main()
                            else:
                                break

        pygame.display.update()

if __name__ == '__main__':
    main()