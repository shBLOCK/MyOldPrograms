import pygame,random,time,sys
from pygame.locals import *

SIZE = (32,32)
START_BALL_COUNT = 1
BOARD_WIDTH = 5
BLOCK_SIZE = 20

AIR = 0
BALL = 1
BOARD = 2
BRICK = 3

AIR_COLOR = (0,0,0)
BALL_COLOR = (255,255,255)
BOARD_COLOR = (0,255,0)
BRICK_COLOR = (0,255,255)
DEAD_LINE_COLOR = (255,0,0)

class Space:
    def __init__(self):
        self.ball_list = []
        for i in range(START_BALL_COUNT):
            self.ball_list.append(Ball([SIZE[0] // 2,3]))
        self.board = Board([SIZE[0] // 2,2],BOARD_WIDTH)
        self.brick_list = []
        for y in range(20,SIZE[1]):
            for x in range(SIZE[0]):
                self.brick_list.append(Brick((x,y)))
        #print(len(self.brick_list))

    def update(self):
        for i in range(len(self.ball_list)):
            self.ball_list[i].move()

        to_del_count = 0
        for i in range(len(self.ball_list)):
            if self.ball_list[i].pos[1] <= 0:
                self.ball_list[i] = False
                to_del_count += 1
        for i in range(to_del_count):
            self.ball_list.remove(False)

        if len(self.ball_list) <= 0:
            return 0

        for i in range(len(self.ball_list)):
            self.ball_list[i].check_hit_the_wall()

        for i in range(len(self.ball_list)):
            b_pos = self.ball_list[i].pos
            if self.board.check_ball_on(b_pos):
                self.ball_list[i].vec[1] = 1

        for b in range(len(self.ball_list)):
            b_pos = self.ball_list[b].pos
            to_del_count = 0
            for i in range(len(self.brick_list)):
                brick_return = self.brick_list[i].rebound(b_pos)
                if brick_return != None:
                    if brick_return[0] != None:
                        self.ball_list[b].vec[brick_return[0]] = brick_return[0]
                    if brick_return[1] != None:
                        self.ball_list[b].vec[brick_return[1]] = brick_return[1]
                    self.brick_list[i] = False
                    to_del_count += 1
            for i in range(to_del_count):
                self.brick_list.remove(False)

        return 1

    def get_list(self):
        r_list = []
        for y in range(SIZE[1]):
            x_list = []
            for x in range(SIZE[0]):
                x_list.append(AIR)
            r_list.append(list(x_list))

        for i in range(len(self.ball_list)):
            b_pos = self.ball_list[i].pos
            r_list[b_pos[1]][b_pos[0]] = BALL

        for i in self.board.get_pixel_list():
            r_list[i[1]][i[0]] = BOARD

        for i in range(len(self.brick_list)):
            b_pos = self.brick_list[i].pos
            r_list[b_pos[1]][b_pos[0]] = BRICK
        return r_list

class Ball:
    def __init__(self,pos):
        if random.randint(0,1):
            vec_x = 1
        else:
            vec_x = -1
        self.vec = [vec_x,1]
        self.pos = pos

    def move(self):
        self.pos[0] += self.vec[0]
        self.pos[1] += self.vec[1]

    def check_hit_the_wall(self):
        if self.pos[0] <= 0:
            self.vec[0] = 1
        if self.pos[0] >= SIZE[0] - 1:
            self.vec[0] = -1
        if self.pos[1] <= 0:
            self.vec[1] = 1
        if self.pos[1] >= SIZE[1] - 1:
            self.vec[1] = -1

class Brick:
    def __init__(self,pos):
        self.pos = pos

    def rebound(self,ball_pos):
        if ball_pos[1] == self.pos[1] + 1 and ball_pos[0] == self.pos[0]:#up
            #print('up')
            return None,1
        elif ball_pos[1] == self.pos[1] - 1 and ball_pos[0] == self.pos[0]:#down
            #print('down')
            return None,-1
        elif ball_pos[0] == self.pos[0] + 1 and ball_pos[1] == self.pos[1]:#left
            #print('left')
            return 1,None
        elif ball_pos[0] == self.pos[0] - 1 and ball_pos[1] == self.pos[1]:#right
            #print('right')
            return -1,None

        elif ball_pos[1] == self.pos[1] + 1 and ball_pos[0] == self.pos[0] + 1:
            return 1,1
        elif ball_pos[1] == self.pos[1] - 1 and ball_pos[0] == self.pos[0] + 1:
            return 1,-1
        elif ball_pos[1] == self.pos[1] + 1 and ball_pos[0] == self.pos[0] - 1:
            return -1,1
        elif ball_pos[1] == self.pos[1] - 1 and ball_pos[0] == self.pos[0] - 1:
            return -1,-1
        return None

class Board:
    def __init__(self,pos,width):
        self.pos = pos
        self.width = width

    def move(self,vec_x):
        if (vec_x == -1 and self.pos[0] > (self.width - 1) // 2) or vec_x == 1 and self.pos[0] < SIZE[0] - 1 - ((self.width - 1) // 2):
            self.pos[0] += vec_x
            return True
        return  False

    def check_ball_on(self,ball_pos):
        if ball_pos[1] == self.pos[1] + 1:
            if ball_pos[0] >= self.pos[0] - (self.width - 1) // 2 - 1 and ball_pos[0] <= self.pos[0] + (self.width - 1) // 2 + 1:
                #('!!!')
                return True
        return False

    def get_pixel_list(self):
        r_list = []
        for i in range(self.pos[0] - (self.width - 1) // 2,self.pos[0] + (self.width - 1) // 2 + 1):
            r_list.append((int(i),int(self.pos[1])))
        return r_list

def draw_space(data_list):
    data_list.reverse()
    for y in range(SIZE[1]):
        for x in range(SIZE[0]):
            if data_list[y][x] == AIR:
                color = AIR_COLOR
            elif data_list[y][x] == BALL:
                color = BALL_COLOR
            elif data_list[y][x] == BOARD:
                color = BOARD_COLOR
            elif data_list[y][x] == BRICK:
                color = BRICK_COLOR

            if y >= SIZE[1] - 1:
                color = DEAD_LINE_COLOR

            pygame.draw.rect(pygame.display.get_surface(), color,(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SIZE[0] * BLOCK_SIZE,SIZE[1] * BLOCK_SIZE))
    pygame.key.set_repeat(50,50)

    space = Space()

    UPDATE = USEREVENT
    pygame.time.set_timer(UPDATE,100)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                if event.key == K_RIGHT:
                    space.board.move(1)
                if event.key == K_LEFT:
                    space.board.move(-1)

            if event.type == UPDATE or True:
                #space.board.move(space.ball_list[0].vec[0])
                if space.update() == 0:
                    pygame.quit()
                    sys.exit()

        draw_space(space.get_list())

        pygame.display.flip()

if __name__ == '__main__':
    main()