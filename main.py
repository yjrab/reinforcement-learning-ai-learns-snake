from game import SnakeGameAI
from agent import Agent
from plotter import plot


def train():
    scores = []
    mean_scores = []
    total_score = 0
    record = 0
    game = SnakeGameAI()
    agent = Agent()

    while True:
        # get current state
        current_state = agent.get_state(game)

        # get action
        action = agent.get_action(current_state)

        # apply action and get new state
        reward, game_over, score = game.play_step(action)
        new_state = agent.get_state(game)

        # train single step
        agent.train_single_step(current_state, action, reward, new_state, game_over)

        # store in memory
        agent.store(current_state, action, reward, new_state, game_over)

        if game_over:
            # train on all past games and plot results
            game.reset()
            agent.games += 1
            agent.train_batch()

            if score > record:
                record = score
                agent.model.save()

            print(f"Game: {agent.games} - Score: {score} - Record: {record}")

            # plotting
            scores.append(score)
            total_score += score
            mean_score = total_score / agent.games
            mean_scores.append(mean_score)
            plot(scores, mean_scores)


if __name__ == "__main__":
    train()
