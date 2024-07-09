#!/usr/bin/python

import numpy as np


class Item(object):
    def __init__(self, pos_x, pos_y):
        self.x = pos_x
        self.y = pos_y


class MovableItem(Item):
    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y)
        self.initial_x = pos_x
        self.initial_y = pos_y

    def move(self, x, y):
        self.x = x
        self.y = y

    def refresh(self):
        self.x = self.initial_x
        self.y = self.initial_y


class Food(MovableItem):
    # 0 for unchoopped 1 for chopped
    def __init__(self, pos_x, pos_y, chopped=False, cooked=False):
        super().__init__(pos_x, pos_y)
        self.chopped = chopped
        self.cooked = cooked
        self.cur_chopped_times = 0
        self.required_chopped_times = 3
        self.cur_cooked_times = 0
        self.required_cooked_times = 0

    def refresh(self):
        self.x = self.initial_x
        self.y = self.initial_y
        self.chopped = False
        self.cooked = False
        self.cur_cooked_times = 0
        self.cur_chopped_times = 0

    @property
    def is_need_chop(self):
        if self.required_chopped_times == 0:
            return False
        else:
            return True

    @property
    def is_need_cook(self):
        if self.required_cooked_times == 0:
            return False
        else:
            return True


class Meat(Food):
    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y)
        self.required_cooked_times = 15
        self.burned = False
        self.required_burned_times = 35

    def refresh(self):
        self.x = self.initial_x
        self.y = self.initial_y
        self.chopped = False
        self.cooked = False
        self.burned = False
        self.cur_chopped_times = 0
        self.cur_cooked_times = 0


class Tomato(Food):
    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y)
        self.rawName = "tomato"

    @property
    def name(self):
        if self.chopped:
            return "ChoppedTomato"
        else:
            return "FreshTomato"


class Lettuce(Food):
    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y)
        self.rawName = "lettuce"

    @property
    def name(self):
        if self.chopped:
            return "ChoppedLettuce"
        else:
            return "FreshLettuce"


class Onion(Food):
    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y)
        self.rawName = "onion"

    @property
    def name(self):
        if self.chopped:
            return "ChoppedOnion"
        else:
            return "FreshOnion"


class Steak(Meat):
    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y)
        self.rawName = "steak"

    @property
    def name(self):
        if self.burned:
            return "burnedSteak"
        elif self.chopped and self.cooked:
            return "welldoneSteak"
        elif self.chopped:
            return "choppedSteak"
        elif self.cooked:
            return "cookedSteak"
        else:
            return "rawSteak"


class FixedItem(Item):
    def __init__(self, pos_x, pos_y, holding=None):
        super().__init__(pos_x, pos_y)
        self.holding = holding
        self.holdable_list = []
        self.lock = False

    def hold(self, item):
        if item.__class__ in self.holdable_list and not self.holding:
            self.holding = item
            item.move(self.x, self.y)
            self.lock = True
            return True
        else:
            return False

    def release(self):
        if self.holding:
            item = self.holding
            self.holding = None
            return item


class Counter(FixedItem):
    def __init__(self, pos_x, pos_y, holding=None):
        super().__init__(pos_x, pos_y, holding)
        self.rawName = "counter"

    def hold(self, item):
        self.holding = item
        item.move(self.x, self.y)
        return True

    @property
    def name(self):
        if self.holding:
            return "counter_with_" + self.holding.name
        else:
            return "counter"


class Knife(FixedItem):
    def __init__(self, pos_x, pos_y, holding=None):
        super().__init__(pos_x, pos_y, holding)
        self.rawName = "knife"
        self.holdable_list = [Tomato, Onion, Lettuce, Steak]

    def chop(self):
        if self.holding:
            item = self.holding
            if item.is_need_chop:
                item.cur_chopped_times += 1
                if item.cur_chopped_times >= item.required_chopped_times:
                    item.chopped = True
                    self.lock = False
                    return True

    def hold(self, item):
        if not item.chopped:
            return super().hold(item)
        else:
            return False

    @property
    def name(self):
        return "cutboard"


class Pan(FixedItem):
    def __init__(self, pos_x, pos_y, holding=None, burned_able=True):
        super().__init__(pos_x, pos_y, holding)
        self.rawName = "pan"
        self.holdable_list = [Steak]
        self.burned_able = True

    def cook(self):
        if self.holding:
            item = self.holding
            self.lock = True
            item.cur_cooked_times += 1
            if item.cur_cooked_times >= item.required_cooked_times:
                item.cooked = True
                self.lock = False
            if self.burned_able and item.cur_cooked_times >= item.required_burned_times:
                item.burned = True
                self.lock = False

    def hold(self, item):
        if not item.cooked or not item.burned:
            return super().hold(item)
        else:
            return False

    @property
    def name(self):
        return "pan"


class Sink(FixedItem):
    def __init__(self, pos_x, pos_y, holding=None):
        super().__init__(pos_x, pos_y, holding)
        self.rawName = "sink"
        self.holdable_list = [Plate]

    def wash(self):
        if self.holding:
            item = self.holding
            if item.dirty:
                item.cur_wash_times += 1
                if item.cur_wash_times >= item.required_wash_times:
                    item.dirty = False
                    self.lock = False

    def hold(self, item):
        if (
            item.__class__ in self.holdable_list
            and not self.holding
            and item.dirty
            and not item.containing
        ):
            self.holding = item
            item.move(self.x, self.y)
            self.lock = True
            return True
        else:
            return False

    @property
    def name(self):
        if self.holding:
            if self.holding.dirty:
                return "sink_with_dirtyplate"
            else:
                return "sink_with_plate"
        else:
            return "sink"


class Delivery(FixedItem):
    def __init__(self, pos_x, pos_y, holding=None):
        super().__init__(pos_x, pos_y, holding)
        self.holding = holding
        self.rawName = "delivery"
        self.lock = True

    def deliver(self, plate):
        if plate.__class__ == Plate:
            plate.refresh()

    @property
    def name(self):
        return "delivery"


class Plate(MovableItem):
    def __init__(self, pos_x, pos_y, containing=[], dirtyable=True):
        super().__init__(pos_x, pos_y)
        self.containing = containing
        self.rawName = "plate"
        self.dirty = False
        self.dirtyable = dirtyable
        self.cur_wash_times = 0
        self.required_wash_times = 3

    def contain(self, item):
        if not item.cooked and not item.chopped:
            return False
        if not self.dirty:
            self.containing.append(item)
            for item in self.containing:
                item.move(self.x, self.y)
            return True
        else:
            return False

    def move(self, x, y):
        super().move(x, y)
        if self.containing:
            for item in self.containing:
                item.move(x, y)

    def release(self):
        if self.containing:
            items = self.containing
            self.containing = []
            return items

    def refresh(self):
        self.x = self.initial_x
        self.y = self.initial_y
        self.containing = []
        self.dirty = self.dirtyable
        self.cur_wash_times = 0

    @property
    def name(self):
        if self.dirty:
            return "dirtyPlate"
        else:
            return "plate"

    @property
    def containedName(self):
        dishName = ""
        vegList = [Lettuce, Onion, Tomato]
        meatList = [Steak]

        contained_veg = []
        contained_meat = []
        veg_name = ""
        meat_name = ""

        for item in self.containing:
            if item.__class__ in meatList:
                contained_meat.append(item.name)
            elif item.__class__ in vegList:
                contained_veg.append(item.name)

        veg_name = "-".join(contained_veg)
        meat_name = "-".join(contained_meat)
        dishName = veg_name + "-" + meat_name

        return dishName, veg_name, meat_name


class TrashCan(FixedItem):
    def __init__(self, pos_x, pos_y, holding=None):
        super().__init__(pos_x, pos_y, holding)
        self.rawName = "trash_can"
        self.lock = True

    def throw(self, item):
        item.refresh()


class Agent(MovableItem):
    def __init__(self, pos_x, pos_y, holding=None, color=None):
        super().__init__(pos_x, pos_y)
        self.holding = holding
        self.color = color
        self.moved = False
        self.obs = None
        self.pomap = None
        self.communication = []
        self.reward = []
        self.rawName = "agent"

    def pickup(self, item):
        self.holding = item
        item.move(self.x, self.y)

    def putdown(self, x, y):
        self.holding.move(x, y)
        self.holding = None

    def move(self, x, y):
        super().move(x, y)
        self.moved = True
        if self.holding:
            self.holding.move(x, y)

    def receive(self, communication):
        self.communication.append(communication)
