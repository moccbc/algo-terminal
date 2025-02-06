from enum import Enum

class Message(str, Enum):
    ASK_FOR_USER_NAME = "What is your name?"
    WELCOME = "Welcome "
    WAIT_FOR_GAME_START = "Waiting for game to start."
    WAITING_FOR_MORE_PLAYERS = "Waiting for another player to join."
    ASK_FOR_ACTION = "Enter number to take the action:"
    OPTION_1 = "1: Move cursor left"
    OPTION_2 = "2: Move cursor right"
    OPTION_3 = "3: Guess number"
    OPTION_4 = "4: Quit turn"
    ASK_FOR_GUESS = "Enter your guess."

    INVALID_INPUT = "Invalid input: "

    WAITING_FOR_OPPONENT = "Waiting for opponent to choose a card."
    WAITING_FOR_OPPONENT_TO_GUESS = "Waiting for opponent to guess a number."
    OPPONENT_GUESSED_CORRECTLY = "Opponent has guessed correctly!"
    OPPONENT_CONTINUING_TURN = "They are continuing their turn."

    WAITING_FOR_PLAYERS_ACCEPTANCE = "Asking everyone if they want to play."
    IN_GAME = "In game:"
    YOU_HAVE_ACCEPTED = "You have accepted!"
    WAITING_FOR_OTHER_PLAYER_ACCEPTANCE = "Asking if the other player wants to play."
