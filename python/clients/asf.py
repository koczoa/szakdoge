import os
from datetime import datetime
from time import sleep

from Team import Team
from Wrapper import Wrapper

print(os.getcwd())

def setupMessageParser(payload):
    global t
    t = Team(payload["teamName"], payload["strategy"], payload["mapSize"])
    print("setup:", t)


def commMessageParser(payload):
    t.addUnits(payload["units"])
    t.updateWorld(payload["map"])
    # print(t.plotState())
    t.intel()
    # t.autoEncoder()
    w.send(t.dummy())
    t.clear()


def endMessageParser(payload):
    pass


def fromjson(x):
    if x["type"] == "setupMessage":
        setupMessageParser(x["payload"])
    elif x["type"] == "commMessage":
        commMessageParser(x["payload"])
    elif x["type"] == "endMessage":
        endMessageParser(x["payload"])


w = Wrapper()

ctr = 0
while True:
    msg = w.receive(False)
    if msg is not None:
        fromjson(msg)
        ctr += 1
        print(f"-----------inter:{ctr}-----------")
    if ctr == 40:
        break
    sleep(0.1)

w.close()
