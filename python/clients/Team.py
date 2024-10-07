import math
import random
import time
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np

from ControlPoint import ControlPoint
from Field import Field
from MapPart import MapPart
from PriorityQueue import PriorityQueue
from Unit import Unit
from UnitView import UnitView

plt.ion()


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
    terrainMemory: list[Field]

    def __init__(self, name: str, strategy: str, ms: int):
        self.name = name
        self.strategy = strategy
        self.units = []
        self.seenUnits = []
        self.seenControlPoints = []
        self.seenFields = []
        self.mapSize = ms
        self.desiredPartSize = 5
        self.row = (self.mapSize // self.desiredPartSize)
        self.col = (self.mapSize // self.desiredPartSize)
        self.mapParts = [[MapPart(i, j) for i in range(self.col)] for j in range(self.row)]
        self.messageQueue = []
        self.terrainMemory = []

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

        for f in self.seenFields:
            if f not in self.terrainMemory:
                self.terrainMemory.append(f)

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

    def moveUnitDummy(self, u: Unit):
        print("called")
        choseOne = random.choice([n for n in self.getNeighbours(u.currentField) if n.typ in u.steppables])
        if choseOne is not None:
            pos = {"x": choseOne.pos.x, "y": choseOne.pos.y}
        else:
            pos = {"x": u.currentField.pos.x, "y": u.currentField.pos.y}
        self.messageQueue.append({"id": u.uid, "action": "move", "target": pos})

    def moveUnitAStar(self, u: Unit, goal: Field):
        came_from = self.a_star_search(u, goal)
        pathTo = self.reconstruct_path(came_from, u.currentField, goal)

        if len(pathTo) < 2:
            self.moveUnitDummy(u)
            return

        self.messageQueue.append(
            {"id": u.uid, "action": "move", "target": {"x": pathTo[1].pos.x, "y": pathTo[1].pos.y}})

    def getNeighbours(self, fiq: Field) -> list[Field]:
        return [f for f in self.terrainMemory
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

        for f in self.seenFields:
            x = math.floor(f.pos.x / self.desiredPartSize)
            y = math.floor(f.pos.y / self.desiredPartSize)
            self.mapParts[x][y].addField(f)

        # for a in self.mapParts:
        #     for b in a:
        #         print(f"{str(b)} -> {b.score(self.name)}")
        #         print(f"{b.printStatus()}")

    def autoEncoder(self, show: bool = False):
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

        plt.clf()
        toPlt = np.transpose(mapData)
        plt.title(self.name)
        plt.imshow(toPlt, cmap='viridis', interpolation='none', vmin=0, vmax=27)
        plt.colorbar()
        plt.draw()
        plt.ioff()
        plt.savefig(f"{self.name}/{self.name}{int(time.time()*1000)}.png")
        if show and self.strategy != "dummy":
            plt.show()

    def dummyMove(self) -> None:
        for u in [u for u in self.units if u.fuel > 0]:
            self.moveUnitDummy(u)


    def dummyShoot(self) -> None:
        for u in self.units:
            if u.typ == "SCOUT" or u.ammo <= 0:
                break
            choseOne = random.choice([f for f in self.seenFields if f.pos.dist(u.currentField.pos) < u.shootRange])
            pos = {"x": choseOne.pos.x, "y": choseOne.pos.y}
            self.messageQueue.append({"id": u.uid, "action": "shoot", "target": pos})

    def scouting(self) -> None:
        scout = [s for s in self.units if s.typ == "SCOUT"][0]
        x = int(sum(u.currentField.pos.x for u in self.units) / len(self.units))
        y = int(sum(u.currentField.pos.y for u in self.units) / len(self.units))

        centerOfMass = [f for f in self.seenFields if f.pos.x == x and f.pos.y == y][0]
        farthest = scout.currentField
        if len(self.seenControlPoints) != 0:
            selectedCp = [cp for cp in self.seenControlPoints][0]
            farthest = [f for f in self.seenFields if f.pos == selectedCp.pos][0]
        else:
            maxDist = 0
            for f in self.seenFields:
                currDist = f.pos.dist(centerOfMass.pos)
                if currDist > maxDist:
                    farthest = f
                    maxDist = currDist

        self.moveUnitAStar(scout, farthest)

    def conquer(self, mp: MapPart):
        for u in [u for u in self.units if u.typ != "SCOUT"]:
            self.moveUnitAStar(u, random.choice([f for f in mp.fields if f.typ in u.steppables]))

    def attack(self, mp: MapPart):
        pass

    def retreat(self):
        pass

    def heuristic(self) -> None:
        self.scouting()
        if len(self.seenControlPoints) > 0:
            # this will be the retreat function
            # selectedMapPart = max((mp for mps in self.mapParts for mp in mps), key=lambda mp: mp.score(self.name))
            selectedMapPart = [mp for mps in self.mapParts for mp in mps if len(mp.cps) > 0][0]
            self.conquer(selectedMapPart)

    def doAction(self):
        if self.strategy == "dummy":
            self.dummyMove()
            self.dummyShoot()
        elif self.strategy == "heuristic":
            self.heuristic()
        return self.messageQueue

    def a_star_search(self,  u: Unit, goal: Field):
        frontier = PriorityQueue()
        frontier.put(u.currentField, 0)
        came_from: dict[Field, Optional[Field]] = {}
        cost_so_far: dict[Field, float] = {}
        came_from[u.currentField] = None
        cost_so_far[u.currentField] = 0

        while not frontier.empty():
            current: Field = frontier.get()

            if current == goal:
                break

            for next in [n for n in self.getNeighbours(current) if n.typ in u.steppables]:
                new_cost = cost_so_far[current] + 1
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + self.heu(next, goal)
                    frontier.put(next, priority)
                    came_from[next] = current

        return came_from

    def heu(self, a: Field, b: Field) -> float:
        x1 = a.pos.x
        y1 = a.pos.y
        x2 = b.pos.x
        y2 = b.pos.y

        return abs(x1 - x2) + abs(y1 - y2)

    def reconstruct_path(self, came_from: dict[Field, Optional[Field]], start: Field, goal: Field) -> list[Field]:
        current: Field = goal
        path: list[Field] = []
        if goal not in came_from.keys():
            return []
        while current != start:
            path.append(current)
            current = came_from[current]
        path.append(start)
        path.reverse()
        return path
