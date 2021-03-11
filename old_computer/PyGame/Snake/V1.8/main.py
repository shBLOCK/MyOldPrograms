import pygame,random,time,sys
from pygame.locals import *

SIZE = [16,16]
LED_COUNT = 256
LED_PIN = 18
LED_FREQ_HZ = 800000
LED_DMA = 5
LED_BRIGHTNESS = 30
LED_INVERT = False

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

FOOD_COUNT = 5

SPEED = 100

class Snake:
    def __init__(self,space_size,count_food):#space_size:(x,y)
        #self.count_food = count_food
        self.space_size = space_size
        self.body_list = [[0,0]]
        self.head = [0,0]
        self.direction = RIGHT
        self.food = []
        for i in range(count_food):
            s_food = self.summon_food()
            if s_food != None:
                self.food.append(s_food)
        self.score = 0
        self.increase = False

    def set_direction(self,new):
        if ((self.direction != UP and self.direction != DOWN) and (new == UP or new == DOWN)) or ((self.direction != RIGHT and self.direction != LEFT) and (new == RIGHT or new == LEFT)):
            self.direction = new

    def summon_food(self):
        for i in range(self.space_size[0] * self.space_size[1] + 50):
            food = []
            food.append(random.randint(0,self.space_size[0] - 1))
            food.append(random.randint(0,self.space_size[1] - 1))
            if not food in self.body_list and not food in self.food:
                return food
        
        for x in range(self.space_size[0]):
            for y in range(self.space_size[1]):
                if not [x,y] in self.body_list and not food in self.food:
                    return [x,y]
        
        return None

    def update(self):
        self.head[0] += self.direction[0]
        self.head[1] += self.direction[1]
        #print(self.head)

        self.body_list.insert(0,list(self.head))
        if self.increase == False:
            self.body_list.pop()
            
        self.increase = False

        #print(self.body_list)

        if self.head in self.food:
            self.food.remove(self.head)
            self.increase = True
            new_food = self.summon_food()
            if new_food != None:
                self.food.append(new_food)
            self.score += 1
            return 1
        
        if self.score >= self.space_size[0] * self.space_size[1] - 1:
            return 2

        if self.body_list.count(self.body_list[0]) >= 2:
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

        for i in self.food:
            r_list[i[1]][i[0]] = FOOD

        return r_list

def draw_snake_and_return_headpos(s_list,led):
    for y in range(SIZE[1]):
        for x in range(SIZE[0]):
            if s_list[y][x] == AIR:
                color = AIR_COLOR
            elif s_list[y][x] == BODY:
                color = BODY_COLOR
            elif s_list[y][x] == HEAD:
                h_pos = [x,y]
                color = HEAD_COLOR
            elif s_list[y][x] == FOOD:
                color = FOOD_COLOR

            pygame.draw.rect(pygame.display.get_surface(),color,(x * BLOCK_SIZE,y * BLOCK_SIZE,BLOCK_SIZE,BLOCK_SIZE),0)
            pygame.draw.rect(pygame.display.get_surface(), (255,255,255),(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)
    return h_pos

class Success:
    def __init__(self):
        self.space_size = SIZE
        self.count = SIZE[0] * SIZE[1]
        self.mode = 0
        
        self.r = 250
        self.g = 0
        self.b = 0
        
        self.speed = 2
        
        self.colors = []
        
        for i in range(self.count):
            if self.mode == 0 and self.r <= 0:
                self.mode = 1
            if self.mode == 1 and self.g <= 0:
                self.mode = 2
            if self.mode == 2 and self.b <= 0:
                self.mode = 0
            
            if self.mode == 0:
                self.r -= self.speed
                self.g += self.speed
            if self.mode == 1:
                self.g -= self.speed
                self.b += self.speed
            if self.mode == 2:
                self.b -= self.speed
                self.r += self.speed
            
            self.colors.append([self.r,self.g,self.b])
        
    def run(self):
        self.r = self.colors[1][0]
        self.g = self.colors[1][1]
        self.b = self.colors[1][2]
        for i in range(self.count):
            if self.mode == 0 and self.r <= 0:
                self.mode = 1
            if self.mode == 1 and self.g <= 0:
                self.mode = 2
            if self.mode == 2 and self.b <= 0:
                self.mode = 0
            
            if self.mode == 0:
                self.r -= self.speed
                self.g += self.speed
            if self.mode == 1:
                self.g -= self.speed
                self.b += self.speed
            if self.mode == 2:
                self.b -= self.speed
                self.r += self.speed
            self.colors[i] = [self.r,self.g,self.b]
        
        for y in range(self.space_size[1]):
            for x in range(self.space_size[0]):
                pygame.draw.rect(pygame.display.get_surface(),self.colors[x*y],(x * BLOCK_SIZE,y * BLOCK_SIZE,BLOCK_SIZE,BLOCK_SIZE),0)
        pygame.display.flip()

def game_discontinue(mode,head_pos):
    if mode == 0:
        for i in range(5):
            pygame.draw.rect(pygame.display.get_surface(),(0,0,0),(head_pos[0] * BLOCK_SIZE,head_pos[1] * BLOCK_SIZE,BLOCK_SIZE,BLOCK_SIZE),0)
            pygame.display.flip()
            time.sleep(0.1)
            pygame.draw.rect(pygame.display.get_surface(),(255,0,0),(head_pos[0] * BLOCK_SIZE,head_pos[1] * BLOCK_SIZE,BLOCK_SIZE,BLOCK_SIZE),0)
            pygame.display.flip()
            time.sleep(0.1)
    elif mode == 1:
        success = Success()
    while True:
        if mode == 1:
            success.run()
            time.sleep(0.01)
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYUP:
                if event.key == K_r:
                    pygame.event.clear()
                    main()
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type == MOUSEBUTTONUP and event.button == 1:
                pygame.event.clear()
                main()

def main():
    pygame.init()
    screen = pygame.display.set_mode((SIZE[0] * BLOCK_SIZE,SIZE[1] * BLOCK_SIZE))

    UPDATE = USEREVENT
    pygame.time.set_timer(UPDATE, SPEED)

    snake = Snake(SIZE,FOOD_COUNT)

    can_set_direction = True

    while True:
        #print(snake.body_list)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if can_set_direction:
                can_set_direction = False
                if event.type == KEYDOWN:
                    if event.key == K_UP:
                        snake.set_direction(UP)
                    elif event.key == K_DOWN:
                        snake.set_direction(DOWN)
                    elif event.key == K_LEFT:
                        snake.set_direction(LEFT)
                    elif event.key == K_RIGHT:
                        snake.set_direction(RIGHT)
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()

            if event.type == UPDATE:
                can_set_direction = True
                sur = snake.update()
                if sur == 0:
                    game_discontinue(0,h_pos)
                elif sur == 2:
                    game_discontinue(1,h_pos)
                
                h_pos = draw_snake_and_return_headpos(snake.get_list(),True)
                
                pygame.display.set_caption('Snake Score:%s' % snake.score)

        pygame.display.flip()

if __name__ == '__main__':
    main()