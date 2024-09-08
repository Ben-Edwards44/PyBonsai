#!/usr/bin/env python3


#   
#                #&                                  
#              %&@&                                  
#       &%@% %&  %@|                                 
#    &&@@&%#@%_\@@&&@#       @=&                     
#   &#@# #%##  ;&@%#  %@    @% &%                    
#     @  %  #&  %%~|       @%@%@&#                   
#                  |;;         # %                   
#                     \\        @ % %@%#             
#                      |~     =;@ __%%               
#                      =|   ~_=___  %&#              
#                      || /~         % #             
#                      |//           &               
#                      |=                            
#                      ~|                            
#                      ;|                            
#       .---.        ./||\.    .-.     
#   
#       I speak for the trees, for the trees have no voice.
#       - The Lorax, 1971
#   


import draw
import tree

import random
from sys import argv
from math import radians
from os import get_terminal_size


VERSION = "1.2.2"
DESC = "PyBonsai procedurally generates ASCII art trees in your terminal."


class Options:
    #stores all parameters that can be edited via the command line arguments
    
    #default values
    NUM_LAYERS = 8
    INITIAL_LEN = 15
    ANGLE_MEAN = 40

    LEAF_LEN = 4

    INSTANT = False
    WAIT_TIME = 0

    BRANCH_CHARS = "~;:="
    LEAF_CHARS = "&%#@"

    WINDOW_WIDTH = 80
    WINDOW_HEIGHT = 25

    FIXED = False

    OPTION_DESCS = f"""
OPTIONS:
    -h, --help            display help
        --version         display version

    -s, --seed            seed for the random number generator

    -i, --instant         instant mode: display finished tree immediately
    -w, --wait            time delay between drawing characters when not in instant mode [default {WAIT_TIME}]

    -c, --branch-chars    string of chars randomly chosen for branches [default "{BRANCH_CHARS}"]
    -C, --leaf-chars      string of chars randomly chosen for leaves [default "{LEAF_CHARS}"]

    -x, --width           maximum width of the tree [default {WINDOW_WIDTH}]
    -y, --height          maximum height of the tree [default {WINDOW_HEIGHT}]

    -t, --type            tree type: integer between 0 and 3 inclusive [default random]
    -S, --start-len       length of the root branch [default {INITIAL_LEN}]
    -L, --leaf-len        length of each leaf [default {LEAF_LEN}]
    -l, --layers          number of branch layers: more => more branches [default {NUM_LAYERS}]
    -a, --angle           mean angle of branches to their parent, in degrees; more => more arched trees [default {ANGLE_MEAN}]

    -f, --fixed-window    do not allow window height to increase when tree grows off screen
    """

    SHORT_OPTIONS = {
        "-h" : "--help",
        "-i" : "--instant",
        "-c" : "--branch-chars",
        "-C" : "--leaf-chars",
        "-w" : "--wait",
        "-x" : "--width",
        "-y" : "--height",
        "-t" : "--type",
        "-s" : "--seed",
        "-S" : "--start-len",
        "-L" : "--leaf-len",
        "-l" : "--layers",
        "-a" : "--angle",
        "-f" : "--fixed-window"
    }
    
    def __init__(self):
        #set the default values
        self.num_layers = Options.NUM_LAYERS
        self.initial_len = Options.INITIAL_LEN
        self.angle_mean = radians(Options.ANGLE_MEAN)

        self.leaf_len = Options.LEAF_LEN

        self.instant = Options.INSTANT
        self.wait_time = Options.WAIT_TIME

        self.branch_chars = Options.BRANCH_CHARS
        self.leaf_chars = Options.LEAF_CHARS

        self.user_set_type = False
        self.type = random.randint(0, 3)

        self.fixed_window = Options.FIXED

        self.window_width, self.window_height = self.get_default_window()

    def get_default_window(self):
        #ensure the default values fit the current terminal size
        width, height = get_terminal_size()

        #check the default values fit the current terminal
        width = min(width, Options.WINDOW_WIDTH)
        height = min(height, Options.WINDOW_HEIGHT)

        return width, height
    
    def set_option(self, option_name, value):
        if option_name[1] != "-":
            #this is a shorthand option name
            if option_name not in Options.SHORT_OPTIONS:
                self.show_invalid(option_name)

            option_name = Options.SHORT_OPTIONS[option_name]

        match option_name:
            case "--layers":
                self.num_layers = int(value)
            case "--start-len":
                self.initial_len = int(value)
            case "--angle":
                self.angle_mean = radians(int(value))
            case "--leaf-len":
                self.leaf_len = int(value)
            case "--instant":
                self.instant = value
            case "--wait":
                self.wait_time = float(value)
            case "--branch-chars":
                self.branch_chars = parse_string(value)
            case "--leaf-chars":
                self.leaf_chars = parse_string(value)
            case "--type":
                self.type = int(value)
                self.user_set_type = True
            case "--width":
                self.window_width = int(value)
            case "--height":
                self.window_height = int(value)
            case "--help":
                self.show_help()
            case "--version":
                self.show_version()
            case "--seed":
                self.set_seed(int(value))
            case "--fixed-window":
                self.fixed_window = True
            case _:
                self.show_invalid(option_name)

    def show_help(self):
        print("USEAGE pybonsai [OPTION]...\n")
        print(DESC)
        print(Options.OPTION_DESCS)

        quit()

    def show_version(self):
        print(f"PyBonsai version {VERSION}")

        quit()

    def show_invalid(self, option_name):
        raise Exception(f"Invalid option: {option_name}. Use pybonsai --help for useage.")
    
    def set_seed(self, seed):
        random.seed(seed)

        #the type must be re-chosen because the rng seed has been changed (this ensures repeatable results)
        if not self.user_set_type:
            self.type = random.randint(0, 3)


def parse_args():
    #convert sys.argv into a dictionary in the form {option_name : option_value}
    args = argv[1:]  #remove the script name

    arg_values = {}
    for i, x in enumerate(args):
        if x[0] == "-":
            value = get_arg_value(args, i)

            is_short = x[1] != "-"

            if is_short and len(x) > 2:
                #multiple flags have been set at once (e.g. pybonsai -fi)
                for y in x[1:]:
                    arg_values[f"-{y}"] = value
            else:
                arg_values[x] = value

    return arg_values


def get_arg_value(args, inx):
    value_inx = inx + 1

    if value_inx >= len(args):
        return True
    
    value = args[value_inx]
    if value[0] == "-":
        #this is just another argument, not the value itself. Therefore, the argument must have been a flag
        return True
    else:
        return value
    

def parse_string(string):
    #remove outside quotation marks (if there are any)
    if len(string) < 2:
        return string

    if string[0] == string[-1] == "'":
        return string[1:-1]
    elif string[0] == string[-1] == '"':
        return string[1:-1]
    else:
        return string
    

def get_options(args):
    options = Options()

    for option_name, value in args.items():
        options.set_option(option_name, value)

    return options


def get_tree(window, options):
    root_x = window.width // 2

    root_y = tree.Tree.BOX_HEIGHT + 4
    root_y = root_y + root_y % 2  #round to nearest even number (odd numbers cause off-by-one errors as chars are twice as tall as they are wide)

    root_pos = (root_x, root_y)

    if options.type == 0:
        t = tree.ClassicTree(window, root_pos, options)
    elif options.type == 1:
        t = tree.FibonacciTree(window, root_pos, options)
    elif options.type == 2:
        t = tree.OffsetFibTree(window, root_pos, options)
    else:
        t = tree.RandomOffsetFibTree(window, root_pos, options)

    return t


def main():
    args = parse_args()
    options = get_options(args)
    window = draw.TerminalWindow(options.window_width, options.window_height, options)

    t = get_tree(window, options)

    t.draw()
    window.draw()
    window.reset_cursor()


if __name__ == "__main__":
    main()