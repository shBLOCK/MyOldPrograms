import pygame,sys
from pygame.locals import *

WHITE = (255,255,255)
BLACK = (0,0,0)

'''
CENTER = 'center'
TOP = 'top'
BOTTOM = 'bottom'
LEFT = 'left'
RIGHT = 'right'
TOPLEFT = 'topleft'
BOTTOMLIFT = 'bottomleft'
TOPRIGHT = 'topright'
BOTTOMRIGHT = 'bottomright'
'''

class Aide_rect:
    def __init__(self,pos,size,image = None):
        self.rect = pygame.rect.Rect((0,0),size)
        self.rect.center = pos
        self.screen = pygame.display.get_surface()

        if image != None:
            self.surface = pygame.image.load(image).convert_alpha()
            if self.surface.get_rect().size != self.rect.size:
                self.surface = pygame.transform.scale(self.surface,self.rect.size)
        else:
            self.surface = False

    def check_drag(self,motion):
        retValue = 0
        mpos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mpos):
            self.move(motion)
            retValue = 1
            print(motion)
        return retValue

    def move(self,motion):
        self.rect.move_ip(motion)

    def draw(self):
        if self.surface:
            self.screen.blit(self.surface,self.rect)
        else:
            pygame.draw.rect(self.screen,WHITE,self.rect,0)
            pygame.draw.rect(self.screen,BLACK,self.rect,2)

class Image:
    def __init__(self,file):
        self.screen = pygame.display.get_surface()
        self.surface = pygame.image.load(file).convert_alpha()
        self.surface_old = self.surface.copy()
        self.rect = self.surface.get_rect()
        self.rect.center = self.screen.get_rect().center
        '''
        self.aide_rects = {
            CENTER:Aide_rect(self.rect.center,(30,30),'../assets/gui/Aide_rect_center.png'),
            TOP:Aide_rect((self.rect.centerx,self.rect.top),(10,10)),
            BOTTOM:Aide_rect((self.rect.centerx,self.rect.bottom),(10,10))
        }
        '''
        #self.aide_rect_center = Aide_rect(self.rect.center,(30,30),'../assets/gui/Aide_rect_center.png')
        self.aide_rect_bottomright = Aide_rect(self.rect.bottomright,(15,15))

    def update_rect(self,retValue):
        if (retValue == 0):
            self.aide_rect_bottomright.rect.center = self.rect.bottomright
        toplefto = self.rect.topleft
        self.rect.size = (self.aide_rect_bottomright.rect.centerx - self.rect.left,
                          self.aide_rect_bottomright.rect.centery - self.rect.top)
        if self.rect.width <= 0:
            self.rect.width = 0
        if self.rect.height <= 0:
            self.rect.height = 0

        self.rect.topleft = toplefto

        self.surface = pygame.transform.scale(self.surface_old,self.rect.size)

    def check_move(self,motion):#接收到MOUSEMOTUION事件并按下左键时执行，检查用户是否在拖动Aide_rect
        retValue = self.aide_rect_bottomright.check_drag(motion)
        if (retValue==0):
            self.check_drag_r(motion)

        self.update_rect(retValue)

    def display(self):
        self.screen.blit(self.surface,self.rect)
        pygame.draw.rect(self.screen,BLACK,self.rect,2)
        self.aide_rect_bottomright.draw()

    def check_drag_r(self,motion):
        mpos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mpos):
            self.move_r(motion)

    def move_r(self,motion):
        self.rect.move_ip(motion)

def main():
    pygame.init()
    pygame.mixer.init()

    clock = pygame.time.Clock()

    screen = pygame.display.set_mode((1440,960),RESIZABLE)
    screen.fill(WHITE)

    im = Image('../assets/album/苏杭/sh1.jpg')

    while True:
        screen.fill(WHITE)
        pygame.display.set_caption('album edit fps:%s' % clock.get_fps())
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEMOTION:
                if event.buttons[0]:
                    im.check_move(event.rel)
        im.display()

        pygame.display.update()

        clock.tick(1000)

if __name__ == '__main__':
    main()