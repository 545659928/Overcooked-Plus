import numpy as np
from queue import PriorityQueue
from gym import spaces
from ..items import Tomato, Onion, Lettuce, Plate, Knife, Delivery, Agent, Food
from .overcooked_LLMA_V3 import Overcooked_LLMA_V3
from .mac_agent import MacAgent
import random
import copy

DIRECTION = [(0, 1), (1, 0), (0, -1), (-1, 0)]
ITEMNAME = [
    "space",
    "counter",
    "agent",
    "tomato",
    "lettuce",
    "plate",
    "knife",
    "delivery",
    "onion",
]
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
}
AGENTCOLOR = ["blue", "magenta", "green", "yellow"]
ACTIONIDX = {"right": 0, "down": 1, "left": 2, "up": 3, "stay": 4}
PRIMITIVEACTION = ["right", "down", "left", "up", "stay"]


class AStarAgent(object):
    def __init__(self, x, y, g, dis, action, history_action, pass_agent):
        """
        Parameters
        ----------
        x : int
            X position of the agent.
        y : int
            Y position of the agent.
        g : int
            Cost of the path from the start node to n.
        dis : int
            Distance of the current path.
            g + h
        pass_agent : int
            Whether there is other agent in the path.
        """

        self.x = x
        self.y = y
        self.g = g
        self.dis = dis
        self.action = action
        self.history_action = history_action
        self.pass_agent = pass_agent

    def __lt__(self, other):
        if self.dis != other.dis:
            return self.dis <= other.dis
        else:
            return self.pass_agent <= other.pass_agent


class Overcooked_DynaLLMA_V3(Overcooked_LLMA_V3):
    """
    Overcooked Domain Description
    ------------------------------
    ITEMNAME = ["space", "counter", "agent", "tomato", "lettuce", "plate", "knife", "delivery", "onion"]
    map_type = ["A", "B", "C"]

    Only macro-action is available in this env.
    Macro-actions in map A:
    ["stay", "get tomato", "get lettuce", "get onion", "get plate 1", "get plate 2", "go to knife 1", "go to knife 2", "deliver", "chop"]
    Macro-actions in map B/C:
    ["stay", "get tomato", "get lettuce", "get onion", "get plate 1", "get plate 2", "go to knife 1", "go to knife 2", "deliver", "chop", "go to counter"]

    1) Agent is allowed to pick up/put down food/plate on the counter;
    2) Agent is allowed to chop food into pieces if the food is on the cutting board counter;
    3) Agent is allowed to deliver food to the delivery counter;
    4) Only unchopped food is allowed to be chopped;
    """

    def __init__(
        self,
        preset,
        map_type,
        grid_dim,
        task,
        rewardList,
        map_type="A",
        map_switch_count=5,
        n_agent=2,
        obs_radius=2,
        mode="vector",
        debug=False,
    ):
        """
        Parameters
        ----------
        gird_dim : tuple(int, int)
            The size of the grid world([7, 7]/[9, 9]).
        task : int
            The index of the target recipe.
        rewardList : dictionary
            The list of the reward.
            e.g rewardList = {"subtask finished": 10, "correct delivery": 200, "wrong delivery": -5, "step penalty": -0.1}
        map_type : str
            The type of the map(A/B/C).
        n_agent: int
            The number of the agents.
        obs_radius: int
            The radius of the agents.
        mode: string
            The type of the observation(vector/image).
        debug : bool
            Whehter print the debug information.
        """

        super().__init__(
            grid_dim, task, rewardList, map_type, n_agent, obs_radius, mode, debug
        )

        if map_type == "Dynamic":
            if self.xlen == 7 and self.ylen == 7:
                dynamic_mapA = [
                    [1, 1, 1, 1, 1, 3, 1],
                    [1, 0, 1, 0, 0, 0, 4],
                    [1, 0, 1, 0, 0, 0, 8],
                    [7, 0, 1, 6, 1, 6, 1],
                    [1, 0, 0, 0, 0, 0, 1],
                    [1, 0, 0, 0, 0, 0, 5],
                    [1, 1, 1, 1, 1, 5, 1],
                ]
                dynamic_mapB = [
                    [1, 1, 1, 1, 1, 3, 1],
                    [1, 0, 2, 0, 0, 0, 4],
                    [1, 0, 0, 0, 0, 0, 8],
                    [7, 0, 1, 6, 1, 6, 1],
                    [1, 0, 1, 0, 0, 0, 1],
                    [1, 0, 1, 0, 0, 0, 5],
                    [1, 1, 1, 1, 1, 5, 1],
                ]
                initcoords = [(1, 1), (5, 1), (1, 5), (5, 5)]
                self.counterSequence = [3, 2, 4, 1, 5]
            if self.xlen == 9 and self.ylen == 9:
                dynamic_mapA = [
                    [1, 1, 1, 1, 1, 1, 1, 3, 1],
                    [1, 0, 0, 1, 0, 0, 0, 0, 4],
                    [1, 0, 0, 1, 0, 0, 0, 0, 8],
                    [7, 0, 0, 1, 0, 0, 0, 0, 1],
                    [1, 0, 0, 1, 1, 6, 1, 6, 1],
                    [1, 0, 0, 0, 0, 0, 0, 0, 1],
                    [1, 0, 0, 0, 0, 0, 0, 0, 1],
                    [1, 0, 0, 0, 0, 0, 0, 0, 1],
                    [1, 1, 1, 1, 1, 1, 1, 5, 1],
                ]
                dynamic_mapB = [
                    [1, 1, 1, 1, 1, 1, 1, 3, 1],
                    [1, 0, 0, 0, 0, 0, 0, 0, 4],
                    [1, 0, 0, 0, 0, 0, 0, 0, 8],
                    [7, 0, 0, 0, 0, 0, 0, 0, 1],
                    [1, 0, 0, 1, 1, 6, 1, 6, 1],
                    [1, 0, 0, 1, 0, 0, 0, 0, 1],
                    [1, 0, 0, 1, 0, 0, 0, 0, 1],
                    [1, 0, 0, 1, 0, 0, 0, 0, 1],
                    [1, 1, 1, 1, 1, 1, 1, 5, 1],
                ]
                initcoords = [(1, 1), (7, 1), (1, 7), (7, 7)]
                self.counterSequence = [4, 3, 5, 2, 6, 1, 7]
            self.diff_A_to_B, self.diff_B_to_A, self.space_list = (
                self._compute_map_diff(dynamic_mapA, dynamic_mapB)
            )
            self.initMap = dynamic_mapA
            self.curerntMap = "A"
            self.map = self._setup_agents_on_map(self.initMap, initcoords)
            self.map_switch_count = map_switch_count
            self.map_change = False

    def _setup_agents_on_map(self, map, initcoords):
        new_map = copy.deepcopy(map)
        for i in range(self.n_agent):
            new_map[initcoords[i][0]][initcoords[i][1]] = ITEMIDX["agent"]
        return new_map

    def _compute_map_diff(self, mapA, mapB):
        diff_A_to_B = []
        diff_B_to_A = []
        space_list = []
        for i in range(len(mapA)):
            for j in range(len(mapA[i])):
                if mapA[i][j] != mapB[i][j]:
                    if mapA[i][j] == 0:
                        diff_B_to_A.append((i, j, mapB[i][j]))
                    if mapB[i][j] == 0:
                        diff_A_to_B.append((i, j, mapA[i][j]))
                if mapA[i][j] == 0 and mapB[i][j] == 0:
                    space_list.append((i, j))
        return diff_A_to_B, diff_B_to_A, space_list

    def _apply_diff(self):
        if self.curerntMap == "A":
            diff = self.diff_A_to_B
            self.curerntMap == "B"
        elif self.curerntMap == "B":
            diff = self.diff_B_to_A
            self.curerntMap == "A"
        for x, y, value in diff:
            self.map[x][y] = value

    def _check_switch_map(self):
        check_count = 0
        for agent in self.agents:
            if (agent.x, agent.y) in self.space_list:
                check_count += 1
        return check_count == len(self.agents)

    def step(self, action):
        result = super().step(action)
        if self.map_type == "Dynamic":
            if self.map_change:
                self._apply_diff()
                self.map_change = False
            else:
                if self.env_step % self.map_switch_count == 0 and self.env_step != 0:
                    self.map_change = self._check_switch_map()
        return result
