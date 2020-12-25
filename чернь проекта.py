import pygame
import os
import sys
from random import randint


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Platform_Bottom(pygame.sprite.Sprite):
    def __init__(self, pos):
        self.image = pygame.Surface((50, 6))
        self.image.fill(pygame.Color('white'))
        super().__init__(all_spr)
        self.add(platform_down)
        self.rect = pygame.Rect(pos[0], pos[1] + 5, 50, 6)
        self.v = 2

    def update(self):
        if pygame.sprite.spritecollideany(self, left):
            self.v = -self.v
        elif pygame.sprite.spritecollideany(self, right):
            self.v = -self.v
        self.rect = self.rect.move(self.v, 0)


class Platform(pygame.sprite.Sprite):
    def __init__(self, pos):
        self.image = pygame.Surface((50, 6))
        self.image.fill(pygame.Color('gray'))
        super().__init__(all_spr)
        self.add(platform_up)
        self.rect = pygame.Rect(pos[0], pos[1], 50, 6)
        self.vel = 2
        Platform_Bottom(pos)

    def update(self):
        if pygame.sprite.spritecollideany(self, left):
            self.vel = -self.vel
        elif pygame.sprite.spritecollideany(self, right):
            self.vel = -self.vel
        self.rect = self.rect.move(self.vel, 0)


class Board(pygame.sprite.Sprite):
    def __init__(self, x1, y1, x2, y2, border):
        super().__init__(all_spr)
        if x1 == x2:
            self.add(border)
            self.image = pygame.Surface((6, y2 - y1))
            self.image.fill(pygame.Color('white'))
            self.rect = pygame.Rect(x1, y1, 5, y2 - y1)
        elif y1 == y2:
            self.add(border)
            self.image = pygame.Surface((x2 - x1, 6))
            self.image.fill(pygame.Color('white'))
            self.rect = pygame.Rect(x1, y1, x2 - x1, 5)


class Character(pygame.sprite.Sprite):
    def __init__(self, pos):
        self.image = load_image('heart.png')
        super().__init__(all_spr)
        self.add(characters)
        self.rect = pygame.Rect(pos[0], pos[1], 30, 30)
        self.v = 60

    def update(self):
        global fps, move_up, move_down, move_left, move_right
        if not pygame.sprite.spritecollideany(self, down):
            if not pygame.sprite.spritecollideany(self, platform_up):
                self.rect = self.rect.move(0, self.v // fps)
            else:
                if pygame.sprite.spritecollideany(self, platform_down):
                    self.rect = self.rect.move(0, self.v // fps)
        if (move_up and (not pygame.sprite.spritecollideany(self, platform_down)
                         and not pygame.sprite.spritecollideany(self, up))):
            self.rect = self.rect.move(0, -((self.v + 60) // fps))
            if (pygame.sprite.spritecollideany(self, up)
                    or pygame.sprite.spritecollideany(self, platform_down)
                    or pygame.sprite.spritecollideany(self, left)
                    or pygame.sprite.spritecollideany(self, right)):
                move_up = False
        if move_left and not pygame.sprite.spritecollideany(self, left) \
                and not pygame.sprite.spritecollideany(self, platform_down):
            self.rect = self.rect.move(-((self.v + 60) // fps), 0)
        if move_right and not pygame.sprite.spritecollideany(self, right) \
                and not pygame.sprite.spritecollideany(self, platform_down):
            self.rect = self.rect.move(((self.v + 60) // fps), 0)
        if pygame.sprite.spritecollideany(self, platform_up) \
                or pygame.sprite.spritecollideany(self, platform_down):
            if not (pygame.sprite.spritecollideany(self, border)):
                if pygame.sprite.spritecollideany(self, platform_up):
                    v = pygame.sprite.spritecollideany(self, platform_up).vel
                    if (v < 0 and not pygame.sprite.spritecollideany(self, left)) \
                            or (v > 0 and not pygame.sprite.spritecollideany(self, right)):
                        self.rect = self.rect.move(v, 0)


class Monika(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(all_spr)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        if timer_M % 5 == 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]



if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('МоникаТале')
    size = width, height = 600, 700
    screen = pygame.display.set_mode(size)
    screen.fill((0, 0, 0))
    running = True
    fps = 30
    timer = 0
    timer_M = 0

    platform_down = pygame.sprite.Group()
    platform_up = pygame.sprite.Group()
    clock = pygame.time.Clock()
    border = pygame.sprite.Group()
    all_spr = pygame.sprite.Group()
    ladders = pygame.sprite.Group()
    up = pygame.sprite.Group()
    down = pygame.sprite.Group()
    left = pygame.sprite.Group()
    right = pygame.sprite.Group()
    characters = pygame.sprite.Group()

    ctrl = False
    Board(200, 400, 400, 400, up)
    Board(200, 600, 400, 600, down)
    Board(200, 400, 200, 600, left)
    Board(400, 400, 400, 606, right)
    move_up = False
    move_left = False
    move_right = False
    Platform((250, 450))
    Platform((300, 500))
    c = 0
    monika = Monika(load_image('MONIK_2.png'), 5, 2, 200, 0)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                cube = Character(event.pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    move_left = True
                elif event.key == pygame.K_RIGHT:
                    move_right = True
                elif event.key == pygame.K_UP:
                    if pygame.sprite.spritecollideany(cube, down) \
                            or pygame.sprite.spritecollideany(cube, platform_up):
                        move_up = True
                elif event.key == pygame.K_DOWN:
                    move_down = True
                elif event.mod == pygame.KMOD_LCTRL or event.key == 1073742052:
                    ctrl = True
            elif event.type == pygame.KEYUP:
                if event.key == 1073742048 or event.key == 1073742052:
                    ctrl = False
                elif event.key == pygame.K_LEFT:
                    move_left = False
                elif event.key == pygame.K_RIGHT:
                    move_right = False
                elif event.key == pygame.K_UP:
                    move_up = False
                elif event.key == pygame.K_DOWN:
                    move_down = False
                    timer = 0
        if timer >= fps:
            move_up = False
            timer = 0
        if move_up:
            timer += 0.5
        timer_M += 1
        all_spr.draw(screen)
        all_spr.update()
        clock.tick(30)
        pygame.display.flip()
        screen.fill((0, 0, 0))

    pygame.quit()
