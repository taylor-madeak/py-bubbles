import pygame, os
from src.playfield import Playfield
from src.bubble import Bubble
from src.constants import *
from pygame.locals import *


def main():

    # initialize pygame
    pygame.init()

    # set up the main window
    screen = pygame.display.set_mode(DISP_SIZE)
    pygame.display.set_caption('Py-Bubbles')
    screen.set_colorkey(pygame.Color('MAGENTA'))

    # set up the background
    # test background for now
    # later, src.Playfield will handle this part
    test_bkg = pygame.image.load(os.path.join(BGI_PATH, 'test_bkg.jpg'))

    #background = pygame.Surface(screen.get_size()).convert()
    # background.fill(pygame.Color('blue'))
    background = pygame.transform.scale(test_bkg, DISP_SIZE).convert()

    # load music
    # this may need to move or use a variable to integrate level music later
    pygame.mixer.music.load(os.path.join(BGM_PATH, 'test_music_drums.wav'))

    # start playing the music
    if BGM_ENABLED:
        pygame.mixer.music.set_volume(BGM_VOLUME)
        pygame.mixer.music.play(loops=-1, start=0.0)

    playfield = Playfield(PFLD_SIZE, CELL_SIZE)
    playfield.load_map(os.path.join(os.curdir, 'maps', 'TEST_MAP1.JSON'))
    playfield.rect.center = screen.get_rect().center

    ball_angle = 20

    clock = pygame.time.Clock()

    while True:
        # paste the background
        screen.blit(background, (0, 0))

        # update the playfield and blit it
        playfield.update()
        screen.blit(playfield.surface, playfield.rect.topleft)

        # this is the event handler, which we should move to src.Control
        # this is where any graphical updates are blitted to the display
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    fire_test(playfield, ball_angle)

                    if ball_angle < 160:
                        ball_angle += 5
                    else:
                        ball_angle = 20

        # update the display to show changes
        # in production, we will use "dirty rect" updating to improve performance
        pygame.display.update()

        pygame.event.pump()

        # set framerate to no more than 60FPS
        clock.tick(60)

    # stop music playback
    # this will need to move later to the appropriate place based on design
    pygame.mixer.music.stop()

    pygame.quit()


def fire_test(playfield: Playfield, angle):
    b_start_addr = (-1, 14)
    b_start = list(playfield.hexmap.board.get(b_start_addr).get_pixelpos())
    b_start[0] = int(b_start[0] + (playfield.get_surface().get_size()[0] / 2) - b_start[0])

    if len(playfield.active_bubble) == 0:
        fire = Bubble(
            b_start_addr,                                       # address
            b_start,                                            # pixelpos
            playfield.get_surface().get_rect(),                 # bounds
            int(playfield.hexmap.cellsize[0] - 2),              # radius
            'RED',                                              # fill_color
            'BLACK',                                            # stroke_color
            angle,                                              # angle
            10,                                                 # velocity
            (playfield.all_sprites, playfield.active_bubble)    # *groups
        )
        #playfield.active_bubble.add(fire)
        #playfield.all_sprites.add(fire)

if __name__ == "__main__":
    main()
