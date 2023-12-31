from gymnasium import spaces, Env
import pygame
import numpy as np

class MinesweeperGame(Env):
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
        self.window_height = self.cell_size * self.height
        self.window_width = self.cell_size * self.width

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
                    self.desk[i][j] = self._get_mines_around(i, j)

        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self.render()

        return observation, info

    def _get_mines_around(self, x: int, y: int) -> int:
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
        reward = 0

        x, y = int(action[0]), int(action[1])
        if x not in range(self.height) or y not in range(self.width):
            raise Exception("Coordinates are out of range")

        if self.playerDesk[x][y] != -2:
            reward = -1
            print("This cell is already opened")

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

        if self.desk[x][y] == -1:
            self.terminated = True
            reward = -5
            print("You lose")

        is_end = True
        for i in range(self.height):
            for j in range(self.width):
                if self.playerDesk[i][j] == -2 and self.desk[i][j] >= 0:
                    is_end = False
                    reward = 1

        if is_end:
            self.terminated = True
            reward = 10
            print("You win")

        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self.render()

        return observation, reward, self.terminated, False, info

    def render(self):
        pygame.init()
        # Creating display
        if self.window is None and self.render_mode == "human":
            pygame.display.init()
            self.window = pygame.display.set_mode((self.window_width, self.window_height))
        if self.clock is None and self.render_mode == "human":
            self.clock = pygame.time.Clock()

        # Creating blank canvas
        canvas = pygame.Surface((self.window_width, self.window_height))
        canvas.fill((255, 255, 255))

        # Add some gridlines to canvas
        for x in range(self.width + 1):
            pygame.draw.line(
                canvas,
                0,
                (self.cell_size * x, 0),
                (self.cell_size * x, self.window_height),
                width=2,
            )
        for x in range(self.height + 1):
            pygame.draw.line(
                canvas,
                0,
                (0, self.cell_size * x),
                (self.window_width, self.cell_size * x),
                width=2,
            )

        # Printing result of step on canvas
        font = pygame.font.Font(None, 20)

        def draw_digit(digit, xs, y):
            digit_text = str(digit)
            text_surface = font.render(digit_text, True, (0, 0, 0))
            canvas.blit(text_surface, (xs, y))

        for i in range(self.height):
            for j in range(self.width):
                if self.playerDesk[i][j] == -1:
                    draw_digit('B', (0.1 + i) * self.cell_size, (0.1 + j) * self.cell_size)
                elif self.playerDesk[i][j] != -2:
                    draw_digit(self.playerDesk[i][j], (0.1 + i) * self.cell_size, (0.1 + j) * self.cell_size)

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


