import pygame
import numpy as np
import pprint
import random
import argparse
import time

log_id = time.time()

# Board size: 7 cols, 6 rows (7x6)

pointer_yellow_img = pygame.image.load("yellow_triangle.png")
pointer_red_img = pygame.image.load("red_triangle.png")

parser = argparse.ArgumentParser()
parser.add_argument("mode",action="store",type=str)
args = parser.parse_args()
print(args.mode)


class Point:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)


class Circle:
    """
    With status: 0 = empty slot, 1 = red slot, 2 = yellow slot
    """

    def __init__(self, surface, pos, radius, status) -> None:
        self.surface = surface
        self.pos = pos
        self.radius = radius
        self.update_status(status)

    def update_status(self, status):
        self.status = status
        if self.status == 0:
            self.colour = (255, 255, 255)
        elif self.status == 1:
            self.colour = (235, 64, 52)
        elif self.status == 2:
            self.colour = (222, 205, 58)
        else:
            print(f"Error: invalid slot status: {self.colour}")


class Pointer:
    def __init__(self, size, pos,status) -> None:
        self.size = size*2
        self.pos = pos
        self.selected = 0
        self.status = status

    def update_position(self, selected):
        self.selected = selected
        self.pos.x = self.selected*((self.size+board_padding)*1.75)

    def draw(self):
        if self.status == 1:
            pointer_red = pygame.transform.scale(
                pointer_red_img, (self.size, self.size))
            screen.blit(pointer_red, (self.pos.x, self.pos.y))
        elif self.status == 2:
            pointer_yellow = pygame.transform.scale(
                pointer_yellow_img, (self.size, self.size))
            screen.blit(pointer_yellow, (self.pos.x, self.pos.y))


def get_grid_status(grid):
    string = ""
    for a in grid:
        string += "\n["
        for b in a:
            string += " " + str(b.status)
        string += " ]"
    return string


def is_col_full(grid, req_col):
    """
    This function will return True if the column is full and False if every slot in the column is empty.
    """
    for row in grid:
        if row[req_col].status == 0:
            return False
    return True


def check_slot_availability(grid, req_col):
    """
    grid: The LoL containing the data for each slot
    req_col: Requested Column (Column to check)

    This function returns:
        -1 if all cells in column are filled OR;
        The coordinates of the available slot of the column
    """

    col_sum = 0
    for i in range(len(grid)):
        col_sum += grid[i][req_col].status
        #TODO: Move if is_col_full to out of for loop
        if is_col_full(grid, req_col):
            return -1
    if col_sum == 0:
        #print("Slot empty.")
        return (req_col, 5)
    for i in reversed(range(len(grid))):
        if grid[i][req_col].status == 0:
            return (req_col, i)


pygame.init()

SCREEN_SIZE = (600, 600)
BOARD_SIZE = pygame.Rect(0, 100, SCREEN_SIZE[0], SCREEN_SIZE[1])

screen = pygame.display.set_mode(SCREEN_SIZE)


circle = Circle(screen, Point(200, 200), 75, 0)
board_padding = 7
slots = [[], [], [], [], [], []]
rand_row = random.randint(0, 5)
rand_col = random.randint(0, 6)
slot_size = ((450*2)/(board_padding*7)+(board_padding/2))

for n in range(0, 6):
    for i in range(0, 7):
        circle = Circle(screen, Point(i*((SCREEN_SIZE[0]-board_padding)/7)+slot_size+(
            board_padding*2), n*((BOARD_SIZE.height-board_padding)/7)+110+(slot_size)), slot_size, 0)
        slots[n].append(circle)
slots[5][rand_col].update_status(2)
available_cols = list(range(0,7))


pointer = Pointer(slot_size, Point(board_padding*2, 50),1)

print(get_grid_status(slots))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT and pointer.selected != 0:
                pointer.update_position(pointer.selected-1)
            if event.key == pygame.K_RIGHT and pointer.selected != 6:
                pointer.update_position(pointer.selected+1)
            if event.key == pygame.K_RETURN:
                available_slot = check_slot_availability(
                    slots, pointer.selected)
                if available_slot != -1:
                    slots[available_slot[1]][available_slot[0]].update_status(pointer.status)
                elif available_slot == -1:
                    pass
                if args.mode == "multiplayer":
                    pointer.status = 2 if pointer.status+1==2 else 1
                elif args.mode == "random":
                    #red
                    rand_col = random.randint(0,6)
                    available_slot = check_slot_availability(
                                    slots,rand_col)
                    while available_slot == -1:
                        rand_col = random.randint(0,6)
                        available_slot = check_slot_availability(
                                        slots,rand_col)
                slots[available_slot[1]][available_slot[0]].update_status(2)
                with open(f"logs/log_{log_id}.txt","a+") as f:
                    f.write(get_grid_status(slots) + "\n")

        if event.type == pygame.QUIT:
            running = False
    screen.fill((255, 255, 255, 255))

    pygame.draw.rect(screen, (57, 137, 163, 255), BOARD_SIZE)
    for i in range(len(slots)):
        for n in range(len(slots[i])):
            circle = slots[i][n]
            pygame.draw.circle(circle.surface, circle.colour,
                               (circle.pos.x, circle.pos.y), circle.radius)
    pointer.draw()

    pygame.display.flip()
pygame.quit()
