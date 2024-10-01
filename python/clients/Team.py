import json
import math
import random

import matplotlib.pyplot as plt
import numpy as np

from Pos import Pos
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
    mapPartsSize: int
    mapParts: list[list[MapPart]]
    messageQueue: list[str]
    col:int
    row: int

    def __init__(self, name: str, strategy: str, ms: int):
        self.name = name
        self.strategy = strategy
        self.units = []
        self.seenUnits = []
        self.seenControlPoints = []
        self.seenFields = []
        self.mapSize = ms
        self.desiredPartSize = 10
        self.row = (self.mapSize // self.desiredPartSize)
        self.col = (self.mapSize // self.desiredPartSize)
        self.mapParts = [[MapPart(i, j) for i in range(self.col)] for j in range(self.row)]
        self.messageQueue = []

    def __str__(self):
        return f"teamName: {self.name}, strategy: {self.strategy}, units: {[str(u) for u in self.units]}"

    def addUnits(self, payload: list[any]):
        for i in payload:
            self.units.append(Unit(i))

    def updateWorld(self, payload: list[any]):
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
        self.mapParts = [[MapPart(i, j) for i in range(self.col)] for j in range(self.row)]
        self.messageQueue = []

    def plotState(self):
        return f"sf: {[str(f) for f in self.seenFields]} \n su: {[str(u) for u in self.seenUnits]}"

    def moveUnit(self):
        # this should do the a* part
        # it is here, because this is the part where all the seen fields are present
        # i do not want to give the seenFields to everyone one by one
        #   this would help actually, because the unit knows what it can step on
        pass

    def getNeighbours(self, fiq: Field) -> list[Field]:
        return [f for f in self.seenFields
                if abs(f.pos.x - fiq.pos.x) <= 1
                and abs(f.pos.y - fiq.pos.y) <= 1
                and f != fiq]

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

    def autoEncoder(self):
        mapData = np.zeros((self.mapSize, self.mapSize), np.int32)
        for f in self.seenFields:
            match f.typ:
                case "GRASS":
                    mapData[f.pos.x][f.pos.y] += 1
                case "WATER":
                    mapData[f.pos.x][f.pos.y] += 2
                case "MARSH":
                    mapData[f.pos.x][f.pos.y] += 3
                case "FOREST":
                    mapData[f.pos.x][f.pos.y] += 4
                case "BUILDING":
                    mapData[f.pos.x][f.pos.y] += 5

        # TODO: this could and SHOULD be optimised...
        for u in self.seenUnits:
            if u.team == self.name:
                match u.typ:
                    case "TANK":
                        mapData[u.pos.x][u.pos.y] += 6
                    case "INFANTRY":
                        mapData[u.pos.x][u.pos.y] += 7
                    case "SCOUT":
                        mapData[u.pos.x][u.pos.y] += 8
            else:
                match u.typ:
                    case "TANK":
                        mapData[u.pos.x][u.pos.y] += 9
                    case "INFANTRY":
                        mapData[u.pos.x][u.pos.y] += 10
                    case "SCOUT":
                        mapData[u.pos.x][u.pos.y] += 11

        for cp in self.seenControlPoints:
            mapData[cp.pos.x][cp.pos.y] += 12

        toPlt = np.transpose(mapData)
        plt.title(self.name)
        plt.imshow(toPlt, cmap='viridis', interpolation='none')
        plt.show()

    def attack(self):
        pass

    def dummy(self) -> list[str]:
        for u in self.units:
            msg = {}
            negihs = [n for n in self.getNeighbours(u.currentField) if n.typ in u.steppables]
            choseOne = random.choice(negihs)
            if choseOne is not None:
                pos = {"x": choseOne.pos.x, "y": choseOne.pos.y}
            else:
                pos = {"x": u.currentField.pos.x, "y": u.currentField.pos.y}
            if random.randint(1, 2) == 1 or u.typ == "SCOUT":
                msg["id"] = u.uid
                msg["action"] = "move"
                msg["target"] = pos
            else:
                msg["id"] = u.uid
                msg["action"] = "shoot"
                msg["target"] = pos
            self.messageQueue.append(msg)
        return self.messageQueue
