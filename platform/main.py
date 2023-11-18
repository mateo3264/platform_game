#4:27
import pygame as pg
import random
from settings import *
from sprites import *
from os import path
import sys
import pygame.midi as midi
import datetime 
from send_email import *
from itertools import chain
import numpy as np




class Game:
    def __init__(self, configs):
        
        pg.init()
        pg.mixer.init()
        midi.init()

        self.configs = configs

        #load piano if connected else pc keyboard
        #TODO: quitar hardcoded 1
        try:
            self.midi_input = midi.Input(1)
            self.playing_with_piano = True
        except:
            self.playing_with_piano = False 

        self.midi_output = midi.Output(0)

        random_instrument = random.randrange(100)
        print('random instrument:', random_instrument)
        self.midi_output.set_instrument(random_instrument)



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

        # print(self.patterns)

        self.available_notes = list(chain.from_iterable(self.patterns))

    def load_pattern_configurations(self):
        self.patterns = [
                        [67],
                        [52],
                        [60]
                        ]

        # print(self.patterns)
        self.note_dividing_left_and_right_hands = self.patterns[0][0]
        

        

        self.available_notes = list(chain.from_iterable(self.patterns))

    def load_audio_data(self):
        self.pyau = pyaudio.PyAudio()

        self.stream = self.pyau.open(
            format=AUDIO_FORMAT,
            channels=AUDIO_CHANNELS,
            rate=AUDIO_RATE,
            input=True,
            frames_per_buffer=AUDIO_CHUNK_SIZE
        )
    def load_data(self):
        self.load_audio_data()
        if hasattr(sys, '_MEIPASS'):
            self.dir = sys._MEIPASS
        else:
            self.dir = path.dirname(__file__)
        # print('self.dir', self.dir)

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
        # 28, 23
        self.standing_frame = pg.image.load(path.join(img_dir, 'ghost1.png')).convert()
        self.wind_image = pg.image.load(path.join(img_dir, 'wind.png')).convert()
        self.wind_image = pg.transform.scale(self.wind_image, (128, 128))
        self.wind_image = pg.transform.flip(self.wind_image, True, False)
        self.wind_image.set_colorkey(WHITE)
        
        self.spritesheet = Spritesheet(path.join(img_dir, SPRITESHEET))

        self.channel = pg.mixer.find_channel()
        

        self.jump_sound = pg.mixer.Sound(path.join(self.snd_dir, 'Jump4.wav'))
        self.landed_sound = pg.mixer.Sound(path.join(self.snd_dir, 'landed.wav'))
        self.boost_sound = pg.mixer.Sound(path.join(self.snd_dir, 'boost2.wav'))
        self.wings_sound = pg.mixer.Sound(path.join(self.snd_dir, 'wings.wav'))
        self.wind_sound = pg.mixer.Sound(path.join(self.snd_dir, 'wind.wav'))
        self.wind_sound.set_volume(0.2)

    def new(self):
        self.score = 0
        self.lives = 3
        self.remaining_platforms = 20
        self.max_n_platforms = 6
        self.pow_spawn_pct = 0#self.configs['max_pct_pows']
        self.last_score = 0
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

        self.fly_percent = 100

        self.bgcolor = [0, 155, 155]

        self.player_grav = .5


        self.player_text = False

        self.factor_for_change_of_scale = 1
        self.play_notes = False
        self.random_scale_idx = None

        self.last_chord_attack = 0
        
        pg.mixer.music.load(path.join(self.snd_dir, 'happytune.ogg'))
    
        self.run()

    def run(self):

        pg.mixer.music.play(loops=-10)
        pg.mixer.music.set_volume(0.0)
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
        
        audio_data = self.stream.read(AUDIO_CHUNK_SIZE)
        audio_array = np.frombuffer(audio_data, dtype=np.int16)

        if max(audio_array) > 100000:
            
        
            self.player.fly()
        else:
            self.player.flying = False



        hits = pg.sprite.spritecollide(self.player, self.platforms, False)

        if hits:
            lowest = hits[0]

            for hit in hits:
                if hit.rect.bottom > lowest.rect.bottom:
                    lowest = hit
            if self.player.pos.x < lowest.rect.right + 20\
                and self.player.pos.x > lowest.rect.left - 20:
                if self.player.pos.y < lowest.rect.centery:
                    if self.player.vel.y > 0:
                        self.player.pos.y = lowest.rect.top
                        if self.player.is_jumping:
                            # print('lowest.rect.top')
                            # print(lowest.rect.top)
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
                wind.rect.y += max(abs(self.player.vel.y) / 2, 2)

            for mob in self.mobs:
                mob.rect.y += max(abs(self.player.vel.y), 2)

            for plat in self.platforms:
                plat.rect.y += max(abs(self.player.vel.y), 2)
                if plat.rect.top >= HEIGHT + 100:
                    plat.kill()
                    self.score += 10
            
        pow_hits = pg.sprite.spritecollide(self.player, self.powerups, True)
        
        for pow in pow_hits:
            
            if pow.type == 'boost':
            
                self.player.vel.y = -BOOST_POWER * math.sqrt(self.player_grav)
                self.player.is_jumping = False
                self.player.landed = False
                self.boost_sound.play()
            
            elif pow.type == 'wings':
                if self.fly_percent <= 90:
                    self.fly_percent += randrange(self.configs['wings_range'][0], self.configs['wings_range'][1])
                self.wings_sound.play()

        while len(self.platforms) < self.max_n_platforms:
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
                self.player.jump(False)
                
            if self.lives == 0:
                self.playing = False
                self.midi_output.note_off(CHORD_PROGRESSION[self.random_scale_idx][0], 0)
                self.midi_output.note_off(CHORD_PROGRESSION[self.random_scale_idx][1], 0)
                self.midi_output.note_off(CHORD_PROGRESSION[self.random_scale_idx][2], 0)

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
        
        #todo: fix. it will substract until pow_spawn_pct is = 7
        if self.score % 100 == 0:
            if self.score - self.last_score > 100:
                
                if self.pow_spawn_pct > self.configs['min_pct_pows']:
                    self.pow_spawn_pct -= 1 
            if self.score > 300:
                if self.score > 500:
                    if self.score - self.last_score > 100:
                        self.bgcolor[1] -= 15
                        self.bgcolor[2] -= 15

                        if self.bgcolor[1] < 0:
                            self.bgcolor[1] = 0
                        
                        if self.bgcolor[2] < 0:
                            self.bgcolor[2] = 0
                        print('self.bgcolor')
                        print(self.bgcolor)
                        print('self.player_grav')
                        print(self.player_grav)
                        self.player_grav -= .1
                        if self.player_grav < .5:
                            self.player_grav = .5
                if self.score - self.last_score > 100:
                    
                    self.last_score = self.score
                    self.player.player_friction += .005
                    print('self.player.player_friction')
                    print(self.player.player_friction)
                
                if self.player.player_friction > -.05:
                    self.player.player_friction = -.05

        if self.play_notes:  
            #print('play') 
            self.random_scale_idx = random.randrange(len(CHORD_PROGRESSION))
            self.midi_output.note_on(CHORD_PROGRESSION[self.random_scale_idx][0], 100)
            self.midi_output.note_on(CHORD_PROGRESSION[self.random_scale_idx][1], 100)
            self.midi_output.note_on(CHORD_PROGRESSION[self.random_scale_idx][2], 100)
            self.play_notes = False
            self.last_chord_attack = pg.time.get_ticks()

            self.player.pattern_checker_arpegios.pattern = CHORD_PROGRESSION[self.random_scale_idx]
            self.player.pattern_checker_jump.pattern = [note - 12 for note in CHORD_PROGRESSION[self.random_scale_idx]]
            
            
        if not self.play_notes and self.random_scale_idx is not None:
            if pg.time.get_ticks() - self.last_chord_attack > 2000:
                self.last_chord_attack = pg.time.get_ticks()
                self.midi_output.note_off(CHORD_PROGRESSION[self.random_scale_idx][0], 0)
                self.midi_output.note_off(CHORD_PROGRESSION[self.random_scale_idx][1], 0)
                self.midi_output.note_off(CHORD_PROGRESSION[self.random_scale_idx][2], 0)
                self.random_scale_idx = None
                

        if self.score % (50 * self.factor_for_change_of_scale) == 0 and self.score != 0:
            print('cuando', self.factor_for_change_of_scale)
            print('50 * self.factor_for_change_of_scale')
            print(50 * self.factor_for_change_of_scale)
            self.factor_for_change_of_scale += 1
            self.play_notes = True


        
        
                


        if self.player.rect.top > HEIGHT + 200:
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
                if event.key == pg.K_h:
                    self.player_text = not self.player_text
                    
            if event.type == pg.KEYUP:
                if event.key == pg.K_a:
                    if self.remaining_platforms > 0:
                        Platform(self, 20, HEIGHT // 2, 0) 
                        self.remaining_platforms -= 1     
                if event.key == pg.K_w:
                    if self.remaining_platforms > 0:
                        Platform(self, WIDTH // 2 - 50, 20, 0)      
                        self.remaining_platforms -= 1     
                if event.key == pg.K_d:
                    if self.remaining_platforms > 0:
                        Platform(self, WIDTH - 120, HEIGHT // 2, 0)      
                        self.remaining_platforms -= 1     
                if event.key == pg.K_s:
                    if self.remaining_platforms > 0:
                        Platform(self, WIDTH - 120, HEIGHT - 20, 0)      
                        self.remaining_platforms -= 1     
                    
            if event.type == pg.KEYUP:
                if event.key == pg.K_SPACE:
                    self.player.jump_cut()

    def draw_flytime_bar(self, surf, x, y):
        fill = (self.fly_percent / 100) * 200
        fill_rect = pg.Rect(x, y, fill, 20)
        whole_rect = pg.Rect(x, y, 200, 20)
        pg.draw.rect(surf, RED, whole_rect)
        pg.draw.rect(surf, GREEN, fill_rect)

    def draw(self):

        self.screen.fill(self.bgcolor)
        self.all_sprites.draw(self.screen)
        
        self.draw_text(str(self.score), 22, WHITE, WIDTH / 2, 15)
        self.draw_text(str(self.lives), 32, GREEN, WIDTH - 50, 15)
        self.draw_text(str(self.remaining_platforms), 32, BLACK, WIDTH - 50, 55)
        
        self.draw_flytime_bar(self.screen, 20, 20)
        plat = self.spritesheet.get_image(218, 1456, 201, 100)
        plat.set_colorkey(BLACK)
        rect = plat.get_rect()
        plat = pg.transform.scale(plat, (rect.width // 4, rect.height // 4))
        rect.top = 50
        rect.right = WIDTH - 50
        self.screen.blit(plat, rect.center)

        plat = self.spritesheet.get_image(812, 554, 54, 49)
        plat.set_colorkey(BLACK)
        rect = plat.get_rect()
        plat = pg.transform.scale(plat, (rect.width, rect.height))
        rect.center = WIDTH - 100, 25
        self.screen.blit(plat, rect.center)
        
        if self.player_text:
            draw_speech_bubble(self.screen, 'Hi! My name is caffe 5', BLACK, WHITE, 
                               (self.player.rect.right - 10, self.player.rect.top + 10), 20
            )


        pg.display.flip()

    def show_start_screen(self):
        pg.mixer.music.load(path.join(self.snd_dir, 'Yippee.ogg'))
        pg.mixer.music.play(-1)
        pg.mixer.music.set_volume(0.1)
        if not self.playing_with_piano:
            self.screen.fill(BGCOLOR)
        else:
            self.screen.fill(RED)
        self.draw_text(TITLE, 50, WHITE, WIDTH / 2, HEIGHT / 4) 
        self.draw_text(f'High Score: {str(self.highscore)}', 40, WHITE, WIDTH / 2, HEIGHT / 2) 
        self.draw_text(f'space: jump', 25, WHITE, WIDTH / 2, int(4 * HEIGHT / 6) )
        self.draw_text(f'left arrow:left', 25, WHITE, WIDTH / 2, int(4 * HEIGHT / 6) + 30 )
        self.draw_text(f'right arrow: right', 25, WHITE, WIDTH / 2, int(4 * HEIGHT / 6) + 60)
        #self.draw_text(f'E: easy; H: hard', 25, WHITE, WIDTH / 2, int(4 * HEIGHT / 6) + 80)
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
        try:
            if self.score > 2000:
                send_mail(self.score)
        except:
            print('Seems that internet connection is not working!')
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


g = Game(easy_configs)
g.show_start_screen()

while g.running:
    g.new()
    g.show_go_screen()

pg.quit()
g.stream.stop_stream()
g.stream.close()
g.pyau.terminate()
