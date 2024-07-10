import gym
import numpy as np
from .render.game import Game
from gym import spaces
from .items import *
from .constants import *
from .map_manager import MapManager
from .item_manager import ItemManager
from .event_manager import EventManager
from .perception_manager import PerceptionManager
from .task_manager import TaskManager


class OvercookedPlus(gym.Env):
    """
    Overcooked Domain Description
    ------------------------------
    Agent with primitive actions ["right", "down", "left", "up"]

    1) Agent is allowed to pick up/put down food/plate on the counter;
    2) Agent is allowed to chop food into pieces if the food is on the cutting board counter;
    3) Agent is allowed to deliver food to the delivery counter;
    4) Only unchopped food is allowed to be chopped;
    """

    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 60}

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
        fixed_task=False,
        agent_communication=False,
        GUI=False,
        human_player=False,
        min_ing=1,
        max_ing=4,
    ):
        """
        Args:
            rewardList (list): Custom reward function in the format:
                rewardList = {
                    "subtask finished": 10,
                    "correct delivery": 200,
                    "wrong delivery": -5,
                    "step penalty": -0.1,
                    "burned penalty": -2,
                }
            n_agent (int): The specified number of agents, which cannot exceed the map configuration limit.
            n_task (int, optional): The number of tasks that can be completed simultaneously. Defaults to 2.
            map_name (str, optional): The name of the map configuration file, which exists in the maps/ folder in YAML format. Defaults to "mapC".
            obs_radius (int, optional): Observation radius, 0 for full observability. Defaults to 2.
            obs_mode (str, optional): Observation mode, options are "vector" or "image". Defaults to "vector".
            debug (bool, optional): For development debugging purposes. Defaults to False.
            dynamic_map (bool, optional): Whether to enable dynamic maps (requires support from the map configuration file). Defaults to None.
            fixed_task (bool, optional): Whether to enable fixed tasks. Defaults to False.
            agent_communication (bool, optional): Whether to enable communication between agents. Defaults to False.
            GUI (bool, optional): Whether to enable GUI display. Defaults to False.
            human_player (bool, optional): Whether to enable human players. Defaults to False.
            min_ing (int, optional): The minimum number of ingredients required for each task. Defaults to 1.
            max_ing (int, optional): The maximum number of ingredients required for each task. Defaults to 4.
        
        Returns:
            OvercookedPlus object
        """
        self.rewardList = rewardList
        self.debug = debug
        self.n_agent = n_agent
        self.obs_mode = obs_mode
        self.obs_radius = obs_radius
        self.GUI = GUI
        self.human_player = human_player
        self.n_task = n_task
        self.fixed_task = fixed_task

        self.env_step = 0
        self.total_return = 0
        self.discount = 1
        self.agent_communication = agent_communication

        self.map_Manager = MapManager(map_name, n_agent, dynamic_map)
        self.xlen, self.ylen = self.map_Manager.dimensions
        self.item_Manager = ItemManager(self.map_Manager)
        self.task_Manager = TaskManager(self.get_step_count, self.item_Manager,
                                        self.n_task, self.fixed_task, min_ing,
                                        max_ing)
        self.event_Manager = EventManager(
            self.item_Manager,
            self.map_Manager,
            self.task_Manager,
            rewardList,
        )
        self.game = Game(self)
        self.game
        self.preception_Manager = PerceptionManager(obs_radius, obs_mode,
                                                    self.map_Manager,
                                                    self.item_Manager,
                                                    self.task_Manager,
                                                    self.game)

        # action: move(up, down, left, right), stay
        self.action_space = spaces.Discrete(5)

        # Observation: agent(pos[x,y]) dim = 2
        #    knife(pos[x,y]) dim = 2
        #    delivery (pos[x,y]) dim = 2
        #    plate(pos[x,y]) dim = 2
        #    food(pos[x,y]/status) dim = 3
        self.observation_space = spaces.Box(low=0,
                                            high=1,
                                            shape=(len(self.get_obs()), ),
                                            dtype=np.float32)

    def get_obs(self):
        if self.n_agent == 1:
            return self.preception_Manager.get_obs()[0]
        else:
            return self.preception_Manager.get_obs()

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
        return self.map_Manager.map

    @property
    def tasks(self):
        return self.task_Manager.tasks

    @property
    def agent(self):
        return self.item_Manager.agent

    def get_step_count(self):
        return self.env_step

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
        self.map_Manager.reset()
        self.item_Manager.reset()
        self.task_Manager.reset()
        self.preception_Manager.reset()

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
        #if isinstance(action, int):
        #    action = [action]

        done = False
        info = {}
        info["cur_mac"] = action
        info["mac_done"] = [True] * self.n_agent

        all_action_done = False

        for agent in self.agent:
            agent.moved = False

        # if self.debug:
        #     print("in overcooked primitive actions:", action)

        while not all_action_done:
            self.event_Manager.process_action(agent, action)

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

        if self.map_Manager.dynamic_map == True:
            self.map_Manager.check_switch_map(self.agent)

        if self.GUI:
            self.render()

        reward_list = [agent.reward[-1] for agent in self.agent]
        if self.n_agent == 1:
            return self.get_obs(), reward_list[0], done, info
        else:
            return self.get_obs(), reward_list, done, info

    def render(self, mode="human"):
        return self.game.on_render()
