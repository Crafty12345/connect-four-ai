import pygame
import numpy as np
import pprint
import random
import argparse
import time
import gym
import pandas
import math


pygame.init()
log_id = time.time()

status_dict = {
    0: "NONE",
    1: "RED",
    2: "YELLOW"
}

# Board size: 7 cols, 6 rows (7x6)

pointer_yellow_img = pygame.image.load("yellow_triangle.png")
pointer_red_img = pygame.image.load("red_triangle.png")

end_game_font = pygame.font.Font("freesansbold.ttf", 56)

parser = argparse.ArgumentParser()
parser.add_argument("mode", action="store", type=str)
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


def sigmoid(x):
    return 1/(1+math.exp(-x))


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


def printDict(_dict):
    print("\n")
    print("\n".join("{}\t\t{}".format(k, v) for k, v in _dict.items()))


def check_for_in_a_row(grid, status):
    count_list = {
        "STATUS": status_dict[status],
        "horizontal": [],
        "vertical": [],
        "down_right_diagonal": [],
        "up_right_diagonal": [],
    }

    count_summarised = {
        "STATUS": status_dict[status],
        "horizontal": 0,
        "vertical": 0,
        "down_right_diagonal": 0,
        "up_right_diagonal": 0,
    }

    stats = {
        "horizontal": {
            "mean": 0,
            "median": 0,
            "mode": 0,
            "std": 0,
        },
        "vertical": {
            "mean": 0,
            "median": 0,
            "mode": 0,
            "std": 0,
        },

        "down_right_diagonal": {
            "mean": 0,
            "median": 0,
            "mode": 0,
            "std": 0,
        },

        "up_right_diagonal": {
            "mean": 0,
            "median": 0,
            "mode": 0,
            "std": 0,
        },



    }


    lst_horizontal = []
    lst_vertical = []
    lst_downRight = []
    lst_upRight = []
    indexes = ["horizontal","vertical","down_right_diagonal","up_right_diagonal"]

    for row_index in range(len(grid)):
        for i in range(len(grid[row_index])):
            if grid[row_index][i].status != 0:
                for _ in range(0, 3):
                
                    temp_horizontal = 0
                    temp_vertical = 0
                    temp_downRight = 0
                    temp_upRight = 0

                    #Check num in row horizontally
                    if i + _ <= len(grid[row_index]) - 1:
                        if grid[row_index][i+_].status == status:
                            temp_horizontal += 1
                    if row_index + _ <= len(grid)-1:
                        if grid[row_index + _][i].status == status:
                            temp_vertical += 1
                    if i + _ <= len(grid[row_index]) - 1 and row_index + _ <= len(grid)-1:
                        if grid[row_index + _][i + _].status == status:
                            temp_downRight += 1
                    if i + _ <= len(grid[row_index])-1 and row_index - _ >= 0:
                        if grid[row_index - _][i + _].status == status:
                            temp_upRight += 1

                    lst_horizontal.append(temp_horizontal)
                    lst_vertical.append(temp_vertical)
                    lst_downRight.append(temp_downRight)
                    lst_upRight.append(temp_upRight)


    stats["horizontal"]["std"] = np.std(lst_horizontal)
    stats["vertical"]["std"] = np.std(lst_vertical)
    stats["down_right_diagonal"]["std"] = np.std(lst_downRight)
    stats["up_right_diagonal"]["std"] = np.std(lst_upRight)

    lst_horizontal.sort()
    lst_horizontal = lst_horizontal[int(stats["horizontal"]["std"]*len(lst_horizontal)):]
    lst_vertical.sort()
    lst_vertical = lst_vertical[int(stats["vertical"]["std"]*len(lst_vertical)):]
    lst_downRight.sort()
    lst_downRight = lst_downRight[int(stats["down_right_diagonal"]["std"]*len(lst_downRight)):]
    lst_upRight.sort()
    lst_upRight = lst_upRight[int(stats["up_right_diagonal"]["std"]*len(lst_upRight)):]

    count_list["horizontal"].extend(lst_horizontal)
    count_list["vertical"].extend(lst_vertical)
    count_list["down_right_diagonal"].extend(lst_downRight)
    count_list["up_right_diagonal"].extend(lst_upRight)

    for index in indexes:
        count_summarised[index] = np.average((count_list[index]))
    printDict(count_summarised)
    print("Standard Deviation: ",np.std(count_list[index]))
    print("Mean: ",np.mean(count_list[index]))
    print("Median: ",np.median(count_list[index]))
    print("n Scores: ", len(count_list[index]))
    #print(len(count_list["horizontal"]))


def check_for_win(grid, statuses) -> int:
    for status in statuses:
        for row_index in range(len(grid)):
            for i in range(len(grid[row_index])):
                #Check for horizontal win
                if i+3 <= len(grid[row_index])-1:
                    if (grid[row_index][i].status == status and
                        grid[row_index][i+1].status == status and
                        grid[row_index][i+2].status == status and
                            grid[row_index][i+3].status == status):
                        return status
                if row_index+3 <= len(grid)-1:
                    #Check for vertical win
                    if (grid[row_index][i].status == status and
                        grid[row_index+1][i].status == status and
                        grid[row_index+2][i].status == status and
                            grid[row_index+3][i].status == status):
                        return status
                if i+3 <= len(grid[row_index])-1 and row_index+3 <= len(grid)-1:
                    #Check for down-right diagonal win
                    if (grid[row_index][i].status == status and
                        grid[row_index+1][i+1].status == status and
                        grid[row_index+2][i+2].status == status and
                            grid[row_index+3][i+3].status == status):
                        return status
                if i+3 <= len(grid[row_index])-1 and row_index-3 >= 0:
                    #Check for up-right diagonal win
                    if (grid[row_index][i].status == status and
                        grid[row_index-1][i+1].status == status and
                        grid[row_index-2][i+2].status == status and
                            grid[row_index-3][i+3].status == status):
                        return status
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
                        check_for_in_a_row(slots, 1)
                        check_for_in_a_row(slots, 2)
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
                    with open(f"logs/log_{log_id}.txt", "a+") as f:
                        f.write(get_grid_status(slots) + "\n")
            if event.key == pygame.K_SPACE and game_ended:
                slots = generate_slots([[], [], [], [], [], []])
                pointer = DEF_SETTINGS["pointer"]
                win_status = DEF_SETTINGS["win_status"]
                game_ended = DEF_SETTINGS["game_ended"]

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
        game_ended = True
        if win_status == 2:
            text = end_game_font.render(
                "Yellow Wins!", True, pygame.Color(222, 205, 58), None)
            #print("Yellow wins!")
        elif win_status == 1:
            text = end_game_font.render(
                "Red Wins!", True, pygame.Color(235, 64, 52), None)
            #print("Red wins!")
        textRect = text.get_rect()
        textRect.center = (SCREEN_SIZE[0]/2, SCREEN_SIZE[1]/2)
        screen.blit(text, textRect)

    pygame.display.flip()
pygame.quit()
