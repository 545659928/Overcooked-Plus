from ..items import *
from ..constants import *


class ItemManager:
    """
    ItemManager class is responsible for managing all items in the environment.
    """

    def __init__(self, map_Manager):
        self.itemList = {}
        self.map_Manager = map_Manager
        self.init_items(self.map_Manager)

    def init_items(self, map_Manager):
        map = map_Manager.map
        self.xlen = map_Manager.xlen
        self.ylen = map_Manager.ylen
        self.agent = []
        self.knife = []
        self.delivery = []
        self.tomato = []
        self.lettuce = []
        self.onion = []
        self.plate = []
        self.pan = []
        self.steak = []
        self.sink = []
        self.trash_can = []
        self.itemList = []
        self.block = []
        self.counter = []
        agent_idx = 0
        for x in range(self.xlen):
            for y in range(self.ylen):
                if map[x][y] == ITEMIDX["agent"]:
                    self.agent.append(Agent(x, y, color=AGENTCOLOR[agent_idx]))
                    agent_idx += 1
                elif map[x][y] == ITEMIDX["knife"]:
                    self.knife.append(Knife(x, y))
                elif map[x][y] == ITEMIDX["delivery"]:
                    self.delivery.append(Delivery(x, y))
                elif map[x][y] == ITEMIDX["tomato"]:
                    self.tomato.append(Tomato(x, y))
                elif map[x][y] == ITEMIDX["lettuce"]:
                    self.lettuce.append(Lettuce(x, y))
                elif map[x][y] == ITEMIDX["onion"]:
                    self.onion.append(Onion(x, y))
                elif map[x][y] == ITEMIDX["plate"]:
                    self.plate.append(Plate(x, y))
                elif map[x][y] == ITEMIDX["pan"]:
                    self.pan.append(Pan(x, y))
                elif map[x][y] == ITEMIDX["steak"]:
                    self.steak.append(Steak(x, y))
                elif map[x][y] == ITEMIDX["sink"]:
                    self.sink.append(Sink(x, y))
                elif map[x][y] == ITEMIDX["trash_can"]:
                    self.trash_can.append(TrashCan(x, y))
                elif map[x][y] == ITEMIDX["block"]:
                    self.trash_can.append(Block(x, y))

                if map[x][y] != ITEMIDX["space"] and map[x][y] != ITEMIDX[
                        "block"]:
                    self.counter.append(Counter(x, y))

        self.itemDic = {
            "tomato": self.tomato,
            "lettuce": self.lettuce,
            "onion": self.onion,
            "plate": self.plate,
            "knife": self.knife,
            "delivery": self.delivery,
            "agent": self.agent,
            "pan": self.pan,
            "steak": self.steak,
            "sink": self.sink,
            "trash_can": self.trash_can,
            "counter": self.counter,
            "block": self.block,
        }

        if not self.sink:
            for plate in self.plate:
                plate.dirtyable = False

        if not self.trash_can:
            for steak in self.steak:
                steak.burnable = False

        for key in self.itemDic:
            self.itemList += self.itemDic[key]
        pass

    def findItem(self, x, y, itemName):
        for item in self.itemDic[itemName]:
            if item.x == x and item.y == y:
                return item
        return None

    def reset(self):
        self.init_items(self.map_Manager)
        pass
