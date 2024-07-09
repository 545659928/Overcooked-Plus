import gym


rewardList = {
    "subtask finished": 10,
    "correct delivery": 200,
    "wrong delivery": -5,
    "burned": -3,
    "step penalty": -0.1,
}

presets = {
    "easy": {
        "map_name": "mapA",
        "dynamic_map": False,
        "rewardList": rewardList,
        "n_agent": 1,
        "agent_communication": False,
        "obs_radius": 2,
        "obs_mode": "vector",
        "GUI": False,
    },
    "medium": {
        "map_name": "mapB",
        "dynamic_map": False,
        "rewardList": rewardList,
        "n_agent": 1,
        "agent_communication": False,
        "obs_radius": 2,
        "obs_mode": "vector",
        "GUI": False,
    },
    "hard": {
        "map_name": "mapC",
        "dynamic_map": True,
        "rewardList": rewardList,
        "n_agent": 2,
        "agent_communication": False,
        "obs_radius": 2,
        "obs_mode": "vector",
        "GUI": False,
    },
}


def create_env(preset=None, **kwargs):
    if preset:
        config = {**presets[preset], **kwargs}
    else:
        config = kwargs
    return gym.make("Overcooked-Plus", **config)