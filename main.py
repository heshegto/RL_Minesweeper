# importing the shit
import gym_minesweeper
import gymnasium as gym
from gymnasium.utils.env_checker import check_env
# Load Environment
env = gym.make('MinesweeperGame', render_mode="human")
check_env(env)

# episodes = 5
# for episode in range(episodes):
#     state = env.reset()
#     done = False
#     score = 0
#     while not done:
#         env.render()
#         action = env.action_space.sample()
#         n_state, reward, done, kek, info = env.step(action)
#         score += reward
#     print('Episode:{} Score:{}'.format(episode+1, score))
# env.close()
