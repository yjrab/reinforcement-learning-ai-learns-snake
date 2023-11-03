import pygame
import random
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


class SnakeGame:
    def __init__(self, width=640, height=480):
        # initialise display
        self.width = width
        self.height = height
        self.display = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Snake")
        self.clock = pygame.time.Clock()
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

    def play_step(self):
        # user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT and self.direction != Direction.LEFT:
                    self.direction = Direction.RIGHT
                elif event.key == pygame.K_LEFT and self.direction != Direction.RIGHT:
                    self.direction = Direction.LEFT
                elif event.key == pygame.K_UP and self.direction != Direction.DOWN:
                    self.direction = Direction.UP
                elif event.key == pygame.K_DOWN and self.direction != Direction.UP:
                    self.direction = Direction.DOWN
        # move snake
        self._move_head(self.direction)
        self.snake.insert(0, self.head)
        # check game over
        game_over = False
        if self._collide():
            game_over = True
            pygame.quit()
            return game_over, self.score
        # update food
        if self.head.x == self.food.x and self.head.y == self.food.y:
            self.score += 1
            self._render_food()
        else:
            self.snake.pop()
        # update screen and clock
        self._update_screen()
        self.clock.tick(FRAMERATE)

        return game_over, self.score

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

    def _move_head(self, direction):
        x, y = self.head.x, self.head.y
        if direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif direction == Direction.UP:
            y -= BLOCK_SIZE
        elif direction == Direction.DOWN:
            y += BLOCK_SIZE
        self.head = Coordinate(x, y)

    def _collide(self):
        # hits walls
        if (
            self.head.x > self.width - BLOCK_SIZE
            or self.head.x < 0
            or self.head.y > self.height - BLOCK_SIZE
            or self.head.y < 0
        ):
            return True
        # hits itself
        for block in self.snake[1:]:
            if self.head.x == block.x and self.head.y == block.y:
                return True

        return False
