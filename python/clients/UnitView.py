from Pos import Pos

class UnitView:
    pos: Pos
    uid: int
    health: int
    team: str
    typ: str

    def __init__(self, payload):
        self.uid = payload["id"]
        self.health = payload["health"]
        self.pos = Pos(payload["pos"])
        self.team = payload["team"]
        self.typ = payload["type"]

    def __str__(self):
        return f"id: {self.uid}, type: {self.typ}, field: {self.pos}"