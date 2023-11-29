import pygame as pg
from os import path

rel_path = '../tile_based/snd/score1.png'
dir_path = path.abspath(rel_path)

# img_path = path.join(dir_path, 'img')

print('dir_path', dir_path)


def draw_speech_bubble(screen, text, text_colour, bg_colour, pos, size):

    font = pg.font.SysFont(None, size)
    text_surface = font.render(text, True, (*text_colour, 100))
    text_rect = text_surface.get_rect(bottomleft=pos)

    # background
    bg_rect = text_rect.copy()
    bg_rect.inflate_ip(10, 10)

    # Frame
    frame_rect = bg_rect.copy()
    frame_rect.inflate_ip(4, 4)

    pg.draw.rect(screen, text_colour, frame_rect)
    pg.draw.rect(screen, (*bg_colour, 100), bg_rect)
    screen.blit(text_surface, text_rect)


def draw_image_bubble(screen,  pos, filename):
    image = pg.image.load(filename).convert()
    image.set_alpha(128)
    rect = image.get_rect()
    rect.center = pos
    rect.width = 350
    rect.height = 150

    #tmp_surf = pg.Surface((350, 150))

    #tmp_surf.blit(image, (0, 0, 350, 150))
    
    

    # background
    # bg_rect = rect.copy()
    # bg_rect.inflate_ip(10, 10)

    # Frame
    # frame_rect = bg_rect.copy()
    # frame_rect.inflate_ip(4, 4)

    #pg.draw.rect(tmp_surf, (255, 255, 255), frame_rect)
    #pg.draw.rect(tmp_surf, (255, 255, 255), bg_rect)
    screen.blit(image, (350, 150), (50, 0, 350, 150))

