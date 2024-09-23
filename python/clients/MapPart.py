from UnitView import UnitView
from ControlPoint import ControlPoint


class MapPart:
    x: int
    y: int
    red_uvs = list[UnitView]
    white_uvs = list[UnitView]
    cps = list[ControlPoint]

    def __init__(self, x:int, y:int):
        self.x = x
        self.y = y
        self.red_uvs = []
        self.white_uvs = []
        self.cps = []

    def __str__(self):
        return f"x:{self.x} y:{self.y}"

    def addUnit(self, uv: UnitView):
        if uv.team == "red":
            self.red_uvs.append(uv)
        elif uv.team == "white":
            self.white_uvs.append(uv)

    def addCp(self, cp: ControlPoint):
        self.cps.append(cp)

    def printStatus(self):
        return f"units: red: {[str(uv) for uv in self.red_uvs]}, white: {[str(uv) for uv in self.white_uvs]}, cps: {[str(cp) for cp in self.cps]}"

    def score(self, teamName: str) -> int:
        teamScore = 0
        match teamName:
            case "white":
                for u in self.white_uvs:
                    teamScore += u.health
                for u in self.red_uvs:
                    teamScore -= u.health
                return teamScore
            case "red":
                for u in self.white_uvs:
                    teamScore -= u.health
                for u in self.red_uvs:
                    teamScore += u.health
                return teamScore
