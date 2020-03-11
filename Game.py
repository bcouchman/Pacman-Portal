import sys
import pygame as pg
from pygame.locals import *
from pygame.sprite import Group
from pygame.sprite import Sprite
from vector import Vector


class Testman(Sprite):
    def __init__(self, x, y):
        self.rect = pg.Rect(x, y, 30, 30)


class Pacman(Sprite):
    def __init__(self, game, x, y):
        self.velocity = Vector()
        self.nextmove = Vector()
        self.game = game
        self.screen = game.screen
        self.score = 0
        self.font = pg.font.SysFont("comicsansms", 36)
        self.text = self.font.render("Score: 0", True, (0, 0, 0))
        self.image = [pg.image.load('pacman1.png'), pg.image.load('pacman2.png'), pg.image.load('pacman3.png'),
                      pg.image.load('pacman4.png')]
        self.image.append(pg.transform.rotate(self.image[0], 90))
        self.image.append(pg.transform.rotate(self.image[1], 90))
        self.image.append(pg.transform.rotate(self.image[2], 90))
        self.image.append(pg.transform.rotate(self.image[3], 90))
        self.image.append(pg.transform.rotate(self.image[0], 180))
        self.image.append(pg.transform.rotate(self.image[1], 180))
        self.image.append(pg.transform.rotate(self.image[2], 180))
        self.image.append(pg.transform.rotate(self.image[3], 180))
        self.image.append(pg.transform.rotate(self.image[0], -90))
        self.image.append(pg.transform.rotate(self.image[1], -90))
        self.image.append(pg.transform.rotate(self.image[2], -90))
        self.image.append(pg.transform.rotate(self.image[3], -90))
        self.facing = 0
        self.facingnext = 0
        self.frame = 0
        self.img = 0
        self.rect = self.image[self.img].get_rect()
        self.rect.x = x
        self.rect.y = y
        self.test = Testman(self.rect.x, self.rect.y)

    def draw(self):
        if self.rect.x <= -30:
            self.rect.x += self.game.MWidth * 30
        elif self.rect.x >= self.game.MWidth * 30:
            self.rect.x -= self.game.MWidth * 30
        self.screen.blit(self.image[self.img + self.facing], self.rect)
        if self.rect.x < 0:
            self.rect.x += self.game.MWidth * 30
            self.screen.blit(self.image[self.img + self.facing], self.rect)
        elif self.rect.x > self.game.MWidth * 30 - 29:
            self.rect.x -= self.game.MWidth * 30
            self.screen.blit(self.image[self.img + self.facing], self.rect)
        text = "Score: " + str(self.score)
        self.text = self.font.render(text, True, (0, 0, 0))
        self.screen.blit(self.text, (100, 0))

    def move(self):
        if self.nextmove != Vector():
            self.test.rect.x = self.rect.x + self.nextmove.x
            self.test.rect.y = self.rect.y + self.nextmove.y
            if 0 == len(pg.sprite.spritecollide(self.test, self.game.walls, False)):
                self.velocity.x = self.nextmove.x
                self.velocity.y = self.nextmove.y
                self.rect.x = self.test.rect.x
                self.rect.y = self.test.rect.y
                self.facing = self.facingnext
                return
        if self.velocity != Vector():
            self.test.rect.x = self.rect.x + self.velocity.x
            self.test.rect.y = self.rect.y + self.velocity.y
            hit = pg.sprite.spritecollide(self.test, self.game.walls, False)
            if 0 == len(hit):
                self.rect.x = self.test.rect.x
                self.rect.y = self.test.rect.y
            else:
                self.velocity = Vector()

    def update(self):
        self.frame += 1
        if self.frame == 3:
            self.img += 1
            self.frame = 0
            if self.img == 4:
                self.img = 0
        if 0 != len(pg.sprite.spritecollide(self, self.game.food, True)):
            self.score += 1
        self.move()
        self.draw()


class Ghost(Sprite):
    def __init__(self, game, x, y, ai):
        super().__init__()
        colors = {'1': (255, 0, 0), '2': (255, 200, 255), '3': (0, 255, 255), '4': (255, 200, 82)}
        self.heading = {'u': Vector(0, -1 * game.SPEED), 'd': Vector(0, game.SPEED),
                        'r': Vector(game.SPEED, 0), 'l': Vector(-1 * game.SPEED, 0)}
        self.facings = {'u': 1, 'd': 3, 'r': 0, 'l': 2}
        self.a = {'1': 0, '2': 2, '3': 0, '4': 2}
        self.b = {'1': 0, '2': 0, '3': 2, '4': 2}
        self.ai = ai
        self.ai_cnt = 0
        self.mode = 0  # 0 for normal, 1 for eyes, 2+ for weak
        self.game = game
        self.move = Vector()
        self.home = Vector(x // 30, y // 30)
        if ai == '1':
            self.corner = Vector(1, 1)
        elif ai == '2':
            self.corner = Vector(self.game.MWidth - 2, 1)
        elif ai == '3':
            self.corner = Vector(self.game.MWidth - 2, self.game.MHeight - 2)
        elif ai == '4':
            self.corner = Vector(1, self.game.MHeight - 2)
        else:
            self.corner = self.home
        self.fear = [pg.image.load('Ghost.png')]
        self.fear.append(pg.transform.flip(self.fear[0], True, False))
        self.image = [pg.transform.flip(self.fear[0], False, False)]
        for i in range(0, 30):
            for j in range(0, 30):
                a = self.image[0].get_at((i, j))[3]
                self.image[0].set_at((i, j), (colors[self.ai][0], colors[self.ai][1], colors[self.ai][2], a))
        self.image.append(pg.transform.flip(self.image[0], True, False))
        self.eyes = [pg.Surface((10, 5))]
        for i in range(1, 7):
            self.eyes.append(pg.Surface((10, 5)))
        eye = pg.Surface((5, 5))
        eye.fill(colors[self.ai])
        pg.draw.circle(eye, (255, 255, 255), (3, 3), 3)
        pg.draw.rect(eye, (0, 0, 255), Rect(4, 2, 2, 2), 2)
        for i in range(0, 5):
            for j in range(0, 5):
                r, g, b, a = eye.get_at((i, j))
                eye.set_at((i, j), (r, g, b, 0))

        self.eyes[0].blit(eye, (0, 0))
        self.eyes[0].blit(eye, (5, 0))
        self.eyes[1].blit(pg.transform.rotate(eye, 90), (0, 0))
        self.eyes[1].blit(pg.transform.rotate(eye, 90), (5, 0))
        self.eyes[2].blit(pg.transform.flip(eye, True, False), (0, 0))
        self.eyes[2].blit(pg.transform.flip(eye, True, False), (5, 0))
        self.eyes[3].blit(pg.transform.rotate(eye, -90), (0, 0))
        self.eyes[3].blit(pg.transform.rotate(eye, -90), (5, 0))
        self.frame = 0
        self.img = 0
        self.facing = 0
        self.screen = self.game.screen
        self.rect = self.image[self.img].get_rect()
        self.rect.x = x
        self.rect.y = y

    def hunt(self, x, y):
        target_x = x
        target_y = y
        i = 0
        search = [self.game.nodes[self.rect.y // 30][self.rect.x // 30]]
        path = ['']
        if search[0].x == target_x and search[0].y == target_y:
            return Vector()
        while True:
            for N in search[i].next:
                if not (search[i].next[N] in search):
                    search.append(search[i].next[N])
                    path.append(path[i] + N)
                    if search[i].next[N].x == target_x and search[i].next[N].y == target_y:
                        self.facing = self.facings[path[-1][0]]
                        return self.heading[path[-1][0]]
            i += 1
            if i == len(search):
                return Vector()

    def blinky(self):
        target_x = round(self.game.player.rect.x / 30)
        target_y = round(self.game.player.rect.y / 30)
        return self.hunt(target_x, target_y)

    def pinky(self):
        target_x = round(self.game.player.rect.x / 30)
        target_y = round(self.game.player.rect.y / 30)
        if 0 < self.game.player.velocity.x:
            target_x += 4
        if 0 > self.game.player.velocity.x:
            target_x -= 4
        if 0 < self.game.player.velocity.y:
            target_y += 4
        if 0 > self.game.player.velocity.y:
            target_y -= 4
        if target_x >= self.game.MWidth:
            target_x = self.game.MWidth - 2
        if target_y >= self.game.MHeight:
            target_y = self.game.MHeight - 2
        if target_x < 1:
            target_x = 1
        if target_y < 1:
            target_y = 1
        if not self.game.nodes[target_y][target_x].notwall:
            shift_x = -1
            shift_y = 0
            while not self.game.nodes[target_y + shift_y][target_x + shift_x].notwall:
                if shift_y == 0:
                    shift_y = shift_x
                elif shift_x == 0:
                    shift_x = shift_y * -1
                elif shift_x == shift_y:
                    shift_x = 0
                elif shift_x > shift_y:
                    shift_y = 0
                else:
                    shift_y = 0
                    shift_x -= 1
            target_x += shift_x
            target_y += shift_y
        return self.hunt(target_x, target_y)

    def inky(self):
        if 6 < self.ai_cnt:
            target_x = self.corner.x
            target_y = self.corner.y
        else:
            target_x = round(self.game.player.rect.x / 30)
            target_y = round(self.game.player.rect.y / 30)
            if 0 < self.game.player.velocity.x:
                target_x += 2
            if 0 > self.game.player.velocity.x:
                target_x -= 2
            if 0 < self.game.player.velocity.y:
                target_y += 2
            if 0 > self.game.player.velocity.y:
                target_y -= 2
            if target_x >= self.game.MWidth:
                target_x = self.game.MWidth - 2
            if target_y >= self.game.MHeight:
                target_y = self.game.MHeight - 2
            if target_x < 1:
                target_x = 1
            if target_y < 1:
                target_y = 1

            if not self.game.nodes[target_y][target_x].notwall:
                shift_x = -1
                shift_y = 0
                while not self.game.nodes[target_y + shift_y][target_x + shift_x].notwall:
                    if shift_y == 0:
                        shift_y = shift_x
                    elif shift_x == 0:
                        shift_x = shift_y * -1
                    elif shift_x == shift_y:
                        shift_x = 0
                    elif shift_x > shift_y:
                        shift_y = 0
                    else:
                        shift_y = 0
                        shift_x -= 1
                target_x += shift_x
                target_y += shift_y
        return self.hunt(target_x, target_y)

    def clyde(self):
        target_x = round(self.game.player.rect.x / 30)
        target_y = round(self.game.player.rect.y / 30)
        if 64 > ((target_x - self.rect.x / 30) ** 2 + (target_y - self.rect.y / 30) ** 2):
            target_x = 1
            target_y = self.game.MHeight - 2
        return self.hunt(target_x, target_y)

    def collide(self):
        if pg.sprite.collide_rect(self, self.game.player):
            if 0 == self.mode:  # should be 0 not 9
                pg.display.set_caption('You lose!')
                self.game.finished = True
            elif 1 != self.mode:
                self.mode = 1
                self.game.player.score += 200

    def afraid(self):
        self.mode = 50

    def draw(self):
        if self.mode == 0:
            self.screen.blit(self.image[self.img], self.rect)
        self.screen.blit(self.eyes[self.facing], (self.rect.x + 10, self.rect.y + 5))
        if 2 <= self.mode:
            if self.mode in (3, 5, 8, 11, 15):
                self.screen.blit(self.image[self.img], self.rect)
            else:
                self.screen.blit(self.fear[self.img], self.rect)

    def update(self):
        self.frame += 1
        if self.frame == 5:
            self.frame = 0
            self.img += 1
            if self.img == 2:
                self.img = 0
        if 0 == self.rect.x % 30:
            if 0 == self.rect.y % 30:
                if self.mode == 2:
                    self.mode = 0
                elif self.mode > 2:
                    self.mode -= 1
                if self.mode == 1:
                    if self.home.x == self.rect.x // 30:
                        if self.home.y == self.rect.y // 30:
                            self.mode = 0
                self.ai_cnt += 1
                self.ai_cnt = self.ai_cnt % 12

                if self.mode == 1:
                    self.move = self.hunt(self.home.x, self.home.y)
                elif 2 <= self.mode:
                    if self.a[self.ai] == self.game.player.rect.x % 4:
                        a = 1
                    else:
                        a = self.game.MWidth - 2
                    if self.b[self.ai] == self.game.player.rect.y % 4:
                        b = 1
                    else:
                        b = self.game.MHeight - 2
                    self.move = self.hunt(a, b)
                elif 9 < self.ai_cnt:
                    self.move = self.hunt(self.corner.x, self.corner.y)
                else:
                    if self.ai == '1':
                        self.move = self.blinky()
                    if self.ai == '2':
                        self.move = self.pinky()
                    if self.ai == '3':
                        self.move = self.inky()
                    if self.ai == '4':
                        self.move = self.clyde()
        self.rect.x += self.move.x
        self.rect.y += self.move.y
        self.draw()
        self.collide()


class Portal(Sprite):
    def __init__(self, game, x, y, key, velocity):
        super().__init__()
        self.image = pg.Surface((30, 30))
        self.key = key
        pg.draw.circle(self.image, (200 - 200 * self.key, 100, 200 * self.key), (14, 14), 5)
        self.game = game
        self.decay = 0
        self.screen = self.game.screen
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.velocity = velocity
        self.inbound = Vector(-1 * self.velocity.x, -1 * self.velocity.y)

    def draw(self):
        self.screen.blit(self.image, self.rect)

    def update(self):
        if self.decay == 1:
            if not pg.sprite.collide_rect(self, self.game.player):
                pg.mixer.Sound.play(self.game.portal_closing)
                self.game.walls.add(Wall(self.game, self.rect.x, self.rect.y))
                self.game.portals.pop()
        if self.velocity == Vector():
            if 2 == len(self.game.portals):
                pg.sprite.spritecollide(self, self.game.walls, True)
                if pg.sprite.collide_rect(self, self.game.player):
                    pg.mixer.Sound.play(self.game.portal_transport)
                    self.game.player.rect.x = self.game.portals[self.key - 1].rect.x
                    self.game.player.rect.y = self.game.portals[self.key - 1].rect.y
                    self.game.player.velocity.x = self.game.portals[self.key - 1].inbound.x
                    self.game.player.velocity.y = self.game.portals[self.key - 1].inbound.y
                    self.game.player.nextmove = Vector()
                    self.game.walls.add(Wall(self.game, self.rect.x, self.rect.y))
                    self.game.portals[self.key - 1].decay = 1
                    self.game.portals.pop(self.key)
        else:
            self.rect.x += self.velocity.x * 3
            self.rect.y += self.velocity.y * 3
            hits = pg.sprite.spritecollide(self, self.game.walls, False)
            for wall in hits:
                pg.mixer.Sound.play(self.game.portal_opening)
                self.rect.x = wall.rect.x
                self.rect.y = wall.rect.y
                self.velocity = Vector()
                pg.draw.circle(self.image, (200 - 200 * self.key, 100, 200 * self.key), (14, 14), 15)
        self.draw()


class Wall(Sprite):
    def __init__(self, game, x, y):
        super().__init__()
        self.image = pg.Surface((30, 30))
        self.image.fill((0, 0, 255))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.screen = game.screen

    def draw(self):
        self.screen.blit(self.image, self.rect)

    def update(self):
        self.draw()


class Food(Sprite):
    def __init__(self, game, x, y):
        super().__init__()
        self.game = game
        self.screen = self.game.screen
        self.color = (255, 255, 255)
        self.rect = pg.Rect(0, 0, 2, 2)
        self.rect.x = x
        self.rect.y = y
        self.size = 2

    def draw(self): pg.draw.circle(self.screen, self.color, (self.rect.x + 1, self.rect.y + 1), 2)

    def update(self):
        self.draw()


class Cookie(Sprite):
    def __init__(self, game, x, y):
        super().__init__()
        self.game = game
        self.screen = self.game.screen
        self.color = (255, 255, 255)
        self.rect = pg.Rect(0, 0, 2, 2)
        self.rect.x = x
        self.rect.y = y
        self.size = 2

    def draw(self):
        pg.draw.circle(self.screen, self.color, (self.rect.x + 4, self.rect.y + 4), 5)

    def update(self):
        if pg.sprite.collide_rect(self, self.game.player):
            self.game.player.score += 50
            for g in self.game.ghosts:
                g.afraid()
        self.draw()


class Node:

    def __init__(self, game, ntype, x, y):
        self.next = {}
        self.x = x
        self.y = y
        self.notwall = True
        self.game = game
        if ntype == 'w':
            self.notwall = False
            self.game.walls.add(Wall(self.game, 30 * x, 30 * y))
        if not self.notwall:
            return
        self.isfood = False
        if ntype == '-':
            self.isfood = True
            newfood = Food(self.game, x * 30 + 14, y * 30 + 14)
            self.game.food.add(newfood)
        if ntype == '+':
            self.isfood = True
            newfood = Cookie(self.game, x * 30 + 11, y * 30 + 11)
            self.game.food.add(newfood)
        if ntype in ['1', '2', '3', '4']:
            newGhost = Ghost(self.game, x * 30, y * 30, ntype)
            self.game.ghosts.add(newGhost)

    def setUp(self, next):
        self.next["u"] = next

    def setDown(self, next):
        self.next["d"] = next

    def setRight(self, next):
        self.next["r"] = next

    def setLeft(self, next):
        self.next["l"] = next


class Game:
    # SPEED = 5
    # MWidth = 27
    # MHeigth = 22

    def __init__(self):
        pg.init()
        pg.mixer.init()
        pg.mixer.music.load('sounds/Pac-Man-Theme-Song.mp3')
        pg.mixer.music.play(-1, 0.0)
        self.bg_color = (40, 40, 40)  # dark grey
        self.finished: bool = False
        levelfile = open("level-1.txt")
        dat = levelfile.readline()
        self.MWidth = int(dat[2:4])
        self.MHeight = int(dat[7:9])
        self.screen = pg.display.set_mode((self.MWidth * 30, 30 * self.MHeight))
        self.SPEED = int(dat[12:13])
        dat = levelfile.readline()
        j = -1
        self.food = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.ghosts = pg.sprite.Group()
        self.portals = []
        self.nodes = []
        self.portal_opening = pg.mixer.Sound("sounds/portal_open.wav")
        self.portal_closing = pg.mixer.Sound("sounds/portal_close.wav")
        self.portal_fire = pg.mixer.Sound("sounds/portal_fire.wav")
        self.portal_transport = pg.mixer.Sound("sounds/portal_transport.wav")
        while len(dat) > 0:
            j = j + 1
            self.nodes.append([Node(self, dat[0:1], 0, j)])
            current = self.nodes[j]
            for i in range(1, self.MWidth):
                current.append(Node(self, dat[i:i + 1], i, j))
                if dat[i:i + 1] == "p":
                    self.player = Pacman(self, i * 30, j * 30)
                if dat[i:i + 1] == "p":
                    self.player = Pacman(self, i * 30, j * 30)

            dat = levelfile.readline()
        for j in range(0, self.MHeight - 1):
            for i in range(0, self.MWidth - 1):
                if self.nodes[j][i].notwall:
                    if self.nodes[j - 1][i].notwall:
                        self.nodes[j][i].setUp(self.nodes[j - 1][i])
                    if self.nodes[j + 1][i].notwall:
                        self.nodes[j][i].setDown(self.nodes[j + 1][i])
                    if self.nodes[j][i - 1].notwall:
                        self.nodes[j][i].setLeft(self.nodes[j][i - 1])
                    if i == self.MWidth:
                        if self.nodes[j][0].notwall:
                            self.nodes[j][i].setRight(self.nodes[j][0])
                    elif self.nodes[j][i + 1].notwall:
                        self.nodes[j][i].setRight(self.nodes[j][i + 1])

    def process_events(self):
        movement = {K_RIGHT: Vector(1, 0), K_LEFT: Vector(-1, 0), K_UP: Vector(0, -1), K_DOWN: Vector(0, 1)}
        translate = {K_d: K_RIGHT, K_a: K_LEFT, K_w: K_UP, K_s: K_DOWN}
        facing = {K_RIGHT: 0, K_LEFT: 8, K_UP: 4, K_DOWN: 12}
        for event in pg.event.get():
            e_type = event.type
            if e_type == pg.KEYDOWN:
                k = event.key
                if k == K_q:
                    self.finished = True
                elif k in translate.keys() or k in translate.values():  # movement
                    if k in translate.keys():
                        k = translate[k]
                    self.player.nextmove = movement[k] * 6  # self.SPEED
                    self.player.facingnext = facing[k]
                elif k == K_z:
                    if self.player.velocity != Vector():
                        if 1 == len(self.portals):
                            if self.portals[0].decay == 1:
                                return
                        if 2 == len(self.portals):
                            p = self.portals.pop(0)
                            self.walls.add(Wall(self, p.rect.x, p.rect.y))
                            p.kill()
                        pg.mixer.Sound.play(self.portal_fire)
                        self.portals.append(Portal(self, self.player.rect.x, self.player.rect.y,
                                                   len(self.portals), Vector(self.player.velocity.x,
                                                                             self.player.velocity.y)))
            elif e_type == QUIT:  # quit
                self.finished = True

    def update(self):
        self.screen.fill(self.bg_color)
        self.walls.update()
        for p in self.portals:
            p.update()
        self.food.update()
        self.ghosts.update()
        self.player.update()

    def play(self):
        while not self.finished:
            self.process_events()
            self.update()
            pg.display.update()
            if len(self.food) == 0:
                pg.display.set_caption('You WIN!')
                pg.display.update()
                return
        text = "Score: " + str(self.player.score)
        self.player.text = self.player.font.render(text, True, (255, 255, 255))
        self.screen.blit(self.player.text, (100, 0))
        pg.display.update()
        while self.finished:
            for event in pg.event.get():
                e_type = event.type
                if e_type == pg.KEYDOWN:
                    self.finished = False


class DGhost(Sprite):
    def __init__(self, demo):
        super().__init__()
        self.demo = demo
        colors = (255, 0, 0)
        self.heading = {'u': Vector(0, -5), 'd': Vector(0, 5), 'r': Vector(5, 0), 'l': Vector(-5, 0)}
        self.facings = {'u': 1, 'd': 3, 'r': 0, 'l': 2}
        self.a = {'1': 0, '2': 2, '3': 0, '4': 2}
        self.b = {'1': 0, '2': 0, '3': 2, '4': 2}
        self.mode = 0  # 0 for normal, 1 for eyes, 2+ for weak
        self.game = self.demo.game
        self.move = Vector()
        self.fear = [pg.Surface((60, 60))]
        pg.transform.scale2x(pg.image.load('Ghost.png'), self.fear[0])
        self.fear.append(pg.transform.flip(self.fear[0], True, False))
        self.image = [pg.Surface((60, 60))]
        for i in range(0, 60):
            for j in range(0, 60):
                r, g, b, a = self.fear[0].get_at((i, j))
                if b == 255:
                    self.image[0].set_at((i, j), (colors[0], colors[1], colors[2], a))
                else:
                    self.image[0].set_at((i, j), (0, 0, 0, 0))
        self.image.append(pg.transform.flip(self.image[0], True, False))
        self.eyes = [pg.Surface((20, 10))]
        for i in range(1, 7):
            self.eyes.append(pg.Surface((20, 10)))
        eye = pg.Surface((10, 10))
        eye.fill(colors)
        pg.draw.circle(eye, (255, 255, 255), (6, 6), 6)
        pg.draw.rect(eye, (0, 0, 255), Rect(8, 4, 4, 4), 3)
        for i in range(0, 10):
            for j in range(0, 10):
                r, g, b, a = eye.get_at((i, j))
                eye.set_at((i, j), (r, g, b, 0))

        self.eyes[0].blit(eye, (0, 0))
        self.eyes[0].blit(eye, (10, 0))
        self.eyes[1].blit(pg.transform.rotate(eye, 90), (0, 0))
        self.eyes[1].blit(pg.transform.rotate(eye, 90), (10, 0))
        self.eyes[2].blit(pg.transform.flip(eye, True, False), (0, 0))
        self.eyes[2].blit(pg.transform.flip(eye, True, False), (10, 0))
        self.eyes[3].blit(pg.transform.rotate(eye, -90), (0, 0))
        self.eyes[3].blit(pg.transform.rotate(eye, -90), (10, 0))
        self.frame = 0
        self.img = 0
        self.facing = 0
        self.screen = self.game.screen
        self.rect = self.image[self.img].get_rect()
        self.rect.x = 60
        self.rect.y = 240

    def draw(self):
        if self.mode == 0:
            self.screen.blit(self.image[self.img], self.rect)
        self.screen.blit(self.eyes[self.facing], (self.rect.x + 20, self.rect.y + 10))
        if 2 <= self.mode:
            if self.mode in (3, 5, 8, 11, 15):
                self.screen.blit(self.image[self.img], self.rect)
            else:
                self.screen.blit(self.fear[self.img], self.rect)

    def update(self):
        self.frame += 1
        if self.frame == 5:
            self.frame = 0
            self.img += 1
            if self.img == 2:
                self.img = 0
        if self.mode < 2:
            self.move = Vector(5, 0)
        else:
            self.move = Vector(-5, 0)
        self.rect.x += self.move.x
        self.rect.y += self.move.y
        if self.rect.x > self.screen.get_width():
            self.mode = 0
            self.rect.x = -122
            self.demo.pac.velocity = Vector(5, 0)
        self.draw()


class DPac(Sprite):
    def __init__(self, demo):
        super().__init__()
        self.demo = demo
        self.velocity = Vector(6, 0)
        self.game = self.demo.game
        self.screen = self.game.screen
        self.image = [pg.Surface((60, 60)), pg.Surface((60, 60)), pg.Surface((60, 60)), pg.Surface((60, 60))]
        img = pg.image.load('pacman1.png')
        for i in range(0,29):
            for j in range(0, 29):
                r, g, b, a = img.get_at((i, j))
                self.image[0].set_at((2 * i, 2 * j), (r, g, b, a))
                self.image[0].set_at((2 * i + 1, 2 * j), (r, g, b, a))
                self.image[0].set_at((2 * i, 2 * j + 1), (r, g, b, a))
                self.image[0].set_at((2 * i + 1, 2 * j + 1), (r, g, b, a))

        img = pg.image.load('pacman2.png')
        for i in range(0, 29):
            for j in range(0, 29):
                r, g, b, a = img.get_at((i, j))
                self.image[1].set_at((2 * i, 2 * j), (r, g, b, a))
                self.image[1].set_at((2 * i + 1, 2 * j), (r, g, b, a))
                self.image[1].set_at((2 * i, 2 * j + 1), (r, g, b, a))
                self.image[1].set_at((2 * i + 1, 2 * j + 1), (r, g, b, a))

        img = pg.image.load('pacman3.png')
        for i in range(0,29):
            for j in range(0, 29):
                r, g, b, a = img.get_at((i, j))
                self.image[2].set_at((2 * i, 2 * j), (r, g, b, a))
                self.image[2].set_at((2 * i + 1, 2 * j), (r, g, b, a))
                self.image[2].set_at((2 * i, 2 * j + 1), (r, g, b, a))
                self.image[2].set_at((2 * i + 1, 2 * j + 1), (r, g, b, a))

        self.image[3] = self.image[1]
        self.image.append(pg.transform.rotate(self.image[0], 90))
        self.image.append(pg.transform.rotate(self.image[1], 90))
        self.image.append(pg.transform.rotate(self.image[2], 90))
        self.image.append(pg.transform.rotate(self.image[3], 90))
        self.image.append(pg.transform.rotate(self.image[0], 180))
        self.image.append(pg.transform.rotate(self.image[1], 180))
        self.image.append(pg.transform.rotate(self.image[2], 180))
        self.image.append(pg.transform.rotate(self.image[3], 180))
        self.image.append(pg.transform.rotate(self.image[0], -90))
        self.image.append(pg.transform.rotate(self.image[1], -90))
        self.image.append(pg.transform.rotate(self.image[2], -90))
        self.image.append(pg.transform.rotate(self.image[3], -90))
        self.facing = 0
        self.frame = 0
        self.img = 0
        self.rect = self.image[self.img].get_rect()
        self.rect.x = 150
        self.rect.y = 240

    def draw(self):
        self.screen.blit(self.image[self.img + self.facing], self.rect)

    def move(self):
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y

    def update(self):
        self.frame += 1
        if self.frame == 3:
            self.img += 1
            self.frame = 0
            if self.img == 4:
                self.img = 0
        if self.rect.x > self.screen.get_width():
            self.velocity = Vector(-6, 0)
            self.facing = 8
            self.demo.ghost.mode = 80
            self.move()
            self.move()
            self.move()
        if self.rect.x < -60:
            self.velocity = Vector()
            self.rect.x = -60
            self.facing = 0
        if self.facing == 0 and self.rect.x == 150:
            self.velocity = Vector(6, 0)
        self.move()
        self.draw()


class Demo:
    def __init__(self, game):
        self.game = game
        self.ghost = DGhost(self)
        self.pac = DPac(self)
        self.hold = True
        self.finished = False
        self.image = pg.image.load('Title.png')
        self.rect = self.image.get_rect()
        self.rect.x = self.game.screen.get_width() / 2 - 400
        self.rect.y = 20
        self

    def play(self):
        while self.hold:
            for event in pg.event.get():
                e_type = event.type
                if e_type == pg.KEYDOWN:
                    if event.key == K_q:
                        return True
                    self.hold = False
            self.game.screen.fill((0, 0, 0))
            self.game.screen.blit(self.image, self.rect)
            self.ghost.update()
            self.pac.update()
            if pg.sprite.collide_rect(self.ghost, self.pac):
                self.ghost.mode = 1
            pg.display.update()
        self.game.play()
        return False


def main():
    finished = False
    while not finished:
        g = Game()
        d = Demo(g)
        finished = d.play()


if __name__ == '__main__':
    main()
