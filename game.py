import numpy as np
import pprint
import random
import argparse
import time
import gym
import pandas
import math
import pygame


log_id = time.time()

status_dict = {
    0: "NONE",
    1: "RED",
    2: "YELLOW"
}

# Board size: 7 cols, 6 rows (7x6)

scores = [0,0]

parser = argparse.ArgumentParser()
parser.add_argument("mode", action="store", type=str)
parser.add_argument("--output-stats",action=argparse.BooleanOptionalAction,type=bool,
                    help="""Whether or not to print statistics about the current game to the console
                    upon every turn.""",required=False,default=False)
parser.add_argument("--count-states",action=argparse.BooleanOptionalAction,type=bool,required=False,default=False,
                    help="""Whether or not to count
                    the number of unique board states.""")
parser.add_argument("--visualise",action=argparse.BooleanOptionalAction,type=bool,required=False,default=True,
                    help="""Whether or not to show the game on screen.""")
parser.add_argument("--track-win-progress",action=argparse.BooleanOptionalAction,type=bool,required=False,default=True,
                    help="""Whether or not to run the check_n_in_row()
                            and process_stats() methods.""")

args = parser.parse_args()
print(args)

SCREEN_SIZE = (600, 600)
BOARD_SIZE = pygame.Rect(0, 100, SCREEN_SIZE[0], SCREEN_SIZE[1])


if args.visualise == True:
    pygame.init()
    pointer_yellow_img = pygame.image.load("yellow_triangle.png")
    pointer_red_img = pygame.image.load("red_triangle.png")

    end_game_font = pygame.font.Font("freesansbold.ttf", 56)
    score_font = pygame.font.Font("freesansbold.ttf", 34)

    pygame.display.set_caption("Connect Four Bot")

    screen = pygame.display.set_mode(SCREEN_SIZE)


with open("data/possible_combinations","r") as f:
    unique_state_list = eval(f.read())
    num_combinations = len(unique_state_list)
with open("data/num_duplicates","r") as f:
    duplicate_combinations = int(f.read())

class Point:
    """
    This class pretty much just exists for convinience, no real other reason.
    """

    def __init__(self, x: float, y: float):
        """
        x = the horizontal coordinate of the point \n
        y = the vertical coordinate of the point 
        """
        self.x = x
        self.y = y


class Circle:
    """
    A class to store the data for the slots/tokens in the game. \n
    IMPORTANT: always use update_status() when changing the status of a Circle.
    """

    def __init__(self, pos: Point, radius: float, status: int) -> None:
        """
        - With status:
        - - 0 = empty slot;
        - - 1 = red slot;
        - - 2 = yellow slot
        """
        
        global args
        if (args.visualise == True):
            global screen
            self.surface = screen
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
    """
    A simple class to control attributes of the pointer.
    IMPORTANT: When updating the position of the pointer, use
    update_position() instead of changing the variable manually.
    """

    def __init__(self, size, pos, status) -> None:
        self.size = size*2
        self.pos = pos
        self.selected = 0
        self.status = status

    def update_position(self, selected: int):
        """
        This method is used to update the position of the pointer.
        - "selected" is an integer, which refers to the index that the pointer
            will be moved to.
        """
        self.selected = selected
        self.pos.x = self.selected*((self.size+board_padding)*1.75)

    def draw(self):
        """
        This method must be called every single frame,
        otherwise the pointer will not render.
        """

        if self.status == 1:
            pointer_red = pygame.transform.scale(
                pointer_red_img, (self.size, self.size))
            screen.blit(pointer_red, (self.pos.x, self.pos.y))
        elif self.status == 2:
            pointer_yellow = pygame.transform.scale(
                pointer_yellow_img, (self.size, self.size))
            screen.blit(pointer_yellow, (self.pos.x, self.pos.y))


def sigmoid(x: float,a: float=1,c: float=0) -> float:
    return 1/(1+math.exp((-a)*x-c))

def custom_exp(x,i,c,m) -> float:
    """
    This is quite a confusing function, so visit the Desmos Graph (https://www.desmos.com/calculator/1g22flrvnn)
    to play with different values and properly understand.\n
    The gist is that this function makes lower values lower than their original value
    and higher values higher than their original value.
    """
    return math.exp(i*x)/(c-(m*math.e))*math.e


def get_grid_status(grid) -> str:
    """
    This function returns a string, which resembles the current board.
    """
    string = ""
    for a in grid:
        string += "\n["
        for b in a:
            string += " " + str(b.status)
        string += " ]"
    return string


def is_col_full(grid, req_col) -> bool:
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
    """
    A function which outputs a dictionary in a visually appealing way\n
    _dict: The dictionary to be outputted
    """
    print("\n")
    print("\n".join("{}\t\t{}".format(k, v) for k, v in _dict.items()))


def process_stats(lst_horizontal: list, lst_vertical: list,
                  lst_downRight: list, lst_upRight: list, indexes: list, status: int,
                  pos_spaces: int):
    """
    This function should ONLY be called by the function "check_for_in_a_row".
    This function performs operations on the data relating to the state of the game and the player
    or bot's progress towards winning.
    """

    global n_turns

    space_efficiency = sigmoid(pos_spaces,a=0.65,c= -3.5) / n_turns[status] if n_turns[status] > 0 else 0
    #space_efficiency = pos_spaces

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
        "space_efficiency": space_efficiency,
        "n_turns": n_turns
    }

    stats = {"horizontal": {
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

    # lst_horizontal = [X for X in lst_horizontal if X != 0]
    # lst_vertical = [X for X in lst_vertical if X != 0]
    # lst_downRight = [X for X in lst_downRight if X != 0]
    # lst_upRight = [X for X in lst_upRight if X != 0]

    if (len(lst_horizontal)>0 and
        len(lst_vertical)>0 and
        len(lst_downRight)>0 and
        len(lst_upRight)>0):
            stats["horizontal"]["std"] = np.std(lst_horizontal)
            stats["vertical"]["std"] = np.std(lst_vertical)
            stats["down_right_diagonal"]["std"] = np.std(lst_downRight)
            stats["up_right_diagonal"]["std"] = np.std(lst_upRight)

            lst_horizontal.sort()
            lst_horizontal = lst_horizontal[int(
                stats["horizontal"]["std"]*len(lst_horizontal)):]
            lst_vertical.sort()
            lst_vertical = lst_vertical[int(
                stats["vertical"]["std"]*len(lst_vertical)):]
            lst_downRight.sort()
            lst_downRight = lst_downRight[int(
                stats["down_right_diagonal"]["std"]*len(lst_downRight)):]
            lst_upRight.sort()
            lst_upRight = lst_upRight[int(
                stats["up_right_diagonal"]["std"]*len(lst_upRight)):]

            count_list["horizontal"].extend(lst_horizontal)
            count_list["vertical"].extend(lst_vertical)
            count_list["down_right_diagonal"].extend(lst_downRight)
            count_list["up_right_diagonal"].extend(lst_upRight)

            for index in indexes:
                count_summarised[index] = sigmoid(custom_exp(
                np.average((count_list[index])), 5, 64.67, 3.67))
                #count_summarised[index] = np.average((count_list[index]))
                stats[index]["std"] =  np.std(count_list[index])
                stats[index]["mean"] = np.mean(count_list[index])
                stats[index]["median"] = np.median(count_list[index])
                #print(index, " ",  np.average((count_list[index])))

            global args
            if args.output_stats == True:
                printDict(count_summarised)


def check_n_in_row(grid: list, status: int):
    """
    This function iterates through every grid cell to check how close the queried player is to winning.
    
    Grid: The grid of cells to query
    Status: The status code of the player\n
        - 1 = red
        - 2 = yellow
    """

    lst_horizontal = []
    lst_vertical = []
    lst_downRight = []
    lst_upRight = []

    positive_spaces = 0

    indexes = ["horizontal", "vertical",
               "down_right_diagonal", "up_right_diagonal"]

    for row_index in range(len(grid)):
        for i in range(len(grid[row_index])):   
            if grid[row_index][i].status == status:

                #Check num in row horizontally
                for _ in range(0, 3):
                    temp_horizontal = 0
                    if i + _ <= len(grid[row_index]) - 1:
                        if grid[row_index][i+_].status == status:
                            temp_horizontal += 1
                        if grid[row_index][i+_].status == status or grid[row_index][i+_].status == 0:
                            positive_spaces += 1
                        else:
                            break
                lst_horizontal.append(temp_horizontal)

                for _ in range(0, 3):
                    temp_vertical = 0
                    if row_index + _ <= len(grid)-1:
                        if grid[row_index + _][i].status == status:
                            temp_vertical += 1
                        if grid[row_index + _][i].status == status or grid[row_index + _][i].status == 0:
                            positive_spaces += 1
                        else:
                            break
                    else:
                        break
                lst_vertical.append(temp_vertical)

                for _ in range(0, 3):
                    temp_downRight = 0
                    if i + _ <= len(grid[row_index]) - 1 and row_index + _ <= len(grid)-1:
                        if grid[row_index + _][i + _].status == status:
                            temp_downRight += 1
                        else:
                            break
                    else:
                        break
                lst_downRight.append(temp_downRight)

                for _ in range(0, 3):
                    temp_upRight = 0
                    if i + _ <= len(grid[row_index])-1 and row_index - _ >= 0:
                        if grid[row_index - _][i + _].status == status:
                            temp_upRight += 1
                        else:
                            break
                    else:
                        break
                lst_upRight.append(temp_upRight)

    process_stats(lst_horizontal, lst_vertical,
                  lst_downRight, lst_upRight, indexes, status,positive_spaces)


def is_grid_full(grid):
    for row in grid:
        for n in row:
            if n.status == 0:
                return False
    return True

def check_for_win(grid: list, statuses: list[int]) -> int:
    """
    This function will iterate through all cells to check if a player has won
    (achieved 4 pieces in a row) and return:
    - The status code of the player that has won OR;
    - 0, if no player has won
    """
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
    if is_grid_full(grid):
        return -1
    return 0


def generate_slots(slots):
    """
    A simple setup function used simply to create and/or reset the board. 
    """

    for n in range(0, 6):
        for i in range(0, 7):
            circle = Circle(Point(i*((SCREEN_SIZE[0]-board_padding)/7)+slot_size+(
                board_padding*2), n*((BOARD_SIZE.height-board_padding)/7)+110+(slot_size)), slot_size, 0)
            slots[n].append(circle)
    return slots


board_padding = 7
slot_size = ((450*2)/(board_padding*7)+(board_padding/2))

DEF_SETTINGS = {
    "slots": [[], [], [], [], [], []],
    "pointer": Pointer(slot_size, Point(board_padding*2, 50), 1),
    "game_ended": False,
    "win_status": 0,

    "n_turns": {
        1: 0,
        2: 0
    },
    "turn_played": False

}


slots = generate_slots(DEF_SETTINGS["slots"])
pointer = DEF_SETTINGS["pointer"]
win_status = DEF_SETTINGS["win_status"]
game_ended = DEF_SETTINGS["game_ended"]
n_turns = DEF_SETTINGS["n_turns"]
turn_played = DEF_SETTINGS["turn_played"]

running = True
while running:
    """
    Main Loop
    """
    turn_played = False
    if args.visualise==True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if not game_ended:
                    if event.key == pygame.K_LEFT and pointer.selected != 0:
                        pointer.update_position(pointer.selected-1)
                    if event.key == pygame.K_RIGHT and pointer.selected != 6:
                        pointer.update_position(pointer.selected+1)
                    if event.key == pygame.K_RETURN:
                        turn_played = False
                        available_slot = check_slot_availability(
                            slots, pointer.selected)
                        if available_slot != -1:
                            n_turns[pointer.status] += 1
                            slots[available_slot[1]][available_slot[0]
                                                    ].update_status(pointer.status)
                            turn_played = True
                        elif available_slot == -1:
                            pass
                        if args.mode == "PvP":
                            pointer.status = 2 if pointer.status+1 == 2 else 1
                        elif args.mode == "PvR":
                            # red
                            turn_played = False
                            n_turns[2] += 1
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
                        
                        if args.count_states == True:
                            board_state_enc = [[X.status for X in row] for row in slots]
                            with open("data/possible_combinations","r") as combination_file_read:
                                unique_state_list = eval(combination_file_read.read())
                                if board_state_enc not in unique_state_list:
                                    num_combinations += 1
                                    unique_state_list.append(board_state_enc)
                                    with open("data/possible_combinations","w+") as combination_file_write:
                                        combination_file_write.write(str(unique_state_list))
                                else:
                                    duplicate_combinations += 1
                                    with open("data/num_duplicates","w+") as num_duplicates_file_write:
                                        num_duplicates_file_write.write(str(duplicate_combinations))
                            unique_state_list = []
                            print(f"Possible combinations: {num_combinations}, Duplicate combinations: {duplicate_combinations}")
                        if parser.track_win_progress == True:
                            check_n_in_row(slots, 1)
                            check_n_in_row(slots, 2)
                        turn_played = True
                if event.key == pygame.K_SPACE and game_ended:
                    slots = generate_slots([[], [], [], [], [], []])
                    pointer = DEF_SETTINGS["pointer"]
                    win_status = DEF_SETTINGS["win_status"]
                    game_ended = DEF_SETTINGS["game_ended"]
                    n_turns = DEF_SETTINGS["n_turns"]
                    turn_played = DEF_SETTINGS["turn_played"]
                if event.type == pygame.QUIT:
                    running = False

    if not game_ended and turn_played==False:
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
            if win_status > 0:
                scores[win_status-1] += 1
            turn_played = True
    if args.count_states == True and turn_played == True:
        board_state_enc = [[X.status for X in row] for row in slots]
        with open("data/possible_combinations","r") as combination_file_read:
            unique_state_list = eval(combination_file_read.read())
            if board_state_enc not in unique_state_list:
                num_combinations += 1
                unique_state_list.append(board_state_enc)
                with open("data/possible_combinations","w+") as combination_file_write:
                    combination_file_write.write(str(unique_state_list))
            else:
                duplicate_combinations += 1
                with open("data/num_duplicates","w+") as num_duplicates_file_write:
                    num_duplicates_file_write.write(str(duplicate_combinations))
        unique_state_list = []
        print(f"Possible combinations: {num_combinations}, Duplicate combinations: {duplicate_combinations}")
    if args.visualise == True:
        screen.fill((255, 255, 255, 255))

    if args.visualise == True:
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
            if args.visualise == True:
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

    if args.visualise == True:
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
    if args.visualise == True:
        pygame.display.flip()
if args.visualise == True:
    pygame.quit()