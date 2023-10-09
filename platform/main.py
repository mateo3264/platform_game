#4:27
import pygame as pg
import random
from settings import *
from sprites import *


class Game:
    def __init__(self):
        
        pg.init()
        pg.mixer.init()

        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)

        self.clock = pg.time.Clock()

        

        self.running = True

    def new(self):
        self.all_sprites = pg.sprite.Group()
        self.platforms = pg.sprite.Group()
        self.player = Player(self)
        p1 = Platform(0, HEIGHT - 40, WIDTH, 40)
        self.all_sprites.add(self.player)

        for p_coors in PLATFORM_LIST:
            p = Platform(*p_coors)
            self.all_sprites.add(p)
            self.platforms.add(p)
        
        self.run()

    def run(self):
        self.playing = True 

        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def update(self):
        self.all_sprites.update()
        

        hits = pg.sprite.spritecollide(self.player, self.platforms, False)

        if hits:
            if self.player.vel.y > 0:
                self.player.pos.y = hits[0].rect.top
                self.player.vel.y = 0
        
        if self.player.pos.y < HEIGHT / 4:
            self.player.pos.y += abs(self.player.vel.y)

            for plat in self.platforms:
                plat.rect.y += abs(self.player.vel.y)
                if plat.rect.top >= HEIGHT:
                    plat.kill()
            
            while len(self.platforms) < 6:
                width = random.randrange(60, 120)
                p = Platform(random.randrange(0, WIDTH - width), 
                             random.randrange(-100, -30, 20),
                             width,
                             20
                             )
                self.platforms.add(p)
                self.all_sprites.add(p)

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.player.jump()
                    self.player.is_jumping = True

    def draw(self):
        self.screen.fill(BLACK)
        self.all_sprites.draw(self.screen)
        

        pg.display.flip()

    def show_start_screen(self):
        pass 

    def show_go_screen(self):
        pass

g = Game()
g.show_start_screen()

while g.running:
    g.new()
    g.show_go_screen()

pg.quit()