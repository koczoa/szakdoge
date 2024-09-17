from Pos import Pos


class Field:
    pos: Pos
    type: str

    def __init__(self, payload):
        self.pos = Pos(payload["pos"])
        self.type = payload["type"]

    def __eq__(self, other):
        return self.pos == other.pos

    def __str__(self):
        return str(self.pos)

    def getPos(self):
        return self.pos.val()

    def getType(self):
        return self.type
