from .item_manager import *

# 盘子从水槽里拿不出来 #拿着盘子没法从砧板里拿出来
DIRECTION = [(0, 1), (1, 0), (0, -1), (-1, 0)]
ITEMIDX = {
    "space": 0,
    "counter": 1,
    "agent": 2,
    "tomato": 3,
    "lettuce": 4,
    "plate": 5,
    "knife": 6,
    "delivery": 7,
    "onion": 8,
    "pan": 9,
    "steak": 10,
    "sink": 11,
    "trash_can": 12,
}
AGENTCOLOR = ["blue", "magenta", "green", "yellow"]

TASKLIST = [
    "tomato salad",
    "lettuce salad",
    "onion salad",
    "lettuce-tomato salad",
    "onion-tomato salad",
    "lettuce-onion salad",
    "lettuce-onion-tomato salad",
    "steak",
    "steak with lettuce",
    "steak with tomato",
    "steak with onion",
    "steak with lettuce and tomato",
    "steak with lettuce and onion",
    "steak with tomato and onion",
    "steak with lettuce and tomato and onion",
]


class EventManager:
    def __init__(self, itemManager, mapManager, taskManager, rewardList):
        self.itemManager = itemManager
        self.mapManager = mapManager
        self.rewardList = rewardList
        self.taskManager = taskManager

    def process_action(self, agent, action):
        for idx, agent in enumerate(self.itemManager.agent):
            agent_action = action[idx]
            if agent.moved:
                continue
            agent.moved = True

            agent.reward.append(self.rewardList["step penalty"])

            if agent_action < 4:
                target_x, target_y = self.calculate_target_position(agent, agent_action)
                target_name = list(ITEMIDX.keys())[
                    self.mapManager.map[target_x][target_y]
                ]

                if target_name == "space":
                    self.move_agent(agent, target_x, target_y)
                elif target_name == "agent":
                    self.handle_agent_collision(agent, target_x, target_y, action)
                else:
                    target = self.itemManager.findItem(target_x, target_y, target_name)
                    if target:
                        self.process_interaction(agent, target)

        for pan in self.itemManager.pan:
            if pan.holding:
                temp_state = [pan.holding.cooked, pan.holding.burned]
                pan.cook()
                new_state = [pan.holding.cooked, pan.holding.burned]
                if temp_state[0] != new_state[0]:
                    for agent in self.itemManager.agent:
                        agent.reward[-1] += self.rewardList["subtask finished"]
                if temp_state[1] != new_state[1]:
                    for agent in self.itemManager.agent:
                        agent.reward[-1] += self.rewardList["burned penalty"]

    def calculate_target_position(self, agent, action):
        dx, dy = DIRECTION[action]
        return agent.x + dx, agent.y + dy

    def handle_agent_collision(self, agent, target_x, target_y, action):
        target_agent = self.itemManager.findItem(target_x, target_y, "agent")
        if not target_agent.moved:
            agent.moved = False
            target_action = action[AGENTCOLOR.index(target_agent.color)]
            if target_action < 4:
                new_target_agent_x = target_agent.x + DIRECTION[target_action][0]
                new_target_agent_y = target_agent.y + DIRECTION[target_action][1]
                if new_target_agent_x == agent.x and new_target_agent_y == agent.y:
                    target_agent.move(new_target_agent_x, new_target_agent_y)
                    agent.move(target_x, target_y)
                    agent.moved = True
                    target_agent.moved = True

    def move_agent(self, agent, target_x, target_y):
        # Update map and agent position
        self.mapManager.map[agent.x][agent.y] = ITEMIDX["space"]
        agent.move(target_x, target_y)
        self.mapManager.map[target_x][target_y] = ITEMIDX["agent"]

    def process_interaction(self, agent, target):
        if not agent.holding:
            if target.rawName == "counter":
                return
            if isinstance(target, MovableItem):
                self.process_pickup(agent, target)
            elif isinstance(target, FixedItem):
                if target.lock == False and target.holding:
                    self.process_pickup(agent, target)
                else:
                    return self.process_usage(agent, target)
        elif agent.holding:
            if agent.holding.rawName == "plate":
                if target.rawName == "delivery":
                    self.process_deliver(agent, target)
                elif target.rawName == "trash_can":
                    self.process_dump(agent, target)
                elif target.rawName == "counter" or target.rawName == "sink":
                    self.process_putdown(agent, target)
                else:
                    self.process_pickup_into_plate(agent, target)
            else:
                if target.rawName == "trash_can":
                    self.process_dump(agent, target)
                elif isinstance(target, FixedItem) or target.rawName == "plate":
                    self.process_putdown(agent, target)

    def process_usage(self, agent, target):
        if target.rawName == "knife":
            self.process_chop(agent, target)
        elif target.rawName == "sink":
            self.process_wash(agent, target)

    def process_putdown(self, agent, target):
        if target.rawName == "counter":
            self.mapManager.map[target.x][target.y] = ITEMIDX[agent.holding.rawName]

        if target.rawName == "plate":
            if target.contain(agent.holding):
                agent.putdown(target.x, target.y)
        else:
            if target.hold(agent.holding):
                agent.putdown(target.x, target.y)

    def process_pickup(self, agent, target):
        if isinstance(target, MovableItem):
            self.mapManager.map[target.x][target.y] = ITEMIDX["counter"]
            agent.pickup(target)
        else:
            if target.lock == False:
                item = target.release()
                agent.pickup(item)

    def process_dump(self, agent, target):
        if agent.holding.rawName == "plate":
            items = agent.holding.containing
            items.append(agent.holding)
        else:
            items = [agent.holding]

        for item in items:
            item.refresh()
            self.mapManager.map[item.x][item.y] = ITEMIDX[item.rawName]
            agent.holding = None

    def process_pickup_into_plate(self, agent, target):
        plate = agent.holding
        x, y = target.x, target.y
        if isinstance(target, MovableItem) and target != plate:
            if plate.contain(target):
                self.mapManager.map[x][y] = ITEMIDX["counter"]
        else:
            if target.lock == False and not plate.dirty:
                item = target.release()
                if item:
                    plate.contain(item)

    def process_chop(self, agent, target):
        if target.chop():
            agent.reward[-1] = self.rewardList["subtask finished"]

    def process_wash(self, agent, target):
        if target.wash():
            agent.reward[-1] = self.rewardList["subtask finished"]

    def process_deliver(self, agent, target):
        plate = agent.holding
        if plate.containing:
            if self.taskManager.check_task_completion(plate.containing):
                self.process_dump(agent, target)
                agent.reward[-1] = self.rewardList["correct delivery"]
            else:
                self.process_dump(agent, target)
                agent.reward[-1] = self.rewardList["wrong delivery"]
        else:
            self.process_dump(agent, target)
            agent.reward[-1] = self.rewardList["wrong delivery"]

    def apply_item_change_on_map(self, x, y, item):
        new_value = ITEMIDX[item.rawName]
        old_value = self.mapManager.map[x][y]

        self.mapManager.map[x][y] = new_value
