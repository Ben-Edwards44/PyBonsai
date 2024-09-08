import math
import utils
import random


class Tree:
    #base tree class - not a drawable tree
    BOX_HEIGHT = 3
    MAX_TOP_WIDTH = 35

    MOUND_THRESHOLD = 0.1
    SOIL_CHAR_THRESHOLD = 0.1

    SOIL_CHARS = ".~*"

    MOUND_WIDTH_MEAN = 2
    MOUND_WIDTH_STD_DEV = 1

    SOIL_COLOUR = (0, 150, 0)
    BOX_COLOUR = (200, 200, 200)

    BRANCH_COLOUR = ((200, 255), (150, 255), (0, 0))  #range of rgb values

    def __init__(self, window, root_pos, options):
        self.window = window
        self.root_x, self.root_y = root_pos
        self.options = options

        self.box_top_width = self.get_box_width()

    def get_box_width(self):
        width = min(self.window.width // 3, Tree.MAX_TOP_WIDTH)

        if width % 2 == 0:
            width += 1  #width should be odd to allow tree to go in middle

        return width

    def draw_box(self):
        root_inx1, root_inx2 = self.window.plane_to_screen(self.root_x, self.root_y)

        for i in range(Tree.BOX_HEIGHT):
            inx1 = root_inx1 + i
            width = self.box_top_width - i * 2

            for x in range(width):
                inx2 = root_inx2 - width // 2 + x

                if x == 0:
                    char = "\\"
                    colour = Tree.BOX_COLOUR
                elif x == width - 1:
                    char = "/"
                    colour = Tree.BOX_COLOUR
                elif i == 0:
                    char = "_"
                    colour = Tree.SOIL_COLOUR
                elif i == Tree.BOX_HEIGHT - 1:
                    char = "_"
                    colour = Tree.BOX_COLOUR
                else:
                    if random.uniform(0, 1) < Tree.SOIL_CHAR_THRESHOLD:
                        char = random.choice(Tree.SOIL_CHARS)
                    else:
                        char = " "

                    colour = Tree.SOIL_COLOUR

                self.window.set_char_instant(inx1, inx2, char, colour, True)

        self.draw_box_feet(root_inx1, root_inx2)
        self.draw_all_mounds(root_inx1, root_inx2)  #must be called after the top layer has been drawn normally

    def draw_box_feet(self, root_inx1, root_inx2):
        #draw feet for the box        
        inx1 = root_inx1 + Tree.BOX_HEIGHT
        offset = self.box_top_width // 2 - Tree.BOX_HEIGHT - 1

        for sign in range(-1, 2, 2):
            inx2 = root_inx2 + sign * offset
            self.window.set_char_instant(inx1, inx2, "‾", Tree.BOX_COLOUR, True)

    def draw_all_mounds(self, root_inx1, root_inx2):
        #draw .---._____.--. on top layer      
        num_drawn = 0
        for i in range(1, self.box_top_width):
            inx2 = root_inx2 - self.box_top_width // 2 + i

            if random.uniform(0, 1) < Tree.MOUND_THRESHOLD / (num_drawn + 1):
                num_drawn += 1
                max_width = self.box_top_width - i - 1

                self.draw_mound(root_inx1, inx2, max_width)

    def draw_mound(self, inx1, start_inx2, max_width):
        top_width = round(random.normalvariate(Tree.MOUND_WIDTH_MEAN, Tree.MOUND_WIDTH_STD_DEV))
        top_width = min(top_width, max_width - 2)

        if top_width <= 0:
            return

        for i in range(top_width + 2):
            inx2 = start_inx2 + i

            if i == 0 or i == top_width + 1:
                char = "."
            else:
                char = "-"

            self.window.set_char_instant(inx1, inx2, char, Tree.SOIL_COLOUR, True)

    def draw_tree_base(self, trunk_width):
        #just add some extra padding at the bottom of the trunk to look nice. Must be called after tree is grown
        inx1, inx2 = self.window.plane_to_screen(self.root_x, self.root_y)

        left_x = inx2 - trunk_width // 2
        right_x = inx2 + trunk_width // 2

        #off-by-one error: line drawing moves left to right, causing trunk to be to the left of the center, so move the base right to compensate
        if trunk_width % 2 == 0:
            right_x -= 1

        self.window.set_char_instant(inx1, left_x - 2, ".", (255, 255, 0), True)
        self.window.set_char_instant(inx1, left_x - 1, "/", (255, 255, 0), True)
        self.window.set_char_instant(inx1, right_x + 1, "\\", (255, 255, 0), True)
        self.window.set_char_instant(inx1, right_x + 2, ".", (255, 255, 0), True)


class RecursiveTree(Tree):
    #all recursive tree types are based off of the fractal canopy: https://en.wikipedia.org/wiki/Fractal_canopy
    ANGLE_STD_DEV = math.radians(8)

    LEN_SCALE = 0.75

    MAX_INITIAL_WIDTH = 6

    def __init__(self, window, root_pos, options):
        super().__init__(window, root_pos, options)

    def get_end_coords(self, start_x, start_y, length, theta):
        x = start_x + length * math.sin(theta)
        y = start_y + length * math.cos(theta)

        return x, y
    
    def get_initial_params(self):
        initial_width = self.options.initial_len // 5
        initial_angle = random.normalvariate(0, RecursiveTree.ANGLE_STD_DEV)

        #ensure the width is in a suitable range
        initial_width = max(0, initial_width)
        initial_width = min(RecursiveTree.MAX_INITIAL_WIDTH, initial_width)

        return initial_width, initial_angle


class ClassicTree(RecursiveTree):
    #trees with a random number of branches on each layer
    MEAN_BRANCHES = 2
    BRANCHES_STD_DEV = 0.5

    def __init__(self, window, root_pos, options):
        super().__init__(window, root_pos, options)

    def draw_branch(self, x, y, layer, length, width, theta):
        if layer >= self.options.num_layers:
            leaves = Leaves(self.window, (x, y), self.options)
            leaves.draw()

            return
        
        end_x, end_y = self.get_end_coords(x, y, length, theta)

        self.window.draw_line((x, y), (end_x, end_y), ClassicTree.BRANCH_COLOUR, round(width))

        self.draw_end_branches(x, y, layer, length, width, theta)

    def draw_end_branches(self, start_x, start_y, layer, length, width, theta):
        sign = 1
        num_branches = max(0, round(random.normalvariate(ClassicTree.MEAN_BRANCHES, ClassicTree.BRANCHES_STD_DEV)))

        step = length / num_branches if num_branches != 0 else 0

        new_width = max(1, width - 1)
        new_length = length * ClassicTree.LEN_SCALE

        for i in range(num_branches):
            dist_up_branch = (i + 1) * step  #branches are linearly distributed along the parent
            new_theta = theta + sign * random.normalvariate(self.options.angle_mean, ClassicTree.ANGLE_STD_DEV)

            x, y = self.get_end_coords(start_x, start_y, dist_up_branch, theta)  #start point of new branch

            self.draw_branch(x, y, layer + 1, new_length, new_width, new_theta)

            sign *= -1  #ensure next branch is on opposite side of the parent

    def draw(self):
        initial_width, initial_angle = self.get_initial_params()

        self.draw_box()
        self.draw_tree_base(initial_width)

        self.draw_branch(self.root_x, self.root_y, 1, self.options.initial_len, initial_width, initial_angle)


class FibonacciTree(RecursiveTree):
    #trees with a fibonacci number of branches on each layer
    def __init__(self, window, root_pos, options):
        super().__init__(window, root_pos, options)

        self.fib = self.fib_nums()
        self.branch_nums = self.generate_branch_nums()

    def fib_nums(self):
        fib = [1, 1]

        for _ in range(self.options.num_layers):
            fib.append(fib[-1] + fib[-2])

        return fib
    
    def generate_branch_nums(self):
        #generate the number of child branches branching off of each parent
        branch_nums = [[1]]  #1st index is the layer from the root, 2nd index is the position of the parent branch in its layer
        for i in range(self.options.num_layers):
            num_branches = self.fib[i + 2]
            num_parents = sum(branch_nums[-1])

            base = num_branches // num_parents
            diff = num_branches - base * num_parents

            current_nums = [base + 1 if x < diff else base for x in range(num_parents)]

            random.shuffle(current_nums)

            branch_nums.append(current_nums)

        return branch_nums
    
    def draw_branch(self, x, y, layer_inx, branch_inx, length, width, theta):
        if layer_inx > self.options.num_layers:
            leaf = Leaves(self.window, (x, y), self.options)
            leaf.draw()

            return
        
        end_x, end_y = self.get_end_coords(x, y, length, theta)

        self.window.draw_line((x, y), (end_x, end_y), FibonacciTree.BRANCH_COLOUR, round(width))

        self.draw_end_branches(x, y, layer_inx, branch_inx, length, width, theta)

    def draw_end_branches(self, start_x, start_y, layer_inx, branch_inx, length, width, theta):
        #draw the child branches off of the end of the parent branch
        sign = 1
        num_branches = self.branch_nums[layer_inx][branch_inx]
        new_width = max(1, width - 1)

        x, y = self.get_end_coords(start_x, start_y, length, theta)

        for i in range(num_branches):
            angle = random.normalvariate(self.options.angle_mean, FibonacciTree.ANGLE_STD_DEV)
            new_theta = theta + sign * angle

            new_len = length * FibonacciTree.LEN_SCALE

            self.draw_branch(x, y, layer_inx + 1, branch_inx + i, new_len, new_width, new_theta)
 
            sign *= -1

    def draw(self):
        initial_width, initial_angle = self.get_initial_params()

        self.draw_box()
        self.draw_tree_base(initial_width)

        self.draw_branch(self.root_x, self.root_y, 1, 0, self.options.initial_len, initial_width, initial_angle)


class OffsetFibTree(FibonacciTree):
    #similar to fibonacci tree, but branches grow from the middle of the parent branch
    def __init__(self, window, root_pos, options):
        super().__init__(window, root_pos, options)

    def draw_end_branches(self, start_x, start_y, layer_inx, branch_inx, length, width, theta):
        sign = 1
        num_branches = self.branch_nums[layer_inx][branch_inx]

        step = length / num_branches if num_branches != 0 else 0

        new_width = max(1, width - 1)
        new_length = length * ClassicTree.LEN_SCALE

        for i in range(num_branches):
            dist_up_branch = (i + 1) * step  #branches are now linearly distributed along the parent branch
            new_theta = theta + sign * random.normalvariate(self.options.angle_mean, OffsetFibTree.ANGLE_STD_DEV)

            x, y = self.get_end_coords(start_x, start_y, dist_up_branch, theta)

            self.draw_branch(x, y, layer_inx + 1, branch_inx + i, new_length, new_width, new_theta)

            sign *= -1


class RandomOffsetFibTree(FibonacciTree):
    #an offset fib tree, but the branches are randomly placed along parent branch and leaves can grow on non end branches
    GROW_END_THRESHOLD = 0.5

    NON_END_MIN = 0.3
    NON_END_MAX = 0.9

    def __init__(self, window, root_pos, options):
        super().__init__(window, root_pos, options)

    def draw_end_branches(self, start_x, start_y, layer_inx, branch_inx, length, width, theta):
        sign = 1
        num_branches = self.branch_nums[layer_inx][branch_inx]

        new_width = max(1, width - 1)
        new_length = length * ClassicTree.LEN_SCALE

        need_leaves = True
        for i in range(num_branches):
            grow_at_end = random.uniform(0, 1) < RandomOffsetFibTree.GROW_END_THRESHOLD

            if grow_at_end:
                #this branch will grow at the end of the parent, so do not draw leaves at the end of the parent
                need_leaves = False
                dist_up_branch = length
            else:
                #this branch will grow at a random distance along the parent (not the end), so we may need leaves at the end of the parent
                dist_up_branch = random.uniform(length * RandomOffsetFibTree.NON_END_MIN, length * RandomOffsetFibTree.NON_END_MAX)

            new_theta = theta + sign * random.normalvariate(self.options.angle_mean, OffsetFibTree.ANGLE_STD_DEV)

            x, y = self.get_end_coords(start_x, start_y, dist_up_branch, theta)

            self.draw_branch(x, y, layer_inx + 1, branch_inx + i, new_length, new_width, new_theta)

            sign *= -1

        if need_leaves:
            #no branches have grown at the end of the parent, so we can grow leaves
            end_pos = self.get_end_coords(start_x, start_y, length, theta)

            leaves = Leaves(self.window, end_pos, self.options)
            leaves.draw()


class Leaves:
    NUM_LEAVES = 4

    def __init__(self, window, branch_end, options):
        self.window = window
        self.branch_x, self.branch_y = branch_end
        self.options = options

    def draw(self):
        g = utils.Vector(0, -1)

        for _ in range(Leaves.NUM_LEAVES):
            vel = utils.Vector(random.uniform(-1, 1), random.uniform(-1, 1))  #random starting velocity for the leaves to step along
            vel.normalise()
            pos = utils.Vector(self.branch_x, self.branch_y)

            for i in range(self.options.leaf_len):
                pos += vel

                colour = (0, random.randint(75, 255), 0)
                char = random.choice(self.options.leaf_chars)

                if self.options.instant:
                    self.window.set_char_instant(pos.x, pos.y, char, colour, False)
                else:
                    self.window.set_char_wait(pos.x, pos.y, char, colour, False, self.options.wait_time)

                #make the leaves droop downwards by adding some gravity force
                weight = i / self.options.leaf_len
                vel += g * weight