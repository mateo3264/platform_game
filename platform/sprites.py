from settings import *
import pygame as pg
import pygame.midi as midi
from random import choice, randrange
import math 

vec = pg.math.Vector2

    

class PatternChecker:
    def __init__(self, game):
        
        # 0:left, 1:jump, 2:right
        self.game = game

        #self.game.patterns = self.game.patterns
        self.user_pattern = [[], []]
        self.active_moves = [False, False, False]

        self.total_time_of_running_pattern = 0


    def reset_active_moves(self):
        self.active_moves = [False, False, False]

    #add note to user pattern
    def add_note_to_user_pattern(self):
        now = pg.time.get_ticks() 
        if self.game.midi_input.poll():
            midi_events = self.game.midi_input.read(10)
            
            for midi_event in midi_events:
                info, note_on, volume, _ = midi_event[0]
                timestamp = midi_event[1]
                               
                if note_on in self.game.available_notes:
                    if volume != 0:
                        
                        if note_on < self.game.note_dividing_left_and_right_hands:
                            
                            if len(self.user_pattern[0]) > 1:
                                time_between_notes = self.user_pattern[0][-1][1] - self.user_pattern[0][-2][1]
                                if  time_between_notes < MAX_TIME_BETWEEN_NOTES:
                                    self.total_time_of_running_pattern += time_between_notes
                                    self.user_pattern[0].append([note_on, timestamp])
                                else:
                                    self.user_pattern[0] = []
                                    self.total_time_of_running_pattern = 0
                            else:
                                self.user_pattern[0].append([note_on, timestamp])
                        else:
                            
                            if len(self.user_pattern[1]) > 1:
                                time_between_notes = self.user_pattern[1][-1][1] - self.user_pattern[1][-2][1]
                                if time_between_notes < MAX_TIME_BETWEEN_NOTES:
                                    self.total_time_of_running_pattern += time_between_notes
                                    self.user_pattern[1].append([note_on, timestamp])         
                                else:
                                    self.user_pattern[1] = []
                                    self.total_time_of_running_pattern = 0
                            else:
                                self.user_pattern[1].append([note_on, timestamp])
                    #elif volume == 0 and         
                                

    def check_pattern(self):
        is_pattern_completed = False
        idx_of_pattern = []
        
        for i, user_pattern in enumerate(self.user_pattern):
            match = False
          
            user_pattern = [note[0] for note in user_pattern]
            # print(user_pattern)
            for j, pattern in enumerate(self.game.patterns):
                
                if user_pattern == pattern:
                    self.user_pattern[i] = []
                    self.active_moves[j] = True
                    match = True
                elif user_pattern == pattern[:len(user_pattern)]:
                    match = True
            if not match:
                    self.user_pattern[i] = []
        return self.active_moves


class Spritesheet:
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert()
    
    def get_image(self, x, y, width, height):
        image = pg.Surface((width, height))
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        image = pg.transform.scale(image, (width // 2, height // 2))
        return image


class Player(pg.sprite.Sprite):
    def __init__(self, game):
        self._layer = PLAYER_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        
        # midi.init()
        # self.midi_input = midi.Input(1)

        

        self.game = game
        self.pattern_checker = PatternChecker(game)

        self.load_images()
        # print('self.standing_frames')
        # print(self.standing_frames)
        self.image = self.standing_frames[0]
        

        self.rect = self.image.get_rect()

        self.rect.center = (40, HEIGHT - 100)

        self.pos = vec(40, HEIGHT -100)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)


        self.player_acc = 1

        self.player_friction = -.12

        
        self.flying = False

        self.direction = 0

        self.curr_pattern = []

        
        
        #animation

        

        self.is_jumping = False
        self.walking = False
        self.landed = False
        self.current_frame = 0
        self.last_update = 0

    def load_images(self):
        # self.standing_frames = [self.game.spritesheet.get_image(614, 1063, 120, 191),
        #                         self.game.spritesheet.get_image(690, 406, 120, 201)
        #                         ]
        self.standing_frames = [self.game.standing_frame
                                ]
        image = pg.transform.scale(self.standing_frames[0], (120, 97))
        image.set_colorkey(WHITE)
        self.standing_frames = [image]
        # self.standing_frames[0] = self.standing_frames[0]
        # for frame in self.standing_frames:
        #     frame.set_colorkey(BLACK)
        self.walk_frames_r = [self.game.spritesheet.get_image(678, 860, 120, 201),
                              self.game.spritesheet.get_image(692, 1458, 120, 207),
                                ]
        for frame in self.walk_frames_r:
            frame.set_colorkey(BLACK)
        self.walk_frames_l = []

        for frame in self.walk_frames_r:
            self.walk_frames_l.append(pg.transform.flip(frame, True, False))
        
        for frame in self.walk_frames_l:
            frame.set_colorkey(BLACK)

        self.jump_frame = self.game.spritesheet.get_image(382, 763, 150, 181)

        self.jump_frame.set_colorkey(BLACK)
    
    def fly(self):
        if self.game.fly_percent > 1:
            self.vel.y = -10
            self.game.fly_percent -= 1
            self.flying = True

    def jump_cut(self):
        if self.is_jumping and self.vel.y < -3:
            self.vel.y = -3

    def jump(self, platform=True):
        if platform:
            self.rect.y += 2
            hits = pg.sprite.spritecollide(self, self.game.platforms, False)
            self.rect.y -= 2
        else:
            hits = True
            self.is_jumping = False

        if hits and not self.is_jumping:
            # Y velocity is proportional to X velocity
            self.game.jump_sound.play()
            self.vel.y = -JUMP_VEL - min(abs(self.vel.x), 4)
            self.vel.y *= math.sqrt(self.game.player_grav)
            self.is_jumping = True
            self.landed = False

    def animate(self):
        now = pg.time.get_ticks()
        if not self.is_jumping and not self.walking:
            if now - self.last_update > 350:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.standing_frames)
                bottom = self.rect.bottom
                self.image = self.standing_frames[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom

        elif self.walking:
            if now - self.last_update > 200:
                
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.standing_frames)
                bottom = self.rect.bottom
                if self.vel.x < 0:
                    self.image = self.walk_frames_l[self.current_frame]
                    self.rect = self.image.get_rect()
                    self.rect.bottom = bottom
                elif self.vel.x > 0:
                    self.image = self.walk_frames_r[self.current_frame]
                    self.rect = self.image.get_rect()
                    self.rect.bottom = bottom

        elif self.is_jumping:
            
            self.last_update = now
            self.image = self.jump_frame
        
        self.mask = pg.mask.from_surface(self.image)

    def normal_update(self):
        keys = pg.key.get_pressed()
        
        if keys[pg.K_LEFT]:
            self.walking = True
            self.direction = -1
            self.acc.x = -self.player_acc
            self.game.player_moves += '<-\n'
        if keys[pg.K_RIGHT]:
            self.walking = True
            self.direction = 1
            self.acc.x = self.player_acc
            self.game.player_moves += '->\n'
        # if keys[pg.K_SPACE]:
        #     self.jump()

    def piano_update(self):
        self.pattern_checker.add_note_to_user_pattern()


        self.pattern_checker.check_pattern()


        for i, active_move in enumerate(self.pattern_checker.active_moves):
            if active_move:
                if i == 0:
                    self.walking = True
                    self.direction = 1
                    self.player_acc = 1
                    self.player_acc = min(120 * self.player_acc / self.pattern_checker.total_time_of_running_pattern, 3)
                    print('self.player_acc')
                    print(self.player_acc)
                    print('self.pattern_checker.total_time_of_running_pattern')
                    print(self.pattern_checker.total_time_of_running_pattern)
                    self.game.player_moves += '->\n'
                    
                elif i == 1:
                    self.jump()
                    self.game.player_moves += '^\n'
                    # self.is_jumping = True
                else:
                    self.walking = True
                    self.direction = -1
                    self.player_acc = 1
                    self.player_acc = min(120 * self.player_acc / self.pattern_checker.total_time_of_running_pattern, 3)
                    print('self.player_acc')
                    print(self.player_acc)
                    print('self.pattern_checker.total_time_of_running_pattern')
                    print(self.pattern_checker.total_time_of_running_pattern)
                    self.game.player_moves += '<-\n'
                    
                    
                    
        
        self.pattern_checker.reset_active_moves()



    def update(self):

        self.animate()
        
        # if not self.flying:
        #     if self.game.fly_percent < 100:
        #         self.game.fly_percent += 1

        # print('NORMAL')
        # print(self.vel.x)
        #doesn't allow to slide forever
        if abs(self.direction) < .01:
            self.direction = 0
            self.walking = False
        #reduces velocity by reducing factor multiplying acceleration
        self.direction *= .9 
        self.acc  = vec(0, self.game.player_grav)
        
        
        if self.game.playing_with_piano:
            self.piano_update()
        else:
            self.normal_update()
              
        self.acc.x = self.player_acc * self.direction
        
        self.acc.x += self.vel.x * self.player_friction + self.game.wind
        self.vel += self.acc 
        self.pos += self.vel + self.player_acc * self.acc
        
        if self.pos.x > WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = WIDTH

        self.rect.midbottom = self.pos

        self.pattern_checker.total_time_of_running_pattern = 0


class Platform(pg.sprite.Sprite):
    def __init__(self, game, x, y, type=0):
        self._layer = PLATFORM_LAYER
        self.groups = game.all_sprites, game.platforms
        pg.sprite.Sprite.__init__(self, self.groups)

        self.game = game
        images = [
            self.game.spritesheet.get_image(0, 288, 380, 94).convert(),
            self.game.spritesheet.get_image(213, 1662, 201, 100).convert()
        ]

        for image in images:
            image.set_colorkey(BLACK)

        

        self.type = type

        if self.type == 0:
            self.image = images[0]
        else:
            self.image = images[1]
        
        self.rect = self.image.get_rect()
        scale = max(.5, min(1000 / (self.game.score + 1), 2))
        self.image = pg.transform.scale(self.image, (self.rect.width * scale, self.rect.height))
        self.rect = self.image.get_rect()

        self.rect.x = x
        self.rect.y = y

        if randrange(100) < self.game.pow_spawn_pct:
            p = Pow(self.game, self, choice(['boost', 'wings']))


class Pow(pg.sprite.Sprite):
    def __init__(self, game, plat, tipo='boost'):
        self._layer = POW_LAYER
        self.groups = game.all_sprites, game.powerups
        pg.sprite.Sprite.__init__(self, self.groups)

        self.game = game
        self.plat = plat

        self.type = tipo
    
        if self.type == 'boost':
            self.image = self.game.spritesheet.get_image(820, 1805, 71, 70)
        else:
            self.image = self.game.spritesheet.get_image(826, 1292, 71, 70)

        self.image.set_colorkey(BLACK)

        self.rect = self.image.get_rect()

        self.rect.centerx = self.plat.rect.centerx
        self.rect.bottom = self.plat.rect.top - 5
        
    
    def update(self):
        self.rect.bottom = self.plat.rect.top - 5

        if not self.game.platforms.has(self.plat):
            self.kill()
        
        


class Mob(pg.sprite.Sprite):
    def __init__(self, game):
        self._layer = MOB_LAYER
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)

        self.game = game

        self.image_up = self.game.spritesheet.get_image(566, 510, 122, 139).convert()
        self.image_up.set_colorkey(BLACK)

        self.image_down = self.game.spritesheet.get_image(568, 1534, 122, 135).convert()
        self.image_down.set_colorkey(BLACK)

        self.image = self.image_down

        self.rect = self.image.get_rect()

        self.rect.centerx = choice([-100, WIDTH + 100])

        self.vx = randrange(1, 4)

        if self.rect.centerx > WIDTH:
            self.vx *= -1
        
        self.rect.y = randrange(HEIGHT / 2)

        self.vy = 0
        self.dy = 0.5

    def update(self):
        self.rect.x += self.vx
        self.vy += self.dy

        if self.vy > 3 or self.vy < -3:
            self.dy *= -1
        
        center = self.rect.center

        if self.dy < 0:
            self.image = self.image_up 
        else:
            self.image = self.image_down 
        
        self.rect = self.image.get_rect()

        self.rect.center = center

        self.rect.y += self.vy 

        if self.rect.right < -100 or self.rect.left > WIDTH + 100:
            self.kill()
        
        self.mask = pg.mask.from_surface(self.image)

class Cloud(pg.sprite.Sprite):
    def __init__(self, game):
        self.layer_idx = choice(CLOUD_LAYER)
        self._layer = self.layer_idx
        self.groups = game.all_sprites, game.clouds
        pg.sprite.Sprite.__init__(self, self.groups)

        self.game = game

        self.image = choice(self.game.cloud_images)


        self.image.set_colorkey(BLACK)

        self.rect = self.image.get_rect()
        if self.layer_idx == 3:
            
            self.image = pg.transform.scale(self.image, (self.rect.width * 2, int(self.rect.height * 4 / 3)))
        else:
            scale = randrange(50, 100) / 100
            self.image = pg.transform.scale(self.image, (self.rect.width * scale, int(self.rect.height * scale)))
        self.rect = self.image.get_rect()
        
        self.rect.x = randrange(WIDTH - self.rect.width)

        self.rect.y = randrange(-500, -50)
    
    def update(self):
        if self.rect.top > HEIGHT * 2:
            self.kill()

class Wind(pg.sprite.Sprite):
    def __init__(self, game, x, vel_dir):
        self._layer = 3 
        self.groups = game.all_sprites, game.winds

        pg.sprite.Sprite.__init__(self, self.groups)

        self.game = game

        self.image = self.game.wind_image

        self.rect = self.image.get_rect()

        if vel_dir == -1:
            self.rect.centerx = WIDTH + x
            self.image = pg.transform.flip(self.image, True, False)
        elif vel_dir == 1:
            self.rect.centerx = -x

        
        self.rect.y = HEIGHT / 4
        
        self.vx = vel_dir * 5
    
    def update(self):
        self.rect.x += self.vx 

        if self.rect.x  < -200 or self.rect.x > WIDTH + 200:
            self.kill()
        
        if self.rect.y > HEIGHT:
            self.kill()
        