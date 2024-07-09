import pygame
import gym
import numpy as np
from overcookedPlus.env_creater import create_env
from overcookedPlus.utils.utils import key2action

rewardList = {
    "subtask finished": 10,
    "correct delivery": 200,
    "wrong delivery": -5,
    "step penalty": -0.1,
    "burned penalty": -2,
}

env = create_env(preset="medium", n_agent=1, GUI=True)

done = False
obs = env.reset()

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.KEYDOWN:
            key = pygame.key.name(event.key)
            print(f"Key: {key}")
            action = key2action(key)
            if action is not None:
                new_obs, reward, done, info = env.step([action])
                print(f"Reward: {reward}, Done: {done}, Info: {info}")
                obs = new_obs

pygame.quit()
