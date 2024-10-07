from Pos import Pos


class ControlPoint:
    pos: Pos
    uid: int
    size: int
    percentage: int

    def __init__(self, payload):
        self.pos = Pos(payload["pos"])
        self.percentage = payload["percentage"]
        self.size = payload["size"]
        self.uid = payload["id"]

    def __str__(self):
        return f"id: {self.uid}, pos: {self.pos}"
