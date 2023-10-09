from settings import *
import pygame as pg


vec = pg.math.Vector2

class Player(pg.sprite.Sprite):
    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)
        
        self.game = game

        self.image = pg.Surface((30, 40))
        self.image.fill(WHITE)

        self.rect = self.image.get_rect()

        self.rect.center = (WIDTH / 2, HEIGHT / 2)

        self.pos = vec(WIDTH / 2, HEIGHT / 2)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

        self.is_jumping = False
        

    def jump(self):
        self.rect.y += 1
        hits = pg.sprite.spritecollide(self, self.game.platforms, False)
        self.rect.y -= 1

        if hits:
            
            self.vel.y = -20

    def update(self):
        
        self.acc = vec(0, PLAYER_GRAV)

        keys = pg.key.get_pressed()

        if keys[pg.K_LEFT]:
            self.acc.x = -PLAYER_ACC
        if keys[pg.K_RIGHT]:
            self.acc.x = PLAYER_ACC


        self.acc.x += self.vel.x * PLAYER_FRICTION
        self.vel +=  self.acc
        self.pos += self.vel + PLAYER_ACC * self.acc 

        if self.pos.x > WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = WIDTH

        self.rect.midbottom = self.pos


class Platform(pg.sprite.Sprite):
    def __init__(self, x, y, w, h):
        pg.sprite.Sprite.__init__(self)

        self.image = pg.Surface((w, h))
        self.image.fill(CAFE5_PURPLE)

        self.rect = self.image.get_rect()

        self.rect.x = x
        self.rect.y = y