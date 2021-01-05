import pygame
import os
import sys
from random import randint
import math

pygame.init()


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
        global fps, move_up, move_down, move_left, move_right, stuck, energy, blue, gravity_force
        if blue:
            self.image = self.blue
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
                        else:
                            self.rect = self.rect.move(0, (self.v + 10) // fps)
            else:
                if gravity_force:
                    gravity_force = False
                    energy = True
            if energy:
                if (not pygame.sprite.spritecollideany(self, platform_down)
                        and not pygame.sprite.spritecollideany(self, up)):
                    self.g += 9
                    self.rect = self.rect.move(0, -((self.v + (100 - self.g)) // fps))
                    if self.g > 90:
                        energy = False
                        self.g = 0
            if (move_up and (not pygame.sprite.spritecollideany(self, platform_down)
                             and not pygame.sprite.spritecollideany(self, up))):
                if stuck:
                    self.rect = self.rect.move(0, -((self.v) // fps))
                else:
                    self.rect = self.rect.move(0, -((self.v + (100)) // fps))
                if (pygame.sprite.spritecollideany(self, up)
                        or pygame.sprite.spritecollideany(self, platform_down)):
                    stuck = True
                else:
                    stuck = False
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
        else:
            self.image = self.red
            if move_up and not pygame.sprite.spritecollideany(self, up):
                self.rect = self.rect.move(0, -((self.v + 60) // fps))
            if move_down and not pygame.sprite.spritecollideany(self, down):
                self.rect = self.rect.move(0, ((self.v + 60) // fps))
            if move_left and not pygame.sprite.spritecollideany(self, left):
                self.rect = self.rect.move(-((self.v + 60) // fps), 0)
            if move_right and not pygame.sprite.spritecollideany(self, right):
                self.rect = self.rect.move(((self.v + 60) // fps), 0)


class Vrag(pygame.sprite.Sprite):
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


class Button():
    def __init__(self, start_x, start_y, width, height, screen, text):
        self.on = False
        self.text = text
        self.start_x = start_x
        self.start_y = start_y
        self.width = width
        self.height = height
        self.font = pygame.font.Font(None, 30)
        self.screen = screen
        string_rendered = self.font.render(text, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        intro_rect.y = self.start_y
        intro_rect.x = self.start_x
        self.start_y += intro_rect.height
        screen.blit(string_rendered, intro_rect)
        pygame.draw.rect(screen, 'white', (self.start_x - 10, self.start_y - 35, 200, 50), 3)

    def on_it(self, pos):
        x = pos[0]
        y = pos[1]
        if (self.start_x - 10) <= x <= (self.start_x - 10 + 200) \
                and (self.start_y - 35) <= y <= (self.start_y + 20):
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
            string_rendered = self.font.render(self.text, 1, pygame.Color('green'))
            intro_rect = string_rendered.get_rect()
            intro_rect.y = self.start_y - 20
            intro_rect.x = 200
            self.screen.blit(string_rendered, intro_rect)
            pygame.draw.rect(self.screen, 'green', (self.start_x - 10, self.start_y - 35, 200, 50), 3)
        else:
            string_rendered = self.font.render(self.text, 1, pygame.Color('white'))
            intro_rect = string_rendered.get_rect()
            intro_rect.y = self.start_y - 20
            intro_rect.x = 200
            self.screen.blit(string_rendered, intro_rect)
            pygame.draw.rect(self.screen, 'white', (self.start_x - 10, self.start_y - 35, 200, 50), 3)


def start_screen(fps, size):
    fon = pygame.display.set_mode(size)
    pygame.display.set_caption('МоникаТале')
    fon.fill((0, 0, 0))
    start_button = Button(200, 300, 100, 50, fon, 'НАЧАТЬ')
    # developers_button = Button(200, 375, 100, 125, fon, 'РАЗРАБОТЧИКИ')
    exit_button = Button(200, 450, 100, 200, fon, 'ВЫХОД')
    on_button = False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEMOTION:
                start_button.on_it(event.pos)
                # developers_button.on_it(event.pos)
                exit_button.on_it(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if start_button.clicked(event.pos):
                    beggining(size, fon)
                    pygame.mixer.Sound('data//begin.wav').play()
                    return True
                elif exit_button.clicked(event.pos):
                    return False

        start_button.update()
        # developers_button.update()
        exit_button.update()
        pygame.display.flip()


def beggining(size, fon):
    global fps
    fon.fill((0, 0, 0))
    fort = pygame.font.Font('data//font.ttf', 25)
    text = ['*Вы оказываетесь в пустой комнате с девушкой...', '*Это Моника.', '*Странный свет заполняет комнату...',
            '*Вы понимаете...', '*В р е м я  н е п р и я т н о с т е й.  .  .']
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
                if event.type == pygame.KEYDOWN:
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


class Health_bar():
    def __init__(self):
        pygame.draw.rect(screen, 'white', (200, 630, 200, 30), 3)
        pygame.draw.rect(screen, 'red', (203, 633, 197, 27))
        pygame.draw.rect(screen, 'green', (203, 633, 197, 27))

    def update(self, hp, screen):
        pygame.init()
        fort = pygame.font.Font(None, 40)
        hp_c = fort.render(f'{hp}/100', True, (255, 255, 255))
        hp_rect = hp_c.get_rect()
        hp_rect.y = 640
        hp_rect.x = 420
        screen.blit(hp_c, hp_rect)
        pygame.draw.rect(screen, 'white', (200, 630, 200, 30), 3)
        pygame.draw.rect(screen, 'red', (202, 632, 197, 27))
        if hp >= 0:
            pygame.draw.rect(screen, 'green', (202, 632, (1.97 * hp), 27))


def death():
    death_screen = pygame.display.set_mode((700, 800))
    pygame.display.set_caption('МоникаТале')
    death_screen.fill((0, 0, 0))
    font = pygame.font.Font(None, 70)
    line = pygame.font.Font(None, 24)
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


def dialog_start(fps, text):
    global dialogue, screen, speech_sound
    dialogue = True
    fort = pygame.font.Font(None, 22)
    for i in range(len(text)):
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
                if event.type == pygame.KEYDOWN:
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
    dialogue = False


class Projectale_Targeted(pygame.sprite.Sprite):
    def __init__(self, image, target):
        super().__init__(all_spr)
        self.add(projectales)
        self.image = load_image(image)
        self.rect = self.image.get_rect()
        out_space = False
        self.now_a = 0
        while not out_space:
            self.rect.x = randint(100, 500)
            self.rect.y = randint(300, 650)
            if (200 < self.rect.x < 400) or (400 < self.rect.y < 600):
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

    def update(self):
        global seconds_passed, timer_M, fps, invisibility, character_exist, hp_counter
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
                damage_sound = pygame.mixer.Sound(damage_sounds[randint(0, 1)])
                damage_sound.set_volume(0.1)
                damage_sound.play()
                invisibility = True
                hp_counter -= 10

    def targetting(self):
        x_start = self.rect.x
        y_start = self.rect.y
        x_end = self.target.rect.x
        y_end = self.target.rect.y
        if x_start > x_end:
            a = x_start - x_end
        else:
            a = x_end - x_start
        if y_start > y_end:
            b = y_start - y_end
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
    def __init__(self, image, pos=None):
        super().__init__(all_spr)
        self.add(projectales)
        self.image = load_image(image)
        self.rect = self.image.get_rect()
        if pos:
            self.rect.x = pos[0]
            self.rect.y = pos[1]
        else:
            out_space = False
            while not out_space:
                self.rect.x = randint(50, 500)
                self.rect.y = randint(400, 600)
                if 150 <= self.rect.x <= 400:
                    out_space = False
                else:
                    out_space = True
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
        global seconds_passed, timer_M, fps, invisibility, character_exist, hp_counter
        if not self.start_move:
            if seconds_passed - self.start_timer == 2:
                self.start_move = True
        else:
            self.rect = self.rect.move(self.v / fps, 0)
        if not invisibility and character_exist:
            if pygame.sprite.collide_mask(self, cube):
                damage_sound = pygame.mixer.Sound(damage_sounds[randint(0, 1)])
                damage_sound.set_volume(0.1)
                damage_sound.play()
                invisibility = True
                hp_counter -= 10


def first_attack(intervale, n):
    global attack, screen, fps, clock, all_spr, timer_M, seconds_passed, hp, \
        hp_counter, running, move_left, move_right, move_up, \
        move_down, energy, blue, invisibility, invisibility_timer, timer, alive
    pygame.init()
    counter_pens = 0
    attack = True
    while attack:
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
                    if move_up:
                        energy = True
                    move_up = False
                    timer = 0
                    c = 0
                elif event.key == pygame.K_DOWN:
                    move_down = False
        screen.fill((0, 0, 0))
        if invisibility:
            invisibility_timer += 1
        if invisibility_timer == fps * 3:
            invisibility = False
            invisibility_timer = 0
        if timer == fps:
            timer = 0
            move_up = False
            energy = True
        if move_up:
            if blue:
                timer += 1
        if timer_M >= fps:
            if seconds_passed % intervale == 0:
                Projectale_Targeted('pen.png', cube)
                counter_pens += 1
            seconds_passed += 1
            timer_M = 0
        hp.update(hp_counter, screen)
        if counter_pens >= n and seconds_passed >= 30:
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


def second_attack(intervale, n):
    global attack, screen, fps, clock, all_spr, timer_M, seconds_passed, hp, \
        hp_counter, running, move_left, move_right, move_up, \
        move_down, energy, blue, invisibility, invisibility_timer, timer, alive
    pygame.init()
    counter_pens = 0
    attack = True
    while attack:
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
                    if move_up:
                        energy = True
                    move_up = False
                    timer = 0
                    c = 0
                elif event.key == pygame.K_DOWN:
                    move_down = False
        screen.fill((0, 0, 0))
        if invisibility:
            invisibility_timer += 1
        if invisibility_timer == fps * 3:
            invisibility = False
            invisibility_timer = 0
        if timer == fps:
            timer = 0
            move_up = False
            energy = True
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
        if counter_pens >= n and seconds_passed >= 51:
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


def third_attack(intervale, n):
    global attack, screen, fps, clock, all_spr, timer_M, seconds_passed, hp, \
        hp_counter, running, move_left, move_right, move_up, \
        move_down, energy, blue, invisibility, invisibility_timer, timer, alive, gravity_force
    pygame.init()
    counter_pens = 0
    attack = True
    blue = True
    while attack:
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
                    if move_up:
                        energy = True
                    move_up = False
                    timer = 0
                    c = 0
                elif event.key == pygame.K_DOWN:
                    move_down = False
        screen.fill((0, 0, 0))
        if invisibility:
            invisibility_timer += 1
        if invisibility_timer == fps * 3:
            invisibility = False
            invisibility_timer = 0
        if timer == fps:
            timer = 0
            move_up = False
            energy = True
        if move_up:
            if blue:
                timer += 1
        if timer_M >= fps:
            if seconds_passed % 1 == 0 and counter_pens < n:
                Projectale('pen.png')
                counter_pens += 1
            if seconds_passed % intervale == 0:
                gravity_force = True
            seconds_passed += 1
            timer_M = 0
        hp.update(hp_counter, screen)
        if counter_pens >= n and seconds_passed >= 51:
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
    global seconds_passed, fps
    if alive:
        first_attack(2, 5)
    if alive:
        second_attack(1, 14)
    if alive:
        background_music.pause()
        dialog_start(fps, ['Послушай...', 'Я не хочу причинять тебе боль',
                           'Однако, твои действия...',
                           'Говорят, что удержать тебя со мной...', 'п р и д е т с я  с и л о й .  .  .'])
        seconds_passed = 52
        background_music.unpause()
    if alive:
        first_attack(1, 15)
    if alive:
        second_attack(0.5, 25)
    if alive:
        third_attack(3, 30)


if __name__ == '__main__':
    speech_sound = pygame.mixer.Sound('data\speech.wav')
    speech = pygame.mixer.Channel(1)
    fps = 30
    size = width, height = 700, 800
    running = start_screen(fps, size)
    pygame.display.set_caption('МоникаТале')
    screen = pygame.display.set_mode(size)
    screen.fill((0, 0, 0))
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
    projectales = pygame.sprite.Group()
    characters = pygame.sprite.Group()
    ctrl = False
    move_up = False
    move_left = False
    move_right = False
    move_down = False
    stuck = False
    blue = False
    natsuki = Vrag(load_image('NAT.png'), 5, 2, 100, 0)
    sayori = Vrag(load_image('SAY.png'), 5, 2, 300, 0)
    yuri = Vrag(load_image('YRR.png'), 5, 2, 150, 0)
    monika = Vrag(load_image('MONIK_2.png'), 5, 2, 200, 0)
    counter = 0
    hp = Health_bar()
    invisibility = False
    invisibility_timer = 0
    hp_counter = 100
    energy = False
    seconds_passed = 0
    started = False
    character_exist = False
    dialogue = False
    pen_counter = 17
    attack = False
    alive = True
    gravity_force = False
    playing_background = False
    damage_sounds = ['data//classic_hurt.wav', 'data//damaged.wav']
    music_1 = pygame.mixer.Sound('data\Phase1.wav')
    background_music = pygame.mixer.Channel(0)
    music_1.set_volume(0.1)
    spawning_sound = pygame.mixer.Sound('data//spawn.wav')
    spawning_sound.set_volume(0.1)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
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
                    if move_up:
                        energy = True
                    move_up = False
                    timer = 0
                    c = 0
                elif event.key == pygame.K_DOWN:
                    move_down = False
        screen.fill((0, 0, 0))
        if invisibility:
            invisibility_timer += 1
        if invisibility_timer == fps:
            invisibility = False
            invisibility_timer = 0
        if timer == fps:
            timer = 0
            move_up = False
            energy = True
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
                dialog_start(fps, ['Каждый день...', 'Я мечтала о будущем, что ждет нас.',
                                   'Теперь... Ты просто уходишь?',
                                   'Как ты можешь?', 'Я не позволю просто так стереть мои старания!'])
                seconds_passed += 1
            if seconds_passed >= 7:
                if not character_exist:
                    cube = Character((250, 450))
                    Board(200, 400, 400, 400, up)
                    Board(200, 600, 400, 600, down)
                    Board(200, 400, 200, 600, left)
                    Board(400, 400, 400, 606, right)
                    character_exist = True
                    dialog_start(fps, ['Что? Ты думал я просто дам тебе начать первым?',
                                       'Дамы вперёд, знаешь ли.'])
                    background_music.play(music_1)
            if seconds_passed == 10:
                phase_1()
        all_spr.draw(screen)
        all_spr.update()
        if hp_counter <= 0:
            platform_down.empty()
            platform_up.empty()
            border.empty()
            all_spr.empty()
            ladders.empty()
            up.empty()
            down.empty()
            left.empty()
            right.empty()
            projectales.empty()
            characters.empty()
            running = death()
            character_exist = False
            hp_counter = 100
            seconds_passed = 0
            alive = True
            monika = Vrag(load_image('MONIK_2.png'), 5, 2, 200, 0)
        clock.tick(fps)
        pygame.display.flip()
    pygame.quit()
    sys.exit()
