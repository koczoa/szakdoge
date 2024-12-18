import json

from Field import Field


class Unit:
    def __init__(self, payload):
        teamName: str
        ammo: int
        actionPoints: int
        fuel: int
        currentField: Field
        health: int
        uid: int
        typ: str
        steppables: list[str]

        self.teamName = payload["teamName"]
        self.ammo = payload["ammo"]
        self.actionPoints = payload["actionPoints"]
        self.fuel = payload["fuel"]
        self.currentField = Field(payload["currentField"])
        self.health = payload["health"]
        self.uid = payload["id"]
        self.typ = payload["type"]
        desc = json.loads(open(f"/home/kocc/szakdoge/app/src/main/resources/descriptors/{self.typ}.json").read())
        self.steppables = desc["steppables"]
        self.shootRange = desc["shootRange"]
        self.consumption = desc["consumption"]

    def __str__(self):
        return f"id: {self.uid}, type: {self.typ}, field: {self.currentField}"
