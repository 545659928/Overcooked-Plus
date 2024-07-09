import random
import itertools

# 初始食材列表
INGLIST = ["tomato", "lettuce", "onion", "steak"]


class TaskManager:
    def __init__(self, itemManager, n_task=2, min_ing=1, max_ing=4):
        self.itemManager = itemManager
        self.n_task = n_task
        self.min_ing = min_ing
        self.max_ing = max_ing
        self.tasks = []
        self.taskpool = []
        self.inglist = []
        self.init_taskpool()
        self.create_tasks()

    def init_taskpool(self):
        # 筛选环境中可用的食材
        for key in self.itemManager.itemDic:
            if key in INGLIST:
                self.inglist.append(key)

        if self.max_ing > len(self.inglist):
            self.max_ing = len(self.inglist)
        # 生成任务池
        self.generate_task_pool()

    def generate_task_pool(self):
        for r in range(self.min_ing, self.max_ing):
            for combination in itertools.combinations(self.inglist, r):
                task = {
                    "ingredients": combination,
                    "task_encoding": self.encode_task(combination),
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

    def create_tasks(self):
        # 从任务池中随机选取n个任务
        self.tasks = random.sample(self.taskpool, self.n_task)
        return self.tasks

    def replenish_task(self):
        # Ensure there are still tasks in the taskpool
        if self.taskpool:
            new_task = random.choice(self.taskpool)
            self.tasks.append(new_task)

    def reset(self):
        self.create_tasks()
        return self.tasks
