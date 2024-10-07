from UnitView import UnitView
from ControlPoint import ControlPoint
from Field import Field


class MapPart:
    x: int
    y: int
    red_uvs = list[UnitView]
    white_uvs = list[UnitView]
    cps = list[ControlPoint]
    fields = list[Field]

    def __init__(self, x:int, y:int):
        self.x = x
        self.y = y
        self.red_uvs = []
        self.white_uvs = []
        self.cps = []
        self.fields = []

    def __str__(self):
        return f"x:{self.x} y:{self.y}"

    def addField(self, f: Field):
        self.fields.append(f)

    def addUnit(self, uv: UnitView):
        if uv.team == "red":
            self.red_uvs.append(uv)
        elif uv.team == "white":
            self.white_uvs.append(uv)

    def addCp(self, cp: ControlPoint):
        self.cps.append(cp)

    def printStatus(self):
        return (f"units: red: {[str(uv) for uv in self.red_uvs]}, "
                f"white: {[str(uv) for uv in self.white_uvs]}, "
                f"cps: {[str(cp) for cp in self.cps]}, "
                f"len(fields): {len(self.fields)}")

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
