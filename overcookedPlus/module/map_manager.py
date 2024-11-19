import os
import yaml
import copy
from collections import namedtuple
from ..constants import *

MapDiff = namedtuple("MapDiff", ["diff_A_to_B", "diff_B_to_A", "space_list"])


class MapManager:
    """
        The MapManager class is responsible for managing the map in the environment.
        The map configuration files are saved in the overcookedPlus/maps folder in YAML format.
        The map configuration files include information such as the size of the map, the layout of the map, dynamic objects on the map, the initial positions of agents on the map, and more.
        Additionally, the MapManager class integrates the functionality to switch maps.
    """

    def __init__(self, map_name, n_agent, dynamic_map=None):
        self.n_agent = n_agent
        self.map_config = self._load_mapconfig(map_name, self.n_agent,
                                               dynamic_map)
        self.dimensions = self.map_config["dimensions"]
        self.ylen, self.xlen = self.dimensions
        self.initMap = copy.deepcopy(self.map_config["map"])
        self.currentMap = "A"
        self.dynamic_map = self.map_config["dynamic_map"]
        if self.dynamic_map:
            self.mapA = self.map_config["map"]
            self.mapB = self.map_config["switch_map"]
            diffs = self._compute_map_diff(self.mapA, self.mapB)
            self.diff_A_to_B, self.diff_B_to_A, self.space_list = (
                diffs.diff_A_to_B,
                diffs.diff_B_to_A,
                diffs.space_list,
            )
            self.switch_flag = False
            self.cur_switch_count = 0
            self.switch_step = self.map_config["map_switch_step"]
        self.map = self._setup_agents_on_map(
            n_agent, self.initMap,
            self.map_config["agent_initial_coordinates"])
        self.currentMap = "A"

    def _load_mapconfig(self, map_name, n_agent, dynamic_map):
        file_path = os.path.join("./overcookedPlus/maps", map_name + ".yaml")
        try:
            with open(file_path, "r") as file:
                map_config = yaml.safe_load(file)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"The map configuration file {file_path} was not found.")
        except yaml.YAMLError as exc:
            raise yaml.YAMLError(f"Error parsing YAML file: {exc}")

        if n_agent > map_config["max_n_agent"]:
            raise ValueError(
                "Number of agents should be less than or equal to the maximum number of agents allowed in the map."
            )

        if dynamic_map != map_config["dynamic_map"]:
            if dynamic_map and not map_config["dynamic_map"]:
                raise ValueError("The specified map is not dynamic.")
            if dynamic_map is not None:
                map_config["dynamic_map"] = dynamic_map

        return map_config

    def _setup_agents_on_map(self, n_agent, map, coordinates):
        new_map = copy.deepcopy(map)
        for i in range(n_agent):
            new_map[coordinates[i][0]][coordinates[i][1]] = ITEMIDX["agent"]
        return new_map

    def _compute_map_diff(self, mapA, mapB):
        diff_A_to_B = []
        diff_B_to_A = []
        space_list = []
        for i in range(len(mapA)):
            for j in range(len(mapA[i])):
                if mapA[i][j] != mapB[i][j]:
                    diff_B_to_A.append((i, j, mapB[i][j]))
                    diff_A_to_B.append((i, j, mapA[i][j]))
                if mapA[i][j] == ITEMIDX["space"] and mapB[i][j] == ITEMIDX[
                        "space"]:
                    space_list.append((i, j))
        return MapDiff(diff_A_to_B, diff_B_to_A, space_list)

    def _apply_diff(self):
        if self.currentMap == "A":
            diff = self.diff_A_to_B
            self.currentMap = "B"
        elif self.currentMap == "B":
            diff = self.diff_B_to_A
            self.currentMap = "A"

        for x, y, value in diff:
            self.map[x][y] = value

        self.cur_switch_count = 0

    def _check_available(self, agent_list):
        check_count = 0
        for agent in agent_list:
            if (agent.x, agent.y) in self.space_list:
                check_count += 1

        if check_count == len(agent_list):
            self._apply_diff()
            return False
        return True

    def check_switch_map(self, agent_list):
        if not self.map_config["dynamic_map"]:
            return
        if self.switch_flag:
            self.switch_flag = self._check_available(agent_list)
        else:
            self.cur_switch_count += 1
            if self.cur_switch_count >= self.switch_step:
                self.switch_flag = True

    def reset(self):
        self.map = self._setup_agents_on_map(
            self.n_agent,
            self.initMap,
            self.map_config["agent_initial_coordinates"],
        )
        self.currentMap = "A"
        self.switch_flag = False
        self.cur_switch_count = 0
