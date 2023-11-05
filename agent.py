import random
import torch
import numpy as np
from collections import deque
from game import Direction, Coordinate
from model import Linear_QNet, QTrainer

BLOCK_SIZE = 20
MAX_MEMORY = 100_000
STATES = 11
ACTIONS = 3
# hyperparameters
HIDDEN_LAYER_SIZE = 256
BATCH_SIZE = 1000
LEARNING_RATE = 0.001
GAMMA = 0.9  # discount rate
EXPLORATION_NUMBER = 100


class Agent:
    def __init__(self):
        self.games = 0
        self.epsilon = 0  # randomness for exploration
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = Linear_QNet(STATES, HIDDEN_LAYER_SIZE, ACTIONS)
        self.trainer = QTrainer(self.model, LEARNING_RATE, GAMMA)

    def get_state(self, game):
        head = game.snake[0]
        # surroundings
        surrounding_right = Coordinate(head.x + BLOCK_SIZE, head.y)
        surrounding_left = Coordinate(head.x - BLOCK_SIZE, head.y)
        surrounding_up = Coordinate(head.x, head.y - BLOCK_SIZE)
        surrounding_down = Coordinate(head.x, head.y + BLOCK_SIZE)
        # direction
        direction_right = game.direction == Direction.RIGHT
        direction_left = game.direction == Direction.LEFT
        direction_up = game.direction == Direction.UP
        direction_down = game.direction == Direction.DOWN
        # 11 states for detecting near dangers (3), current direction (4), and food placement (4)
        state = [
            # Danger Straight
            (direction_right and game.is_collision(surrounding_right))
            or (direction_left and game.is_collision(surrounding_left))
            or (direction_up and game.is_collision(surrounding_up))
            or (direction_down and game.is_collision(surrounding_down)),
            # Danger Right
            (direction_right and game.is_collision(surrounding_down))
            or (direction_left and game.is_collision(surrounding_up))
            or (direction_up and game.is_collision(surrounding_right))
            or (direction_down and game.is_collision(surrounding_left)),
            # Danger left
            (direction_right and game.is_collision(surrounding_up))
            or (direction_left and game.is_collision(surrounding_down))
            or (direction_up and game.is_collision(surrounding_left))
            or (direction_down and game.is_collision(surrounding_right)),
            # Directions
            direction_right,
            direction_left,
            direction_up,
            direction_down,
            # Food Placement
            game.food.x > game.head.x,  # food right
            game.food.x < game.head.x,  # food left
            game.food.y < game.head.y,  # food up
            game.food.y > game.head.y,  # food down
        ]
        # convert booleans to integers 0 or 1
        return np.array(state, dtype=int)

    def store(self, state, action, reward, next_state, game_over):
        # memory pops from left side if MAX_MEMORY limit is reached
        self.memory.append((state, action, reward, next_state, game_over))

    def train_single_step(self, state, action, reward, next_state, game_over):
        self.trainer.train_step(state, action, reward, next_state, game_over)

    def train_batch(self):
        if len(self.memory) > BATCH_SIZE:
            sample = random.sample(self.memory, BATCH_SIZE)  # returns list of tuples
        else:
            sample = self.memory

        states, actions, rewards, next_steps, game_overs = zip(*sample)
        self.trainer.train_step(states, actions, rewards, next_steps, game_overs)

    def get_action(self, state):
        # use epsilon for exploration vs exploitation (explore environment vs greedy behaviour)
        # perform random moves for exploring the environment at the beginning
        # as number of games increases the epsilon decreases thus exploration decreases
        self.epsilon = EXPLORATION_NUMBER - self.games
        action = [0, 0, 0]
        if self.epsilon < random.randint(0, 2 * EXPLORATION_NUMBER):
            move = random.randint(0, 2)
            action[move] = 1
        else:
            state = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state)
            move = torch.argmax(prediction).item()
            action[move] = 1

        return action
