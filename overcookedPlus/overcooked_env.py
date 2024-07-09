import gym
import numpy as np
from .render.game import Game
from gym import spaces
from .items import *
from .map_manager import MapManager
from .item_manager import ItemManager
from .event_manager import EventManager
from .perception_manager import PerceptionManager
from .task_manager import TaskManager

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
    "pan",
    "steak",
    "sink",
    "trash_can",
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
    "pan": 9,
    "steak": 10,
    "sink": 11,
    "trash_can": 12,
}
AGENTCOLOR = ["blue", "magenta", "green", "yellow"]


class Overcooked_Plus(gym.Env):
    """
    Overcooked Domain Description
    ------------------------------
    Agent with primitive actions ["right", "down", "left", "up"]

    1) Agent is allowed to pick up/put down food/plate on the counter;
    2) Agent is allowed to chop food into pieces if the food is on the cutting board counter;
    3) Agent is allowed to deliver food to the delivery counter;
    4) Only unchopped food is allowed to be chopped;
    """

    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 5}

    def __init__(
        self,
        rewardList,
        n_agent,
        n_task=2,
        map_name="mapC",
        obs_radius=2,
        obs_mode="vector",
        debug=False,
        dynamic_map=None,
        agent_communication=False,
        GUI=False,
        human_player=False,
    ):
        self.rewardList = rewardList
        self.debug = debug
        self.n_agent = n_agent
        self.obs_mode = obs_mode
        self.obs_radius = obs_radius
        self.GUI = GUI
        self.human_player = human_player

        self.env_step = 0
        self.total_return = 0
        self.discount = 1
        self.agent_communication = agent_communication

        self.mapManager = MapManager(map_name, n_agent, dynamic_map)
        self.xlen, self.ylen = self.mapManager.dimensions
        self.itemManager = ItemManager(self.mapManager)
        self.taskManager = TaskManager(self.itemManager, n_task)
        self.eventManager = EventManager(
            self.itemManager,
            self.mapManager,
            self.taskManager,
            rewardList,
        )
        self.preceptionManager = PerceptionManager(
            obs_radius, obs_mode, self.mapManager, self.itemManager, self.taskManager
        )

        # action: move(up, down, left, right), stay
        self.action_space = spaces.Discrete(5)

        # Observation: agent(pos[x,y]) dim = 2
        #    knife(pos[x,y]) dim = 2
        #    delivery (pos[x,y]) dim = 2
        #    plate(pos[x,y]) dim = 2
        #    food(pos[x,y]/status) dim = 3
        self.observation_space = spaces.Box(
            low=0, high=1, shape=(len(self.get_obs()[0]),), dtype=np.float32
        )
        self._getItems()
        if debug or GUI:
            self.game = Game(self)

    def get_obs(self):
        return self.preceptionManager.get_obs()

    @property
    def state_size(self):
        return self.get_state().shape[0]

    @property
    def obs_size(self):
        return [self.observation_space.shape[0]] * self.n_agent

    @property
    def n_action(self):
        return [a.n for a in self.action_spaces]

    @property
    def action_spaces(self):
        return [self.action_space] * self.n_agent

    @property
    def map(self):
        return self.mapManager.map

    @property
    def tasks(self):
        return self.taskManager.tasks

    def _getItems(self):
        self.agent = self.itemManager.agent
        self.knife = self.itemManager.knife
        self.delivery = self.itemManager.delivery
        self.tomato = self.itemManager.tomato
        self.lettuce = self.itemManager.lettuce
        self.onion = self.itemManager.onion
        self.plate = self.itemManager.plate
        self.pan = self.itemManager.pan
        self.steak = self.itemManager.steak
        self.sink = self.itemManager.sink
        self.trash_can = self.itemManager.trash_can
        self.itemList = self.itemManager.itemList
        self.itemDic = self.itemManager.itemDic

    def get_avail_actions(self):
        return [self.get_avail_agent_actions(i) for i in range(self.n_agent)]

    def get_avail_agent_actions(self, nth):
        return [1] * self.action_spaces[nth].n

    def action_space_sample(self, i):
        return np.random.randint(self.action_spaces[i].n)

    def reset(self):
        """
        Returns
        -------
        obs : list
            observation for each agent.
        """
        self.total_return = 0
        self.env_step = 0
        self.discount = 1
        self.mapManager.reset()
        self.itemManager.reset()
        self.taskManager.reset()
        self.preceptionManager.reset()
        self._getItems()

        if self.debug:
            self.game.on_cleanup()

        if self.GUI:
            self.render()
        return self.get_obs()

    def step(self, action):
        """
        Parameters
        ----------
        action: list
            action for each agent
        Returns
        -------
        obs : list
            observation for each agent.
        rewards : list
            reward for each agent.
        terminate : list
        info : dictionary
        """
        done = False
        info = {}
        info["cur_mac"] = action
        info["mac_done"] = [True] * self.n_agent
        info["collision"] = []

        all_action_done = False

        for agent in self.agent:
            agent.moved = False

        # if self.debug:
        #     print("in overcooked primitive actions:", action)

        while not all_action_done:
            self.eventManager.process_action(agent, action)

            all_action_done = True
            for agent in self.agent:
                if agent.moved == False:
                    all_action_done = False

        self.env_step += 1
        self.discount *= 0.99
        done = True if self.env_step >= 200 else done
        if done:
            episode_info = {
                "r": self.total_return,
                "l": self.env_step,
            }
            info["episode"] = episode_info

        if self.mapManager.dynamic_map == True:
            self.mapManager.check_switch_map(self.agent)

        if self.GUI:
            self.render()

        return self.get_obs(), [agent.reward[-1] for agent in self.agent], done, info

    def render(self, mode="human"):
        return self.game.on_render()
