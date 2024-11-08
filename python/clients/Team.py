import json
import math
import os
import random
import time
from typing import Optional, Callable, List
from enum import Enum
import matplotlib.pyplot as plt
import numpy as np

from ControlPoint import ControlPoint
from Field import Field
from MapPart import MapPart
from PriorityQueue import PriorityQueue
from Unit import Unit
from UnitView import UnitView


class TeamColor(Enum):
    WHITE = "white"
    RED = "red"


def heu(a: Field, b: Field) -> float:
    return abs(a.pos.x - b.pos.x) + abs(a.pos.y - b.pos.y)


def heu2(a: Field, b: Field) -> float:
    return heu(a, b) + random.uniform(-2, 2)


def a_star_search(start: Field, getNeighbours: Callable[[Field], list[Field]], goal: Field) -> list[Field]:
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from: dict[Field, Optional[Field]] = {start: None}
    cost_so_far: dict[Field, float] = {start: 0.0}
    while not frontier.empty():
        current: Field = frontier.get()
        if current == goal:
            break
        for next in getNeighbours(current):
            new_cost = cost_so_far[current] + random.uniform(0.5, 1.5)
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + heu(next, goal)
                frontier.put(next, priority)
                came_from[next] = current
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


def bfs_search(start: Field, getNeighbours: Callable[[Field], list[Field]], goal: Callable[[Field], bool]) -> list[
    Field]:
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from: dict[Field, Optional[Field]] = {start: None}
    cost_so_far: dict[Field, float] = {start: 0.0}
    while not frontier.empty():
        current: Field = frontier.get()
        if goal(current):
            break
        for next in getNeighbours(current):
            new_cost = cost_so_far[current] + random.uniform(0.5, 1.5)
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + 0
                frontier.put(next, priority)
                came_from[next] = current
    path: list[Field] = []
    if not goal(current):
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
    units: dict[int, Unit]
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

    def __init__(self, name: str, strategy: str, ms: int, save: bool):
        self.name = name
        self.strategy = strategy
        self.units = {}
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
        if self.strategy != "dummy" and save:
            self.folderName = f"replay_{self.name}_{int(time.time() * 1000)}"
            os.mkdir(self.folderName)
        self.scoutDesc = json.loads(open("../../app/src/main/resources/descriptors/SCOUT.json").read())
        self.tankDesc = json.loads(open("../../app/src/main/resources/descriptors/TANK.json").read())
        self.infantryDesc = json.loads(open("../../app/src/main/resources/descriptors/INFANTRY.json").read())
        self.history = []
        self.mapData = np.zeros((self.mapSize, self.mapSize), np.int32)
        self.save = save

    def __str__(self):
        return f"teamName: {self.name}, strategy: {self.strategy}, units: {[str(u) for u in self.units]}"

    def addUnits(self, payload: list[any]):
        for i in payload:
            u = Unit(i)
            if u.uid not in self.units:
                self.units[u.uid] = u
            else:
                self.units[u.uid].currentField = u.currentField
                self.units[u.uid].ammo = u.ammo
                self.units[u.uid].health = u.health
                self.units[u.uid].fuel = u.fuel

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
        self.seenUnits = []
        self.seenFields = []
        self.seenControlPoints = []
        self.mapParts = [[MapPart(i, j) for i in range(self.col)] for j in range(self.row)]
        self.messageQueue = []

    def plotState(self):
        return f"sf: {[str(f) for f in self.seenFields]} \n su: {[str(u) for u in self.seenUnits]}"

    def moveUnitDummy(self, u: Unit):
        if u.fuel - u.consumption > 0:
            choseOne = random.choice([n for n in self.getNeighbours(u.currentField)
                                      if n.typ in u.steppables
                                      if n.pos not in [uv.pos for uv in self.seenUnits]])
            if choseOne is not None:
                pos = {"x": choseOne.pos.x, "y": choseOne.pos.y}
            else:
                pos = {"x": u.currentField.pos.x, "y": u.currentField.pos.y}
            self.messageQueue.append({"id": u.uid, "action": "move", "target": pos})

    def moveUnitAStar(self, u: Unit, goal: Field):
        if goal is None:
            return
        if u.fuel - u.consumption > 0:
            pathTo = a_star_search(
                u.currentField,
                lambda f: [n for n in self.getNeighbours(f)
                           if n is not None
                           if n.typ in u.steppables
                           if n.pos not in [uv.pos for uv in self.seenUnits
                                            if uv.pos != goal.pos]
                           ],
                goal)
            if len(pathTo) < 2:
                self.moveUnitDummy(u)
            else:
                self.messageQueue.append(
                    {"id": u.uid,
                     "action": "move",
                     "target": {"x": pathTo[1].pos.x, "y": pathTo[1].pos.y}})

    def moveUnitBFS(self, u: Unit):
        if u.fuel - u.consumption > 0:
            closest_perimeter = bfs_search(
                u.currentField,
                lambda f: [n for n in self.getNeighbours(f)
                           if n is None or n.typ in u.steppables
                           if n is None or n.pos not in [uv.pos for uv in self.seenUnits]],
                lambda f: f is None)
            if len(closest_perimeter) < 2:
                print(f"{closest_perimeter=}")
                self.moveUnitDummy(u)
            else:
                self.messageQueue.append(
                    {"id": u.uid,
                     "action": "move",
                     "target": {"x": closest_perimeter[1].pos.x, "y": closest_perimeter[1].pos.y}})

    def getNeighbours(self, fiq: Field) -> list[Field]:
        neighs = [self.terrainMemory[a][b] for (x, y) in
                  [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
                  if 0 <= (a := fiq.pos.x + x) < self.mapSize
                  if 0 <= (b := fiq.pos.y + y) < self.mapSize]
        random.shuffle(neighs)
        return neighs

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

    def autoEncoder(self):
        self.mapData = np.full(shape=(self.mapSize, self.mapSize, 8), dtype=float, fill_value=0.0)
        for r in self.terrainMemory:
            for f in r:
                if f is not None:
                    match f.typ:
                        case "GRASS":
                            self.mapData[f.pos.x][f.pos.y][0] = 0.25
                        case "WATER":
                            self.mapData[f.pos.x][f.pos.y][0] = 0.4
                        case "MARSH":
                            self.mapData[f.pos.x][f.pos.y][0] = 0.55
                        case "FOREST":
                            self.mapData[f.pos.x][f.pos.y][0] = 0.7
                        case "BUILDING":
                            self.mapData[f.pos.x][f.pos.y][0] = 0.85

        for cp in self.seenControlPoints:
            self.mapData[cp.pos.x][cp.pos.y][1] = 1

        for u in self.seenUnits:
            if u.team != self.name:
                match u.typ:
                    case "TANK":
                        self.mapData[u.pos.x][u.pos.y][2] = u.health / self.tankDesc["maxHealth"]
                        self.mapData[u.pos.x][u.pos.y][3] = 0
                    case "INFANTRY":
                        self.mapData[u.pos.x][u.pos.y][2] = u.health / self.infantryDesc["maxHealth"]
                        self.mapData[u.pos.x][u.pos.y][3] = 0.5
                    case "SCOUT":
                        self.mapData[u.pos.x][u.pos.y][2] = u.health / self.scoutDesc["maxHealth"]
                        self.mapData[u.pos.x][u.pos.y][3] = 1


        for u in self.units.values():
            match u.typ:
                case "TANK":
                    self.mapData[u.currentField.pos.x][u.currentField.pos.y][4] = u.health / self.tankDesc["maxHealth"]
                    self.mapData[u.currentField.pos.x][u.currentField.pos.y][5] = 0
                    self.mapData[u.currentField.pos.x][u.currentField.pos.y][6] = u.ammo / self.tankDesc["maxAmmo"]
                    self.mapData[u.currentField.pos.x][u.currentField.pos.y][7] = u.fuel / self.tankDesc["maxFuel"]
                case "INFANTRY":
                    self.mapData[u.currentField.pos.x][u.currentField.pos.y][4] = u.health / self.infantryDesc["maxHealth"]
                    self.mapData[u.currentField.pos.x][u.currentField.pos.y][5] = 0.5
                    self.mapData[u.currentField.pos.x][u.currentField.pos.y][6] = u.ammo / self.infantryDesc["maxAmmo"]
                    self.mapData[u.currentField.pos.x][u.currentField.pos.y][7] = u.fuel / self.infantryDesc["maxFuel"]
                case "SCOUT":
                    self.mapData[u.currentField.pos.x][u.currentField.pos.y][4] = u.health / self.scoutDesc["maxHealth"]
                    self.mapData[u.currentField.pos.x][u.currentField.pos.y][5] = 1
                    self.mapData[u.currentField.pos.x][u.currentField.pos.y][6] = 0
                    self.mapData[u.currentField.pos.x][u.currentField.pos.y][7] = u.fuel / self.scoutDesc["maxFuel"]

    def visualize(self):
        self.visData = np.zeros((self.mapSize, self.mapSize), np.int32)
        for r in self.terrainMemory:
            for f in r:
                if f is not None:
                    match f.typ:
                        case "GRASS":
                            self.visData[f.pos.x][f.pos.y] += 1
                        case "WATER":
                            self.visData[f.pos.x][f.pos.y] += 2
                        case "MARSH":
                            self.visData[f.pos.x][f.pos.y] += 3
                        case "FOREST":
                            self.visData[f.pos.x][f.pos.y] += 4
                        case "BUILDING":
                            self.visData[f.pos.x][f.pos.y] += 5

        # for f in self.seenFields:
        #     match f.typ:
        #         case "GRASS":
        #             visData[f.pos.x][f.pos.y] += 1
        #         case "WATER":
        #             visData[f.pos.x][f.pos.y] += 2
        #         case "MARSH":
        #             visData[f.pos.x][f.pos.y] += 3
        #         case "FOREST":
        #             visData[f.pos.x][f.pos.y] += 4
        #         case "BUILDING":
        #             visData[f.pos.x][f.pos.y] += 5

        # TODO: this could and SHOULD be optimised...
        for u in self.seenUnits:
            if u.team == self.name:
                match u.typ:
                    case "TANK":
                        self.visData[u.pos.x][u.pos.y] += 6
                    case "INFANTRY":
                        self.visData[u.pos.x][u.pos.y] += 7
                    case "SCOUT":
                        self.visData[u.pos.x][u.pos.y] += 8
            else:
                match u.typ:
                    case "TANK":
                        self.visData[u.pos.x][u.pos.y] += 9
                    case "INFANTRY":
                        self.visData[u.pos.x][u.pos.y] += 10
                    case "SCOUT":
                        self.visData[u.pos.x][u.pos.y] += 11

        for cp in self.seenControlPoints:
            self.visData[cp.pos.x][cp.pos.y] += 12


        plt.clf()
        toPlt = np.transpose(self.visData)
        plt.title(self.name)
        plt.imshow(toPlt, cmap="viridis", interpolation="none", vmin=0, vmax=27)
        plt.colorbar()
        plt.draw()
        plt.ioff()
        plt.figure(1)

        plt.savefig(f"{self.folderName}/{int(time.time() * 1000)}.png")

    def dummyMove(self) -> None:
        for u in [u for u in self.units.values() if u.fuel > 0]:
            self.moveUnitDummy(u)

    def dummyShoot(self) -> None:
        for u in self.units.values():
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
    def unitViewProfiler(self, uv: UnitView) -> float:
        maxHealth, damage, magic_offset = 0, 0, 0
        match uv.typ:
            case "TANK":
                maxHealth = self.tankDesc["maxHealth"]
                damage = self.tankDesc["damage"]
                magic_offset = 50
            case "SCOUT":
                maxHealth = self.scoutDesc["maxHealth"]
                damage = self.scoutDesc["damage"]
            case "INFANTRY":
                maxHealth = self.infantryDesc["maxHealth"]
                damage = self.infantryDesc["damage"]
                magic_offset = 25
        return damage * (uv.health / maxHealth) + magic_offset

    def unitProfiler(self, u: Unit) -> List[float]:
        pass

    def scouting(self) -> None:
        # print("scouting")
        scouts = [s for s in self.units.values() if s.typ == "SCOUT"]
        if len(scouts) > 0:
            scout = scouts[0]
            self.moveUnitBFS(scout)

    def conquer(self, mp: MapPart):
        # print("conquering")
        for u in self.units.values():
            self.moveUnitAStar(u, random.choice([f for f in mp.fields if f.typ in u.steppables]))

    def attack(self, mp: MapPart, enemies: list[UnitView]):
        # print("attacking")
        # an enemy unit is strongest when it could deal the most damage before the team kills it
        # strongest = enemies[0]  # this should be selected by the unitProfiler
        strongest = max((uv for uv in enemies), key=lambda uv: self.unitViewProfiler(uv))
        pos = {"x": strongest.pos.x, "y": strongest.pos.y}
        for u in [u for u in self.units.values() if u.typ != "SCOUT" and u.ammo > 0]:
            if u.currentField.pos.dist(strongest.pos) >= u.shootRange - 1:
                try:
                    self.moveUnitAStar(u, random.choice([f for f in mp.fields if f.typ in u.steppables]))
                except IndexError:
                    self.moveUnitDummy(u)
            else:
                if u.ammo > 1:
                    self.messageQueue.append({"id": u.uid, "action": "shoot", "target": pos})

    def retreat(self):
        # print("retreating")
        # selectedMapPart = max((mp for mps in self.mapParts for mp in mps), key=lambda mp: mp.score(self.name))
        selectedMapPart = max((mp for mps in self.mapParts for mp in mps), key=lambda mp: len(mp.cps))
        for u in self.units.values():
            try:
                self.moveUnitAStar(u, random.choice([f for f in selectedMapPart.fields if f.typ in u.steppables]))
            except IndexError:
                self.moveUnitDummy(u)

    def heuristic(self) -> None:
        if len(self.units) == 0:
            return
        us = [u for u in self.seenUnits if u.team == self.name]
        them = [u for u in self.seenUnits if u.team != self.name]
        self.autoEncoder()
        if self.teamProfiler(us) < 0.25:
            self.retreat()
            choice = 0
        else:
            if len(them) == 0:
                if len(self.seenControlPoints) == 0 or self.teamProfiler(us) > 0.75:
                    self.scouting()
                    choice = 1
                else:
                    selectedMapPart = [mp for mps in self.mapParts for mp in mps if len(mp.cps) > 0][0]
                    self.conquer(selectedMapPart)
                    choice = 2
            else:
                if self.name == "white":
                    selectedMapPart = [mp for mps in self.mapParts for mp in mps if len(mp.red_uvs) > 0][0]
                else:
                    selectedMapPart = [mp for mps in self.mapParts for mp in mps if len(mp.white_uvs) > 0][0]
                self.attack(selectedMapPart, them)
                choice = 3
        toHist = self.mapData.flatten()
        a = random.random()
        if a < 0.25:
            toHist = np.transpose(toHist)
        elif 0.25 <= a < 0.5:
            toHist = np.flip(toHist)
        self.history.append([choice] + toHist.tolist())
        if self.save:
            self.visualize()

    def doAction(self):
        self.intel()
        if self.strategy == "dummy":
            self.dummyMove()
            self.dummyShoot()
        elif self.strategy == "heuristic":
            self.heuristic()
        return self.messageQueue

    def saveGame(self):
        np.save(f"train_data_2/{int(time.time() * 1000)}.npy", np.array(self.history))
