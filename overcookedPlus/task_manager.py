import random
import itertools
from .constants import *



class TaskManager:
    def __init__(self, get_step_count, itemManager, n_task=2, min_ing=1, max_ing=4):
        self.get_step_count = get_step_count
        self.itemManager = itemManager
        self.n_task = n_task
        self.min_ing = min_ing
        self.max_ing = max_ing
        self.tasks = []
        self.taskpool = []
        self.inglist = []
        self.completed_tasks = []
        self.init_taskpool()
        self.replenish_task()

    def init_taskpool(self):
        # 筛选环境中可用的食材
        for key in self.itemManager.itemDic:
            if key in INGLIST and self.itemManager.itemDic[key]:
                self.inglist.append(key)

        if self.max_ing > len(self.inglist):
            self.max_ing = len(self.inglist)
        # 生成任务池
        self.generate_task_pool()

    def generate_task_pool(self):
        for r in range(self.min_ing, self.max_ing+1):
            for combination in itertools.combinations(self.inglist, r):
                task = {
                    "ingredients": combination,
                    "task_encoding": self.encode_task(combination),
                    "task_start_time": -1,
                    "task_end_time": -1,
                }
                self.taskpool.append(task)

    def encode_task(self, ingredients):
        # 独热编码逻辑
        encoding = [0] * len(INGLIST)
        for ing in ingredients:
            index = INGLIST.index(ing)
            encoding[index] = 1
        return encoding

    def display_taskpool(self):
        # 显示任务池中的所有任务
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
                self.tasks.remove(task)
                self.replenish_task()
                return True
        return False

    def replenish_task(self):
        step_count = self.get_step_count()
        add_n_task = self.n_task - len(self.tasks)
        # Ensure there are still tasks in the taskpool
        if self.taskpool:
            for _ in range(add_n_task):
                new_task = random.choice(self.taskpool)
                new_task["task_start_time"] = step_count
                self.tasks.append(new_task)

    def reset(self):
        self.tasks = []
        self.replenish_task()
        return self.tasks
