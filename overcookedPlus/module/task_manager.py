import random
import itertools
from ..constants import *


class TaskManager:
    """
    TaskManager class is responsible for managing the tasks in the environment.
    """

    def __init__(self,
                 get_step_count,
                 item_Manager,
                 n_task=2,
                 fixed_task=False,
                 task_idx=None,
                 min_ing=1,
                 max_ing=4):
        """
        Args:
            get_step_count (func): Function to get the step count of the environment.
            item_Manager (class): ItemManager class in the environment.
            n_task (int, optional): The number of tasks that can be completed simultaneously. Defaults to 2.
            fixed_task (bool, optional): Whether to enable fixed tasks. Defaults to False.
            task_idx (list, optional): The index of the task. Only valid when fixed_task is True. Defaults to None. Task list is listed in the constants.py file.
            min_ing (int, optional): The minimum number of ingredients required for each task. Defaults to 1.
            max_ing (int, optional): The maximum number of ingredients required for each task. Defaults to 4.
        """
        self.get_step_count = get_step_count
        self.item_Manager = item_Manager
        self.n_task = n_task
        self.min_ing = min_ing
        self.max_ing = max_ing
        self.fixed_task = fixed_task
        self.task_idx = task_idx
        self.tasks = []
        self.taskpool = []
        self.inglist = []
        self.completed_tasks = []
        self.init_taskpool()
        if self.task_idx:
            if not fixed_task:
                raise ValueError(
                    "task_idx is only valid when fixed_task is True.")
            self.generate_task_from_idx(self.task_idx)
        else:
            self.replenish_task()

    def init_taskpool(self):
        # Filter available ingredients in the environment
        for key in self.item_Manager.itemDic:
            if key in INGLIST and self.item_Manager.itemDic[key]:
                self.inglist.append(key)

        if self.max_ing > len(self.inglist):
            self.max_ing = len(self.inglist)
        # Generate the task pool
        self.generate_task_pool()

    def generate_task_pool(self):
        for r in range(self.min_ing, self.max_ing + 1):
            for combination in itertools.combinations(self.inglist, r):
                task = {
                    "ingredients": combination,
                    "task_encoding": self.encode_task(combination),
                    "task_start_time": -1,
                    "task_end_time": -1,
                }
                self.taskpool.append(task)

    def encode_task(self, ingredients):
        # One-hot encoding logic
        encoding = [0] * len(INGLIST)
        for ing in ingredients:
            index = INGLIST.index(ing)
            encoding[index] = 1
        return encoding

    def display_taskpool(self):
        # Display all tasks in the task pool
        for task in self.taskpool:
            print(
                f"Ingredients: {task['ingredients']}, Encoding: {task['task_encoding']}"
            )

    def check_task_completion(self, ingredients):
        step_count = self.get_step_count()
        ingredients_name = [ing.rawName for ing in ingredients]
        for task in self.tasks:
            if set(task["ingredients"]) == set(ingredients_name):
                task["task_end_time"] = step_count
                self.completed_tasks.append(task)
                if not self.fixed_task:
                    self.tasks.remove(task)
                    self.replenish_task()
                return True
        return False

    def replenish_task(self):
        if self.fixed_task:
            random.seed(42)
        step_count = self.get_step_count()
        add_n_task = self.n_task - len(self.tasks)
        # Ensure there are still tasks in the task pool
        if self.taskpool:
            for _ in range(add_n_task):
                new_task = random.choice(self.taskpool)
                new_task["task_start_time"] = step_count
                self.tasks.append(new_task)

    def generate_task_from_idx(self, idx_list):
        for idx in idx_list:
            task = {
                "ingredients": TASK_ING_LIST[idx],
                "task_encoding": self.encode_task(TASK_ING_LIST[idx]),
                "task_start_time": -1,
                "task_end_time": -1,
            }
            self.tasks.append(task)
        self.check_task_ing_in_pool()

    def check_task_ing_in_pool(self):
        for task in self.tasks:
            if task['task_encoding'] not in [
                    t['task_encoding'] for t in self.taskpool
            ]:
                raise ValueError("Task ingredients not in this map.")

    def reset(self):
        self.tasks = []
        if self.task_idx:
            self.generate_task_from_idx(self.task_idx)
        else:
            self.replenish_task()
        return self.tasks
