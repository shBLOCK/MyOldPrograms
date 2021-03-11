import pygame, json, sys
from pygame.locals import *

SLOT_CNT = 55
pygame.init()
board = pygame.image.load('../assets-old/triangle/board.png')
board_clear = board.copy()

board_list = []
l = 0
n = 1
for y in [i + 1 for i in range(10)][::-1]:
    board_list.append([])
    for x in range(y):
        board_list[l].append(n)
        n += 1
    l += 1

parts_mods_cnt = [4, 4, 1, 4, 1, 8, 8, 8, 8, 4, 2, 8]

parts = []
parts_surface = []

now_part = 0
now_pos = [0, 0]
last_max_rotate = 4
now_rotate_part = 0
start = []
ans = []

ans_cnt = 0

def can_put(part, pos):
    for point in parts[part][1]:
        try:
            if board.get_at((point[0] + pos[0], point[1] + pos[1])) != (0, 0, 0, 255):
                return False
        except:
            return False
    return True

def init_surfaces():
    global parts_enable
    parts_enable = tuple(range(1, 13))
    for i in range(1, 13):
        im = pygame.image.load('../assets/%s.png' % str(i))
        im_f = pygame.transform.flip(im.copy(), True, False)
        mode_cnt = 0
        mode_ok = False
        for part in range(4):
            if mode_cnt >= parts_mods_cnt[i - 1]:
                mode_ok = True
                break
            mode_cnt += 1
            parts_surface.append((i, im.copy()))
            im = pygame.transform.rotate(im, 90)
        if mode_ok:
            continue
        for part in range(4):
            if mode_cnt >= parts_mods_cnt[i - 1]:
                break
            mode_cnt += 1
            parts_surface.append((i, im_f.copy()))
            im_f = pygame.transform.rotate(im_f, 90)

def init_parts():
    global parts
    for s in parts_surface:
        surface = s[1]
        part = []
        for x in range(surface.get_width()):
            for y in range(surface.get_height()):
                if surface.get_at((x, y))[3] != 0:
                    part.append((x, y))
        part = tuple(part)
        parts.append((s[0], part))

def draw_board():
    b = board.copy()
    b.blit(parts_surface[now_rotate_part][1], now_pos)
    screen.blit(pygame.transform.scale(b, (500, 500)), (0, 0))

def check_start(now_ans):
    for part in start:
        if part not in now_ans:
            return False
    return True

def find_ans():
    file = open('../assets/triangle/pyramid.json', encoding='utf_8-sig')

    for s in file:
        now_ans = json.loads(s)
        if check_start(now_ans):
            ans.append(now_ans.copy())
    if len(ans) != 0:
        draw_ans()
    else:
        pygame.quit()
        sys.exit()

def draw_ans():
    print(len(ans))
    while True:
        for a in range(len(ans)):
            b = board_clear.copy()
            for part in ans[a]:
                b.blit(parts_surface[part[0]][1], part[1])
            screen.blit(pygame.transform.scale(b, (500, 500)), (0, 0))
            pygame.display.flip()
            while True:
                next_part = False
                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == KEYDOWN:
                        if event.key == K_SPACE:
                            next_part = True
                            break
                if next_part:
                    break

                pygame.display.flip()

if __name__ == '__main__':
    screen = pygame.display.set_mode((500, 500))

    init_surfaces()
    init_parts()

    while True:
        screen.fill((80, 80, 80))

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_UP:
                    if now_pos[1] >= 1:
                        now_pos[1] -= 1
                if event.key == K_DOWN:
                    now_pos[1] += 1
                if event.key == K_LEFT:
                    if now_pos[0] >= 1:
                        now_pos[0] -= 1
                if event.key == K_RIGHT:
                    now_pos[0] += 1
                if event.key == K_SPACE:
                    now_rotate_part += 1
                    if now_rotate_part >= last_max_rotate:
                        now_rotate_part = last_max_rotate - parts_mods_cnt[now_part]
                if event.key == K_ESCAPE:
                    if now_part >= 11:
                        find_ans()
                    now_pos = [0, 0]
                    now_part += 1
                    last_max_rotate += parts_mods_cnt[now_part]
                    now_rotate_part = last_max_rotate - 1
                if event.key == K_RETURN:
                    if can_put(now_rotate_part, now_pos):
                        board.blit(parts_surface[now_rotate_part][1], now_pos)
                        if now_part >= 11:
                            find_ans()
                        start.append([now_rotate_part, now_pos])
                        now_pos = [0, 0]
                        now_part += 1
                        last_max_rotate += parts_mods_cnt[now_part]
                        now_rotate_part = last_max_rotate - 1

        draw_board()
        pygame.display.flip()
