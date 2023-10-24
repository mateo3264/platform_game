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
                        [57, 59],
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
        
        

        
        self.spritesheet = Spritesheet(path.join(img_dir, SPRITESHEET))

        self.jump_sound = pg.mixer.Sound(path.join(self.snd_dir, 'Jump4.wav'))
        self.landed_sound = pg.mixer.Sound(path.join(self.snd_dir, 'landed.wav'))
        self.boost_sound = pg.mixer.Sound(path.join(self.snd_dir, 'boost2.wav'))

    def new(self):
        self.score = 0
        self.all_sprites = pg.sprite.Group()
        self.platforms = pg.sprite.Group()
        self.powerups = pg.sprite.Group()
        self.player = Player(self)
        p1 = Platform(self, 0, HEIGHT - 40)

        for p_coors in PLATFORM_LIST:
            typ = random.choice([0, 1])
            p = Platform(self, *p_coors, typ)

        
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


               

        
        if self.player.rect.top > HEIGHT:
            for sprite in self.all_sprites:
                sprite.rect.y -= max(self.player.vel.y, 10)
                if sprite.rect.top < 0:
                    sprite.kill()
        if len(self.platforms) == 0:
            self.playing = False
    # def piano_events(self):
    #     if   self.midi_input.poll():
    #         self.midi_events = self.midi_input.read(10)
    #         for midi_event in self.midi_events:
    #             timestamp, note_on, _, _ = midi_event[0]
    #             if note_on == 64:
    #                 self.player.jump()
    #                 self.player.is_jumping = True
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
        self.screen.blit(self.player.image, self.player.rect)
        self.draw_text(str(self.score), 22, WHITE, WIDTH / 2, 15)
        

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