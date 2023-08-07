from gymnasium.envs.registration import register

register(
     id="MinesweeperGame",
     entry_point="gym_minesweeper.envs:MinesweeperGame",
     max_episode_steps=300,
)