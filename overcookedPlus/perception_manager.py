import numpy as np
import copy
from .items import *

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


class PerceptionManager:
    def __init__(self, obs_radius, obs_mode, mapManager, itemManager, taskManager):
        self.obs_radius = obs_radius
        self.obs_mode = obs_mode
        self.mapManager = mapManager
        self.xlen = mapManager.xlen
        self.ylen = mapManager.ylen
        self.itemList = itemManager.itemList
        self.taskManager = taskManager
        self.agent = itemManager.agent
        self.n_agent = len(self.agent)
        self._initObs()

    def _initObs(self):
        obs = []
        for item in self.itemList:
            obs.append(item.x / self.xlen)
            obs.append(item.y / self.ylen)
            if isinstance(item, Food):
                obs.append(item.cur_chopped_times / item.required_chopped_times)

        obs += self.oneHotTask
        for agent in self.agent:
            agent.obs = obs
        return [np.array(obs)] * self.n_agent

    def _get_vector_state(self):
        state = []
        for item in self.itemList:
            x = item.x / self.xlen
            y = item.y / self.ylen
            state.append(x)
            state.append(y)
            if isinstance(item, Food):
                state.append(item.cur_chopped_times / item.required_chopped_times)

        state += self.oneHotTask
        return [np.array(state)] * self.n_agent

    def _get_image_state(self):
        return [self.game.get_image_obs()] * self.n_agent

    def get_obs(self):
        """
        Returns
        -------
        obs : list
            observation for each agent.
        """

        vec_obs = self._get_vector_obs()
        if self.obs_radius > 0:
            if self.obs_mode == "vector":
                return vec_obs
            elif self.obs_mode == "image":
                return self._get_image_obs()
        else:
            if self.obs_mode == "vector":
                return self._get_vector_state()
            elif self.obs_mode == "image":
                return self._get_image_state()

    def _get_vector_obs(self):
        """
        Returns
        -------
        vector_obs : list
            vector observation for each agent.
        """

        po_obs = []

        for agent in self.agent:
            obs = []
            idx = 0

            agent.pomap = copy.deepcopy(self.mapManager.map)
            for x in range(self.xlen):
                for y in range(self.ylen):
                    if agent.pomap[x][y] == 2:
                        agent.pomap[x][y] = 0
                    elif agent.pomap[x][y] != 0:
                        agent.pomap[x][y] = 1

            for item in self.itemList:
                if item.rawName == "counter":
                    continue
                if (
                    item.x >= agent.x - self.obs_radius
                    and item.x <= agent.x + self.obs_radius
                    and item.y >= agent.y - self.obs_radius
                    and item.y <= agent.y + self.obs_radius
                    or self.obs_radius == 0
                ):
                    x = item.x / self.xlen
                    y = item.y / self.ylen
                    obs.append(x)
                    obs.append(y)
                    idx += 2
                    if isinstance(item, Food):
                        obs.append(item.cur_chopped_times / item.required_chopped_times)
                        idx += 1
                    if isinstance(item, Meat):
                        obs.append(item.cur_cooked_times / item.required_cooked_times)
                        idx += 1
                else:
                    x = agent.obs[idx] * self.xlen
                    y = agent.obs[idx + 1] * self.ylen
                    if (
                        x >= agent.x - self.obs_radius
                        and x <= agent.x + self.obs_radius
                        and y >= agent.y - self.obs_radius
                        and y <= agent.y + self.obs_radius
                    ):
                        if isinstance(item, MovableItem):
                            x = item.initial_x
                            y = item.initial_y
                        else:
                            x = item.x
                            y = item.y
                    x = x / self.xlen
                    y = y / self.ylen

                    obs.append(x)
                    obs.append(y)
                    idx += 2
                    if isinstance(item, Food):
                        obs.append(agent.obs[idx] / item.required_chopped_times)
                        idx += 1
                    if isinstance(item, Meat):
                        obs.append(agent.obs[idx] / item.required_cooked_times)
                        idx += 1

                agent.pomap[int(x * self.xlen)][int(y * self.ylen)] = ITEMIDX[
                    item.rawName
                ]
            agent.pomap[agent.x][agent.y] = ITEMIDX["agent"]
            obs += self.oneHotTask
            agent.obs = obs
            po_obs.append(np.array(obs))
        return po_obs

    def _get_image_obs(self):
        """
        Returns
        -------
        image_obs : list
            image observation for each agent.
        """

        po_obs = []
        frame = self.game.get_image_obs()
        old_image_width, old_image_height, channels = frame.shape
        new_image_width = int(
            (old_image_width / self.xlen) * (self.xlen + 2 * (self.obs_radius - 1))
        )
        new_image_height = int(
            (old_image_height / self.ylen) * (self.ylen + 2 * (self.obs_radius - 1))
        )
        color = (0, 0, 0)
        obs = np.full(
            (new_image_height, new_image_width, channels), color, dtype=np.uint8
        )

        x_center = (new_image_width - old_image_width) // 2
        y_center = (new_image_height - old_image_height) // 2

        obs[
            x_center : x_center + old_image_width,
            y_center : y_center + old_image_height,
        ] = frame

        for idx, agent in enumerate(self.agent):
            agent_obs = self._get_PO_obs(
                obs, agent.x, agent.y, old_image_width, old_image_height
            )
            po_obs.append(agent_obs)
        return po_obs

    def _get_PO_obs(self, obs, x, y, ori_width, ori_height):
        x1 = (x - 1) * int(ori_width / self.xlen)
        x2 = (x + self.obs_radius * 2) * int(ori_width / self.xlen)
        y1 = (y - 1) * int(ori_height / self.ylen)
        y2 = (y + self.obs_radius * 2) * int(ori_height / self.ylen)
        return obs[x1:x2, y1:y2]

    @property
    def oneHotTask(self):
        tasks = self.taskManager.tasks
        return [code for task in tasks for code in task["task_encoding"]]

    def reset(self):
        self._initObs()
        return self.get_obs()