from Pos import Pos


class ControlPoint:
    pos: Pos
    id: int
    size: int
    percentage: int

    def __init__(self, payload):
        self.pos = Pos(payload["pos"])
        self.percentage = payload["percentage"]
        self.size = payload["size"]
        self.id = payload["id"]

