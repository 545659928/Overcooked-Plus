import gym
from gym import spaces
import numpy as np
from stable_baselines3 import PPO
import pygame

from overcookedPlus.utils.utils import key2action
from overcookedPlus.env_creater import create_env

env = create_env(preset="medium", n_agent=1, GUI=False)
env.reset()
done = False
model = PPO('MlpPolicy', env, verbose=1)
model.learn(total_timesteps=10000)
