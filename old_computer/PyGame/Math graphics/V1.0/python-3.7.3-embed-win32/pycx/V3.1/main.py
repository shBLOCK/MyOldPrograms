import pygame,random,time,json,math,sys
from pygame.locals import *

import pymunk
import pymunk.pygame_util
from pymunk import Vec2d

BALL_SIZE = 12
GRAVITY = (0,-1000)
DT = 1.0/60.0
MAX_BODY = 300

class Clock:
    def __init__(self,pos,cfg,old_time):
        self.space = pymunk.Space()
        self.space.gravity = GRAVITY
        self.pos = pos
        self.cfg = cfg
        self.old_time = list(old_time)
        self.screen = pygame.display.get_surface()
        self.balls = []
        self.images = []
        for im in self.cfg['images']:
            self.images.append(pygame.transform.scale(pygame.image.load(im).convert_alpha(),(BALL_SIZE * 2,BALL_SIZE * 2)))

        static_body = self.space.static_body
        static_lines = [pymunk.Segment(static_body, (0, 0), (self.screen.get_rect().width, 0), 0.0)]
        for line in static_lines:
            line.elasticity = 0.95
            line.friction = 0.9
        self.space.add(static_lines)

    def update(self,new_time,all_summon,apply_impulse):
        new_time = list(new_time)
        for i in range(len(new_time)):
            if new_time[i] != self.old_time[i] or all_summon:
                self.old_time[i] = new_time[i]
                self.display_num(i, new_time[i], True,apply_impulse)
            else:
                self.display_num(i, new_time[i],False,apply_impulse)
        self.space.step(DT)
        self.display_ball()
        self.update_balls()

    def display_num(self,pos,num,do_summon,apply_impulse):
        yp = self.pos[1]
        xp = self.pos[0] + pos * 180
        old_xp = xp
        for y in self.cfg[num]:
            for x in y:
                if x:
                    self.screen.blit(self.images[x - 1],(xp - BALL_SIZE,yp - BALL_SIZE))
                    if do_summon:
                        self.summon_ball((xp,yp),10,BALL_SIZE,0.9,0.5,self.images[x - 1],apply_impulse)
                xp += BALL_SIZE * 2
            xp = old_xp
            yp += BALL_SIZE * 2

    def summon_ball(self,pos,mass,radius,elasticity,friction,image,apply_impulse = True):
        pos = pymunk.pygame_util.to_pygame(pos,self.screen)
        inertia = pymunk.moment_for_circle(mass,0,radius,(0,0))
        body = pymunk.Body(mass,inertia)
        body.position = pos
        if apply_impulse:
            body.apply_impulse_at_local_point((random.randint(-1,1) / 10000000,0))
        shape = pymunk.Circle(body,radius,(0,0))
        shape.elasticity = elasticity
        shape.friction = friction
        self.space.add(body,shape)
        self.balls.append(shape)
        self.balls.append(image)

    def flipy(self,y):
        return  -y + self.screen.get_rect().height

    def update_balls(self):
        if len(self.balls) > MAX_BODY:
            rp = BALL_SIZE + 5
        else:
            rp = -50

        balls_to_remove = []

        for ball in range(len(self.balls) // 2):
            if self.balls[ball * 2].body.position.y < -50:
                balls_to_remove.append((self.balls[ball * 2],self.balls[ball * 2 + 1]))

        for ba in balls_to_remove:
            self.space.remove(ba[0],ba[0].body)
            rr = self.balls.index(ba[0])
            self.balls.pop(rr)
            self.balls.pop(rr)

        if len(self.balls) // 2 > MAX_BODY:
            '''
            while True:
                r = random.randint(0,(len(self.balls) - 1) // 2)
                ro = self.balls[r * 2]
                if ro.body.position.y < BALL_SIZE + 3:
                    break
            '''
            for r in range(len(self.balls) // 2):
                ro = self.balls[r * 2]
                if ro.body.position.y < BALL_SIZE + 3:
                    break
            self.space.remove(self.balls[r * 2],self.balls[r * 2].body)
            self.balls.pop(r * 2)
            self.balls.pop(r * 2)

    def display_ball(self):
        #self.space.debug_draw(self.do)
        for one in range(len(self.balls) // 2):
            im = self.balls[one * 2]
            bi = self.balls[one * 2 + 1]

            pos = im.body.position
            pos = Vec2d(pos.x,self.flipy(pos.y))

            angle_degrees = math.degrees(im.body.angle)
            rotated_im = pygame.transform.rotate(bi,angle_degrees)

            offset = Vec2d(rotated_im.get_size()) / 2
            pos = pos - offset

            self.screen.blit(rotated_im,pos)

    def del_all_ball(self):
        for b in range(len(self.balls) // 2):
            self.space.remove(self.balls[b * 2],self.balls[b * 2].body)
        self.balls.clear()

def main():
    shape = 'circle'
    screen = pygame.display.set_mode((1690,720))
    pygame.key.set_repeat(1,1)
    num_font = json.loads(open('../assets/font/num_font.json','r').read())
    clock = pygame.time.Clock()
    main_clock = Clock((150,100),num_font,time.strftime('%H:%M:%S'))
    while True:
        screen.fill((255, 255, 255))
        mousedown_summon = False
        ball_to_su = []
        if time.time() % 1 <= 0.5:
            ntc = time.strftime('%H:%M:%S')
        else:
            ntc = time.strftime('%H %M %S')

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONUP:
                mousedown_summon = True
            if event.type == KEYDOWN:
                if event.key == K_r:
                    main_clock.del_all_ball()

        kp = pygame.key.get_pressed()
        if kp[K_0]:
            ball_to_su.append(0)
        if kp[K_1]:
            ball_to_su.append(1)
        if kp[K_2]:
            ball_to_su.append(2)
        if kp[K_3]:
            ball_to_su.append(3)
        if kp[K_4]:
            ball_to_su.append(4)
        if kp[K_5]:
            ball_to_su.append(5)
        if kp[K_6]:
            ball_to_su.append(6)
        if kp[K_7]:
            ball_to_su.append(7)
        if kp[K_8]:
            ball_to_su.append(8)
        if kp[K_9]:
            ball_to_su.append(9)

        pygame.display.set_caption('bouncing balls clock -- time: %s' % ntc)

        if shape == 'circle':
            main_clock.update(ntc,mousedown_summon,True)
        else:
            main_clock.update(ntc, mousedown_summon, False)

        for b in ball_to_su:
            if b < len(main_clock.images):
                main_clock.summon_ball(pygame.mouse.get_pos(),10,BALL_SIZE,0.9,0.5,main_clock.images[b])

        pygame.display.flip()

        clock.tick(60)

if __name__ == '__main__':
    main()