import math
from typing import Self


class Pos:
    x: int
    y: int

    def __init__(self, payload):
        self.x = payload["x"]
        self.y = payload["y"]

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def val(self):
        return self.x, self.y

    def x(self):
        return self.x

    def y(self):
        return self.y

    # Chebyshev distance
    def dist(self, other: Self):
        return max(abs(self.x - other.x), abs(self.y - other.y))

    def distOL(self, other: Self):
        return max(abs(self.x - other["x"]), abs(self.y - other["y"]))

    def euclDist(self, other: Self):
        return math.sqrt(((self.x - other.x) ** 2) + ((self.y - other.y) ** 2))

    def __str__(self):
        return f"{self.x}, {self.y}"

    def __hash__(self):
        return self.x*100+self.y

    def __lt__(self, other):
        return False

