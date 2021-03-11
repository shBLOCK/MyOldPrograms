import pygame,random,time,sys
from pygame.locals import *

BLOCK_SIZE = 30

UP = [0,-1]
DOWN = [0,1]
LEFT = [-1,0]
RIGHT = [1,0]

AIR = 0
BODY = 1
HEAD = 2
FOOD = 3

AIR_COLOR = (0,0,0)
BODY_COLOR = (0,255,0)
HEAD_COLOR = (0,0,255)
FOOD_COLOR = (255,255,0)

class Snake:
    def __init__(self,space_size):#space_size:(x,y)
        self.space_size = space_size
        self.body_list = [[0,0]]
        self.head = [0,0]
        self.direction = RIGHT
        self.food = [space_size[0] // 2,space_size[1] // 2]
        self.score = 0
        self.increase = False

    def set_direction(self,new):
        if ((self.direction != UP and self.direction != DOWN) and (new == UP or new == DOWN)) or ((self.direction != RIGHT and self.direction != LEFT) and (new == RIGHT or new == LEFT)):
            self.direction = new

    def summon_food(self):
        while True:
            food = []
            food.append(random.randint(0,self.space_size[0] - 1))
            food.append(random.randint(0,self.space_size[1] - 1))
            if not food in self.body_list:
                break
        return food

    def update(self):
        self.head[0] += self.direction[0]
        self.head[1] += self.direction[1]
        print(self.head)

        self.body_list.insert(0,list(self.head))
        if self.increase == False:
            self.body_list.pop()
        self.increase = False

        print(self.body_list)

        if self.head == self.food:
            self.increase = True
            self.food = self.summon_food()
            self.score += 1
            return 1

        if self.body_list.count(self.body_list[0]) >= 2 and False:
            return 0

        if self.body_list[0][0] < 0 or self.body_list[0][0] > self.space_size[0] - 1 or self.body_list[0][1] < 0 or self.body_list[0][1] > self.space_size[1] - 1:
            return 0

        return 1

    def get_list(self):
        r_list = []

        for i in range(self.space_size[1]):
            a_list = []
            for j in range(self.space_size[0]):
                a_list.append(AIR)
            r_list.append(a_list)

        for i in self.body_list:
            r_list[i[1]][i[0]] = BODY

        r_list[self.head[1]][self.head[0]] = HEAD

        r_list[self.food[1]][self.food[0]] = FOOD

        return r_list

def draw_snake(s_list):
    for y in range(16):
        for x in range(16):
            if s_list[y][x] == AIR:
                color = AIR_COLOR
            elif s_list[y][x] == BODY:
                color = BODY_COLOR
            elif s_list[y][x] == HEAD:
                color = HEAD_COLOR
            elif s_list[y][x] == FOOD:
                color = FOOD_COLOR

            pygame.draw.rect(pygame.display.get_surface(),color,[x * BLOCK_SIZE,y * BLOCK_SIZE,BLOCK_SIZE,BLOCK_SIZE],0)

if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((480,480))

    UPDATE = USEREVENT
    pygame.time.set_timer(UPDATE, 200)

    snake = Snake((16,16))

    while True:
        #print(snake.body_list)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == UPDATE:
                if snake.update() == 0:
                    pygame.quit()
                    sys.exit()
                draw_snake(snake.get_list())
                pygame.display.set_caption('Snake Score:%s' % snake.score)

            if event.type == KEYDOWN:
                if event.key == K_UP:
                    snake.set_direction(UP)
                elif event.key == K_DOWN:
                    snake.set_direction(DOWN)
                elif event.key == K_LEFT:
                    snake.set_direction(LEFT)
                elif event.key == K_RIGHT:
                    snake.set_direction(RIGHT)

        pygame.display.flip()