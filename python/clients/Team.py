import math

import matplotlib.pyplot as plt
import numpy as np

from Unit import Unit
from ControlPoint import ControlPoint
from Field import Field
from UnitView import UnitView
from MapPart import MapPart


class Team:
    name: str
    strategy: str
    units: list[Unit]
    seenUnits: list[UnitView]
    seenControlPoints: list[ControlPoint]
    seenFields: list[Field]
    mapSize: int
    mapPartsSize : int
    mapParts = list[list[MapPart]]

    def __init__(self, name: str, strategy: str, ms: int):
        self.name = name
        self.strategy = strategy
        self.units = []
        self.seenUnits = []
        self.seenControlPoints = []
        self.seenFields = []
        self.mapSize = ms
        self.desiredPartSize = 10
        row, col = (self.mapSize // self.desiredPartSize), (self.mapSize // self.desiredPartSize)
        self.mapParts = [[MapPart(i, j) for i in range(col)] for j in range(row)]

    def __str__(self):
        return f"teamName: {self.name}, strategy: {self.strategy}, units: {[str(u) for u in self.units]}"

    def addUnits(self, payload: list[any]):
        for i in payload:
            self.units.append(Unit(i))

    def updateWorld(self, payload : list[any]):
        for cp in payload["seenControlPoints"]:
            self.seenControlPoints.append(ControlPoint(cp))

        for f in payload["seenFields"]:
            self.seenFields.append(Field(f))

        for uv in payload["seenUnits"]:
            self.seenUnits.append(UnitView(uv))

    def clear(self):
        self.units = []
        self.seenUnits = []
        self.seenFields = []
        self.seenControlPoints = []
        self.mapParts = []

    def plotState(self):
        return f"sf: {[str(f) for f in self.seenFields]} \n su: {[str(u) for u in self.seenUnits]}"

    def moveUnit(self):
        # this should do the a* part
        # it is here, because this is the part where all the seen fields are present
        # i do not want to give the seenFields to everyone one by one
        #   this would help actually, because the unit knows what it can step on
        pass

    def intel(self):
        for uv in self.seenUnits:
            x = math.floor(uv.pos.x / self.desiredPartSize)
            y = math.floor(uv.pos.y / self.desiredPartSize)
            self.mapParts[x][y].addUnit(uv)
        for cp in self.seenControlPoints:
            x = math.floor(cp.pos.x / self.desiredPartSize)
            y = math.floor(cp.pos.y / self.desiredPartSize)
            self.mapParts[x][y].addCp(cp)
        # for a in self.mapParts:
        #     for b in a:
        #         print(f"{str(b)} -> {b.score(self.name)}")
        #         print(f"{b.printStatus()}")


    def attack(self):
        pass




