import pygame
import numpy as np
import pprint
import random

#Board size: 7 cols, 6 rows (7x6)

pointer_yellow_img = pygame.image.load("yellow_triangle.png")
pointer_red_img = pygame.image.load("red_triangle.png")

class Point:
    def __init__(self,x,y):
        self.x = float(x)
        self.y = float(y)


class Circle:
    def __init__(self,surface,pos,radius,status) -> None:
        self.surface = surface
        self.pos = pos
        self.radius = radius
        #With status: 0 = empty slot, 1 = red slot, 2 = yellow slot
        self.update_status(status)
    def update_status(self,status):
        self.status = status
        if self.status == 0:
            self.colour = (255,255,255)
        elif self.status == 1:
            self.colour = (235,64,52)
        elif self.status == 2:
            self.colour = (222,205,58)
        else:
            print(f"Error: invalid slot status: {self.colour}")
            
class Pointer:
    def __init__(self,size,pos) -> None:
        self.size = size*2
        self.pos = pos
    def draw(self,status):
        self.status = status
        if self.status == 1:
            pointer_red = pygame.transform.scale(pointer_red_img,(self.size,self.size))
            screen.blit(pointer_red,(self.pos.x,self.pos.y))
        elif self.status == 2:
            pointer_yellow = pygame.transform.scale(pointer_yellow_img,(self.size,self.size))
            screen.blit(pointer_yellow,(self.pos.x,self.pos.y))

pygame.init()

SCREEN_SIZE = (600,600)
BOARD_SIZE = pygame.Rect(0,50,SCREEN_SIZE[0],SCREEN_SIZE[1])

screen = pygame.display.set_mode(SCREEN_SIZE)


circle = Circle(screen,Point(200,200),75,0)
board_padding = 7
slots = [[],[],[],[],[],[]]
rand_row = random.randint(0,5)
rand_col = random.randint(0,6)
slot_size = ((550*2)/(board_padding*7)+(board_padding/2))

for n in range(0,6):
    for i in range(0,7):
        circle = Circle(screen,Point(i*((SCREEN_SIZE[0]-board_padding)/7)+slot_size+(board_padding*2),n*((BOARD_SIZE.height-board_padding)/6)+50+(slot_size*1.1)),slot_size,0)
        slots[n].append(circle)
slots[5][rand_col].update_status(2)


pointer = Pointer(slot_size,Point(board_padding*2,0))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill((255,255,255,255))

    pygame.draw.rect(screen,(57, 137, 163,255), BOARD_SIZE)
    for i in range(len(slots)):
        for n in range(len(slots[i])):
            circle = slots[i][n]
            pygame.draw.circle(circle.surface,circle.colour,(circle.pos.x,circle.pos.y),circle.radius)
    pointer.draw(1)
    

    pygame.display.flip()
pygame.quit()