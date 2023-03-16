import pygame
import numpy as np
import pprint
import random
import argparse
import time


pygame.init()
log_id = time.time()

# Board size: 7 cols, 6 rows (7x6)

pointer_yellow_img = pygame.image.load("yellow_triangle.png")
pointer_red_img = pygame.image.load("red_triangle.png")

end_game_font = pygame.font.Font("freesansbold.ttf", 56)
score_font = pygame.font.Font("freesansbold.ttf", 34)

parser = argparse.ArgumentParser()
parser.add_argument("mode", action="store", type=str)
args = parser.parse_args()
scores = [0, 0]
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
    def __init__(self, size, pos, status) -> None:
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
        # TODO: Move if is_col_full to out of for loop
        if is_col_full(grid, req_col):
            return -1
    if col_sum == 0:
        # print("Slot empty.")
        return (req_col, 5)
    for i in reversed(range(len(grid))):
        if grid[i][req_col].status == 0:
            return (req_col, i)


def is_grid_full(grid):
    for row in grid:
        for n in row:
            if n.status == 0:
                return False
    return True


def check_for_win(grid, statuses) -> int:
    for status in statuses:
        for n in range(len(grid)):
            for i in range(len(grid[n])):
                # Check for horizontal win
                if i+3 <= len(grid[n])-1:
                    if (grid[n][i].status == status and
                        grid[n][i+1].status == status and
                        grid[n][i+2].status == status and
                            grid[n][i+3].status == status):
                        return status
                if n+3 <= len(grid)-1:
                    # Check for vertical win
                    if (grid[n][i].status == status and
                        grid[n+1][i].status == status and
                        grid[n+2][i].status == status and
                            grid[n+3][i].status == status):
                        return status
                if i+3 <= len(grid[n])-1 and n+3 <= len(grid)-1:
                    # Check for down-right diagonal win
                    if (grid[n][i].status == status and
                        grid[n+1][i+1].status == status and
                        grid[n+2][i+2].status == status and
                            grid[n+3][i+3].status == status):
                        return status
                if i+3 <= len(grid[n])-1 and n-3 >= 0:
                    # Check for up-right diagonal win
                    if (grid[n][i].status == status and
                        grid[n-1][i+1].status == status and
                        grid[n-2][i+2].status == status and
                            grid[n-3][i+3].status == status):
                        return status
    if (is_grid_full(grid)):
        return -1

    return 0


def generate_slots(slots):
    for n in range(0, 6):
        for i in range(0, 7):
            circle = Circle(screen, Point(i*((SCREEN_SIZE[0]-board_padding)/7)+slot_size+(
                board_padding*2), n*((BOARD_SIZE.height-board_padding)/7)+110+(slot_size)), slot_size, 0)
            slots[n].append(circle)
    return slots


board_padding = 7
slot_size = ((450*2)/(board_padding*7)+(board_padding/2))

DEF_SETTINGS = {
    "slots": [[], [], [], [], [], []],
    "pointer": Pointer(slot_size, Point(board_padding*2, 50), 1),
    "game_ended": False,
    "win_status": 0

}


pygame.display.set_caption("Connect Four Bot")

SCREEN_SIZE = (600, 600)
BOARD_SIZE = pygame.Rect(0, 100, SCREEN_SIZE[0], SCREEN_SIZE[1])

screen = pygame.display.set_mode(SCREEN_SIZE)


slots = generate_slots(DEF_SETTINGS["slots"])
pointer = DEF_SETTINGS["pointer"]
win_status = DEF_SETTINGS["win_status"]
game_ended = DEF_SETTINGS["game_ended"]

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if not game_ended:
                if not args.mode == "RvR":
                    if event.key == pygame.K_LEFT and pointer.selected != 0:
                        pointer.update_position(pointer.selected-1)
                    if event.key == pygame.K_RIGHT and pointer.selected != 6:
                        pointer.update_position(pointer.selected+1)
                    if event.key == pygame.K_RETURN:
                        available_slot = check_slot_availability(
                            slots, pointer.selected)
                        if available_slot != -1:
                            slots[available_slot[1]][available_slot[0]
                                                     ].update_status(pointer.status)
                        elif available_slot == -1:
                            pass
                        if args.mode == "PvP":
                            pointer.status = 2 if pointer.status+1 == 2 else 1
                        elif args.mode == "PvR":
                            # red
                            rand_col = random.randint(0, 6)
                            available_slot = check_slot_availability(
                                slots, rand_col)
                            while available_slot == -1:
                                rand_col = random.randint(0, 6)
                                available_slot = check_slot_availability(
                                    slots, rand_col)
                            slots[available_slot[1]
                                  ][available_slot[0]].update_status(2)

                        win_status = check_for_win(slots, [1, 2])
                        if win_status > 0:
                            scores[win_status-1] += 1

                        with open(f"logs/log_{log_id}.txt", "a+") as f:
                            f.write(get_grid_status(slots) + "\n")
            if event.key == pygame.K_SPACE and game_ended:
                slots = generate_slots([[], [], [], [], [], []])
                pointer = DEF_SETTINGS["pointer"]
                win_status = DEF_SETTINGS["win_status"]
                game_ended = DEF_SETTINGS["game_ended"]
    if not game_ended:
        if args.mode == "RvR":
            rand_col = random.randint(0, 6)
            available_slot = check_slot_availability(
                slots, rand_col)
            while available_slot == -1:
                rand_col = random.randint(0, 6)
                available_slot = check_slot_availability(
                    slots, rand_col)
            slots[available_slot[1]][available_slot[0]].update_status(1)

            rand_col = random.randint(0, 6)
            available_slot = check_slot_availability(
                slots, rand_col)
            while available_slot == -1:
                rand_col = random.randint(0, 6)
                available_slot = check_slot_availability(
                    slots, rand_col)
            slots[available_slot[1]][available_slot[0]].update_status(2)

            win_status = check_for_win(slots, [1, 2])
            if win_status != 0:
                scores[win_status-1] += 1

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
    if win_status != 0:
        if args.mode != "RvR":
            game_ended = True
            if win_status == 2:
                text = end_game_font.render(
                    "Yellow Wins!", True, pygame.Color(222, 205, 58), None)
                # print("Yellow wins!")
            elif win_status == 1:
                text = end_game_font.render(
                    "Red Wins!", True, pygame.Color(235, 64, 52), None)
                # print("Red wins!")
            elif win_status == -1:
                text = end_game_font.render(
                    "Tie", True, pygame.Color(128, 128, 128), None)
            textRect = text.get_rect()
            textRect.center = (SCREEN_SIZE[0]/2, SCREEN_SIZE[1]/2)
            screen.blit(text, textRect)
        elif args.mode == "RvR":
            game_ended = True
            slots = generate_slots([[], [], [], [], [], []])
            pointer = DEF_SETTINGS["pointer"]
            win_status = DEF_SETTINGS["win_status"]
            game_ended = DEF_SETTINGS["game_ended"]

    total_rounds = sum(scores)

    text = score_font.render(
        str(scores[1]), True, pygame.Color(222, 205, 58), None)
    textRect = text.get_rect()
    textRect.center = (len(str(scores[0]))*30, 20)
    screen.blit(text, textRect)

    percent_string = str(
        round((scores[1]/total_rounds)*100, 2)) + "%" if total_rounds > 0 else "0%"
    text = score_font.render(percent_string, True,
                             pygame.Color(222, 205, 58), None)
    textRect = text.get_rect()
    textRect.center = (len(percent_string)*15, 50)
    screen.blit(text, textRect)

    text = score_font.render(
        str(scores[0]), True, pygame.Color(235, 64, 52), None)
    textRect = text.get_rect()
    textRect.center = (SCREEN_SIZE[0]-(len(str(scores[1]))*30), 20)
    screen.blit(text, textRect)

    percent_string = str(
        round((scores[0]/total_rounds)*100, 2)) + "%" if total_rounds > 0 else "0%"
    text = score_font.render(percent_string, True,
                             pygame.Color(235, 64, 52), None)
    textRect = text.get_rect()
    textRect.center = (SCREEN_SIZE[0]-(len(percent_string)*15),
                       50) if total_rounds > 0 else (SCREEN_SIZE[0]-(len("0%")*15), 50)
    screen.blit(text, textRect)

    text = score_font.render("Total Rounds:", True,
                             pygame.Color(0, 0, 0), None)
    textRect = text.get_rect()
    textRect.center = (SCREEN_SIZE[0]/2, 20)
    screen.blit(text, textRect)

    text = score_font.render((str(total_rounds)), True,
                             pygame.Color(0, 0, 0), None)
    textRect = text.get_rect()
    textRect.center = (SCREEN_SIZE[0]/2, 45)
    screen.blit(text, textRect)

    pygame.display.flip()
pygame.quit()
