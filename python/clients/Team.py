import json
import math
import os
import random
import shutil
import time
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np

from Pos import Pos
from Unit import Unit
from ControlPoint import ControlPoint
from Field import Field
from UnitView import UnitView
from MapPart import MapPart
from PriorityQueue import PriorityQueue


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

    def getNPos(self, fiq: Pos) -> list[Pos]:
        return [f.pos for f in self.seenFields
                if abs(f.pos.x - fiq.x) <= 1
                and abs(f.pos.y - fiq.y) <= 1
                and f.pos != fiq]
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

    def autoEncoder(self, cleanDir: bool = False, show: bool = False):
        if cleanDir:
            shutil.rmtree(f"{self.name}")
            os.mkdir(self.name)
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
        plt.imshow(toPlt, cmap='viridis', interpolation='none')
        plt.colorbar()
        plt.draw()
        plt.ioff()
        plt.savefig(f"{self.name}/{self.name}{int(time.time()*1000)}.png")
        if show and self.strategy != "dummy":
            plt.show()

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

    def heuristic(self) -> list[str]:
        scout = [s for s in self.units if s.typ == "SCOUT"][0]

        # TODO: polák refactoring needed
        x = int(sum(u.currentField.pos.x for u in self.units) / len(self.units))
        y = int(sum(u.currentField.pos.y for u in self.units) / len(self.units))

        centerOfMass = [f for f in self.seenFields if f.pos.x == x and f.pos.y == y][0]

        print(f"com:{centerOfMass}")
        farthest = scout.currentField
        print(f"farthest: {farthest}")
        maxDist = 0
        for f in self.seenFields:
            currDist = f.pos.dist(centerOfMass.pos)
            # print(f"cd:{currDist}, md:{maxDist}, cf:{f.pos}, ff:{farthest}")
            if currDist > maxDist:
                # print("change")
                farthest = f
                maxDist = currDist
        came_from, _ = self.a_star_search(scout.currentField, farthest, scout)
        print(came_from)
        print(hex(id(farthest)))
        pathTo = [p for p in self.reconstruct_path(came_from, scout.currentField, farthest)]
        print([str(p) for p in self.reconstruct_path(came_from, scout.currentField, farthest)])

        msg = {}
        msg["id"] = scout.uid
        msg["action"] = "move"
        msg["target"] = {"x": pathTo[1].pos.x, "y": pathTo[1].pos.y}
        self.messageQueue.append(msg)
        return self.messageQueue

    def doAction(self):
        if self.strategy == "dummy":
            return self.dummy()
        elif self.strategy == "heuristic":
            return self.heuristic()

    def a_star_search(self, start: Field, goal: Field, u: Unit):
        frontier = PriorityQueue()
        frontier.put(start, 0)
        came_from: dict[Field, Optional[Field]] = {}
        cost_so_far: dict[Field, float] = {}
        came_from[start] = None
        cost_so_far[start] = 0

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

        return came_from, cost_so_far

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
