#4:27
import pygame as pg
import random
from settings import *
from sprites import *
from os import path
import sys
import pygame.midi as midi
import datetime 


class Game:
    def __init__(self):
        
        pg.init()
        pg.mixer.init()
        midi.init()


        #load piano if connected else pc keyboard
        #TODO: quitar hardcoded 1
        try:
            self.midi_input = midi.Input(1)
            self.playing_with_piano = True
        except:
            self.playing_with_piano = False 

        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)

        self.clock = pg.time.Clock()

        self.font_name = pg.font.match_font(FONT_NAME)        

        self.running = True
        

        self.load_pattern_configurations()

        self.is_pattern_changed = False
        self.last_platform_type = 0

        self.player_moves = ''

        self.load_data()


    def transpose_pattern(self, value):       
        self.patterns = [[e + value for e in pattern] for pattern in self.patterns]
        self.note_dividing_left_and_right_hands = self.patterns[0][0] 

        print(self.patterns)

        self.available_notes = list(chain.from_iterable(self.patterns))

    def load_pattern_configurations(self):
        self.patterns = [
                        [60, 64, 67],
                        [52, 55, 59],
                        [67, 64, 60]
                        ]

        print(self.patterns)
        self.note_dividing_left_and_right_hands = self.patterns[0][0]
        

        

        self.available_notes = list(chain.from_iterable(self.patterns))


    def load_data(self):
        if hasattr(sys, '_MEIPASS'):
            self.dir = sys._MEIPASS
        else:
            self.dir = path.dirname(__file__)
        print('self.dir', self.dir)

        img_dir = path.join(self.dir, 'img')
        self.snd_dir = path.join(self.dir, 'snd')
        

        with open(path.join(self.dir, HS_FILE), 'a+') as f:
            try:
                f.seek(0)
                self.highscore = int(f.read())
            except:
                self.highscore = 0
        
        self.cloud_images = []
        for i in range(1, 4):
            self.cloud_images.append(pg.image.load(path.join(img_dir, f'cloud{i}.png')).convert())

        self.wind_image = pg.image.load(path.join(img_dir, 'wind.png')).convert()
        self.wind_image = pg.transform.scale(self.wind_image, (128, 128))
        self.wind_image = pg.transform.flip(self.wind_image, True, False)
        self.wind_image.set_colorkey(WHITE)
        
        self.spritesheet = Spritesheet(path.join(img_dir, SPRITESHEET))

        self.channel = pg.mixer.find_channel()
        

        self.jump_sound = pg.mixer.Sound(path.join(self.snd_dir, 'Jump4.wav'))
        self.landed_sound = pg.mixer.Sound(path.join(self.snd_dir, 'landed.wav'))
        self.boost_sound = pg.mixer.Sound(path.join(self.snd_dir, 'boost2.wav'))
        self.wind_sound = pg.mixer.Sound(path.join(self.snd_dir, 'wind.wav'))
        self.wind_sound.set_volume(0.2)

    def new(self):
        self.score = 0
        self.lives = 3
        self.pow_spawn_pct = 20
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.platforms = pg.sprite.Group()
        self.powerups = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.clouds = pg.sprite.Group()
        self.winds = pg.sprite.Group()
        self.player = Player(self)
        p1 = Platform(self, 0, HEIGHT - 40)

        for p_coors in PLATFORM_LIST:
            typ = random.choice([0, 1])
            p = Platform(self, *p_coors, typ)



        self.mob_spawn_timer = 0

        self.wind = 0
        self.wind_spawn_timer = 0
        self.wind_animation_timer = 0
        
        pg.mixer.music.load(path.join(self.snd_dir, 'happytune.ogg'))
    
        self.run()

    def run(self):

        pg.mixer.music.play(loops=-1)
        self.playing = True 
        

        while self.playing:
            self.clock.tick(FPS)
            self.events()
            # self.piano_events()
            self.update()
            self.draw()
        pg.mixer.music.fadeout(500)

    def update(self):
        self.all_sprites.update()
        

        hits = pg.sprite.spritecollide(self.player, self.platforms, False)

        if hits:
            lowest = hits[0]

            for hit in hits:
                if hit.rect.bottom > lowest.rect.bottom:
                    lowest = hit
            if self.player.pos.x < lowest.rect.right + 10\
                and self.player.pos.x > lowest.rect.left - 10:
                if self.player.pos.y < lowest.rect.centery:
                    if self.player.vel.y > 0:
                        self.player.pos.y = lowest.rect.top
                        if self.player.is_jumping:
                            print('lowest.rect.top')
                            print(lowest.rect.top)
                            self.player_moves += f'{lowest.rect.midtop},'
                        self.player.vel.y = 0
                        self.player.is_jumping = False
                        if not self.player.landed:
                            self.landed_sound.play()
                            self.player.landed = True
                        
            if lowest.type == 0:
                if not self.is_pattern_changed and self.last_platform_type == 1:
                    self.transpose_pattern(0)
                    self.is_pattern_changed = True
                    self.last_platform_type = 0
                    
            else:
                if not self.is_pattern_changed and self.last_platform_type == 0:
                    self.transpose_pattern(0)
                    self.is_pattern_changed = True
                    self.last_platform_type = 1
        if self.player.is_jumping:
            self.is_pattern_changed = False
        
        if self.player.pos.y < HEIGHT / 3:
            self.player.pos.y += max(abs(self.player.vel.y), 2)
            
            #number of clouds proportional to score
            if randrange(100) < max(1, self.score / 100):
                Cloud(self)
            
            for cloud in self.clouds:
                if cloud.layer_idx == 0:
                    speed = randrange(50, 200) / 100
                    cloud.rect.y += max(abs(self.player.vel.y / speed), 2)
                else:
                    cloud.rect.y += max(abs(self.player.vel.y * randrange(4, 6) / 3), 2)
            
            for wind in self.winds:
                wind.rect.y += max(abs(self.player.vel.y), 2)

            for mob in self.mobs:
                mob.rect.y += max(abs(self.player.vel.y), 2)

            for plat in self.platforms:
                plat.rect.y += max(abs(self.player.vel.y), 2)
                if plat.rect.top >= HEIGHT:
                    plat.kill()
                    self.score += 10
            
            pow_hits = pg.sprite.spritecollide(self.player, self.powerups, True)

            for pow in pow_hits:
                if pow.type == 'boost':
                    self.player.vel.y = -BOOST_POWER
                    self.player.is_jumping = False
                    self.player.landed = False
                    self.boost_sound.play()

            while len(self.platforms) < 6:
                width = random.randrange(60, 120)
                typ = random.choice([0, 1])
                p = Platform(self, 
                             random.randrange(0, WIDTH - width), 
                             random.randrange(-100, -30, 20),
                             typ
                             )

        now = pg.time.get_ticks()
        if self.score > 200:
            if now - self.mob_spawn_timer > max(MOB_FREQ, random.choice([10000, 12000, 14000, 16000, 18000]) - self.score * 10):
                self.mob_spawn_timer = now
                Mob(self)
        
        mob_hits = pg.sprite.spritecollide(self.player, self.mobs, True, pg.sprite.collide_mask)

        if mob_hits:
            if self.lives > 0:
                self.lives -= 1
            if self.lives == 0:
                self.playing = False

        if self.score > 500:
            if now - self.wind_spawn_timer > 5000:
                self.wind_spawn_timer = now
                wind_magnitude = choice([0, .1, .2, .3 ,self.score / 10000])
                wind_direction = choice([-1, 1])
                self.wind = wind_direction * wind_magnitude

                if self.wind:
                    n_winds = 0
                    while len(self.winds) < 3:
                        Wind(self, 50 + n_winds*50, wind_direction)
                        n_winds += 1
                    
                    self.wind_sound.set_volume(wind_magnitude)
                    self.wind_sound.play(1) 
                    if wind_direction == -1:
                        self.channel.set_volume(1.0, 0.0)
                        self.channel.play(self.wind_sound)
                    else:
                        self.channel.set_volume(0.0, 1.0)
                        self.channel.play(self.wind_sound)

        if self.score % 100 == 0:
            if self.pow_spawn_pct > 7:
                self.pow_spawn_pct -= 1                 

        if self.player.rect.top > HEIGHT:
            for sprite in self.all_sprites:
                sprite.rect.y -= max(self.player.vel.y, 10)
                if sprite.rect.top < 0:
                    sprite.kill()
        if len(self.platforms) == 0:
            self.playing = False
    
    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.player.jump()
                    self.player_moves += '^\n'
                    self.player.is_jumping = True
                    
                    
            if event.type == pg.KEYUP:
                if event.key == pg.K_SPACE:
                    self.player.jump_cut()


    def draw(self):

        self.screen.fill(BGCOLOR)
        self.all_sprites.draw(self.screen)
        
        self.draw_text(str(self.score), 22, WHITE, WIDTH / 2, 15)
        self.draw_text(str(self.lives), 32, GREEN, WIDTH - 50, 15)
        

        pg.display.flip()

    def show_start_screen(self):
        pg.mixer.music.load(path.join(self.snd_dir, 'Yippee.ogg'))
        pg.mixer.music.play(-1)
        if not self.playing_with_piano:
            self.screen.fill(BGCOLOR)
        else:
            self.screen.fill(RED)
        self.draw_text(TITLE, 50, WHITE, WIDTH / 2, HEIGHT / 4) 
        self.draw_text(f'High Score: {str(self.highscore)}', 40, WHITE, WIDTH / 2, HEIGHT / 2) 
        self.draw_text(f'space: jump', 25, WHITE, WIDTH / 2, int(4 * HEIGHT / 6) )
        self.draw_text(f'left arrow:left', 25, WHITE, WIDTH / 2, int(4 * HEIGHT / 6) + 30 )
        self.draw_text(f'right arrow: right', 25, WHITE, WIDTH / 2, int(4 * HEIGHT / 6) + 60)
        pg.display.flip()
        self.wait_for_key()

        pg.mixer.music.fadeout(500)

    def show_go_screen(self):
        pg.mixer.music.load(path.join(self.snd_dir, 'Yippee.ogg'))
        pg.mixer.music.play(-1)
        if not self.running:
            return
        self.screen.fill(BLACK)
        self.draw_text('Game Over!', 40, RED, WIDTH / 2, HEIGHT / 4)
        self.draw_text(f'Score: {self.score}', 30, RED, WIDTH / 2, HEIGHT / 3)
        self.draw_text(f'Press any key to play again!', 20, RED, WIDTH / 2, 3 * HEIGHT / 4)
        if self.score > self.highscore:
            self.highscore = self.score
            self.draw_text(f'New High Score! {self.highscore}', 20, GREEN, WIDTH / 2, HEIGHT / 2)
            with open(path.join(self.dir, HS_FILE), 'w') as f:

                f.write(str(self.score))
        else:
            self.draw_text(f'Score {self.score}', 20, GREEN, WIDTH / 2, HEIGHT / 2)            
        pg.display.flip()

        with open(path.join(self.dir, PLAYER_FILE), 'a') as f:
            now = datetime.datetime.now()
            f.write(15*'*'+'NEW GAME'+' '+now.strftime('%Y-%m-%d %H:%M:%S')+15*'*'+'\n')
            f.write(self.player_moves)
            self.player_moves = ''
        self.wait_for_key()

        pg.mixer.music.fadeout(500)

    def wait_for_key(self):
        waiting = True

        while waiting:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                
                if event.type == pg.KEYUP:
                    waiting = False
                

    def draw_text(self, text, size, color, x, y):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)


g = Game()
g.show_start_screen()

while g.running:
    g.new()
    g.show_go_screen()

pg.quit()