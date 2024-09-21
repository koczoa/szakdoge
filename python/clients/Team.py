from Unit import Unit
from ControlPoint import ControlPoint
from Field import Field
from UnitView import UnitView

class Team:
    name: str
    strategy: str
    untis: list[Unit]
    seenUnits: list[UnitView]
    seenControlPoints: list[ControlPoint]
    seenFields: list[Field]

    def __init__(self, name, strategy):
        self.name = name
        self.strategy = strategy
        self.units = []
        self.seenUnits = []
        self.seenControlPoints = []
        self.seenFields = []

    def __str__(self):
        return f"teamName: {self.name}, strategy: {self.strategy}, units: {[str(u) for u in self.units]}"

    def addUnits(self, payload : list[any]):
        for i in payload:
            self.units.append(Unit(i))

    def updateWorld(self, payload : list[any]):
        for cp in payload["seenControlPoints"]:
            self.seenControlPoints.append(ControlPoint(cp))

        for f in payload["seenFields"]:
            self.seenFields.append(Field(f))

        for uv in payload["seenUnits"]:
            self.seenUnits.append(UnitView(uv))

