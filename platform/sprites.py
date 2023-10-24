from settings import *
import pygame as pg
import pygame.midi as midi
from random import choice, randrange

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
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        
        # midi.init()
        # self.midi_input = midi.Input(1)

        

        self.game = game
        self.pattern_checker = PatternChecker(game)

        self.load_images()

        self.image = self.standing_frames[0]
        

        self.rect = self.image.get_rect()

        self.rect.center = (40, HEIGHT - 100)

        self.pos = vec(40, HEIGHT -100)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)


        self.player_acc = 1

        self.direction = 0

        self.curr_pattern = []

        
        
        #animation

        

        self.is_jumping = False
        self.walking = False
        self.landed = False
        self.current_frame = 0
        self.last_update = 0

    def load_images(self):
        self.standing_frames = [self.game.spritesheet.get_image(614, 1063, 120, 191),
                                self.game.spritesheet.get_image(690, 406, 120, 201)
                                ]
        

        for frame in self.standing_frames:
            frame.set_colorkey(BLACK)
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

    def jump_cut(self):
        if self.is_jumping and self.vel.y < -3:
            self.vel.y = -3

    def jump(self):
        self.rect.y += 2
        hits = pg.sprite.spritecollide(self, self.game.platforms, False)
        self.rect.y -= 2

        if hits and not self.is_jumping:
            # Y velocity is proportional to X velocity
            self.game.jump_sound.play()
            self.vel.y = -JUMP_VEL - min(abs(self.vel.x), 4)
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
        

        # print('NORMAL')
        # print(self.vel.x)
        #doesn't allow to slide forever
        if abs(self.direction) < .01:
            self.direction = 0
            self.walking = False
        #reduces velocity by reducing factor multiplying acceleration
        self.direction *= .9 
        self.acc  = vec(0, PLAYER_GRAV)
        
        
        if self.game.playing_with_piano:
            self.piano_update()
        else:
            self.normal_update()
              
        self.acc.x = self.player_acc * self.direction
        
        self.acc.x += self.vel.x * PLAYER_FRICTION 
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

        self.rect.x = x
        self.rect.y = y

        if randrange(100) < POW_SPAWN_PCT:
            p = Pow(self.game, self)


class Pow(pg.sprite.Sprite):
    def __init__(self, game, plat):
        self.groups = game.all_sprites, game.powerups
        pg.sprite.Sprite.__init__(self, self.groups)

        self.game = game
        self.plat = plat

        self.type = 'boost'
    

        self.image = self.game.spritesheet.get_image(820, 1805, 71, 70).convert()
        self.image.set_colorkey(BLACK)

        self.rect = self.image.get_rect()

        self.rect.centerx = self.plat.rect.centerx
        self.rect.bottom = self.plat.rect.top - 5
        
    
    def update(self):
        self.rect.bottom = self.plat.rect.top - 5

        if not self.game.platforms.has(self.plat):
            self.kill()
