import math
import os
import random
import time
from typing import Optional
import statistics
import timeit

import matplotlib.pyplot as plt
import numpy as np

from ControlPoint import ControlPoint
from Field import Field
from MapPart import MapPart
from PriorityQueue import PriorityQueue
from Unit import Unit
from UnitView import UnitView

times = []
lens = []


def heu(a: Field, b: Field) -> float:
    return abs(a.pos.x - b.pos.x) + abs(a.pos.y - b.pos.y)


def reconstruct_path(came_from: dict[Field, Optional[Field]], start: Field, goal: Field) -> list[Field]:
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
    messageQueue: list[dict]
    col: int
    row: int
    terrainMemory: list[list[Optional[Field]]]
    folderName: str
    maxEnemySize: int

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
        self.terrainMemory = [[None for _ in range(self.mapSize)] for _ in range(self.mapSize)]
        self.maxEnemySize = 0
        if self.strategy != "dummy":
            self.folderName = f"replay_{self.name}_{int(time.time() * 1000)}"
            os.mkdir(self.folderName)

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

        for sf in self.seenFields:
            self.terrainMemory[sf.pos.x][sf.pos.y] = sf

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
        choseOne = random.choice([n for n in self.getNeighbours(u.currentField) if n.typ in u.steppables])
        if choseOne is not None:
            pos = {"x": choseOne.pos.x, "y": choseOne.pos.y}
        else:
            pos = {"x": u.currentField.pos.x, "y": u.currentField.pos.y}
        self.messageQueue.append({"id": u.uid, "action": "move", "target": pos})

    def moveUnitAStar(self, u: Unit, goal: Field):
        # print("a*: ")
        # print(timeit.timeit("self.a_star_search(u, goal)", globals=locals(), number=1))
        came_from = self.a_star_search(u, goal)
        # print("rec path: ")
        # print(timeit.timeit("self.reconstruct_path(came_from, u.currentField, goal)", globals=locals(), number=1))
        pathTo = reconstruct_path(came_from, u.currentField, goal)

        if len(pathTo) < 2:
            self.moveUnitDummy(u)
            return
        self.messageQueue.append(
            {"id": u.uid, "action": "move", "target": {"x": pathTo[1].pos.x, "y": pathTo[1].pos.y}})

    def getNeighbours(self, fiq: Field) -> list[Field]:
        return [res for (x, y) in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
                if 0 <= (a := fiq.pos.x + x) < self.mapSize
                if 0 <= (b := fiq.pos.y + y) < self.mapSize
                if (res := self.terrainMemory[a][b]) is not None]

    def intel(self):
        for uv in self.seenUnits:
            x = math.floor(uv.pos.x / self.desiredPartSize)
            y = math.floor(uv.pos.y / self.desiredPartSize)
            self.mapParts[x][y].addUnit(uv)
            enemySize = len([u for u in self.seenUnits if u.team != self.name])
            if enemySize > self.maxEnemySize:
                self.maxEnemySize = enemySize

        for cp in self.seenControlPoints:
            x = math.floor(cp.pos.x / self.desiredPartSize)
            y = math.floor(cp.pos.y / self.desiredPartSize)
            self.mapParts[x][y].addCp(cp)

        for f in self.seenFields:
            x = math.floor(f.pos.x / self.desiredPartSize)
            y = math.floor(f.pos.y / self.desiredPartSize)
            self.mapParts[x][y].addField(f)

        # for b in self.mapParts:
        #     for c in b:
        #         print(f"{str(c)} -> {c.score(self.name)}")
        #         print(f"{c.printStatus()}")

    def autoEncoder(self, save: bool = False, show: bool = False):
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

        if save:
            plt.clf()
            toPlt = np.transpose(mapData)
            plt.title(self.name)
            plt.imshow(toPlt, cmap='viridis', interpolation='none', vmin=0, vmax=27)
            plt.colorbar()
            plt.draw()
            plt.ioff()
            plt.figure(1)

            plt.savefig(f"{self.folderName}/{int(time.time()*1000)}.png")
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

    """
    this method profiles the enemy team and returns a number between 0 and 1 to report it's health state
    """
    def teamProfiler(self, units: list[UnitView]) -> float:
        theoreticalMaxHealth = 0
        actualHealth = 0
        for u in units:
            match u.typ:
                case "TANK":
                    theoreticalMaxHealth += 80
                case "INFANTRY":
                    theoreticalMaxHealth += 20
                case "SCOUT":
                    theoreticalMaxHealth += 70
            actualHealth += u.health
            if self.maxEnemySize == 0:
                return 1
        if units[0].team == self.name:
            return 0.5 * (actualHealth / theoreticalMaxHealth + len(units) / len(self.units))
        return 0.5 * (actualHealth / theoreticalMaxHealth + len(units) / self.maxEnemySize)

    """
    this method profiles a unit from the team and returns a number between 0 and 1 to report it's general state
    """
    def unitProfiler(self, u: Unit) -> float:
        pass

    def scouting(self) -> None:
        scout = [s for s in self.units if s.typ == "SCOUT"][0]
        x = int(statistics.mean(u.currentField.pos.x for u in self.units))
        y = int(statistics.mean(u.currentField.pos.y for u in self.units))
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

    def attack(self, mp: MapPart, enemies: list[UnitView]):
        strongest = enemies[0]  # this should be selected by the unitProfiler
        pos = {"x": strongest.pos.x, "y": strongest.pos.y}
        for u in [u for u in self.units if u.typ != "SCOUT" and u.ammo > 0]:
            if u.currentField.pos.dist(strongest.pos) > u.shootRange:
                dest = [f for f in self.seenFields if f.pos == strongest.pos][0]
                self.moveUnitAStar(u, dest)
            self.messageQueue.append({"id": u.uid, "action": "shoot", "target": pos})

    def retreat(self):
        selectedMapPart = max((mp for mps in self.mapParts for mp in mps), key=lambda mp: mp.score(self.name))
        for u in self.units:
            self.moveUnitAStar(u, random.choice([f for f in selectedMapPart.fields if f.typ in u.steppables]))

    def heuristic(self) -> None:
        us = [u for u in self.seenUnits if u.team == self.name]
        them = [u for u in self.seenUnits if u.team != self.name]
        if self.teamProfiler(us) < 0.25:
            self.retreat()
            return
        if len(them) == 0:
            if self.teamProfiler(us) > 0.8:
                self.scouting()
            if len(self.seenControlPoints) > 0:
                selectedMapPart = [mp for mps in self.mapParts for mp in mps if len(mp.cps) > 0][0]
                self.conquer(selectedMapPart)
            return
        else:
            selectedMapPart = [mp for mps in self.mapParts for mp in mps if len(mp.white_uvs) > 0][0]
            self.attack(selectedMapPart, them)
            return

    def doAction(self):
        if self.strategy == "dummy":
            self.dummyMove()
            self.dummyShoot()
        elif self.strategy == "heuristic":
            # times.append(timeit.timeit("self.heuristic()", globals=locals(), number=1))
            # lens.append(len(self.terrainMemory))
            # print(f"terrain memory len:{len(self.terrainMemory)}, heu:", timeit.timeit("self.heuristic()", globals=locals(), number=1))
            self.heuristic()
        return self.messageQueue

    def a_star_search(self, u: Unit, goal: Field):
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
                    priority = new_cost + heu(next, goal)
                    frontier.put(next, priority)
                    came_from[next] = current

        return came_from


    def profileSave(self):
        plt.xlabel("lens")
        plt.ylabel("times")
        plt.plot(lens, times)
        plt.savefig("profiling40.png")
