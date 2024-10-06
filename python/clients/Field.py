from Pos import Pos
from typing import Self


class Field:
    pos: Pos
    typ: str

    def __init__(self, payload):
        self.pos = Pos(payload["pos"])
        self.typ = payload["type"]

    def __eq__(self, other: Self):
        return self.pos == other.pos

    def __str__(self):
        return str(self.pos)

    def getPos(self):
        return self.pos.val()

    def getType(self):
        return self.typ

    def __hash__(self):
        return self.pos.__hash__()

    def __lt__(self, other: Self):
        return self.pos < other.pos
