

class Vector(list):

    def __init__(self, x=0, y=0):
        if isinstance(x, (list, tuple)):
            list.__init__(self, x)
        else:
            list.__init__(self, [x, y])

    def __add__(self, other):
        if isinstance(other, list):
            return Vector(self.x + other.x, self.y + other.y)
        else:
            return Vector(self.x + other, self.y + other)

    def __sub__(self, other):
        if type(other) is Vector:
            return Vector(self.x - other.x, self.y - other.y)
        else:
            return Vector(self.x - other, self.y - other)

    def __mul__(self, other): return Vector(self.x * other, self.y * other)
    def __truediv__(self, other): return Vector(self.x / other, self.y / other)
    def __neg__(self): return Vector(-self.x, -self.y)
    def __bool__(self): return self.x != 0 or self.y != 0

    @property
    def x(self): return self[0]

    @property
    def y(self): return self[1]

    @x.setter
    def x(self, value): self[0] = value

    @y.setter
    def y(self, value): self[1] = value


class Matrix:

    def __init__(self, width, height):
        self._data = [[0 for _ in range(width)] for _ in range(height)]
        self._width, self._height = width, height
        self._index = [0, 0]  # x, y

    def __getitem__(self, at):
        x, y = at
        return self._data[y][x]

    def __setitem__(self, at, value):
        x, y = at
        self._data[y][x] = value

    def __iter__(self):
        self._index = [-1, 0]  # x, y
        return self

    def __next__(self):
        self._index[0] += 1

        if self._index[0] >= self._width:
            self._index[0] = 0
            self._index[1] += 1

            if self._index[1] >= self._height:
                raise StopIteration
        return self[self._index], self._index[:]


class Rectangle:

    def __init__(self, x, y, width, height):
        self.pos = Vector(x, y)
        self.width = width
        self.height = height

    def move(self, vector):
        self.pos = self.pos + Vector(vector)

    def repos(self, vector):
        self.pos = Vector(vector)

    def resize(self, width, height):
        self.width = width
        self.height = height

    def focused(self, vector):
        return self.left < vector.x < self.right and self.top < vector.y < self.bottom

    def collide(self, rectangle):
        x = self.left < rectangle.right and self.right > rectangle.left
        y = self.top < rectangle.bottom and self.bottom > rectangle.top
        return x and y

    @property
    def rect(self):
        return self.left, self.top, self.right, self.bottom

    @property
    def left(self):
        return self.pos.x

    @left.setter
    def left(self, value):
        self.pos.x = value

    @property
    def right(self):
        return self.pos.x + self.width

    @right.setter
    def right(self, value):
        self.pos.x = value - self.width

    @property
    def top(self):
        return self.pos.y

    @top.setter
    def top(self, value):
        self.pos.y = value

    @property
    def bottom(self):
        return self.pos.y + self.height

    @bottom.setter
    def bottom(self, value):
        self.pos.y = value - self.height

    @property
    def center(self):
        return self.pos + Vector(self.width/2, self.height/2)

    @center.setter
    def center(self, value):
        self.pos = Vector(*value) - Vector(self.width/2, self.height/2)

    @property
    def midleft(self):
        return self.pos + Vector(0, self.height/2)

    @midleft.setter
    def midleft(self, value):
        self.pos = Vector(*value) - Vector(0, self.height/2)

    @property
    def midright(self):
        return self.pos + Vector(self.width, self.height/2)

    @midright.setter
    def midright(self, value):
        self.pos = Vector(*value) - Vector(self.width, self.height/2)


class Direction:
    UP = Vector(0, -1)
    DOWN = Vector(0, 1)
    LEFT = Vector(-1, 0)
    RIGHT = Vector(1, 0)
