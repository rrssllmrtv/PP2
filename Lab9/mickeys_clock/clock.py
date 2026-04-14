import pygame
import datetime

pygame.init()

screen = pygame.display.set_mode((800, 800))
pygame.display.set_caption("mickey clock")
clock = pygame.time.Clock()
FPS = 1
done = True

myClock = pygame.image.load('images/mainclock.png')
myClock = pygame.transform.scale(myClock, (600, 600))

minute_arrow = pygame.image.load('images/rightarm.png')
minute_arrow = pygame.transform.scale(minute_arrow, (800, 700))
second_arrow = pygame.image.load('images/leftarm.png')
second_arrow = pygame.transform.scale(second_arrow, (40, 500))

while done:
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                        done = False

        my_time = datetime.datetime.now()
        hourINT = int(my_time.strftime("%I"))
        minuteINT = int(my_time.strftime("%M"))
        secondINT = int(my_time.strftime("%S"))

        angleMINUTE = minuteINT * -6 - 25
        angleSECOND = secondINT * -6

        minute = pygame.transform.rotate(minute_arrow, angleMINUTE)
        second = pygame.transform.rotate(second_arrow, angleSECOND)
        
        
        screen.fill((255, 255, 255))
        screen.blit(myClock, (100, 100))
        screen.blit(second, (400 - int(second.get_width() / 2), 400 - int(second.get_height() / 2))) 
        screen.blit(minute, ((400 - int(minute.get_width() / 2), 400 - int(minute.get_height() / 2))))
        pygame.display.flip()
        clock.tick(60)
pygame.quit()