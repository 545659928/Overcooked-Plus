from .item_manager import *
from .constants import *


class EventManager:
    """
    EventManager class is responsible for processing the actions of the agents in the environment.
    """

    def __init__(self, item_Manager, map_Manager, task_Manager, rewardList):
        self.item_Manager = item_Manager
        self.map_Manager = map_Manager
        self.rewardList = rewardList
        self.task_Manager = task_Manager
        self.reverse_itemidx = {v: k for k, v in ITEMIDX.items()}

    def process_action(self, agent, action):
        if not isinstance(action, list):
            action = [action]
        for idx, agent in enumerate(self.item_Manager.agent):
            agent_action = action[idx]
            if agent.moved:
                continue
            agent.moved = True

            agent.reward.append(self.rewardList["step penalty"])

            if agent_action < 4:
                target_x, target_y = self.calculate_target_position(
                    agent, agent_action)
                target_name = self.reverse_itemidx.get(
                    self.map_Manager.map[target_x][target_y])

                if target_name == "space":
                    self.move_agent(agent, target_x, target_y)
                elif target_name == "agent":
                    self.handle_agent_collision(agent, target_x, target_y,
                                                action)
                else:
                    target = self.item_Manager.findItem(
                        target_x, target_y, target_name)
                    if target:
                        self.process_interaction(agent, target)

        for pan in self.item_Manager.pan:
            if pan.holding:
                temp_state = [pan.holding.cooked, pan.holding.burned]
                pan.cook()
                new_state = [pan.holding.cooked, pan.holding.burned]
                if temp_state[0] != new_state[0]:
                    for agent in self.item_Manager.agent:
                        agent.reward[-1] += self.rewardList["subtask finished"]
                if temp_state[1] != new_state[1]:
                    for agent in self.item_Manager.agent:
                        agent.reward[-1] += self.rewardList["burned penalty"]

    def calculate_target_position(self, agent, action):
        dx, dy = DIRECTION[action]
        return agent.x + dx, agent.y + dy

    def handle_agent_collision(self, agent, target_x, target_y, action):
        target_agent = self.item_Manager.findItem(target_x, target_y, "agent")
        if not target_agent.moved:
            agent.moved = False
            target_action = action[AGENTCOLOR.index(target_agent.color)]
            if target_action < 4:
                new_target_agent_x = target_agent.x + DIRECTION[target_action][
                    0]
                new_target_agent_y = target_agent.y + DIRECTION[target_action][
                    1]
                if new_target_agent_x == agent.x and new_target_agent_y == agent.y:
                    target_agent.move(new_target_agent_x, new_target_agent_y)
                    agent.move(target_x, target_y)
                    agent.moved = True
                    target_agent.moved = True

    def move_agent(self, agent, target_x, target_y):
        # Update map and agent position
        self.map_Manager.map[agent.x][agent.y] = ITEMIDX["space"]
        agent.move(target_x, target_y)
        self.map_Manager.map[target_x][target_y] = ITEMIDX["agent"]

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
                elif isinstance(target,
                                FixedItem) or target.rawName == "plate":
                    self.process_putdown(agent, target)

    def process_usage(self, agent, target):
        if target.rawName == "knife":
            self.process_chop(agent, target)
        elif target.rawName == "sink":
            self.process_wash(agent, target)

    def process_putdown(self, agent, target):
        if target.rawName == "counter":
            self.map_Manager.map[target.x][target.y] = ITEMIDX[
                agent.holding.rawName]

        if target.rawName == "plate":
            if target.contain(agent.holding):
                agent.putdown(target.x, target.y)
        else:
            if target.hold(agent.holding):
                agent.putdown(target.x, target.y)

    def process_pickup(self, agent, target):
        if isinstance(target, MovableItem):
            self.map_Manager.map[target.x][target.y] = ITEMIDX["counter"]
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
            self.map_Manager.map[item.x][item.y] = ITEMIDX[item.rawName]
            agent.holding = None

    def process_pickup_into_plate(self, agent, target):
        plate = agent.holding
        x, y = target.x, target.y
        if isinstance(target, MovableItem) and target != plate:
            if plate.contain(target):
                self.map_Manager.map[x][y] = ITEMIDX["counter"]
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
            if self.task_Manager.check_task_completion(plate.containing):
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
        old_value = self.map_Manager.map[x][y]

        self.map_Manager.map[x][y] = new_value
