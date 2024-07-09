class FSM:
    def __init__(self):
        self.state = "idle"
        self.task = None
        self.task_steps = []
        self.current_step = 0
        self.ingredient_map = {
            "tomato": "has_tomato",
            "lettuce": "has_lettuce",
            "onion": "has_onion",
            "steak": "has_steak"
        }

    def set_task(self, task):
        self.task = task
        self.task_steps = self.get_task_steps(task)
        self.current_step = 0

    def get_task_steps(self, task):
        ingredients = task.split(" ")
        steps = []

        if "steak" in ingredients:
            ingredients.remove("steak")
            steps.append("collect_steak")
            steps.append("cook_steak")

        for ingredient in ingredients:
            if ingredient in self.ingredient_map:
                steps.append(f"collect_{ingredient}")

        if ingredients:
            steps.append("cut_ingredients")

        steps.append("serve")

        return steps

    def update_state(self, game_state):
        if self.current_step >= len(self.task_steps):
            self.state = "idle"
            return
        
        next_action = self.task_steps[self.current_step]

        if next_action.startswith("collect_") and not game_state[self.ingredient_map[next_action.split("_")[1]]]:
            self.state = next_action
        elif next_action == "cut_ingredients" and all(game_state[self.ingredient_map[ing]] for ing in self.ingredient_map if f"collect_{ing}" in self.task_steps):
            self.state = "cut_ingredients"
        elif next_action == "cook_steak" and game_state["has_steak"]:
            self.state = "cook_steak"
        elif next_action == "serve":
            self.state = "serve"
        else:
            self.state = "idle"

    def next_step(self):
        if self.current_step < len(self.task_steps):
            self.current_step += 1

    def perform_action(self, game_state):
        action = self.state
        if self.state in ["collect_tomato", "collect_lettuce", "collect_onion", "collect_steak", "cut_ingredients", "cook_steak", "serve"]:
            self.next_step()
        return action

# 示例游戏状态
game_state = {
    "has_tomato": False,
    "has_lettuce": False,
    "has_onion": False,
    "has_steak": False
}

# 创建FSM并设置任务
fsm = FSM()
fsm.set_task("steak with lettuce and tomato and onion")

# 更新和执行状态
fsm.update_state(game_state)
action = fsm.perform_action(game_state)
print(f"Action: {action}")  # Collect steak

# 更新游戏状态以模拟任务进展
game_state["has_steak"] = True
fsm.update_state(game_state)
action = fsm.perform_action(game_state)
print(f"Action: {action}")  # Cook steak

game_state["has_tomato"] = True
game_state["has_lettuce"] = True
game_state["has_onion"] = True
fsm.update_state(game_state)
action = fsm.perform_action(game_state)
print(f"Action: {action}")  # Cut ingredients

game_state["has_tomato"] = False  # Simulate cutting vegetables
game_state["has_lettuce"] = False
game_state["has_onion"] = False
fsm.update_state(game_state)
action = fsm.perform_action(game_state)
print(f"Action: {action}")  # Serve
