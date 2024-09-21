from Pos import Pos

class UnitView:
    pos: Pos
    id: int
    health: int
    team: str
    type: str

    def __init__(self, payload):
        self.id = payload["id"]
        self.health = payload["health"]
        self.pos = Pos(payload["pos"])
        self.team = payload["team"]
        self.type = payload["type"]


"""
"seenUnits": [
        {
          "pos": {
            "x": 7,
            "y": 3
          },
          "health": 80,
          "team": "white",
          "id": 2,
          "type": "TANK"
        }

"""