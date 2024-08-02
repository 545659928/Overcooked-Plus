import pygame
import gym
import numpy as np
import matplotlib.pyplot as plt
from overcookedPlus.env_creater import create_env
from overcookedPlus.utils.utils import key2action

env = create_env(preset="medium", n_agent=1, GUI_enable=True)

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

plt.figure()
plt.title("Reward Curve")
plt.xlabel("Steps")
plt.ylabel("Reward")
for agent in env.agent:
    plt.plot(agent.reward, label=f"Agent {agent.color}")
plt.legend()
plt.show()
