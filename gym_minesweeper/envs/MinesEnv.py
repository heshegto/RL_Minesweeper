import gymnasium
from gymnasium import spaces
import pygame
import numpy as np


class MinesweeperGame(gymnasium.Env):
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 8}

    def __init__(self, render_mode=None, height=5, width=5, mines=5) -> None:
        self.height, self.width, self.mines = height, width, mines

        self.terminated = False

        # creating player's desk
        self.playerDesk = [[-2 for _ in range(self.width)] for _ in range(self.height)]

        # creating game desk
        self.desk = [[0 for _ in range(self.width)] for _ in range(self.height)]

        # Counting window size
        self.cell_size = 15
        self.window_height =

        # Observations are dictionaries with the agent's and the target's location.
        # Each location is encoded as an element of {0, ..., `size`}^2, i.e. MultiDiscrete([size, size]).
        self.observation_space = spaces.Dict(
            {
                "Desk": spaces.Box(-2, 8, shape=(self.height, self.width)),
            }
        )

        self.action_space = spaces.MultiDiscrete([self.height, self.width])

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode

        """
        If human-rendering is used, `self.window` will be a reference
        to the window that we draw to. `self.clock` will be a clock that is used
        to ensure that the environment is rendered at the correct framerate in
        human-mode. They will remain `None` until human-mode is used for the
        first time.
        """
        self.window = None
        self.clock = None

    def _get_obs(self):
        return {"Desk": self.playerDesk}

    def _get_info(self):
        return {"Opened desk": self.desk}

    def reset(self, seed=None, options=None):
        """Creating game desk, with mines, that player doesn't see, and player's desk on which he plays"""

        super().reset(seed=seed)  # We need the following line to seed self.np_random
        self.terminated = False
        self.playerDesk = [[-2 for _ in range(self.width)] for _ in range(self.height)]
        self.desk = [[0 for _ in range(self.width)] for _ in range(self.height)]

        # putting mines randomly
        count = 0
        while count < self.mines:
            i = int(self.np_random.integers(0, self.height, size=1, dtype=int))
            j = int(self.np_random.integers(0, self.width, size=1, dtype=int))
            if self.desk[i][j] != 0:
                continue
            self.desk[i][j] = -1
            count += 1

        # counting how many mines are around each cell
        for i in range(self.height):
            for j in range(self.width):
                if self.desk[i][j] != -1:
                    self.desk[i][j] = self.__get_mines_around(i, j)

        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame()

        return observation, info

    def __get_mines_around(self, x: int, y: int) -> int:
        amount = 0
        for x_ in range(-1, 2):
            for y_ in range(-1, 2):
                x_neighbor = x + x_
                y_neighbor = y + y_
                if x_neighbor in range(self.height) and y_neighbor in range(self.width):
                    if self.desk[x_neighbor][y_neighbor] == -1:
                        amount += 1
        return amount

    def step(self, action):
        """Make move on player's desk"""

        x, y = int(action[0]), int(action[1])
        if x not in range(self.height) or y not in range(self.width):
            raise Exception("Coordinates are out of range")

        if self.playerDesk[x][y] != -2:
            raise Exception("This cell is already opened")

        if self.terminated:
            raise Exception("Game over. Start new one")

        self.playerDesk[x][y] = self.desk[x][y]

        if self.desk[x][y] == 0:
            for x_ in range(-1, 2):
                for y_ in range(-1, 2):
                    x_neighbor = x + x_
                    y_neighbor = y + y_
                    if x_neighbor in range(self.height) and y_neighbor in range(self.width):
                        if self.playerDesk[x_neighbor][y_neighbor] == -2:
                            self.step([x_neighbor, y_neighbor])

        reward = 0
        if self.desk[x][y] == -1:
            self.terminated = True
            reward = -3
            print("You lose")

        is_end = True
        for i in range(self.height):
            for j in range(self.width):
                if self.playerDesk[i][j] == -2 and self.desk[i][j] >= 0:
                    is_end = False
                    reward = 1

        if is_end:
            self.terminated = True
            reward = 5
            print("You win")

        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame()

        return observation, reward, self.terminated, False, info

    def render(self):
        if self.render_mode == "rgb_array":
            return self._render_frame()

    def _render_frame(self):
        if self.window is None and self.render_mode == "human":
            pygame.init()
            pygame.display.init()
            self.window = pygame.display.set_mode((self.window_size, self.window_size))
        if self.clock is None and self.render_mode == "human":
            self.clock = pygame.time.Clock()

        canvas = pygame.Surface((self.window_size, self.window_size))
        canvas.fill((255, 255, 255))
        pix_square_size = (
            self.window_size / max(self.height, self.width)
        )  # The size of a single grid square in pixels

        # Finally, add some gridlines
        for x in range(max(self.height, self.width) + 1):
            pygame.draw.line(
                canvas,
                0,
                (0, pix_square_size * x),
                (self.window_size, pix_square_size * x),
                width=3,
            )
            pygame.draw.line(
                canvas,
                0,
                (pix_square_size * x, 0),
                (pix_square_size * x, self.window_size),
                width=3,
            )

        font = pygame.font.Font(None, 100)

        # def draw_digit(digit, xs, y):
        #     digit_text = str(digit)
        #     text_surface = font.render(digit_text,True, (255, 255, 255))
        #     canvas.blit(text_surface, xs, y)
        #
        # for i in range(self.height):
        #     for j in range(self.width):
        #         draw_digit(self.playerDesk[i][j], (0.5 + i) * pix_square_size, (0.5 + j) * pix_square_size)

        if self.render_mode == "human":
            # The following line copies our drawings from `canvas` to the visible window
            self.window.blit(canvas, canvas.get_rect())
            pygame.event.pump()
            pygame.display.update()

            # We need to ensure that human-rendering occurs at the predefined framerate.
            # The following line will automatically add a delay to keep the framerate stable.
            self.clock.tick(self.metadata["render_fps"])
        else:  # rgb_array
            return np.transpose(
                np.array(pygame.surfarray.pixels3d(canvas)), axes=(1, 0, 2)
            )

    def close(self):
        if self.window is not None:
            pygame.display.quit()
            pygame.quit()

    def __str__(self):
        return f"Minesweeper Game for desk: {self.desk}"