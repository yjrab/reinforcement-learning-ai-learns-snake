from game import SnakeGame

if __name__ == "__main__":
    game = SnakeGame()

    # game loop
    while True:
        game_over, score = game.play_step()
        if game_over:
            break

    print(f"Final Score: {score}")
