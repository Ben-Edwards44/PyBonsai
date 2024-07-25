import math
import utils
import random
from time import sleep


#ANSI escape codes (https://en.wikipedia.org/wiki/ANSI_escape_code)
END_COLOUR = "\033[00m"
HIDE_CURSOR = "\033[?25l"  #not supported in all terminals
SHOW_CURSOR = "\033[?25h"  #not supported in all terminals

CHAR_THRESHOLD = 0.3


class TerminalWindow:
    CHAR_WIDTH = 1
    CHAR_HEIGHT = 2

    BACKGROUND_CHAR = " "

    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.needs_clear = False

        self.chars = [[TerminalWindow.BACKGROUND_CHAR for _ in range(width)] for _ in range(height)]

    colour_char = lambda self, char, r, g, b: f"\033[38;2;{r};{g};{b}m{char}{END_COLOUR}"  #ANSI escape code for 24 bit true colour (which most modern terminals support)
    to_int = lambda self, point: [int(i) for i in point]

    def clear_chars(self):
        self.chars = [[TerminalWindow.BACKGROUND_CHAR for _ in range(self.width)] for _ in range(self.height)]

    def draw(self):
        print(HIDE_CURSOR, end="")

        if self.needs_clear:
            print(f"\033[{self.height}A", end="")  #move cursor to the top

        for i in self.chars:
            print("".join(i))

        print(SHOW_CURSOR, end="")

        self.needs_clear = True

    def plane_to_screen(self, x, y):
        #convert cartesian coords to array indices
        scaled_x = x / TerminalWindow.CHAR_WIDTH
        scaled_y = y / TerminalWindow.CHAR_HEIGHT

        inx1 = round(self.height - scaled_y)
        inx2 = round(scaled_x)

        return inx1, inx2
    
    def screen_to_plane(self, x, y):
        #convert array indices to cartesian coords (inverse of plane_to_screen())
        swapped_x = y
        swapped_y = self.height - x

        scaled_x = swapped_x * TerminalWindow.CHAR_WIDTH
        scaled_y = swapped_y * TerminalWindow.CHAR_HEIGHT

        return scaled_x, scaled_y

    def set_char_instant(self, x, y, char, colour, is_screen_coords):
        if not is_screen_coords:
            x, y = self.plane_to_screen(x, y)

        if not 0 < x < self.height or not 0 < y < self.width:
            return

        coloured = self.colour_char(char, colour[0], colour[1], colour[2])
        self.chars[x][y] = coloured

    def set_char_wait(self, x, y, char, colour, is_screen_coords, wait_time):
        #in non instant mode, we want to draw each new character after it is set
        self.set_char_instant(x, y, char, colour, is_screen_coords)

        self.draw()
        sleep(wait_time)

    def get_line_char(self, line):
        theta = line.get_theta()

        upper = math.pi / 2 * (2 / 3)
        lower = math.pi / 2 * (1 / 3)

        if abs(theta) > upper:
            return "|"
        elif abs(theta) < lower:
            return "_"
        elif theta > 0:
            return "/"
        else:
            return "\\"
        
    def choose_colour(self, colour):
        if type(colour[0]) == int:
            #the colour is not a range, so no choice must be made
            return colour
        elif len(colour[0]) == 2:
            #colour should be random with rgb values in the given range
            rand_colour = []
            for lower, upper in colour:
                value = random.randint(lower, upper)
                rand_colour.append(value)

            return rand_colour
        else:
            raise Exception("Invalid colour argument")
        
    def draw_steep_line(self, start, end, colour, width, params, char, mid_line):
        start_inx, _ = self.plane_to_screen(*start)
        end_inx, _ = self.plane_to_screen(*end)

        step = 1 if end_inx > start_inx else -1

        for inx1 in range(start_inx, end_inx + step, step):
            dists = []
            #get the distance away from the mid line for each cell
            for inx2 in range(self.width):
                x, y = self.screen_to_plane(inx1, inx2)

                desired_x = mid_line.get_x(y)
                dist = abs(desired_x - x)

                dists.append([dist, inx2])
                
            #draw the n closest cells (n = width)
            dists.sort()
            for i in range(width):
                if i >= len(dists):
                    break

                if random.uniform(0, 1) < CHAR_THRESHOLD:
                    chosen_char = random.choice(params.branch_chars)
                else:
                    chosen_char = char

                chosen_colour = self.choose_colour(colour)

                if params.instant:
                    self.set_char_instant(inx1, dists[i][1], chosen_char, chosen_colour, True)
                else:
                    self.set_char_wait(inx1, dists[i][1], chosen_char, chosen_colour, True, params.wait_time)

    def draw_shallow_line(self, start, end, colour, width, params, char, mid_line):
        _, start_inx = self.plane_to_screen(*start)
        _, end_inx = self.plane_to_screen(*end)

        step = 1 if end_inx > start_inx else -1

        for inx2 in range(start_inx, end_inx + step, step):
            dists = []
            #get the distance away from the mid line for each cell
            for inx1 in range(self.height):
                x, y = self.screen_to_plane(inx1, inx2)

                desired_y = mid_line.get_y(x)
                dist = abs(desired_y - y)

                dists.append([dist, inx1])
                
            #draw the n closest cells (n = width)
            dists.sort()
            for i in range(width):
                if i >= len(dists):
                    break

                if random.uniform(0, 1) < CHAR_THRESHOLD:
                    chosen_char = random.choice(params.branch_chars)
                else:
                    chosen_char = char

                chosen_colour = self.choose_colour(colour)

                if params.instant:
                    self.set_char_instant(dists[i][1], inx2, chosen_char, chosen_colour, True)
                else:
                    self.set_char_wait(dists[i][1], inx2, chosen_char, chosen_colour, True, params.wait_time)
    
    def draw_line(self, start, end, colour, width, params):
        mid_line = utils.Line()
        mid_line.set_end_points(start, end)

        char = self.get_line_char(mid_line)

        if mid_line.is_vertical or abs(mid_line.m) >= 1:
            self.draw_steep_line(start, end, colour, width, params, char, mid_line)
        else:
            self.draw_shallow_line(start, end, colour, width, params, char, mid_line)