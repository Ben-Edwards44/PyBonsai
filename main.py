#!/usr/bin/env python3


import draw
import tree

import random
from sys import argv
from os import get_terminal_size


NAME = "pybonsai"
VERSION = "1.0.0"


DEFAULT_WIDTH = 80
DEFAULT_HEIGHT = 35


VALID_ARGS = {
    ("-h", "--help") : "show help",
    ("-s", "--seed") : "seed for the random number generator",
    ("-t", "--type") : "tree type: 0 - classic tree, 1 - fibonacci tree, 2 - offset fibonacci tree, 3 - random fibonacci tree [default random]",
    ("-y", "--height") : f"maximum height of the tree [default {DEFAULT_HEIGHT}]",
    ("-x", "--width") : f"maximum width of the tree [default {DEFAULT_WIDTH}]",
    ("-l", "--layers") : f"number of branch layers: more => more branches [default {tree.Params.NUM_LAYERS}]",
    ("-S", "--start-len") : f"length of the root branch [default {tree.Params.INITIAL_LEN}]",
    ("-i", "--instant") : "instant mode: only display finished tree",
    ("-w", "--wait") : f"time delay between drawing characters [default {tree.Params.WAIT_TIME}]",
    ("-L", "--leaf-len") : f"length of each leaf [default {tree.Params.LEAF_LEN}]",
    ("-a", "--angle") : f"mean angle of branches to their parent, in degrees; more => more arched trees [default {tree.Params.ANGLE_MEAN}]",
    ("-c", "--branch-chars") : f"string of chars randomly chosen for branches [default {tree.Params.BRANCH_CHARS}]",
    ("-C", "--leaf-chars") : f"string of chars randomly chosen for leaves [default {tree.Params.LEAF_CHARS}]",
    ("  ", "--version") : "display version"
}


def parse_args():
    args = argv[1:]  #remove the script name

    arg_values = {}
    for i, x in enumerate(args):
        if x[0] == "-":
            value = get_arg_value(args, i)
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
    #potentially remove outside quotation marks

    if len(string) < 2:
        return string

    if string[0] == string[-1] == "'":
        return string[1:-1]
    elif string[0] == string[-1] == '"':
        return string[1:-1]
    else:
        return string


def show_help():
    print(f"USEAGE: {NAME} [OPTION]")

    max_len = 0
    for option_name in VALID_ARGS:
        total_len = sum([len(i) for i in option_name])

        if total_len > max_len:
            max_len = total_len

    print("OPTIONS:")
    for name, desc in VALID_ARGS.items():
        option_names = ", ".join(name)
        total_len = sum([len(i) for i in name])

        num_space = max_len - total_len + 3

        print(f"{option_names}{" " * num_space}{desc}")


def show_version():
    print(f"{NAME} version {VERSION}")


def check_arg_set(args, option_names, default_value):
    for i in option_names:
        if i in args:
            return args[i]
        
    return default_value


def get_window_size(args):
    term_w, term_h = get_terminal_size()

    #check the default values fit the current terminal
    width_default = min(term_w, DEFAULT_WIDTH)
    height_default = min(term_h, DEFAULT_HEIGHT)

    width = int(check_arg_set(args, ("-x", "--width"), width_default))
    height = int(check_arg_set(args, ("-y", "--height"), height_default))

    return width, height


def get_tree_type(args):
    type = int(check_arg_set(args, ("-t", "--type"), random.randint(0, 3)))

    if not 0 <= type <= 3:
        raise Exception("Invalid type - choose integer between 0 and 3 (inclusive)")
    
    return type


get_num_layers = lambda args: int(check_arg_set(args, ("-l", "--layers"), tree.Params.NUM_LAYERS))
get_initial_len = lambda args: int(check_arg_set(args, ("-S", "--start-len"), tree.Params.INITIAL_LEN))
get_instant_mode = lambda args: check_arg_set(args, ("-i", "--instant"), False)
get_wait_time = lambda args: float(check_arg_set(args, ("-w", "--wait"), tree.Params.WAIT_TIME))
get_leaf_len = lambda args: int(check_arg_set(args, ("-L", "--leaf-len"), tree.Params.LEAF_LEN))
get_angle_mean = lambda args: float(check_arg_set(args, ("-a", "--angle"), tree.Params.ANGLE_MEAN))
get_branch_chars = lambda args: parse_string(check_arg_set(args, ("-c", "--branch-chars"), tree.Params.BRANCH_CHARS))
get_leaf_chars = lambda args: parse_string(check_arg_set(args, ("-C", "--leaf-chars"), tree.Params.LEAF_CHARS))


def set_seed(args):
    #if user specifies a seed, set it
    if "--seed" in args:
        random.seed(int(args["--seed"]))
    elif "-s" in args:
        random.seed(int(args["-s"]))


def get_params(args):
    #get all the parameters set by user
    initial_len = get_initial_len(args)
    num_layers = get_num_layers(args)
    angle_mean = get_angle_mean(args)

    leaf_len = get_leaf_len(args)

    instant = get_instant_mode(args)
    wait_time = get_wait_time(args)

    branch_chars = get_branch_chars(args)
    leaf_chars = get_leaf_chars(args)

    return tree.Params(initial_len, num_layers, angle_mean, leaf_len, instant, wait_time, branch_chars, leaf_chars)


def get_tree(window, args):
    type = get_tree_type(args)
    params = get_params(args)

    root_x = window.width // 2

    if type == 0:
        t = tree.ClassicTree(window, (root_x, tree.ClassicTree.BOX_HEIGHT + 6), params)
    elif type == 1:
        t = tree.FibonacciTree(window, (root_x, tree.FibonacciTree.BOX_HEIGHT + 6), params)
    elif type == 2:
        t = tree.OffsetFibTree(window, (root_x, tree.OffsetFibTree.BOX_HEIGHT + 6), params)
    else:
        t = tree.RandomOffsetFibTree(window, (root_x, tree.RandomOffsetFibTree.BOX_HEIGHT + 6), params)

    return t


def main():
    args = parse_args()

    if "-h" in args or "--help" in args:
        show_help()
        return
    elif "--version" in args:
        show_version()
        return

    set_seed(args)
    width, height = get_window_size(args)

    window = draw.TerminalWindow(width, height - 2)

    t = get_tree(window, args)

    t.draw()
    window.draw()


if __name__ == "__main__":
    main()