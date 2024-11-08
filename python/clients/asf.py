from time import sleep

from Team import Team
from Wrapper import Wrapper


def setupMessageParser(payload):
    global t
    t = Team(payload["teamName"],
             payload["strategy"],
             payload["mapSize"],
             save=False)
    print(f"setup: {t}")


def commMessageParser(payload):
    t.addUnits(payload["units"])
    t.updateWorld(payload["map"])
    w.send(t.doAction())
    t.clear()


def endMessageParser(payload):
    print(payload)
    if payload:
        t.saveGame()
    w.close()
    exit()


def handleMessage(x):
    match x["type"]:
        case "setupMessage":
            setupMessageParser(x["payload"])
        case "commMessage":
            commMessageParser(x["payload"])
        case "endMessage":
            endMessageParser(x["payload"])


w = Wrapper()


def main():
    ctr = 0
    while True:
        msg = w.receive(False)
        if msg is not None:
            ctr += 1
            # print(f"----------------inter:{ctr}----------------")
            handleMessage(msg)
        if ctr == 200:
            print("max inter reached")
            break
        # sleep(0.1)

    w.close()


if __name__ == "__main__":
    main()
