import pygame as pg


pg.init()



screen = pg.display.set_mode(size=(500, 500))

clock = pg.time.Clock()


surf = pg.Surface((140, 140))

rect_x, rect_y = 0, 0

def get_status_key(rect_x, rect_y):
    keys = pg.key.get_pressed()

    if keys[pg.K_LEFT]:
        rect_x -= 10
        
    if keys[pg.K_RIGHT]:
        rect_x += 10
    return rect_x

while True:
    for event in pg.event.get():
        
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
    rect_x = get_status_key(rect_x, rect_y)
        

    
    
    surf.fill((0, 0, 0))
    pg.draw.rect(surf, (255, 255, 0), (rect_x, 40, 40, 80))
    screen.fill('purple')
    screen.blit(surf, (0, 0))
    pg.display.flip()
    clock.tick(60)
