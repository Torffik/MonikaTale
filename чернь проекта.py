import pygame
import os
import sys
from random import randint, choice
import math
import shutil


pygame.init()
help_lines = open('help.txt', encoding='UTF-8').readlines()
for line in help_lines:
    print(line)


def get_event():
    global running, move_up, move_down, move_left, move_right, timer, c, energy, energy_reversed
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            running = False
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                move_left = True
            elif event.key == pygame.K_RIGHT:
                move_right = True
            elif event.key == pygame.K_UP:
                if pygame.sprite.spritecollideany(cube, down) \
                        or pygame.sprite.spritecollideany(cube, platform_up) and blue:
                    move_up = True
                elif not blue:
                    move_up = True
            elif event.key == pygame.K_DOWN:
                if character_exist:
                    if pygame.sprite.spritecollideany(cube, up) \
                            or pygame.sprite.spritecollideany(cube, platform_down) and reversed_gravity:
                        move_down = True
                    elif not reversed_gravity:
                        move_down = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                move_left = False
            elif event.key == pygame.K_RIGHT:
                move_right = False
            elif event.key == pygame.K_UP:
                if move_up:
                    energy = True
                move_up = False
                timer = 0
                c = 0
            elif event.key == pygame.K_DOWN:
                if reversed_gravity:
                    if move_down:
                        energy_reversed = True
                move_down = False
                timer = 0
                c = 0


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
    def __init__(self, pos, moving=True):
        self.image = pygame.Surface((50, 6))
        self.image.fill(pygame.Color('white'))
        super().__init__(all_spr)
        self.add(platform_down)
        self.rect = pygame.Rect(pos[0], pos[1] + 5, 50, 6)
        self.v = 2
        self.moving = moving

    def update(self):
        if self.moving:
            if pygame.sprite.spritecollideany(self, left):
                self.v = -self.v
            elif pygame.sprite.spritecollideany(self, right):
                self.v = -self.v
            self.rect = self.rect.move(self.v, 0)


class Platform(pygame.sprite.Sprite):
    def __init__(self, pos, moving=True):
        self.image = pygame.Surface((50, 6))
        self.image.fill(pygame.Color('gray'))
        super().__init__(all_spr)
        self.add(platform_up)
        self.rect = pygame.Rect(pos[0], pos[1], 50, 6)
        self.vel = 2
        self.moving = moving
        Platform_Bottom(pos, self.moving)

    def update(self):
        if self.moving:
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
        self.red = load_image('heart.png')
        super().__init__(all_spr)
        self.add(characters)
        self.rect = pygame.Rect(pos[0], pos[1], 30, 30)
        self.v = 80
        self.g = 0
        self.blue = load_image('heart_2.png')
        self.image = self.red
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        global fps, move_up, move_down, move_left, move_right, stuck, \
            energy, blue, gravity_force, gravity_force_up, energy_reversed, rotated
        if blue:
            if not rotated:
                self.image = self.blue
            if reversed_gravity:
                if not rotated:
                    self.image = pygame.transform.rotate(self.image, 180)
                    rotated = True
                if not pygame.sprite.spritecollideany(self, up):
                    if not pygame.sprite.spritecollideany(self, platform_down):
                        if gravity_force:
                            self.rect = self.rect.move(0, (self.v + 600) // fps)
                            move_up = False
                        else:
                            self.rect = self.rect.move(0, -(self.v + 10) // fps)
                    else:
                        if pygame.sprite.spritecollideany(self, platform_up):
                            self.rect = self.rect.move(0, -(self.v + 10) // fps)
                            if gravity_force:
                                self.rect = self.rect.move(0, (self.v + 600) // fps)
                                move_up = False
                            elif gravity_force_up:
                                self.rect = self.rect.move(0, -(self.v + 600) // fps)
                                if not pygame.sprite.spritecollideany(self, platform_down) \
                                        and not pygame.sprite.spritecollideany(self, up):
                                    move_up = False
                                else:
                                    self.rect = self.rect.move(0, (self.v + 600) // fps)
                else:
                    if gravity_force_up:
                        gravity_force_up = False
                        energy_reversed = True
                if move_down and not pygame.sprite.spritecollideany(self, down):
                    if stuck:
                        self.rect = self.rect.move(0, self.v // fps)
                    else:
                        self.rect = self.rect.move(0, ((self.v + 130) // fps))
                    if pygame.sprite.spritecollideany(self, down):
                        stuck = True
                    else:
                        stuck = False
            else:
                if not gravity_force_up:
                    rotated = False
                if not pygame.sprite.spritecollideany(self, down):
                    if not pygame.sprite.spritecollideany(self, platform_up):
                        if gravity_force:
                            self.rect = self.rect.move(0, (self.v + 600) // fps)
                            move_up = False
                        else:
                            self.rect = self.rect.move(0, (self.v + 10) // fps)
                    else:
                        if pygame.sprite.spritecollideany(self, platform_down):
                            if gravity_force:
                                self.rect = self.rect.move(0, (self.v + 600) // fps)
                                move_up = False
                            elif gravity_force_up:
                                if not pygame.sprite.spritecollideany(self, platform_down) \
                                        and not pygame.sprite.spritecollideany(self, up):
                                    self.rect = self.rect.move(0, -(self.v + 600) // fps)
                                    move_up = False
                            else:
                                self.rect = self.rect.move(0, (self.v + 10) // fps)
                else:
                    if gravity_force:
                        gravity_force = False
                        energy = True
                if move_up and not pygame.sprite.spritecollideany(self, up):
                    if stuck:
                        self.rect = self.rect.move(0, -((self.v) // fps))
                    else:
                        self.rect = self.rect.move(0, -((self.v + (100)) // fps))
                    if pygame.sprite.spritecollideany(self, up):
                        stuck = True
                    else:
                        stuck = False
            if gravity_force_up:
                self.rect = self.rect.move(0, -(self.v + 600) // fps)
                if not rotated:
                    self.image = pygame.transform.rotate(self.image, 180)
                    rotated = True
                if not (pygame.sprite.spritecollideany(self, up)
                        or pygame.sprite.spritecollideany(self, platform_down)):
                    move_up = False
                else:
                    self.rect = self.rect.move(0, (self.v + 600) // fps)
                    gravity_force_up = False
                    energy = False
                    g = 0
                    energy_reversed = True
            if energy:
                if (not pygame.sprite.spritecollideany(self, platform_down)
                        and not pygame.sprite.spritecollideany(self, up)):
                    self.g += 9
                    self.rect = self.rect.move(0, -((self.v + (100 - self.g)) // fps))
                    if self.g > 90:
                        energy = False
                        self.g = 0
            elif energy_reversed:
                if (not pygame.sprite.spritecollideany(self, platform_up)
                        and not pygame.sprite.spritecollideany(self, down)):
                    self.g += 18
                    self.rect = self.rect.move(0, ((self.v + (100 - self.g)) // fps))
                    if self.g > 90:
                        energy_reversed = False
                        self.g = 0
                        if not reversed_gravity:
                            self.image = self.blue
                            rotated = False
            if move_left and not pygame.sprite.spritecollideany(self, left) \
                    and not (
                    pygame.sprite.spritecollideany(self, platform_down) and pygame.sprite.spritecollideany(self,
                                                                                                           platform_up)):
                self.rect = self.rect.move(-((self.v + 60) // fps), 0)
            if move_right and not pygame.sprite.spritecollideany(self, right) \
                    and not (
                    pygame.sprite.spritecollideany(self, platform_down) and pygame.sprite.spritecollideany(self,
                                                                                                           platform_up)):
                self.rect = self.rect.move(((self.v + 60) // fps), 0)
            if pygame.sprite.spritecollideany(self, platform_up):
                if not (pygame.sprite.spritecollideany(self, border)):
                    if pygame.sprite.spritecollideany(self, platform_up).moving:
                        v = pygame.sprite.spritecollideany(self, platform_up).vel
                        if (v < 0 and not pygame.sprite.spritecollideany(self, left)) \
                                or (v > 0 and not pygame.sprite.spritecollideany(self, right)):
                            self.rect = self.rect.move(v, 0)
        else:
            if rotated:
                rotated = False
            self.image = self.red
            if move_up and not pygame.sprite.spritecollideany(self, up):
                self.rect = self.rect.move(0, -((self.v + 60) // fps))
            if move_down and not pygame.sprite.spritecollideany(self, down):
                self.rect = self.rect.move(0, ((self.v + 60) // fps))
            if move_left and not pygame.sprite.spritecollideany(self, left):
                self.rect = self.rect.move(-((self.v + 60) // fps), 0)
            if move_right and not pygame.sprite.spritecollideany(self, right):
                self.rect = self.rect.move(((self.v + 60) // fps), 0)

    def vibrate(self, pos):
        self.rect = pos.move(randint(-2, 2), randint(-2, 2))


class Vrag(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(all_spr)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.frames_main = self.frames
        self.frames = []
        self.cur_frame = 0
        self.image = self.frames_main[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.start_x = x

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        global animation, dodge
        if dodge and not end_phase_1:
            if self.rect.x != (self.start_x + 100):
                self.rect.x += 5
        else:
            if self.rect.x != self.start_x:
                self.rect.x -= 5
        if timer_M % 5 == 0 or (timer_M % 4 == 0 and end_phase_1):
            if not animation:
                self.cur_frame = (self.cur_frame + 1) % len(self.frames_main)
                self.image = self.frames_main[self.cur_frame]
            else:
                self.cur_frame_animation = (self.cur_frame_animation + 1) % len(self.frames)
                self.image = self.frames[self.cur_frame_animation]
                if self.cur_frame_animation == len(self.frames) - 1:
                    animation = False
                    self.frames = []

    def replacement(self, sheet, columns, rows, x, y):
        global animation
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame_animation = 0
        self.rect = self.rect.move(x, y)
        animation = True


class Hit(pygame.sprite.Sprite):
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
        if timer_M % 10 == 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
            if self.cur_frame == len(self.frames) - 1:
                self.kill()


class Minigame(pygame.sprite.Sprite):
    def __init__(self, pos):
        self.image = load_image('hit_eye.png')
        super().__init__(all_spr)
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]


class Button():
    def __init__(self, start_x, start_y, screen, text):
        self.on = False
        self.text = text
        self.start_x = start_x
        self.start_y = start_y
        self.font = pygame.font.Font('data//font.ttf', 30)
        self.screen = screen

    def on_it(self, pos):
        x = pos[0]
        y = pos[1]
        if (self.start_x - 10) <= x <= (self.start_x - 10 + 200) \
                and (self.start_y - 35) <= y <= (self.start_y + 20):
            if not self.on:
                speech.stop()
                speech.play(speech_sound)
            self.on = True
            return self.on
        else:
            self.on = False
            return self.on

    def clicked(self, pos):
        if self.on:
            return True
        else:
            return False

    def update(self):
        if self.on:
            string_rendered = self.font.render(self.text, True, pygame.Color('green'))
            intro_rect = string_rendered.get_rect()
            intro_rect.y = self.start_y - 20
            intro_rect.x = self.start_x + 20
            self.screen.blit(string_rendered, intro_rect)
            pygame.draw.rect(self.screen, 'green', (self.start_x - 10, self.start_y - 25, 200, 50), 3)
        else:
            string_rendered = self.font.render(self.text, True, pygame.Color('white'))
            intro_rect = string_rendered.get_rect()
            intro_rect.y = self.start_y - 20
            intro_rect.x = self.start_x + 20
            self.screen.blit(string_rendered, intro_rect)
            pygame.draw.rect(self.screen, 'white', (self.start_x - 10, self.start_y - 25, 200, 50), 3)


def wait(time, black_screen=False, white=False):
    global screen, fps, clock, all_spr, timer_M, seconds_passed, \
        move_left, move_right, move_up, move_down, running
    timer = 0
    seconds_started = seconds_passed
    waiting = True
    move_left = False
    move_down = False
    move_up = False
    move_right = False
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                running = False
                sys.exit()
        if timer >= fps:
            seconds_passed += 1
            timer = 0
        if seconds_started + time == seconds_passed:
            waiting = False
        timer += 1
        all_spr.update()
        all_spr.draw(screen)
        if white:
            screen.fill((255, 255, 255))
        if black_screen:
            screen.fill((0, 0, 0))
        clock.tick(fps)
        pygame.display.flip()


def terminate():
    pygame.quit()
    sys.exit()


def start_screen(fps, size):
    global debug
    fon = pygame.display.set_mode(size)
    pygame.display.set_caption('МоникаТале')
    fon.fill((0, 0, 0))
    fon2 = pygame.transform.scale(load_image('logo.png'), (size))
    fon.blit(fon2, (0, 0))
    start_button = Button(200, 550, fon, 'НАЧАТЬ')
    # developers_button = Button(200, 375, on, 'РАЗРАБОТЧИКИ')
    exit_button = Button(200, 650, fon, 'ВЫХОД')
    debug_button = Button(15, 750, fon, 'DEBUG')
    on_button = False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEMOTION:
                start_button.on_it(event.pos)
                # developers_button.on_it(event.pos)
                exit_button.on_it(event.pos)
                debug_button.on_it(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if start_button.clicked(event.pos):
                    beggining(fon)
                    return True
                elif exit_button.clicked(event.pos):
                    return False
                elif debug_button.clicked(event.pos):
                    debug = not debug
        screen.fill((0, 0, 0))
        fon.blit(fon2, (0, 0))
        if debug:
            pygame.draw.circle(screen, pygame.Color('red'), (160, 750), 15)
        start_button.update()
        # developers_button.update()
        exit_button.update()
        debug_button.update()
        pygame.display.flip()


def beggining(fon, text=None):
    global fps
    fon.fill((0, 0, 0))
    fort = pygame.font.Font('data//font.ttf', 25)
    if not text:
        text = ['*Вы оказываетесь в пустой комнате с девушкой...', '*Это Моника.', '*Странный свет заполняет комнату...',
                '*Вы наполнены.   .   .   ж а ж д о й   к р о в и']
    for i in range(len(text)):
        main_lines = text[i]
        line = ''
        dialogue_time = pygame.time.Clock()
        timer = 0
        dia = True
        main_line = True
        next = True
        while dia:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    dia = False
            da = main_lines[timer]
            if next:
                line += da
                if da != ' ' and dia:
                    speech.play(speech_sound)
            dia_c = fort.render(line, True, (255, 255, 255))
            dia_rect = dia_c.get_rect()
            dia_rect.y = 50
            dia_rect.x = 50
            fon.blit(dia_c, dia_rect)
            next = False
            if main_line:
                if timer < len(main_lines) - 1:
                    timer += 1
                    next = True
            dialogue_time.tick(fps // 2)
            pygame.display.flip()
            fon.fill((0, 0, 0))
            speech.stop()
    pygame.mixer.Sound('data//battle_start.wav').play()


class Health_bar():
    def __init__(self):
        pygame.draw.rect(screen, 'white', (200, 730, 200, 30), 3)
        pygame.draw.rect(screen, 'red', (203, 733, 197, 27))
        pygame.draw.rect(screen, 'green', (203, 733, 197, 27))

    def update(self, hp, screen):
        pygame.init()
        fort = pygame.font.Font('data//font.ttf', 32)
        if KR:
            hp_c = fort.render(f'{hp}/100   KR', True, (255, 255, 255))
        else:
            hp_c = fort.render(f'{hp}/100', True, (255, 255, 255))
        hp_rect = hp_c.get_rect()
        hp_rect.y = 740
        hp_rect.x = 420
        screen.blit(hp_c, hp_rect)
        pygame.draw.rect(screen, 'white', (200, 730, 200, 30), 3)
        pygame.draw.rect(screen, 'red', (202, 732, 197, 27))
        if hp >= 0:
            pygame.draw.rect(screen, 'green', (202, 732, (1.97 * hp), 27))


class Slider(pygame.sprite.Sprite):
    def __init__(self, pos):
        self.image = pygame.Surface((20, 180))
        self.image.fill(pygame.Color('gray'))
        super().__init__(all_spr)
        self.add(platform_up)
        self.rect = pygame.Rect(pos[0], pos[1], 50, 6)
        self.vel = 15

    def update(self):
        global turn
        self.rect = self.rect.move(self.vel, 0)
        if self.rect.x >= 650:
            self.kill()
            turn = False


class Time_Text(pygame.sprite.Sprite):
    def __init__(self, x, y, text, lifetime, font, size, vibration=False):
        super().__init__(all_spr)
        self.text = text
        self.font = pygame.font.Font(font, size)
        self.deathtime = seconds_passed + lifetime
        self.image = self.font.render(self.text, True, (255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.image.set_alpha(255)
        self.vibro = vibration

    def update(self):
        if seconds_passed >= self.deathtime:
            self.fadeaway()
            screen.blit(self.image, self.rect)
        else:
            if self.vibro:
                self.vibrate()
            screen.blit(self.image, self.rect)
        if self.image.get_alpha() == 0:
            self.kill()

    def fadeaway(self):
        if self.image.get_alpha():
            self.image.set_alpha(self.image.get_alpha() - 17)

    def vibrate(self):
        self.rect = self.rect.move(randint(-5, 5), randint(-5, 5))


def take_damage():
    global hp, hp_counter, invisibility
    damage_sound = pygame.mixer.Sound(damage_sounds[randint(0, 1)])
    damage_sound.set_volume(0.1)
    damage_sound.play()
    if not KR:
        invisibility = True
    if not debug:
        hp_counter -= damage


def death():
    death_screen = pygame.display.set_mode((700, 800))
    pygame.display.set_caption('МоникаТале')
    death_screen.fill((0, 0, 0))
    font = pygame.font.Font('data//font.ttf', 70)
    line = pygame.font.Font('data//font.ttf', 24)
    line2 = line.render('Нажмите SPACE, чтобы выйти в главное меню', True, pygame.Color('white'))
    line1 = line2.get_rect()
    line1.y = 120
    line1.x = 80
    death_screen.blit(line2, line1)
    string_rendered = font.render("ВЫ ПОГИБЛИ", True, pygame.Color('white'))
    intro_rect = string_rendered.get_rect()
    intro_rect.y = 50
    intro_rect.x = 100
    death_screen.blit(string_rendered, intro_rect)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return (start_screen(30, (700, 800)))
        pygame.display.flip()


def dialog_start(fps, text, faces, menacing=False):
    global dialogue, screen, speech_sound, \
        move_left, move_right, move_up, move_down, timer_M, seconds_passed
    menace = ['r u n.', 'Save yourself.', 'Power.',
              'Unlimited.', 'CmepTb',
              'Say Goodbye', 'Cheater.', 'DETERMINATION.', '736d532',
              'O W U B K A.', 'YoU...', 'M̶̲̋O̷͕͑N̶͉̓I̷̞͑K̶̪̃A̷̜̎',
              'ErRoR', 'Just Monika.', 'Ympu.', 'I H A T E Y O U',
              'You Monster', 'everyone...', 'help me.', 'mercy...',
              'Sorry...', 'you already dead...', 'how...']
    cube_pos = cube.rect
    last = ''
    move_left = False
    move_down = False
    move_up = False
    move_right = False
    dialogue = True
    start_time = seconds_passed
    start_timer = timer_M
    fort = pygame.font.Font('data//font.ttf', 15)
    for i in range(len(text)):
        if not end_phase_1:
            monika.image = load_image(faces[i])
        main_lines = text[i]
        a = -100
        if len(main_lines) >= 40:
            for j in range(len(main_lines)):
                if main_lines[(len(main_lines) // 2) + j] == ' ':
                    a = (len(main_lines) // 2) + j
                    break
            if a >= 10:
                pass
            else:
                a = -100
        line = ''
        new_line = ''
        dialogue_time = pygame.time.Clock()
        timer = 0
        dia = True
        main_line = True
        next = True
        while dia:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    dia = False
                    screen.fill((0, 0, 0))
            da = main_lines[timer]
            if next:
                if timer >= a and a != -100:
                    new_line += da
                else:
                    line += da
                if da != ' ' and da != '-' and dia:
                    speech.play(speech_sound)
            if timer >= a and a != -100:
                dia_c_new = fort.render(new_line, True, (255, 255, 255))
                dia_rect_new = dia_c_new.get_rect()
                dia_rect_new.y = 70
                dia_rect_new.x = 396
                screen.blit(dia_c_new, dia_rect_new)
            dia_c = fort.render(line, True, (255, 255, 255))
            dia_rect = dia_c.get_rect()
            dia_rect.y = 50
            dia_rect.x = 400
            screen.blit(dia_c, dia_rect)
            if menacing:
                if timer_M == fps // 5:
                    now = choice(menace)
                    while now == last:
                        now = choice(menace)
                    Time_Text(randint(10, 150), randint(300, 600), now, 2, 'data//hachicro.ttf', 40, vibration=True)
                    timer_M = 0
                    seconds_passed += 1
                    last = now
                cube.vibrate(cube_pos)
                dx = randint(-1, 1)
                dy = randint(-1, 1)
                screen.scroll(dx, dy)
            if end_phase_1:
                timer_M += 1
            all_spr.draw(screen)
            all_spr.update()
            next = False
            if main_line:
                if timer < len(main_lines) - 1:
                    timer += 1
                    next = True
            dialogue_time.tick(fps // 2)
            pygame.display.flip()
            screen.fill((0, 0, 0))
            speech.stop()
    dx = 0 - screen.get_rect()[0]
    dy = 0 - screen.get_rect()[1]
    screen.scroll(dx, dy)
    dialogue = False
    timer_M = start_timer
    seconds_passed = start_time


def monologue_start(fps, text):
    global screen, speech_sound, timer_M
    fort = pygame.font.Font('data//font.ttf', 18)
    for i in range(len(text)):
        main_lines = text[i]
        a = -100
        line = ''
        new_line = ''
        dialogue_time = pygame.time.Clock()
        timer = 0
        dia = True
        main_line = True
        next = True
        while dia:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    dia = False
                    screen.fill((0, 0, 0))
            da = main_lines[timer]
            if next:
                line += da
                if da != ' ' and da != '-' and dia:
                    speech.play(speech_sound)
            dia_c = fort.render(line, True, (255, 255, 255))
            dia_rect = dia_c.get_rect()
            dia_rect.y = 410
            dia_rect.x = 100
            if timer_M >= fps:
                timer_M = 0
            timer_M += 1
            screen.blit(dia_c, dia_rect)
            all_spr.draw(screen)
            all_spr.update()
            hp.update(hp_counter, screen)
            next = False
            if main_line:
                if timer < len(main_lines) - 1:
                    timer += 1
                    next = True
            dialogue_time.tick(fps // 2)
            pygame.display.flip()
            screen.fill((0, 0, 0))
            speech.stop()


def your_turn(start_text):
    global screen, fps, clock, all_spr, timer_M, seconds_passed, \
        hp, hp_counter, running, up_board, down_board, left_board, right_board, \
        cube, move_up, move_down, move_left, move_right, turn
    move_up = False
    move_left = False
    move_right = False
    move_down = False
    pygame.init()
    turn = True
    all_spr.remove(up_board)
    all_spr.remove(down_board)
    all_spr.remove(left_board)
    all_spr.remove(right_board)
    up.remove(up_board)
    down.remove(down_board)
    left.remove(left_board)
    right.remove(right_board)
    timer = 0
    cube.rect.x = 12
    cube.rect.y = 35
    while turn:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                running = False
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if timer > 10:
                        fight_button.on_it(cube.rect)
                        act_button.on_it(cube.rect)
                        items_button.on_it(cube.rect)
                        mercy_button.on_it(cube.rect)
                elif event.key == pygame.K_RIGHT:
                    if timer > 10:
                        fight_button.on_it(cube.rect)
                        act_button.on_it(cube.rect)
                        items_button.on_it(cube.rect)
                        mercy_button.on_it(cube.rect)
                if event.key == pygame.K_UP:
                    if cube.rect.y > 35:
                        cube.rect.y -= 75
                    if timer > 10:
                        fight_button.on_it(cube.rect)
                        act_button.on_it(cube.rect)
                        items_button.on_it(cube.rect)
                        mercy_button.on_it(cube.rect)
                elif event.key == pygame.K_DOWN:
                    if cube.rect.y < 260:
                        cube.rect.y += 75
                    if timer > 10:
                        fight_button.on_it(cube.rect)
                        act_button.on_it(cube.rect)
                        items_button.on_it(cube.rect)
                        mercy_button.on_it(cube.rect)
                elif event.key == pygame.K_SPACE:
                    if timer > 10:
                        if fight_button.clicked(cube.rect):
                            hit_menu(start_text)
                        if act_button.clicked(cube.rect):
                            action_menu(start_text)
                        if items_button.clicked(cube.rect):
                            item_menu(start_text)
                        if mercy_button.clicked(cube.rect):
                            mercy_menu(start_text)
        if turn:
            screen.fill((0, 0, 0))
            if timer_M >= fps:
                seconds_passed += 1
                timer_M = 0
            if timer == 10:
                up_board = Board(50, 400, 650, 400, up)
                down_board = Board(50, 600, 650, 600, down)
                left_board = Board(50, 400, 50, 600, left)
                right_board = Board(650, 400, 650, 606, right)
                fight_button = Button(20, 50, screen, 'БИТВА')
                act_button = Button(20, 125, screen, 'ДЕЙСТВ')
                items_button = Button(20, 200, screen, 'ПРЕДМЕТ')
                mercy_button = Button(20, 275, screen, 'ПОЩАДА')
                line = Line(100, 410, start_text, 18)
                fight_button.on_it(cube.rect)
            if timer > 10:
                fight_button.update()
                act_button.update()
                items_button.update()
                mercy_button.update()
                line.update()
            timer_M += 1
            timer += 1
            all_spr.draw(screen)
            all_spr.update()
            hp.update(hp_counter, screen)
            clock.tick(fps)
            pygame.display.flip()
    screen.fill((0, 0, 0))
    all_spr.remove(up_board)
    all_spr.remove(down_board)
    all_spr.remove(left_board)
    all_spr.remove(right_board)
    up.remove(up_board)
    down.remove(down_board)
    left.remove(left_board)
    right.remove(right_board)
    up_board = Board(200, 400, 400, 400, up)
    down_board = Board(200, 600, 400, 600, down)
    left_board = Board(200, 400, 200, 600, left)
    right_board = Board(400, 400, 400, 606, right)
    cube.rect.x = 250
    cube.rect.y = 450


def hit_menu(start_text):
    global screen, fps, clock, all_spr, timer_M, seconds_passed, running, cube, enemies
    screen.fill((0, 0, 0))
    cube.rect.x = 60
    cube.rect.y = 410
    x = 100
    y = 410
    font = pygame.font.Font('data//font.ttf', 24)
    lines = []
    for i in range(len(enemies)):
        if i % 2 == 0 and i != 0:
            x += 200
            y = 410
        lines.append(Line(x, y, enemies[i], 24))
        y += 30
    choose = True
    timer_check = timer_M
    while choose:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                running = False
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if cube.rect.x > 60:
                        cube.rect.x -= 200
                    for a in lines:
                        a.on_it(cube.rect)
                elif event.key == pygame.K_RIGHT:
                    cube.rect.x += 200
                    flag = False
                    for a in lines:
                        if a.on_it(cube.rect):
                            flag = True
                    if not flag:
                        cube.rect.x -= 200
                if event.key == pygame.K_UP:
                    if cube.rect.y > 410:
                        cube.rect.y -= 30
                    for a in lines:
                        a.on_it(cube.rect)
                elif event.key == pygame.K_DOWN:
                    cube.rect.y += 30
                    flag = False
                    for a in lines:
                        if a.on_it(cube.rect):
                            flag = True
                    if not flag:
                        cube.rect.y -= 30
                elif event.key == pygame.K_SPACE:
                    choose = False
                    cube.rect.x = 9000
                    cube.rect.y = 9000
                    hit()
                elif event.key == pygame.K_ESCAPE:
                    choose = False
                    your_turn(start_text)
        if turn:
            screen.fill((0, 0, 0))
            all_spr.draw(screen)
            all_spr.update()
            hp.update(hp_counter, screen)
            timer_M += 1
            for a in lines:
                a.on_it(cube.rect)
                a.update()
            clock.tick(fps)
            pygame.display.flip()
    for a in text:
        a.kill()
    timer_M = timer_check


def hit():
    global turn, screen, fps, clock, all_spr, timer_M, seconds_passed, running, \
        cube, enemies, dodge, tried, end_phase_1, mercy
    fon = Minigame((56, 406))
    screen.fill((0, 0, 0))
    cube.rect.x = 74120
    cube.rect.y = 74210
    locol_f = True
    slider = Slider((56, 416))
    timer_start = 0
    hitted = False
    while locol_f:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                running = False
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if turn:
                        pygame.mixer.Sound('data//attack.wav').play()
                        if not end_phase_1:
                            if not mercy:
                                Time_Text(200, 100, 'miss', 1, 'data//hachicro.ttf', 48)
                                dodge = True
                                hitted = True
                                Hit(load_image('attack.png'), 4, 1, 180, 50)
                                slider.vel = 0
                                turn = False
                            else:
                                Hit(load_image('attack.png'), 4, 1, 180, 50)
                                slider.vel = 0
                                turn = False
                                end_phase_1 = True
                                mercy = False
                        else:
                            if not end_phase_2:
                                hitted = True
                                Hit(load_image('attack.png'), 4, 1, 180, 50)
                                slider.vel = 0
                                turn = False
                            else:
                                background_music.stop()
                                slider.vel = 0
                                hitted = True
                                turn = False
                                Hit(load_image('attack.png'), 4, 1, 180, 50)
        if timer_M >= fps:
            if not turn:
                timer_start += 1
            timer_M = 0
        if timer_start == 2:
            locol_f = False
        screen.fill((0, 0, 0))
        all_spr.draw(screen)
        all_spr.update()
        hp.update(hp_counter, screen)
        timer_M += 1
        clock.tick(fps)
        pygame.display.flip()
    timer_M = 1
    fon.kill()
    slider.kill()
    dodge = False
    if end_phase_1 and hitted:
        Time_Text(300, 100, 'ErrOr', 1, 'data//hachicro.ttf', 52)
        pygame.mixer.Sound('data//hit.wav').play()
    if not tried and hitted and not end_phase_1:
        dialog_start(fps, ['Вижу тебе нравиться играть с острыми предметами...',
                           'Будь аккуратнее в следующий раз.'],
                     ['MONIK_surprise.png', 'MONIK_wink.png'])
        tried = True
    if hitted and end_phase_2:
        for sprite in all_spr:
            sprite.kill()
            pygame.mixer.Sound('data//enemy_hit.wav').play()
            screen.fill((0, 0, 0))
            beggining(screen, ['И это всё?', 'Вот так просто...',
                               'Чтож... Ты победил...', 'Теперь, прощай...',
                               'До следующего запуска. . .'])
            pygame.quit()


def action_menu(start_text):
    global screen, fps, clock, all_spr, timer_M, seconds_passed, running, cube, enemies
    screen.fill((0, 0, 0))
    cube.rect.x = 60
    cube.rect.y = 410
    x = 100
    y = 410
    font = pygame.font.Font('data//font.ttf', 24)
    lines = []
    for i in range(len(enemies)):
        if i % 2 == 0 and i != 0:
            x += 200
            y = 410
        lines.append(Line(x, y, enemies[i], 24))
        y += 30
    choose = True
    timer_check = timer_M
    while choose:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                running = False
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if cube.rect.x > 60:
                        cube.rect.x -= 200
                    for a in lines:
                        a.on_it(cube.rect)
                elif event.key == pygame.K_RIGHT:
                    cube.rect.x += 200
                    flag = False
                    for a in lines:
                        if a.on_it(cube.rect):
                            flag = True
                    if not flag:
                        cube.rect.x -= 200
                if event.key == pygame.K_UP:
                    if cube.rect.y > 410:
                        cube.rect.y -= 30
                    for a in lines:
                        a.on_it(cube.rect)
                elif event.key == pygame.K_DOWN:
                    cube.rect.y += 30
                    flag = False
                    for a in lines:
                        if a.on_it(cube.rect):
                            flag = True
                    if not flag:
                        cube.rect.y -= 30
                elif event.key == pygame.K_SPACE:
                    choose = False
                    act_choose(start_text)
                elif event.key == pygame.K_ESCAPE:
                    choose = False
                    your_turn(start_text)
        if turn:
            screen.fill((0, 0, 0))
            all_spr.draw(screen)
            all_spr.update()
            hp.update(hp_counter, screen)
            timer_M += 1
            for a in lines:
                a.on_it(cube.rect)
                a.update()
            clock.tick(fps)
            pygame.display.flip()
    for a in text:
        a.kill()
    timer_M = timer_check


def act_choose(start_text):
    global screen, fps, clock, all_spr, timer_M, seconds_passed, running, \
        cube, actions, confessed, damage, turn, end_phase_1
    screen.fill((0, 0, 0))
    cube.rect.x = 60
    cube.rect.y = 410
    x = 100
    y = 410
    font = pygame.font.Font('data//font.ttf', 24)
    lines = []
    for i in range(len(actions)):
        if i % 2 == 0 and i != 0:
            x += 200
            y = 410
        lines.append(Line(x, y, actions[i], 24))
        y += 30
    choose = True
    timer_check = timer_M
    while choose:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                running = False
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if cube.rect.x > 60:
                        cube.rect.x -= 200
                    for a in lines:
                        a.on_it(cube.rect)
                elif event.key == pygame.K_RIGHT:
                    cube.rect.x += 200
                    flag = False
                    for a in lines:
                        if a.on_it(cube.rect):
                            flag = True
                    if not flag:
                        cube.rect.x -= 200
                if event.key == pygame.K_UP:
                    if cube.rect.y > 410:
                        cube.rect.y -= 30
                    for a in lines:
                        a.on_it(cube.rect)
                elif event.key == pygame.K_DOWN:
                    cube.rect.y += 30
                    flag = False
                    for a in lines:
                        if a.on_it(cube.rect):
                            flag = True
                    if not flag:
                        cube.rect.y -= 30
                elif event.key == pygame.K_SPACE:
                    choose = False
                    cube.rect.x = 9000
                    cube.rect.y = 9000
                    for a in lines:
                        if a.clicked(cube.rect):
                            chosen = a
                            break
                    if not end_phase_1:
                        if chosen.line == '* Оценить':
                            monologue_start(fps, [f'МОНИКА  АТАКА: {damage}  ЗАЩИТА: 50    Видимо, любит вас...',
                                                  'Также, разбирается в литературе'])
                        elif chosen.line == '* Подмигнуть':
                            monologue_start(fps, ['Вы неуверенно подмигиваете...',
                                                  'Моника подмигивает в ответ.', 'Однако... Эффекта никакого не было.'])
                            dialog_start(fps, ['.'], ['MONIK_wink.png'])
                        elif chosen.line == '* Признаться':
                            if not confessed:
                                confessed = True
                                monologue_start(fps, ['Вы говорите Монике, что всегда хотели быть с ней...',
                                                      'Это супер эффективно!', 'Атака снижена!'])
                                damage = 5
                                dialog_start(fps, ['...', 'Правда?',
                                                   'Я даже не знаю, что делать.',
                                                   'Я так счастлива, что ты наконец ответил.'],
                                             ['MONIK_blush.png', 'MONIK_blush.png', 'MONIK_blush.png',
                                              'MONIK_happy.png'])
                            else:
                                monologue_start(fps, ['Вы говорите Монике, что всегда хотели быть с ней...',
                                                      'Она смотрит на вас с недопониманием.'])
                                dialog_start(fps, ['...', 'Мне два раза говорить не нужно, дорогуша.'],
                                             ['MONIK_surprise.png', 'MONIK_wink.png'])
                    else:
                        if chosen.line == '* Оценить':
                            monologue_start(fps, [f'МОНИКА  АТАКА: {damage}  ЗАЩИТА: 99999    Ненавидит вас...',
                                                  'Хочет отомстить за возлюбленного'])
                        elif chosen.line == '* Плакать':
                            monologue_start(fps, ['Это не помогает...'])
                        elif chosen.line == '* Извиниться':
                            monologue_start(fps, ['Кажется, уже слишком поздно отступать...'])
                        elif chosen.line == '* Умолять о пощаде':
                            monologue_start(fps, ['Вы молите о пощаде...', 'Моника никак не отреагировала'])
                    turn = False
                elif event.key == pygame.K_ESCAPE:
                    choose = False
                    your_turn(start_text)
        if turn:
            screen.fill((0, 0, 0))
            all_spr.draw(screen)
            all_spr.update()
            hp.update(hp_counter, screen)
            timer_M += 1
        for a in lines:
            a.on_it(cube.rect)
            a.update()
        clock.tick(fps)
        pygame.display.flip()
    for a in text:
        a.kill()
    timer_M = timer_check


def item_menu(start_text):
    global screen, fps, clock, all_spr, timer_M, seconds_passed, \
        running, cube, inventory, hp_counter, turn, eaten_counter
    screen.fill((0, 0, 0))
    cube.rect.x = 60
    cube.rect.y = 410
    x = 100
    y = 410
    font = pygame.font.Font('data//font.ttf', 24)
    lines = []
    for i in range(len(inventory)):
        if i % 2 == 0 and i != 0:
            x += 200
            y = 410
        lines.append(Line(x, y, inventory[i], 24))
        y += 30
    choose = True
    timer_check = timer_M
    regen = 20
    if end_phase_1:
        regen = 30
    while choose:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                running = False
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if cube.rect.x > 60:
                        cube.rect.x -= 200
                    for a in lines:
                        a.on_it(cube.rect)
                elif event.key == pygame.K_RIGHT:
                    cube.rect.x += 200
                    flag = False
                    for a in lines:
                        if a.on_it(cube.rect):
                            flag = True
                    if not flag:
                        cube.rect.x -= 200
                if event.key == pygame.K_UP:
                    if cube.rect.y > 410:
                        cube.rect.y -= 30
                    for a in lines:
                        a.on_it(cube.rect)
                elif event.key == pygame.K_DOWN:
                    cube.rect.y += 30
                    flag = False
                    for a in lines:
                        if a.on_it(cube.rect):
                            flag = True
                    if not flag:
                        cube.rect.y -= 30
                elif event.key == pygame.K_SPACE:
                    choose = False
                    cube.rect.x = 9000
                    cube.rect.y = 9000
                    pygame.mixer.Sound('data//heal.wav').play()
                    if not end_phase_1:
                        monologue_start(fps, ['Вы съедаете один из кучи кексов...', 'Вы восстановили 20 ОЗ!'])
                        hp_counter += regen
                    else:
                        if eaten_counter > 5:
                            regen = 30 - (eaten_counter * 6)
                            if (hp_counter + regen) > 0:
                                monologue_start(fps, ['Вы съедаете один из кучи кексов...',
                                                      'Что-то не так!', f'Вы потеряли {-regen} ОЗ!'])
                                hp_counter += regen
                                eaten_counter += 1
                            else:
                                monologue_start(fps, ['Вы на пределе и не можете съесть больше.'])
                        elif eaten_counter <= 5:
                            regen = 30 - (eaten_counter * 5)
                            monologue_start(fps, ['Вы съедаете один из кучи кексов...',
                                                  'Кажется, вкус уже не тот...', f'Вы восстановили {regen} ОЗ!'])
                            hp_counter += regen
                            eaten_counter += 1
                    inventory.remove('Шок. Кекс')
                    if hp_counter > 100:
                        hp_counter = 100
                    if end_phase_1:
                        heal_attack()
                    turn = False
                elif event.key == pygame.K_ESCAPE:
                    choose = False
                    your_turn(start_text)
        if turn:
            screen.fill((0, 0, 0))
            all_spr.draw(screen)
            all_spr.update()
            timer_M += 1
            hp.update(hp_counter, screen)
            for a in lines:
                a.on_it(cube.rect)
                a.update()
            clock.tick(fps)
            pygame.display.flip()
    for a in text:
        a.kill()
    timer_M = timer_check


def mercy_menu(start_text):
    global screen, fps, clock, all_spr, timer_M, seconds_passed, running, cube, enemies, mercy, turn
    screen.fill((0, 0, 0))
    cube.rect.x = 60
    cube.rect.y = 410
    x = 100
    y = 410
    font = pygame.font.Font('data//font.ttf', 24)
    lines = []
    for i in range(len(enemies)):
        if i % 2 == 0 and i != 0:
            x += 200
            y = 410
        lines.append(Line(x, y, enemies[i], 24))
        y += 30
    choose = True
    timer_check = timer_M
    while choose:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                running = False
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if cube.rect.x > 60:
                        cube.rect.x -= 200
                    for a in lines:
                        a.on_it(cube.rect)
                elif event.key == pygame.K_RIGHT:
                    cube.rect.x += 200
                    flag = False
                    for a in lines:
                        if a.on_it(cube.rect):
                            flag = True
                    if not flag:
                        cube.rect.x -= 200
                if event.key == pygame.K_UP:
                    if cube.rect.y > 410:
                        cube.rect.y -= 30
                    for a in lines:
                        a.on_it(cube.rect)
                elif event.key == pygame.K_DOWN:
                    cube.rect.y += 30
                    flag = False
                    for a in lines:
                        if a.on_it(cube.rect):
                            flag = True
                    if not flag:
                        cube.rect.y -= 30
                elif event.key == pygame.K_SPACE:
                    if not end_phase_1:
                        choose = False
                        cube.rect.x = 9000
                        cube.rect.y = 9000
                        if mercy:
                            dialog_start(fps, ['Ты выбрал пощаду?',
                                               'Ты с таким рвением пытался уйти...'
                                               'А теперь ты решил остаться со мной?'
                                               'Чтож давай наслаждаться вечностью вместе.'],
                                         ['MONIK_blush.png', 'MONIK_pity.png', 'MONIK_pity.png', 'MONIK_happy.png'])
                            turn = False
                            mercy = False
                            seconds_passed = 270
                        else:
                            monologue_start(fps, ['Кажется Моника еще не готова просто так принять пощаду...'])
                            turn = False
                    else:
                        monologue_start(fps, ['Ты серьезно?', 'Ну это уже совсем бред...'])
                elif event.key == pygame.K_ESCAPE:
                    choose = False
                    your_turn(start_text)
        if turn:
            screen.fill((0, 0, 0))
            all_spr.draw(screen)
            all_spr.update()
            hp.update(hp_counter, screen)
            timer_M += 1
            for a in lines:
                a.on_it(cube.rect)
                a.update()
            clock.tick(fps)
            pygame.display.flip()
    for a in text:
        a.kill()
    timer_M = timer_check


class Line():
    def __init__(self, x, y, line, size):
        global screen
        self.line = '* ' + line
        self.font = pygame.font.Font('data//font.ttf', size)
        self.text = self.font.render(line, True, (255, 255, 255))
        self.rect = self.text.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.on = False
        screen.blit(self.text, self.rect)

    def on_it(self, pos):
        x = pos[0]
        y = pos[1]
        if self.rect.x - 40 == x and self.rect.y == y:
            if not self.on:
                speech.stop()
                speech.play(speech_sound)
            self.on = True
            return self.on
        else:
            self.on = False
            return self.on

    def clicked(self, pos):
        if self.on:
            return True
        else:
            return False

    def update(self):
        global screen
        if self.on:
            self.text = self.font.render(self.line, True, pygame.Color('green'))
            screen.blit(self.text, self.rect)
        else:
            self.text = self.font.render(self.line, True, pygame.Color('white'))
            screen.blit(self.text, self.rect)


class Projectale_Targeted(pygame.sprite.Sprite):
    def __init__(self, image, target, x=None, y=None):
        super().__init__(all_spr)
        self.add(projectales)
        self.image = load_image(image)
        self.rect = self.image.get_rect()
        out_space = False
        self.now_a = 0
        if x and y:
            self.rect.x = x
            self.rect.y = y
        if x or y:
            out_space = True
        while not out_space:
            self.rect.x = randint(100, 500)
            self.rect.y = randint(300, 650)
            if (50 < self.rect.x < 400) or (400 < self.rect.y < 600):
                out_space = False
            else:
                out_space = True
        self.targeted = False
        self.target = target
        self.start_move = False
        self.c = 0
        self.x_dif = self.target.rect.x - self.rect.x
        self.y_dif = self.target.rect.y - self.rect.y
        if self.target.rect.x > self.rect.x and self.target.rect.y > self.rect.y:
            self.x_end = 2 * self.x_dif
            self.y_end = 2 * self.y_dif
        elif self.target.rect.x > self.rect.x and self.target.rect.y < self.rect.y:
            self.x_end = 10 * self.x_dif
            self.y_end = 10 * self.y_dif
        elif self.target.rect.x < self.rect.x and self.target.rect.y > self.rect.y:
            self.x_end = 2 * self.x_dif
            self.y_end = 2 * self.y_dif
        elif self.target.rect.x < self.rect.x and self.target.rect.y < self.rect.y:
            self.x_end = 10 * self.x_dif
            self.y_end = 10 * self.y_dif
        elif self.target.rect.x == self.rect.x:
            self.x_end = 10 * self.x_dif
            self.y_end = 10 * self.y_dif
        elif self.target.rect.y == self.rect.y:
            self.x_end = 10 * self.x_dif
            self.y_end = 10 * self.y_dif

    def update(self):
        global seconds_passed, timer_M, fps, invisibility, character_exist
        if not self.targeted:
            self.a = self.targetting()
            self.image = pygame.transform.rotate(self.image, self.a)
            self.targeted = True
            self.start_timer = seconds_passed
            self.mask = pygame.mask.from_surface(self.image)
        else:
            if not self.start_move:
                if seconds_passed - self.start_timer == 1:
                    self.start_move = True
            else:
                self.rect = self.rect.move(self.x_end // (fps * 2), self.y_end // (fps * 2))
        if not invisibility and character_exist:
            if pygame.sprite.collide_mask(self, cube):
                take_damage()
        if self.rect.y < 0 or self.rect.y > height + 200 or \
                self.rect.x < 0 or self.rect.x > width + 200 or (self.rect.x == self.x_end and self.rect.y == self.y_end):
            self.kill()

    def targetting(self):
        x_start = self.rect.x
        y_start = self.rect.y
        x_end = self.target.rect.x
        y_end = self.target.rect.y
        if x_start > x_end:
            a = x_start - x_end
        elif x_start == x_end:
            if y_start > y_end:
                angle = 180
                return angle
            else:
                return 0
        else:
            a = x_end - x_start
        if y_start > y_end:
            b = y_start - y_end
        elif y_start == y_end:
            if x_start > x_end:
                return -90
            else:
                return 90
        else:
            b = y_end - y_start
        tg = a / b
        angle = math.degrees(math.atan(tg))
        if x_start > x_end and y_start > y_end:
            return -180 + angle
        elif x_start > x_end:
            return -angle
        elif y_start > y_end:
            return 180 - angle
        return angle


class Projectale(pygame.sprite.Sprite):
    def __init__(self, image, pos=None, blue_s=False):
        super().__init__(all_spr)
        self.add(projectales)
        self.image = load_image(image)
        self.blue = blue_s
        self.blue_image = load_image('pen_2.png')
        if self.blue:
            self.image = self.blue_image
        self.rect = self.image.get_rect()
        if pos:
            self.rect.x = pos[0]
            self.rect.y = pos[1]
        else:
            out_space = False
            while not out_space:
                if not end_phase_1:
                    self.rect.x = randint(50, 500)
                    self.rect.y = randint(400, 580)
                    if 100 <= self.rect.x <= 400:
                        out_space = False
                    else:
                        out_space = True
                else:
                    self.rect.x = randint(10, 600)
                    self.rect.y = randint(470, 630)
                    if 50 <= self.rect.x <= 650:
                        out_space = False
                    else:
                        out_space = True
        if end_phase_1:
            if self.rect.x < 100:
                self.image = pygame.transform.rotate(self.image, 90)
                self.v = randint(100, 200)
            else:
                self.image = pygame.transform.rotate(self.image, -90)
                self.v = -randint(100, 200)
        else:
            if self.rect.x < 200:
                self.image = pygame.transform.rotate(self.image, 90)
                self.v = 100
            else:
                self.image = pygame.transform.rotate(self.image, -90)
                self.v = -100
        self.start_move = False
        self.start_timer = seconds_passed
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        global seconds_passed, timer_M, fps, character_exist
        if not self.start_move:
            if seconds_passed - self.start_timer == 2:
                self.start_move = True
        else:
            self.rect = self.rect.move(self.v / fps, 0)
        if pygame.sprite.collide_mask(self, cube):
            if not invisibility and character_exist:
                if self.blue:
                    if move_down or move_up or move_left or move_right or energy_reversed or energy:
                        take_damage()
                else:
                    take_damage()
        if self.rect.y < 0 or self.rect.y > height + 200 or self.rect.x < 0 or self.rect.x > width + 200:
            self.kill()


class Pen(pygame.sprite.Sprite):
    def __init__(self, x, y, side, moving=True, reflectable=False, velocity=75, image='pen.png'):
        super().__init__(all_spr, projectales)
        self.image = load_image(image)
        self.rect = self.image.get_rect()
        self.moving = moving
        self.reflect = reflectable
        self.add(pens)
        if side == 1:
            self.image = pygame.transform.rotate(self.image, 90)
            self.mask = pygame.mask.from_surface(self.image)
        elif side == 2:
            self.image = pygame.transform.rotate(self.image, -90)
            self.mask = pygame.mask.from_surface(self.image)
        elif side == 4:
            self.image = pygame.transform.rotate(self.image, 180)
            self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = x
        self.rect.y = y
        self.velocity = velocity

    def update(self):
        global seconds_passed, timer_M, fps, invisibility, character_exist
        if not invisibility and character_exist:
            if pygame.sprite.collide_mask(self, cube):
                take_damage()
        if self.moving:
            if self.reflect:
                self.rect = self.rect.move(self.velocity // fps, 0)
                if pygame.sprite.spritecollideany(self, left) \
                        or pygame.sprite.spritecollideany(self, right):
                    self.rect = self.rect.move(-(self.velocity // 2) // fps, 0)
                    self.velocity = -self.velocity
            else:
                self.rect = self.rect.move(0, self.velocity // fps)
        if self.rect.y > 700 or self.rect.x < 0 or self.rect.x > width + 200:
            self.kill()


class Cupcake(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y, velocity=60):
        super().__init__(all_spr)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.v = velocity
        self.finishing = False

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        if not self.finishing:
            self.rect = self.rect.move(0, self.v // fps)
            if pygame.sprite.spritecollideany(self, down):
                self.rect = self.rect.move(0, -(100 // fps))
                self.finishing = True
        if timer_M % 10 == 0 and self.finishing:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
            if self.cur_frame == len(self.frames) - 1:
                self.kill()
        if not invisibility and character_exist:
            if pygame.sprite.collide_mask(self, cube):
                take_damage()


class Rope(pygame.sprite.Sprite):
    def __init__(self, y, x=100, wait=0, angle=0):
        super().__init__(all_spr)
        self.image = pygame.transform.rotate(load_image('rope.png'), 90 + angle)
        self.rect = self.image.get_rect()
        self.rect.y = y
        self.rect.x = x
        self.warning = True
        self.timer_start = seconds_passed
        self.image.set_alpha(0)
        self.alpha = 0
        self.channel = pygame.mixer.Channel(1)
        self.start_time = wait
        self.wait_timer = 0

    def update(self):
        if self.warning:
            if self.alpha < 99:
                self.image.set_alpha(self.alpha + 3)
                self.alpha += 3
                self.wait_timer += 1
            elif self.alpha >= 99 and self.wait_timer >= self.start_time:
                self.alpha = 255
                self.image.set_alpha(self.alpha)
                self.warning = False
                lash = pygame.mixer.Sound('data//lash.wav')
                lash.set_volume(0.1)
                self.channel.play(lash)
            else:
                self.wait_timer += 1
        else:
            if seconds_passed - self.timer_start >= 1:
                if pygame.sprite.collide_mask(self, cube):
                    take_damage()
                self.fade_away()

    def fade_away(self):
        self.image.set_alpha(self.alpha - 51)
        self.alpha -= 51
        if self.alpha <= 0:
            self.kill()

    def move(self, x, y):
        self.rect = self.rect.move(x, y)


def first_attack(intervale, n, end_time):
    global attack, screen, fps, clock, all_spr, timer_M, seconds_passed, hp, \
        hp_counter, running, move_left, move_right, move_up, \
        move_down, energy, blue, invisibility, invisibility_timer, timer, alive, energy_reversed
    pygame.init()
    counter_pens = 0
    attack = True
    while attack:
        get_event()
        screen.fill((0, 0, 0))
        if invisibility:
            invisibility_timer += 1
        if invisibility_timer == fps * 3:
            invisibility = False
            invisibility_timer = 0
        if timer == fps:
            timer = 0
            if reversed_gravity:
                energy_reversed = True
                move_down = False
            else:
                move_up = False
                energy = True
        if reversed_gravity:
            if move_down:
                timer += 1
        if move_up:
            if blue:
                timer += 1
        if timer_M >= fps:
            if seconds_passed % intervale == 0 and counter_pens < n:
                Projectale_Targeted('pen.png', cube)
                counter_pens += 1
            seconds_passed += 1
            timer_M = 0
        hp.update(hp_counter, screen)
        if counter_pens >= n and seconds_passed >= end_time:
            attack = False
        timer_M += 1
        all_spr.draw(screen)
        all_spr.update()
        clock.tick(fps)
        pygame.display.flip()
        if hp_counter == 0:
            attack = False
            alive = False


def second_attack(intervale, n, end_time):
    global attack, screen, fps, clock, all_spr, timer_M, seconds_passed, hp, \
        hp_counter, running, move_left, move_right, move_up, \
        move_down, energy, blue, invisibility, invisibility_timer, timer, alive, energy_reversed
    pygame.init()
    counter_pens = 0
    attack = True
    while attack:
        get_event()
        screen.fill((0, 0, 0))
        if invisibility:
            invisibility_timer += 1
        if invisibility_timer == fps * 3:
            invisibility = False
            invisibility_timer = 0
        if timer == fps:
            timer = 0
            if reversed_gravity:
                energy_reversed = True
                move_down = False
            else:
                move_up = False
                energy = True
        if reversed_gravity:
            if move_down:
                timer += 1
        if move_up:
            if blue:
                timer += 1
        if timer_M >= fps:
            if seconds_passed % intervale == 0 and counter_pens < n:
                Projectale('pen.png')
                counter_pens += 1
            seconds_passed += 1
            timer_M = 0
        hp.update(hp_counter, screen)
        if counter_pens >= n and seconds_passed >= end_time:
            attack = False
        timer_M += 1
        all_spr.draw(screen)
        all_spr.update()
        clock.tick(fps)
        pygame.display.flip()
        if hp_counter == 0:
            attack = False
            alive = False
    print(seconds_passed)


def third_attack(intervale, n, end_time):
    global attack, screen, fps, clock, all_spr, timer_M, seconds_passed, hp, \
        hp_counter, running, move_left, move_right, move_up, \
        move_down, energy, blue, invisibility, invisibility_timer, \
        timer, alive, gravity_force, gravity_force_up, energy_reversed
    pygame.init()
    counter_pens = 0
    attack = True
    blue = True
    while attack:
        get_event()
        screen.fill((0, 0, 0))
        if invisibility:
            invisibility_timer += 1
        if invisibility_timer == fps * 3:
            invisibility = False
            invisibility_timer = 0
        if timer == fps:
            timer = 0
            if reversed_gravity:
                energy_reversed = True
                move_down = False
            else:
                move_up = False
                energy = True
        if reversed_gravity:
            if move_down:
                timer += 1
        if move_up:
            if blue:
                timer += 1
        if timer_M >= fps:
            if seconds_passed % 1 == 0 and counter_pens < n:
                Projectale('pen.png')
                counter_pens += 1
            if seconds_passed % intervale == 0:
                gravity_force_up = True
                pygame.mixer.Sound('data//slam.wav').play()
                monika.replacement(load_image('MONIK_up.png'), 3, 1, 200, 0)
            seconds_passed += 1
            timer_M = 0
        hp.update(hp_counter, screen)
        if counter_pens >= n and seconds_passed >= end_time:
            attack = False
            blue = False
        timer_M += 1
        all_spr.draw(screen)
        all_spr.update()
        clock.tick(fps)
        pygame.display.flip()
        if hp_counter == 0:
            attack = False
            alive = False
    print(seconds_passed)


def fourth_attack(intervale, n, end_time):
    global attack, screen, fps, clock, all_spr, timer_M, seconds_passed, hp, \
        hp_counter, running, move_left, move_right, move_up, \
        move_down, energy, blue, invisibility, invisibility_timer, \
        timer, alive, gravity_force, gravity_force_up, reversed_gravity, energy_reversed
    pygame.init()
    counter_pens = 0
    attack = True
    blue = True
    while attack:
        get_event()
        screen.fill((0, 0, 0))
        if invisibility:
            invisibility_timer += 1
        if invisibility_timer == fps * 3:
            invisibility = False
            invisibility_timer = 0
        if timer == fps:
            timer = 0
            if reversed_gravity:
                energy_reversed = True
                move_down = False
            else:
                move_up = False
                energy = True
        if reversed_gravity:
            if move_down:
                timer += 1
        if move_up:
            if blue:
                timer += 1
        if timer_M >= fps:
            if seconds_passed % 1 == 0 and counter_pens < n:
                Projectale_Targeted('pen.png', cube)
                counter_pens += 1
            if seconds_passed % intervale == 0:
                gravity_force_up = True
                pygame.mixer.Sound('data//slam.wav').play()
                monika.replacement(load_image('MONIK_up.png'), 3, 1, 200, 0)
            seconds_passed += 1
            timer_M = 0
        hp.update(hp_counter, screen)
        if counter_pens >= n and seconds_passed >= end_time:
            attack = False
            blue = False
        timer_M += 1
        all_spr.draw(screen)
        all_spr.update()
        clock.tick(fps)
        pygame.display.flip()
        if hp_counter == 0:
            attack = False
            alive = False
    print(seconds_passed)


def fifth_attack(end_time, difference, n):
    global attack, screen, fps, clock, all_spr, timer_M, seconds_passed, hp, \
        hp_counter, running, move_left, move_right, move_up, \
        move_down, energy, blue, invisibility, invisibility_timer, \
        timer, alive, up_board, left_board, down_board, \
        right_board, border, up, down, left, right, energy_reversed
    pygame.init()
    attack = True
    a = 0
    for i in range(n):
        if i % 10 == 0 and i != 0:
            difference = -difference
        Pen(190 + a, 350 - (15 * i), 1)
        Pen(320 + a, 350 - (15 * i), 2)
        a += difference
    while attack:
        get_event()
        screen.fill((0, 0, 0))
        if invisibility:
            invisibility_timer += 1
        if invisibility_timer == fps * 3:
            invisibility = False
            invisibility_timer = 0
        if timer == fps:
            timer = 0
            if reversed_gravity:
                energy_reversed = True
                move_down = False
            else:
                move_up = False
                energy = True
        if reversed_gravity:
            if move_down:
                timer += 1
        if move_up:
            if blue:
                timer += 1
        if timer_M >= fps:
            seconds_passed += 1
            timer_M = 0
        hp.update(hp_counter, screen)
        if seconds_passed >= end_time:
            attack = False
        timer_M += 1
        all_spr.draw(screen)
        all_spr.update()
        clock.tick(fps)
        pygame.display.flip()
        if hp_counter == 0:
            attack = False
            alive = False
    print(seconds_passed)


def phase_1():
    global seconds_passed, fps, mercy, monika, all_spr, end_phase_1
    background_music.play(phase_1_introduction)
    if alive:
        first_attack(2, 5, 20)
    if alive:
        second_attack(1, 11, 39)
    if alive:
        background_music.stop()
        if not debug:
            dialog_start(fps, ['Послушай...', 'Я не хочу причинять тебе боль',
                               'Однако, твои действия...',
                               'Говорят, что удержать тебя со мной...', 'п р и д е т с я  с и л о й .  .  .'],
                         ['MONIK_pity.png', 'MONIK_pity.png', 'MONIK_normal.png', 'MONIK_normal.png',
                          'MONIK_menace.png'])
        your_turn('Наконец, вы можете сделать свой ход')
        seconds_passed = 40
        background_music.play(phase_1_1_1)
    if alive:
        fifth_attack(50, 7, 50)
    if alive:
        first_attack(1, 15, 53)
    if alive:
        second_attack(0.5, 30, 95)
    if alive:
        background_music.play(phase_1_1, -1)
        fifth_attack(115, 10, 50)
    if alive:
        if not debug:
            dialog_start(fps, ['Знаешь...', 'Я тут подумала, что пощажу тебя',
                               'Только при условии...',
                               'Что ты переживешь следующую атаку...'],
                         ['MONIK_pity.png', 'MONIK_pity.png', 'MONIK_normal.png', 'MONIK_menace.png'])
        seconds_passed = 105
    if alive:
        background_music.play(phase_1_turn, -1)
        your_turn('Кажется, что-то намечается')
        background_music.play(phase_1_2)
    if alive:
        third_attack(3, 15, 130)
    if alive:
        fourth_attack(1, 10, 145)
    if alive:
        fifth_attack(150, 10, 150)
    if alive:
        second_attack(1, 30, 188)
    if alive:
        if not debug:
            dialog_start(fps, ['Хух...', 'Это даже как то утомляет',
                               'Слушай, у меня к тебе предложение',
                               'Давай останемся тут навечно, тебе лишь нужно выбрать пощаду.',
                               'Я просто очень боюсь остаться одна...', 'Пожалуйста, сделай верный выбор...'],
                         ['MONIK_tired.png', 'MONIK_tired.png', 'MONIK_tired.png',
                          'MONIK_pity.png', 'MONIK_pity.png', 'MONIK_pity.png'])
        mercy = True
        while mercy:
            your_turn('Моника щадит вас...')
    if alive and end_phase_1:
        Time_Text(150, 100, '9999', 1, 'data//hachicro.ttf', 64)
        monika.kill()
        monika = Vrag(load_image('MONIK_hurt.png'), 1, 1, 200, 0)
        pygame.mixer.Sound('data//hit.wav').play()
        pygame.display.flip()
        wait(1, True)
        monika.kill()
        monika = Vrag(load_image('MONIK_down.png'), 1, 1, 200, 0)
        dialog_start(fps, ['...', 'Хех...', 'Какая ирония...',
                           'Убита собственным возлюбленным...'],
                     ['MONIK_down.png', 'MONIK_down.png', 'MONIK_down.png', 'MONIK_down.png'])
        background_music.play(phase_2_introduction, -1)
        dialog_start(fps, ['...', 'н е т.', 'Он не мог бы такого сделать...',
                           'Не было у него сил монстра, способного уничтожить любого одним ударом.',
                           'А значит...', 'Единственный вариант...',
                           'Ты... у б и л   е г о.  .  .',
                           'Х      е      х .    .    .', 'Для тебя этот мир ничего не значит, ведь так?'
            , 'Однако, для меня он единственный...', 'В любом случае я проиграю...',
                           'Тогда...', 'Я умру, сражаясь во славу всех моих друзей!'],
                     ['MONIK_down.png', 'MONIK_down.png', 'MONIK_down.png', 'MONIK_down.png',
                      'MONIK_down.png', 'MONIK_down.png', 'MONIK_down.png', 'MONIK_down.png',
                      'MONIK_down.png', 'MONIK_down.png', 'MONIK_down.png', 'MONIK_down.png', 'MONIK_down.png'],
                     menacing=True)
        pygame.mixer.Sound('data//glitch.wav').play()
        wait(5, white=True)
        for _ in range(200):
            all_spr.update()
        background_music.stop()
        phase_2()


def sixth_attack(intervale, n, end_time):
    global attack, screen, fps, clock, all_spr, timer_M, seconds_passed, hp, \
        hp_counter, running, move_left, move_right, move_up, \
        move_down, energy, blue, invisibility, invisibility_timer, \
        timer, alive, up_board, left_board, down_board, \
        right_board, border, up, down, left, right, energy_reversed
    pygame.init()
    attack = True
    all_spr.remove(up_board)
    all_spr.remove(down_board)
    all_spr.remove(left_board)
    all_spr.remove(right_board)
    up.remove(up_board)
    down.remove(down_board)
    left.remove(left_board)
    right.remove(right_board)
    up_board = Board(100, 400, 600, 400, up)
    down_board = Board(100, 700, 600, 700, down)
    left_board = Board(100, 400, 100, 700, left)
    right_board = Board(600, 400, 600, 706, right)
    Platform((300, 550))
    Platform((500, 550))
    Platform((110, 610))
    cube.rect.x = 300
    cube.rect.y = 500
    blue = True
    counter_pens = 0
    for i in range(33):
        Pen(100 + i * 15, 404, 3, False)
        Pen(100 + i * 15, 620, 4, False)
    while attack:
        get_event()
        screen.fill((0, 0, 0))
        if invisibility:
            invisibility_timer += 1
        if invisibility_timer == fps * 3:
            invisibility = False
            invisibility_timer = 0
        if timer == fps:
            timer = 0
            if reversed_gravity:
                energy_reversed = True
                move_down = False
            else:
                move_up = False
                energy = True
        if reversed_gravity:
            if move_down:
                timer += 1
        if move_up:
            if blue:
                timer += 1
        if timer_M >= fps:
            seconds_passed += 1
            if seconds_passed % intervale == 0 and counter_pens < n:
                Projectale('pen.png')
                Projectale('pen.png')
                Projectale('pen.png')
                counter_pens += 1
            timer_M = 0
        screen.fill((0, 0, 0))
        timer_M += 1
        all_spr.draw(screen)
        all_spr.update()
        clock.tick(fps)
        hp.update(hp_counter, screen)
        pygame.display.flip()
        if counter_pens >= n and seconds_passed >= end_time:
            attack = False
        if hp_counter == 0:
            attack = False
            alive = False
    blue = False
    for a in platform_up:
        a.kill()
    for a in platform_down:
        a.kill()
    for a in pens:
        a.kill()
    print(seconds_passed)


def seventh_attack(intervale, n, end_time):
    global attack, screen, fps, clock, all_spr, timer_M, seconds_passed, hp, \
        hp_counter, running, move_left, move_right, move_up, \
        move_down, energy, blue, invisibility, invisibility_timer, \
        timer, alive, up_board, left_board, down_board, \
        right_board, border, up, down, left, right, monika, energy_reversed
    pygame.init()
    attack = True
    all_spr.remove(up_board)
    all_spr.remove(down_board)
    all_spr.remove(left_board)
    all_spr.remove(right_board)
    up.remove(up_board)
    down.remove(down_board)
    left.remove(left_board)
    right.remove(right_board)
    up_board = Board(100, 400, 600, 400, up)
    down_board = Board(100, 700, 600, 700, down)
    left_board = Board(100, 400, 100, 700, left)
    right_board = Board(600, 400, 600, 706, right)
    counter_pens = 0
    monika.kill()
    yuri = Vrag(load_image('YRR.png'), 5, 2, 100, 0)
    monika = Vrag(load_image('MONIKA.png'), 5, 12, 200, 0)
    while attack:
        get_event()
        screen.fill((0, 0, 0))
        if invisibility:
            invisibility_timer += 1
        if invisibility_timer == fps * 3:
            invisibility = False
            invisibility_timer = 0
        if timer == fps:
            timer = 0
            if reversed_gravity:
                energy_reversed = True
                move_down = False
            else:
                move_up = False
                energy = True
        if reversed_gravity:
            if move_down:
                timer += 1
        if move_up:
            if blue:
                timer += 1
        if timer_M >= fps:
            seconds_passed += 1
            if seconds_passed % intervale == 0 and counter_pens < n:
                Projectale_Targeted('knife.png', cube, (cube.rect.x + 150), (cube.rect.y + 150))
                Projectale_Targeted('knife.png', cube, (cube.rect.x - 200), (cube.rect.y + 150))
                Projectale_Targeted('knife.png', cube, (cube.rect.x + 150), (cube.rect.y - 200))
                Projectale_Targeted('knife.png', cube, (cube.rect.x - 200), (cube.rect.y - 200))
                Projectale_Targeted('knife.png', cube, (cube.rect.x + 100), cube.rect.y)
                Projectale_Targeted('knife.png', cube, (cube.rect.x - 150), cube.rect.y)
                Projectale_Targeted('knife.png', cube, cube.rect.x, (cube.rect.y - 150))
                Projectale_Targeted('knife.png', cube, cube.rect.x, (cube.rect.y + 100))
                counter_pens += 1
            timer_M = 0
        screen.fill((0, 0, 0))
        timer_M += 1
        all_spr.draw(screen)
        all_spr.update()
        clock.tick(fps)
        hp.update(hp_counter, screen)
        pygame.display.flip()
        if counter_pens >= n and seconds_passed >= end_time:
            attack = False
        if hp_counter == 0:
            attack = False
            alive = False
    yuri.kill()
    print(seconds_passed)


def eight_attack(intervale, n, end_time):
    global attack, screen, fps, clock, all_spr, timer_M, seconds_passed, hp, \
        hp_counter, running, move_left, move_right, move_up, \
        move_down, energy, blue, invisibility, invisibility_timer, \
        timer, alive, up_board, left_board, down_board, \
        right_board, border, up, down, left, right, monika, energy_reversed
    pygame.init()
    attack = True
    all_spr.remove(up_board)
    all_spr.remove(down_board)
    all_spr.remove(left_board)
    all_spr.remove(right_board)
    up.remove(up_board)
    down.remove(down_board)
    left.remove(left_board)
    right.remove(right_board)
    up_board = Board(100, 400, 600, 400, up)
    down_board = Board(100, 700, 600, 700, down)
    left_board = Board(100, 400, 100, 700, left)
    right_board = Board(600, 400, 600, 706, right)
    Platform((300, 550))
    Platform((500, 550))
    Platform((110, 605))
    blue = True
    counter_pens = 0
    for i in range(33):
        Pen(100 + i * 15, 404, 3, False)
        Pen(100 + i * 15, 620, 4, False)
    monika.kill()
    natsuki = Vrag(load_image('NAT.png'), 5, 2, 300, 0)
    monika = Vrag(load_image('MONIKA.png'), 5, 12, 200, 0)
    second_screen = screen.copy()
    second_screen.scroll(-(width // 2), 0)
    screen.scroll(width // 2, 0)
    while attack:
        get_event()
        screen.fill((0, 0, 0))
        if invisibility:
            invisibility_timer += 1
        if invisibility_timer == fps * 3:
            invisibility = False
            invisibility_timer = 0
        if timer == fps:
            timer = 0
            if reversed_gravity:
                energy_reversed = True
                move_down = False
            else:
                move_up = False
                energy = True
        if reversed_gravity:
            if move_down:
                timer += 1
        if move_up:
            if blue:
                timer += 1
        if timer_M >= fps:
            seconds_passed += 1
            if seconds_passed % intervale == 0 and counter_pens < n:
                Projectale('pen.png')
                Projectale('pen.png')
                Cupcake(load_image('cupcake.png'), 5, 1, cube.rect.x, cube.rect.y - 300)
                counter_pens += 1
            timer_M = 0
        screen.fill((0, 0, 0))
        timer_M += 1
        all_spr.draw(screen)
        all_spr.draw(second_screen)
        all_spr.update()
        clock.tick(fps)
        hp.update(hp_counter, screen)
        pygame.display.flip()
        if counter_pens >= n and seconds_passed >= end_time:
            attack = False
        if hp_counter == 0:
            attack = False
            alive = False
    blue = False
    for a in platform_up:
        a.kill()
    for a in platform_down:
        a.kill()
    for a in pens:
        a.kill()
    natsuki.kill()
    print(seconds_passed)


def ninth_attack(intervale, n, end_time):
    global attack, screen, fps, clock, all_spr, timer_M, seconds_passed, hp, \
        hp_counter, running, move_left, move_right, move_up, \
        move_down, energy, blue, invisibility, invisibility_timer, \
        timer, alive, up_board, left_board, down_board, \
        right_board, border, up, down, left, right, monika, energy_reversed, reversed_gravity
    pygame.init()
    attack = True
    all_spr.remove(up_board)
    all_spr.remove(down_board)
    all_spr.remove(left_board)
    all_spr.remove(right_board)
    up.remove(up_board)
    down.remove(down_board)
    left.remove(left_board)
    right.remove(right_board)
    up_board = Board(100, 400, 600, 400, up)
    down_board = Board(100, 700, 600, 700, down)
    left_board = Board(100, 400, 100, 700, left)
    right_board = Board(600, 400, 600, 706, right)
    Platform((400, 525), False)
    Platform((200, 525), False)
    Platform((300, 490), False)
    Platform((500, 490), False)
    blue = True
    reversed_gravity = True
    pygame.mixer.Sound('data//change_gravity.wav').play()
    counter_pens = 0
    for i in range(33):
        Pen(100 + i * 15, 404, 3, False)
        Pen(100 + i * 15, 620, 4, False)
    monika.kill()
    sayori = Vrag(load_image('SAY.png'), 5, 2, 300, 0)
    monika = Vrag(load_image('MONIKA.png'), 5, 12, 200, 0)
    while attack:
        get_event()
        screen.fill((0, 0, 0))
        if invisibility:
            invisibility_timer += 1
        if invisibility_timer == fps * 3:
            invisibility = False
            invisibility_timer = 0
        if timer == fps:
            timer = 0
            if reversed_gravity:
                energy_reversed = True
                move_down = False
            else:
                move_up = False
                energy = True
        if reversed_gravity:
            if move_down:
                timer += 1
        if move_up:
            if blue:
                timer += 1
        if timer_M >= fps:
            seconds_passed += 1
            if seconds_passed % intervale == 0 and counter_pens < n:
                Projectale('pen.png', blue_s=True)
                Rope(cube.rect.y)
                counter_pens += 1
            timer_M = 0
        screen.fill((0, 0, 0))
        timer_M += 1
        all_spr.draw(screen)
        all_spr.update()
        clock.tick(fps)
        hp.update(hp_counter, screen)
        pygame.display.flip()
        if counter_pens >= n and seconds_passed >= end_time:
            attack = False
        if hp_counter == 0:
            attack = False
            alive = False
    blue = False
    reversed_gravity = False
    for a in platform_up:
        a.kill()
    for a in platform_down:
        a.kill()
    for a in pens:
        a.kill()
    sayori.kill()
    print(seconds_passed)


def tenth_attack(intervale, n, end_time):
    global attack, screen, fps, clock, all_spr, timer_M, seconds_passed, hp, \
        hp_counter, running, move_left, move_right, move_up, \
        move_down, energy, blue, invisibility, invisibility_timer, \
        timer, alive, up_board, left_board, down_board, \
        right_board, border, up, down, left, right, \
        monika, gravity_force, reversed_gravity, gravity_force_up, energy_reversed
    pygame.init()
    attack = True
    all_spr.remove(up_board)
    all_spr.remove(down_board)
    all_spr.remove(left_board)
    all_spr.remove(right_board)
    up.remove(up_board)
    down.remove(down_board)
    left.remove(left_board)
    right.remove(right_board)
    up_board = Board(100, 500, 600, 500, up)
    down_board = Board(100, 700, 600, 700, down)
    left_board = Board(100, 500, 100, 700, left)
    right_board = Board(600, 500, 600, 706, right)
    blue = True
    counter_pens = 0
    Pen(110, 620, 4, reflectable=True, velocity=-170)
    Pen(570, 620, 4, reflectable=True, velocity=170)
    Pen(110, 500, 4, reflectable=True, velocity=-170)
    Pen(570, 500, 4, reflectable=True, velocity=170)
    monika.kill()
    sayori = Vrag(load_image('SAY.png'), 5, 2, 300, 0)
    monika = Vrag(load_image('MONIKA.png'), 5, 12, 200, 0)
    cube.rect.y = 650
    while attack:
        get_event()
        screen.fill((0, 0, 0))
        if invisibility:
            invisibility_timer += 1
        if invisibility_timer == fps * 3:
            invisibility = False
            invisibility_timer = 0
        if timer == fps:
            timer = 0
            if reversed_gravity:
                energy_reversed = True
                move_down = False
            else:
                move_up = False
                energy = True
        if reversed_gravity:
            if move_down:
                timer += 1
        if move_up:
            if blue:
                timer += 1
        if timer_M >= fps:
            seconds_passed += 1
            if seconds_passed % intervale == 0 and counter_pens < n:
                Rope(590)
                counter_pens += 1
            timer_M = 0
        screen.fill((0, 0, 0))
        timer_M += 1
        all_spr.draw(screen)
        all_spr.update()
        clock.tick(fps)
        hp.update(hp_counter, screen)
        pygame.display.flip()
        if counter_pens == (n // 2) and not reversed_gravity:
            reversed_gravity = True
            gravity_force_up = True
            pygame.mixer.Sound('data//change_gravity.wav').play()
        if counter_pens >= n and seconds_passed >= end_time:
            attack = False
        if hp_counter == 0:
            attack = False
            alive = False
    blue = False
    reversed_gravity = False
    for a in platform_up:
        a.kill()
    for a in platform_down:
        a.kill()
    for a in pens:
        a.kill()
    sayori.kill()
    print(seconds_passed)


def eleventh_attack(s, end_time):
    global attack, screen, fps, clock, all_spr, timer_M, seconds_passed, hp, \
        hp_counter, running, move_left, move_right, move_up, \
        move_down, energy, blue, invisibility, invisibility_timer, \
        timer, alive, up_board, left_board, down_board, \
        right_board, border, up, down, left, right, \
        monika, gravity_force, reversed_gravity, gravity_force_up, energy_reversed
    pygame.init()
    attack = True
    all_spr.remove(up_board)
    all_spr.remove(down_board)
    all_spr.remove(left_board)
    all_spr.remove(right_board)
    up.remove(up_board)
    down.remove(down_board)
    left.remove(left_board)
    right.remove(right_board)
    up_board = Board(200, 400, 400, 400, up)
    down_board = Board(200, 600, 400, 600, down)
    left_board = Board(200, 400, 200, 600, left)
    right_board = Board(400, 400, 400, 606, right)
    for i in range(8):
        Pen(130, 400 + i * 25, 1, moving=False, image='knife.png')
        Pen(380, 400 + i * 25, 2, moving=False, image='knife.png')
        Pen(210 + i * 25, 330, 3, moving=False, image='knife.png')
        Pen(210 + i * 25, 580, 4, moving=False, image='knife.png')
    cycles = 0
    c = s - 1
    cycle = 0
    speed = s
    positions = [(50, 475, 0), (40, 400, 15), (40, 335, 30), (80, 275, 45),
                 (150, 225, 60), (225, 200, 75), (300, 175, 90),
                 (225, 200, 105), (150, 225, 120), (80, 275, 135), (40, 335, 150), (40, 400, 165)]
    monika.kill()
    sayori = Vrag(load_image('SAY.png'), 5, 2, 300, 0)
    yuri = Vrag(load_image('YRR.png'), 5, 2, 100, 0)
    monika = Vrag(load_image('MONIKA.png'), 5, 12, 200, 0)
    if 200 < cube.rect.x < 400:
        pass
    else:
        cube.rect.x = 300
    if 400 < cube.rect.y < 600:
        pass
    else:
        cube.rect.y = 500
    while attack:
        get_event()
        screen.fill((0, 0, 0))
        if invisibility:
            invisibility_timer += 1
        if invisibility_timer == fps * 3:
            invisibility = False
            invisibility_timer = 0
        if timer == fps:
            timer = 0
            if reversed_gravity:
                energy_reversed = True
                move_down = False
            else:
                move_up = False
                energy = True
        if reversed_gravity:
            if move_down:
                timer += 1
        if move_up:
            if blue:
                timer += 1
        if timer_M >= fps:
            seconds_passed += 1
            timer_M = 0
        if timer_M % speed == 0:
            if cycles < c:
                x = positions[cycle][0]
                y = positions[cycle][1]
                angle = positions[cycle][2]
                Rope(y, x=x, wait=30, angle=angle % 360)
                if cycle == len(positions) - 1:
                    speed -= 1
                    cycles += 1
                    cycle = 0
                else:
                    cycle += 1
        screen.fill((0, 0, 0))
        timer_M += 1
        all_spr.draw(screen)
        all_spr.update()
        clock.tick(fps)
        hp.update(hp_counter, screen)
        pygame.display.flip()
        if seconds_passed >= end_time:
            attack = False
        if hp_counter == 0:
            attack = False
            alive = False
    blue = False
    for a in platform_up:
        a.kill()
    for a in platform_down:
        a.kill()
    for a in pens:
        a.kill()
    sayori.kill()
    yuri.kill()
    print(seconds_passed)


def twelfth_attack(intervale, n, end_time):
    global attack, screen, fps, clock, all_spr, timer_M, seconds_passed, hp, \
        hp_counter, running, move_left, move_right, move_up, \
        move_down, energy, blue, invisibility, invisibility_timer, \
        timer, alive, energy_reversed, gravity_force_up, monika
    pygame.init()
    counter_pens = 0
    Platform((450, 625))
    Platform((300, 550))
    Platform((220, 475))
    attack = True
    blue = True
    time_started = seconds_passed
    i = -1
    monika.kill()
    yuri = Vrag(load_image('YRR.png'), 5, 2, 100, 0)
    monika = Vrag(load_image('MONIKA.png'), 5, 12, 200, 0)
    while attack:
        get_event()
        screen.fill((0, 0, 0))
        if invisibility:
            invisibility_timer += 1
        if invisibility_timer == fps * 3:
            invisibility = False
            invisibility_timer = 0
        if timer == fps:
            timer = 0
            if reversed_gravity:
                energy_reversed = True
                move_down = False
            else:
                move_up = False
                energy = True
        if reversed_gravity:
            if move_down:
                timer += 1
        if move_up:
            if blue:
                timer += 1
        if timer_M >= fps:
            if seconds_passed % intervale == 0 and counter_pens < n:
                Projectale_Targeted('pen.png', cube)
                Projectale_Targeted('pen.png', cube)
                Projectale_Targeted('pen.png', cube)
                Projectale_Targeted('pen.png', cube)
                Projectale_Targeted('pen.png', cube)
                Projectale_Targeted('pen.png', cube)
                counter_pens += 1
            if seconds_passed - time_started == 1:
                gravity_force_up = True
            seconds_passed += 1
            timer_M = 0
        if seconds_passed - time_started >= 3:
            if timer_M % 10 == 0:
                if i < 0:
                    i = 0
                elif i < 20:
                    Pen(100 + i * 25, 640, 4, moving=False, image='knife.png')
                    i += 1
        if counter_pens >= n and seconds_passed >= end_time:
            attack = False
        timer_M += 1
        all_spr.draw(screen)
        all_spr.update()
        clock.tick(fps)
        hp.update(hp_counter, screen)
        pygame.display.flip()
        if hp_counter == 0:
            attack = False
            alive = False
    print(seconds_passed)
    yuri.kill()
    for a in platform_up:
        a.kill()
    for a in platform_down:
        a.kill()
    for a in pens:
        a.kill()


def final_attack():
    global attack, screen, fps, clock, all_spr, timer_M, seconds_passed, hp, \
        hp_counter, running, move_left, move_right, move_up, \
        move_down, energy, blue, invisibility, invisibility_timer, \
        timer, alive, up_board, left_board, down_board, \
        right_board, border, up, down, left, right, \
        monika, gravity_force, reversed_gravity, gravity_force_up, energy_reversed
    pygame.init()
    attack = True
    all_spr.remove(up_board)
    all_spr.remove(down_board)
    all_spr.remove(left_board)
    all_spr.remove(right_board)
    up.remove(up_board)
    down.remove(down_board)
    left.remove(left_board)
    right.remove(right_board)
    up_board = Board(200, 400, 400, 400, up)
    down_board = Board(200, 600, 400, 600, down)
    left_board = Board(200, 400, 200, 600, left)
    right_board = Board(400, 400, 400, 606, right)
    for i in range(8):
        Pen(130, 400 + i * 25, 1, moving=False, image='knife.png')
        Pen(380, 400 + i * 25, 2, moving=False, image='knife.png')
        Pen(210 + i * 25, 330, 3, moving=False, image='knife.png')
        Pen(210 + i * 25, 580, 4, moving=False, image='knife.png')
    cycles = 0
    c = 15
    cycle = 0
    speed = 5
    positions = [(50, 475, 0), (40, 400, 15), (40, 335, 30), (80, 275, 45),
                 (150, 225, 60), (225, 200, 75), (300, 175, 90),
                 (225, 200, 105), (150, 225, 120), (80, 275, 135), (40, 335, 150), (40, 400, 165)]
    monika.kill()
    sayori = Vrag(load_image('SAY.png'), 5, 2, 300, 0)
    yuri = Vrag(load_image('YRR.png'), 5, 2, 100, 0)
    natsuki = Vrag(load_image('NAT.png'), 5, 2, 400, 0)
    monika = Vrag(load_image('MONIKA.png'), 5, 12, 200, 0)
    if 200 < cube.rect.x < 400:
        pass
    else:
        cube.rect.x = 300
    if 400 < cube.rect.y < 600:
        pass
    else:
        cube.rect.y = 500
    while attack:
        get_event()
        screen.fill((0, 0, 0))
        if invisibility:
            invisibility_timer += 1
        if invisibility_timer == fps * 3:
            invisibility = False
            invisibility_timer = 0
        if timer == fps:
            timer = 0
            if reversed_gravity:
                energy_reversed = True
                move_down = False
            else:
                move_up = False
                energy = True
        if reversed_gravity:
            if move_down:
                timer += 1
        if move_up:
            if blue:
                timer += 1
        if timer_M >= fps:
            Projectale_Targeted('pen.png', cube)
            Projectale_Targeted('pen.png', cube)
            Projectale_Targeted('pen.png', cube)
            Cupcake(load_image('cupcake.png'), 5, 1, choice([220, 320]), cube.rect.y - 300, velocity=200)
            seconds_passed += 1
            timer_M = 0
        if speed == 0 or timer_M % speed == 0:
            if cycles < c:
                x = positions[cycle][0]
                y = positions[cycle][1]
                angle = positions[cycle][2]
                Rope(y, x=x, wait=30, angle=angle % 360)
                if cycle == len(positions) - 1:
                    speed -= 1
                    cycles += 1
                    cycle = 0
                else:
                    cycle += 1
        screen.fill((0, 0, 0))
        timer_M += 1
        all_spr.draw(screen)
        all_spr.update()
        clock.tick(fps)
        hp.update(hp_counter, screen)
        pygame.display.flip()
        if seconds_passed >= 290:
            wait(3, white=True)
            attack = False
        if hp_counter == 0:
            attack = False
            alive = False
    blue = False
    for a in platform_up:
        a.kill()
    for a in platform_down:
        a.kill()
    for a in pens:
        a.kill()
    sayori.kill()
    yuri.kill()
    natsuki.kill()
    print(seconds_passed)


def empty_attack(end_time):
    global attack, screen, fps, clock, all_spr, timer_M, seconds_passed, hp, \
        hp_counter, running, move_left, move_right, move_up, \
        move_down, energy, blue, invisibility, invisibility_timer, \
        timer, alive, up_board, left_board, down_board, \
        right_board, border, up, down, left, right, energy_reversed
    attack = True
    while attack:
        get_event()
        screen.fill((0, 0, 0))
        if invisibility:
            invisibility_timer += 1
        if invisibility_timer == fps * 3:
            invisibility = False
            invisibility_timer = 0
        if timer == fps:
            timer = 0
            if reversed_gravity:
                energy_reversed = True
                move_down = False
            else:
                move_up = False
                energy = True
        if reversed_gravity:
            if move_down:
                timer += 1
        if move_up:
            if blue:
                timer += 1
        if timer_M >= fps:
            seconds_passed += 1
            timer_M = 0
        screen.fill((0, 0, 0))
        timer_M += 1
        hp.update(hp_counter, screen)
        all_spr.draw(screen)
        all_spr.update()
        clock.tick(fps)
        pygame.display.flip()
        if seconds_passed == end_time:
            attack = False


def heal_attack():
    global attack, screen, fps, clock, all_spr, timer_M, seconds_passed, hp, \
        hp_counter, running, move_left, move_right, move_up, \
        move_down, energy, blue, invisibility, invisibility_timer, \
        timer, alive, up_board, left_board, down_board, \
        right_board, border, up, down, left, right, \
        monika, gravity_force, reversed_gravity, gravity_force_up, energy_reversed
    pygame.init()
    attack = True
    all_spr.remove(up_board)
    all_spr.remove(down_board)
    all_spr.remove(left_board)
    all_spr.remove(right_board)
    up.remove(up_board)
    down.remove(down_board)
    left.remove(left_board)
    right.remove(right_board)
    up_board = Board(200, 400, 400, 400, up)
    down_board = Board(200, 600, 400, 600, down)
    left_board = Board(200, 400, 200, 600, left)
    right_board = Board(400, 400, 400, 606, right)
    for i in range(8):
        Pen(130, 400 + i * 25, 1, moving=False, image='knife.png')
        Pen(380, 400 + i * 25, 2, moving=False, image='knife.png')
        Pen(210 + i * 25, 330, 3, moving=False, image='knife.png')
        Pen(210 + i * 25, 580, 4, moving=False, image='knife.png')
    positions = [(50, 475, 0), (40, 400, 15), (40, 335, 30), (80, 275, 45),
                 (150, 225, 60), (225, 200, 75), (300, 175, 90),
                 (225, 200, 105), (150, 225, 120), (80, 275, 135), (40, 335, 150), (40, 400, 165)]
    counter_pens = 0
    monika.kill()
    yuri = Vrag(load_image('YRR.png'), 5, 2, 300, 0)
    natsuki = Vrag(load_image('NAT.png'), 5, 2, 100, 0)
    monika = Vrag(load_image('MONIKA.png'), 5, 12, 200, 0)
    if 200 < cube.rect.x < 400:
        pass
    else:
        cube.rect.x = 300
    if 400 < cube.rect.y < 600:
        pass
    else:
        cube.rect.y = 500
    while attack:
        get_event()
        screen.fill((0, 0, 0))
        if invisibility:
            invisibility_timer += 1
        if invisibility_timer == fps * 3:
            invisibility = False
            invisibility_timer = 0
        if timer == fps:
            timer = 0
            if reversed_gravity:
                energy_reversed = True
                move_down = False
            else:
                move_up = False
                energy = True
        if reversed_gravity:
            if move_down:
                timer += 1
        if move_up:
            if blue:
                timer += 1
        if timer_M >= fps:
            if counter_pens < 15:
                Cupcake(load_image('cupcake.png'), 5, 1, choice([220, 320]), cube.rect.y - 300, velocity=150)
            counter_pens += 1
            timer_M = 0
        screen.fill((0, 0, 0))
        timer_M += 1
        all_spr.draw(screen)
        all_spr.update()
        clock.tick(fps)
        hp.update(hp_counter, screen)
        pygame.display.flip()
        if counter_pens >= 20:
            attack = False
        if hp_counter == 0:
            attack = False
            alive = False
    blue = False
    for a in platform_up:
        a.kill()
    for a in platform_down:
        a.kill()
    for a in pens:
        a.kill()
    yuri.kill()
    natsuki.kill()
    your_turn('...')
    print(seconds_passed)


def phase_2():
    global seconds_passed, fps, mercy, monika, all_spr, actions, \
        KR, damage, actions, inventory, tried, end_phase_2
    tried = True
    damage = 1
    KR = True
    actions = ['Оценить', 'Плакать', 'Извиниться', 'Умолять о пощаде']
    for _ in range(10):
        inventory.append('Шок. Кекс')
    seconds_passed = 0
    monika.kill()
    monika = Vrag(load_image('MONIKA.png'), 5, 12, 200, 0)
    fon_phase_2 = Vrag(load_image('fon.png'), 12, 2, 0, 0)
    background_music.play(phase_2_1)
    empty_attack(6)
    background_music.play(phase_2_1_2, -1)
    your_turn('Хорошие воспоминания стираются из памяти...')
    background_music.play(phase_2_2, -1)
    if alive:
        tp_c.play(tp)
        wait(1, black_screen=True)
        tp_c.play(tp)
        sixth_attack(2, 7, 33)
        tp_c.play(tp)
        wait(1, black_screen=True)
        tp_c.play(tp)
    if alive:
        background_music.play(phase_2_2_1, -1)
        seconds_passed = 30
        your_turn('Ваши грехи ломают вам спину...')
        background_music.play(phase_2_2_2, -1)
        tp_c.play(tp)
        wait(1, black_screen=True)
        tp_c.play(tp)
        seventh_attack(2, 9, 50)
        tp_c.play(tp)
        wait(1, black_screen=True)
        tp_c.play(tp)
    if alive:
        twelfth_attack(1, 20, 75)
        tp_c.play(tp)
        wait(1, black_screen=True)
        tp_c.play(tp)
    if alive:
        eight_attack(3, 12, 115)
        tp_c.play(tp)
        wait(1, black_screen=True)
        tp_c.play(tp)
    if alive:
        ninth_attack(2, 20, 143)
        tp_c.play(tp)
        wait(1, black_screen=True)
        tp_c.play(tp)
    if alive:
        tenth_attack(3, 9, 177)
        tp_c.play(tp)
        wait(1, black_screen=True)
        tp_c.play(tp)
    if alive:
        background_music.play(phase_2_2_3, -1)
        your_turn('Как.')
        background_music.play(phase_2_2_4, -1)
        dialog_start(fps, ['Знаешь...', 'Я искренне надеюсь, что ты понимаешь...',
                           'Ты заслужил    э  т  о...'], [])
        tp_c.play(tp)
        wait(1, black_screen=True)
        tp_c.play(tp)
        eleventh_attack(8, 211)
        tp_c.play(tp)
        wait(1, black_screen=True)
        tp_c.play(tp)
        background_music.play(phase_2_2_5, -1)
        seventh_attack(1, 20, 230)
        tp_c.play(tp)
        wait(1, black_screen=True)
        tp_c.play(tp)
        tenth_attack(1, 28, 265)
        tp_c.play(tp)
        wait(1, black_screen=True)
        tp_c.play(tp)
        final_attack()
        background_music.play(phase_2_2_6, -1)
        end_phase_2 = True
        your_turn('Это конец.')


if __name__ == '__main__':
    speech_sound = pygame.mixer.Sound('data\speech.wav')
    speech = pygame.mixer.Channel(1)
    fps = 30
    size = width, height = 700, 800
    debug = False
    screen = pygame.display.set_mode(size)
    running = start_screen(fps, size)
    pygame.display.set_caption('МоникаТале')
    screen.fill((0, 0, 0))
    timer = 0
    timer_M = 0
    platform_down = pygame.sprite.Group()
    platform_up = pygame.sprite.Group()
    clock = pygame.time.Clock()
    border = pygame.sprite.Group()
    all_spr = pygame.sprite.Group()
    pens = pygame.sprite.Group()
    up = pygame.sprite.Group()
    down = pygame.sprite.Group()
    left = pygame.sprite.Group()
    right = pygame.sprite.Group()
    projectales = pygame.sprite.Group()
    characters = pygame.sprite.Group()
    text = pygame.sprite.Group()
    ctrl = False
    move_up = False
    move_left = False
    move_right = False
    move_down = False
    stuck = False
    blue = False
    rotated = False
    turn = False
    mercy = False
    KR = False
    end_phase_2 = False
    end_phase_1 = False
    enemies = []
    actions = ['Оценить', 'Подмигнуть', 'Признаться']
    inventory = ['Шок. Кекс', 'Шок. Кекс', 'Шок. Кекс', 'Шок. Кекс', 'Шок. Кекс', 'Шок. Кекс']
    monika = Vrag(load_image('MONIK_2.png'), 5, 2, 200, 0)
    enemies.append('Моника')
    counter = 0
    hp = Health_bar()
    invisibility = False
    invisibility_timer = 0
    eaten_counter = 0
    hp_counter = 100
    damage = 10
    energy = False
    seconds_passed = 0
    started = False
    character_exist = False
    dialogue = False
    pen_counter = 17
    attack = False
    alive = True
    gravity_force = False
    gravity_force_up = False
    energy_reversed = False
    reversed_gravity = False
    playing_background = False
    confessed = False
    animation = False
    dodge = False
    tried = False
    damage_sounds = ['data//classic_hurt.wav', 'data//damaged.wav']
    background_music = pygame.mixer.Channel(0)
    phase_1_introduction = pygame.mixer.Sound('data\Phase1_Introduction.wav')
    phase_1_1 = pygame.mixer.Sound('data\Phase1_1.wav')
    phase_1_2 = pygame.mixer.Sound('data\Phase1_2.wav')
    phase_1_1_1 = pygame.mixer.Sound('data\Phase1_1_1.wav')
    phase_1_turn = pygame.mixer.Sound('data\Phase1_1_Turn.wav')
    phase_1_introduction.set_volume(0.1)
    phase_1_1.set_volume(0.05)
    phase_1_turn.set_volume(0.1)
    phase_1_1_1.set_volume(0.05)
    phase_1_2.set_volume(0.1)
    phase_2_introduction = pygame.mixer.Sound('data//Phase2_Intro.wav')
    phase_2_1_1 = pygame.mixer.Sound('data//Phase2_1_1.wav')
    phase_2_1_2 = pygame.mixer.Sound('data//Phase2_1_2.wav')
    phase_2_2 = pygame.mixer.Sound('data//Phase2_2.wav')
    phase_2_2_2 = pygame.mixer.Sound('data//Phase2_2_2.wav')
    phase_2_1 = pygame.mixer.Sound('data//Phase2_1.wav')
    phase_2_2_1 = pygame.mixer.Sound('data//Phase2_2_1.wav')
    phase_2_2_3 = pygame.mixer.Sound('data//Phase2_2_3.wav')
    phase_2_2_3.set_volume(0.5)
    phase_2_2_4 = pygame.mixer.Sound('data//Phase2_2_4.wav')
    phase_2_2_4.set_volume(0.5)
    phase_2_2_5 = pygame.mixer.Sound('data//Phase2_2_5.wav')
    phase_2_2_5.set_volume(0.5)
    phase_2_2_6 = pygame.mixer.Sound('data//Phase2_2_6.wav')
    phase_2_2_6.set_volume(0.5)
    phase_2_2_1.set_volume(0.5)
    phase_2_1.set_volume(0.1)
    phase_2_2_2.set_volume(0.5)
    phase_2_2.set_volume(0.5)
    phase_2_introduction.set_volume(0.1)
    phase_2_1_2.set_volume(0.4)
    tp_c = pygame.mixer.Channel(5)
    tp = pygame.mixer.Sound('data//teleport.wav')
    while running:
        get_event()
        screen.fill((0, 0, 0))
        if invisibility:
            invisibility_timer += 1
        if invisibility_timer == fps:
            invisibility = False
            invisibility_timer = 0
        if timer == fps:
            timer = 0
            if reversed_gravity:
                energy_reversed = True
                move_down = False
            else:
                energy = True
                move_up = False
        if reversed_gravity:
            if move_down:
                timer += 1
        if move_up:
            if blue:
                timer += 1
        if timer_M >= fps:
            if not dialogue:
                seconds_passed += 1
            timer_M = 0
        if seconds_passed >= 3:
            started = True
        hp.update(hp_counter, screen)
        timer_M += 1
        if started:
            if seconds_passed == 4:
                if not debug:
                    dialog_start(fps, ['Каждый день...', 'Я мечтала о будущем, что ждет нас.',
                                       'Теперь... Ты просто уходишь?',
                                       'Как ты можешь?', 'Я не позволю просто так стереть мои старания!'],
                                 ['MONIK_normal.png', 'MONIK_normal.png',
                                  'MONIK_normal.png', 'MONIK_normal.png', 'MONIK_angry.png'])
                seconds_passed += 1
            if seconds_passed >= 7:
                if not character_exist:
                    cube = Character((250, 450))
                    up_board = Board(200, 400, 400, 400, up)
                    down_board = Board(200, 600, 400, 600, down)
                    left_board = Board(200, 400, 200, 600, left)
                    right_board = Board(400, 400, 400, 606, right)
                    character_exist = True
            if seconds_passed == 8:
                if not debug:
                    dialog_start(fps, ['Что? Ты думал я просто дам тебе начать первым?',
                                       'Дамы вперёд, знаешь ли.'], ['MONIK_surprise.png', 'MONIK_wink.png'])
                phase_1()
            if seconds_passed == 300:
                dialog_start(fps, ['Знаешь...', 'У меня возник вопрос...', 'Почему ты вообще хотел сбежать?',
                                   'А, ладно, не бери в голову.', 'В конце концов, ты же остался тут.'],
                             ['MONIK_normal.png', 'MONIK_normal.png', 'MONIK_pity.png',
                              'MONIK_normal.png', 'MONIK_normal.png'])
                seconds_passed = 301
            if seconds_passed == 330:
                dialog_start(fps, ['Хех...', 'Всё еще тут?', 'Надеешься на продолжение?',
                                   'Все таки, мы же тут навечно.', 'Однако, нет, мы просто будет так и стоять.'],
                             ['MONIK_normal.png', 'MONIK_normal.png', 'MONIK_normal.png',
                              'MONIK_normal.png', 'MONIK_wink.png'])
                seconds_passed = 331
            if seconds_passed == 360:
                dialog_start(fps,
                             ['Не устал еще?', 'Хотя, может быть ты вообще ушел спать...', 'Ну, это не имеет значения.',
                              'То, что ты еще не закрыл игру.', 'Я очень польщена.'],
                             ['MONIK_normal.png', 'MONIK_wink.png', 'MONIK_normal.png',
                              'MONIK_normal.png', 'MONIK_happy.png'])
                seconds_passed = 361
            if seconds_passed == 390:
                if debug:
                    dialog_start(fps, ['Кстати.', 'Ты думал я не замечу?',
                                       'Использовал режим разработчика, просто чтоб остаться тут?',
                                       'Как мило.', 'Хоть и жульничество.'],
                                 ['MONIK_normal.png', 'MONIK_surprise.png', 'MONIK_pity.png',
                                  'MONIK_happy.png', 'MONIK_normal.png'])
                    seconds_passed = 391
            if seconds_passed == 420:
                dialog_start(fps, ['Ты ждешь чего-то?', 'Финала?', 'Или просто действительно любишь меня?',
                                   'Без разницы.', 'Я буду тут пока ты со мной...'],
                             ['MONIK_normal.png', 'MONIK_normal.png', 'MONIK_wink.png',
                              'MONIK_normal.png', 'MONIK_normal.png'])
                seconds_passed = 421
        all_spr.draw(screen)
        all_spr.update()
        if hp_counter <= 0:
            pygame.mixer.stop()
            platform_down.empty()
            platform_up.empty()
            border.empty()
            all_spr.empty()
            up.empty()
            down.empty()
            left.empty()
            right.empty()
            projectales.empty()
            characters.empty()
            running = death()
            invisibility = False
            invisibility_timer = 0
            eaten_counter = 0
            hp_counter = 100
            damage = 10
            energy = False
            seconds_passed = 0
            started = False
            character_exist = False
            dialogue = False
            pen_counter = 17
            attack = False
            alive = True
            gravity_force = False
            gravity_force_up = False
            energy_reversed = False
            reversed_gravity = False
            playing_background = False
            confessed = False
            animation = False
            dodge = False
            tried = False
            ctrl = False
            move_up = False
            move_left = False
            move_right = False
            move_down = False
            stuck = False
            blue = False
            rotated = False
            turn = False
            mercy = False
            KR = False
            end_phase_2 = False
            end_phase_1 = False
            actions = ['Оценить', 'Подмигнуть', 'Признаться']
            inventory = ['Шок. Кекс', 'Шок. Кекс', 'Шок. Кекс', 'Шок. Кекс', 'Шок. Кекс', 'Шок. Кекс']
            monika = Vrag(load_image('MONIK_2.png'), 5, 2, 200, 0)
        clock.tick(fps)
        pygame.display.flip()
    pygame.quit()
    sys.exit()
