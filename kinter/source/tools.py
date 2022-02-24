

class Vector:

    def __init__(self, x, y):
        self.data = [x, y]

    def __add__(self, other):
        if type(other) is Vector:
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
    def __eq__(self, other): return self.data == other.data
    def __ne__(self, other): return self.data != other.data
    def __str__(self): return f"Vector[{self.x}, {self.y}]"

    @property
    def x(self): return self.data[0]

    @property
    def y(self): return self.data[1]

    @x.setter
    def x(self, value): self.data[0] = value

    @y.setter
    def y(self, value): self.data[1] = value


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
