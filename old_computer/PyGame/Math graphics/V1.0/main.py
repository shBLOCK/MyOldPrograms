import pygame,math,sys
from pygame.locals import *

#mode0
N = 900
R = 350

#mode1
ONE_L = 3

SCREEN_SIZE = (720,720)

POINT_COLOR = (0,0,255)
POINT_SIZE = 2

cs = 0.01

def make_point(mode):
    point_list = []
    if mode == 0:
        for m in range(N):
            point_list.append((int(R * math.cos(m * 2 * math.pi / N) + SCREEN_SIZE[0] / 2),
                               int(R * math.sin(m * 2 * math.pi / N) + SCREEN_SIZE[1] / 2)))

    elif mode == 1:
        one_n = N // 4

        x = -(one_n // 2 * ONE_L) + SCREEN_SIZE[0] // 2
        y = -(one_n // 2 * ONE_L) + SCREEN_SIZE[1] // 2
        for i in range(one_n):
            x += ONE_L
            point_list.append((x,y))

        for i in range(one_n):
            y += ONE_L
            point_list.append((x,y))

        for i in range(one_n):
            x -= ONE_L
            point_list.append((x,y))

        for i in range(one_n):
            y -= ONE_L
            point_list.append((x,y))

        for i in range(int(one_n * 1.5)):
            point_list.append(point_list.pop(0))

    print(point_list)
    return point_list

def main():
    global cs
    pygame.init()
    clock = pygame.time.Clock()
    text = pygame.font.Font(None,30)
    screen = pygame.display.set_mode(SCREEN_SIZE)
    point_list = make_point(0)
    while True:
        screen.fill((255,255,255))
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        for point in point_list:
            pygame.draw.circle(screen,POINT_COLOR,point,POINT_SIZE)
        screen.blit(text.render(str(cs),False,(0,0,0)),(0,0))
        draw_graphics(cs,(255,0,0),point_list,0)
        cs += 0.01
        pygame.display.update()
        clock.tick(30)

def draw_graphics(chengshu,color,point_list,mode):
    global cs
    if mode == 0:
        for i in range(N):
            pygame.draw.line(pygame.display.get_surface(), color, point_list[i], point_list[int((i * chengshu) % N)])
    elif mode == 1:
        for i in range(N):
            pygame.draw.line(pygame.display.get_surface(),color,point_list[i],point_list[int((i * chengshu) % N / cs)])

if __name__ == '__main__':
    main()