from datetime import datetime
from time import sleep


from Team import Team
from Wrapper import Wrapper

asdf = "{'payload': {'teamName': 'white', 'mapSize': 10, 'strategy': 'dummy'}, 'type': 'setupMessage'}"
ctr = 0

def setupMessageParser(payload):
    teamName = payload["teamName"]
    strategy = payload["strategy"]
    global t
    t = Team(teamName, strategy)
    print(t)


def commMessageParser(payload):
    t.addUnits(payload["units"])
    t.updateWorld(payload["map"])
    print(t)


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


while True:
    msg = w.receive()
    if msg is not None:
        print(f"{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}, d:{msg}")
        fromjson(msg)
        ctr += 1
    if ctr == 2:
        break
    sleep(0.05)

w.close()




