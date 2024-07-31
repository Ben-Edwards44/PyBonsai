import math


class Line:
    #line in form y = mx + c
    def __init__(self):
        self.start = None
        self.end = None

        self.m = None
        self.c = None

        self.is_vertical = False

    def get_y(self, x):
        if not self.is_vertical:
            return self.m * x + self.c
        
    def get_x(self, y):
        if self.is_vertical:
            return self.c
        elif self.m != 0:
            return (y - self.c) / self.m

    def set_end_points(self, start, end):
        self.start = start
        self.end = end

        if self.start[0] == self.end[0]:
            self.is_vertical = True
            self.m = None
            self.c = self.start[0]
        else:
            self.m = (self.start[1] - self.end[1]) / (self.start[0] - self.end[0])
            self.c = self.start[1] - self.m * self.start[0]

    def set_gradient(self, m, point):
        self.m = m
        self.c = point[1] - m * point[0]
    
    def get_theta(self):
        #get angle above x axis
        if self.is_vertical:
            return math.pi / 2
        else:
            return math.atan(self.m)


class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    mag = lambda self: (self.x**2 + self.y**2)**0.5

    def __iadd__(self, other_vec):
        return Vector(self.x + other_vec.x, self.y + other_vec.y)
    
    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)
    
    def normalise(self):
        m = self.mag()

        self.x /= m
        self.y /= m