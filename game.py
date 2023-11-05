import pygame
import random
import numpy as np
from enum import Enum

# colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (240, 0, 0)
GREEN = (113, 212, 68)
DARKGREEN = (52, 97, 31)
# settings
BLOCK_SIZE = 20
SMALLER_BLOCK_SIZE = 18
FRAMERATE = 20
ITERATION_LIMIT = 100

# initialise pygame
pygame.init()
font = pygame.font.Font("Fonts/arial.ttf", 20)


class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4


class Coordinate:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class SnakeGameAI:
    def __init__(self, width=640, height=480):
        # initialise display
        self.width = width
        self.height = height
        self.display = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Snake")
        self.clock = pygame.time.Clock()
        # initialise clockwise direction
        self.clock_wise = [
            Direction.RIGHT,
            Direction.DOWN,
            Direction.LEFT,
            Direction.UP,
        ]
        # reset states
        self.reset()

    def reset(self):
        # initialise snake
        self.head = Coordinate(self.width / 2, self.height / 2)
        self.snake = [
            self.head,
            Coordinate(self.head.x - BLOCK_SIZE, self.head.y),
            Coordinate(self.head.x - (2 * BLOCK_SIZE), self.head.y),
        ]
        # initialise game states
        self.direction = Direction.RIGHT
        self.score = 0
        self.frame_iteration = 0
        self.food = None
        self._render_food()

    def _render_food(self):
        # render food in random position
        x = random.randint(0, (self.width - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(0, (self.height - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        self.food = Coordinate(x, y)
        # reposition food if overlaps with initial positions of snake body
        for block in self.snake:
            if self.food.x == block.x and self.food.y == block.y:
                self._render_food()

    def play_step(self, action):
        self.frame_iteration += 1
        # user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        # move snake
        self._move_head(action)
        self.snake.insert(0, self.head)
        # check game over and reward
        reward = 0
        game_over = False
        if self.collide() or self.frame_iteration > ITERATION_LIMIT * len(self.snake):
            game_over = True
            reward = -10
            pygame.quit()
            return reward, game_over, self.score
        # update food
        if self.head.x == self.food.x and self.head.y == self.food.y:
            self.score += 1
            reward = 10
            self._render_food()
        else:
            self.snake.pop()
        # update screen and clock
        self._update_screen()
        self.clock.tick(FRAMERATE)

        return reward, game_over, self.score

    def _update_screen(self):
        # reset screen
        self.display.fill(BLACK)
        # draw snake
        for block in self.snake:
            pygame.draw.rect(
                self.display,
                DARKGREEN,
                pygame.Rect(block.x, block.y, BLOCK_SIZE, BLOCK_SIZE),
            )
            pygame.draw.rect(
                self.display,
                GREEN,
                pygame.Rect(
                    block.x + (BLOCK_SIZE - SMALLER_BLOCK_SIZE) / 2,
                    block.y + (BLOCK_SIZE - SMALLER_BLOCK_SIZE) / 2,
                    SMALLER_BLOCK_SIZE,
                    SMALLER_BLOCK_SIZE,
                ),
            )
        # draw food
        pygame.draw.rect(
            self.display,
            RED,
            pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE),
        )
        # text
        text = font.render(f"Score: {self.score}", True, WHITE)
        self.display.blit(text, [3, 0])

        pygame.display.flip()

    def _move_head(self, action):
        # action in form of [straight, right, left]
        index = self.clock_wise.index(self.direction)
        if np.array_equal(action, [1, 0, 0]):
            new_index = index  # no change
        elif np.array_equal(action, [0, 1, 0]):
            new_index = (index + 1) % 4  # right turn
        else:
            new_index = (index - 1) % 4  # left turn
        new_direction = self.clock_wise[new_index]
        self.direction = new_direction

        x, y = self.head.x, self.head.y
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        self.head = Coordinate(x, y)

    def collide(self, coordinate=None):
        if coordinate is None:
            coordinate = self.head
        # hits walls
        if (
            coordinate.x > self.width - BLOCK_SIZE
            or coordinate.x < 0
            or coordinate.y > self.height - BLOCK_SIZE
            or coordinate.y < 0
        ):
            return True
        # hits itself
        for block in self.snake[1:]:
            if coordinate.x == block.x and coordinate.y == block.y:
                return True

        return False
