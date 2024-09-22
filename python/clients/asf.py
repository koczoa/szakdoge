from time import sleep

from Team import Team
from Wrapper import Wrapper


def setupMessageParser(payload):
    global t
    t = Team(payload["teamName"], payload["strategy"], payload["mapSize"])
    print("setup:", t)


def commMessageParser(payload):
    t.addUnits(payload["units"])
    t.updateWorld(payload["map"])
    print("comm:", t)
    print(t.plotState())
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
        # print(f"{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}, d:{msg}")
        fromjson(msg)
        ctr += 1
    if ctr == 2:
        break
    sleep(0.05)

w.close()