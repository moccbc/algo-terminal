from state import *
from ui import Ui
from card import Card, CardColor
from player import Player
from message import Message
from random import randrange, shuffle

class StateData:
    def __init__(self):
        self.is_game_running = False
        self.player_name = ""
        self.is_ready = False
        self.is_turn = False
        self.is_guessing = False
        self.is_opponent_guessing = False
        self.is_guess_correct = False
        self.is_opponent_guess_correct = False
        self.input_invalid_reason = ""

    def __str__(self):
        return "StateData is_game_running: " + str(self.is_game_running) + \
                ", player_name: " + self.player_name + \
                ", is_turn: " + str(self.is_turn) + \
                ", is_guessing: " + str(self.is_guessing) + \
                ", is_guess_correct: " + str(self.is_guess_correct) + \
                ", invalid_reason: " + self.input_invalid_reason

class GameManager:
    ui = Ui()

    def __init__(self) -> None:
        self.playing = None
        self.deck = []
        self.players = {}
        self.player_states = {}
        self.state_datas = {}
        self.cursor_pos = 0
        self.playing_key = None
        self._debug_previous_player_states = {}
        self._debug_previous_state_datas = {}

    # Functions that handle state management for the game
    def get_state_for_client(self, player_key):
        state_data = self.state_datas[player_key]
        # self.debug_player_states(player_key)
        self.player_states[player_key] = self.player_states[player_key].transition_to(state_data)
        # self.debug_player_states(player_key)
        if self.is_game_ready():
            if not self.is_game_running():
                self.start_game()
                self.set_is_game_running()
        board = self.ui.get_default_board(self.player_states[player_key].get_message())
        if self.is_game_running():
            player_hand, opponent_hand = self.get_player_hands(player_key)
            opponent_hand.reverse()
            board = self.ui.get_board(
                opponent_hand, player_hand, self.player_states[player_key].get_message(), 
                self.is_player_turn(player_key), self.cursor_pos
            )
        return {
            "input_required": self.player_states[player_key].is_input_required(),
            "board": board
        }

    def draw_card(self, player_key):
        card = self.deck.pop()
        card.time = len(self.players[player_key].get_hand())
        self.players[player_key].add_to_hand(card)

    def add_player(self, player_key):
        self.player_states[player_key] = StartState()
        self.state_datas[player_key] = StateData()
        self.players[player_key] = Player("player")

    def start_game(self):
        self.initialize_deck()
        self.hand_out_cards()
        first_turn_player_key = list(self.players.keys())[randrange(2)]
        self.state_datas[first_turn_player_key].is_turn = True
        self.draw_card(first_turn_player_key)
        self.players[first_turn_player_key].look_at_opponents_hand(
            self.get_opponent(first_turn_player_key).get_hand()
        )
        self.players[first_turn_player_key].print_for_ai()

    def set_is_ready(self, player_key, is_ready):
        self.state_datas[player_key].is_ready = is_ready

    def set_is_guessing(self, player_key, is_guessing):
        self.state_datas[player_key].is_guessing = is_guessing
        self.state_datas[self.get_opponent_key(player_key)].is_opponent_guessing = is_guessing

    def set_is_guess_correct(self, player_key, is_guess_correct):
        self.state_datas[player_key].is_guess_correct = is_guess_correct
        self.state_datas[self.get_opponent_key(player_key)].is_opponent_guess_correct = is_guess_correct

    def is_game_ready(self):
        res = self.has_enough_players()
        for state_data in self.state_datas.values():
            res = (res and state_data.is_ready)
        return res

    def is_game_running(self):
        res = self.has_enough_players()
        for state_data in self.state_datas.values():
            res = (res and state_data.is_game_running)
        return res

    def set_is_game_running(self):
        for state_data in self.state_datas.values():
            state_data.is_game_running = True 

    def initialize_deck(self):
        self.deck = [
            Card(x, color, False, False) for color in CardColor for x in range(12)
        ]
        shuffle(self.deck)

    def hand_out_cards(self):
        for i in range(4):
            for player_key in self.players:
                self.draw_card(player_key) 

    def move_cursor_left(self, player_key):
        if self.cursor_pos > 0:
            self.cursor_pos -= 1

    def move_cursor_right(self, player_key):
        if self.cursor_pos < len(self.get_opponent(player_key).hand) - 1:
            self.cursor_pos += 1

    def has_enough_players(self):
        return len(self.players) == 2

    def handle_input(self, player_key, input):
        state = self.player_states[player_key]
        askUserNameStates = [AskUserNameState]
        askActionOptionStates = [AskActionOptionState, AskActionOptionAfterCorrectGuessState]
        askGuessStates = []
        input_invalid_reason = ""
        if self.is_state_same(state, AskUserNameState):
            input_invalid_reason = self.validate_username_input(input)
            if input_invalid_reason == "":
                self.players[player_key].name = input
                self.state_datas[player_key].player_name = input
                self.set_is_ready(player_key, True)
            self.state_datas[player_key].input_invalid_reason = input_invalid_reason
        elif self.is_player_turn(player_key):
            if self.is_state_same(state, AskActionOptionState):
                input_invalid_reason = self.validate_option_input(input, player_key)
                if input_invalid_reason == "":
                    chosen_option = int(input)
                    if chosen_option == 1: # Move cursor left
                        self.move_cursor_left(player_key)
                    elif chosen_option == 2: # Move cursor right
                        self.move_cursor_right(player_key)
                    elif chosen_option == 3: # Enter guessing state
                        self.set_is_guessing(player_key, True)
            elif self.is_state_same(state, AskActionOptionAfterCorrectGuessState):
                input_invalid_reason = self.validate_option_input(input, player_key)
                if input_invalid_reason == "":
                    chosen_option = int(input)
                    if chosen_option == 1: # Move cursor left
                        self.move_cursor_left(player_key)
                    elif chosen_option == 2: # Move cursor right
                        self.move_cursor_right(player_key)
                    elif chosen_option == 3: # Enter guessing state
                        self.set_is_guessing(player_key, True)
                    elif chosen_option == 4: # End turn
                        self.swap_turn(player_key)
            elif self.is_state_same(state, AskGuessState):
                input_invalid_reason = self.validate_guess_input(input)
                if input_invalid_reason == "":
                    guess = int(input)
                    if self.is_guess_correct(player_key, guess):
                        self.set_is_guess_correct(player_key, True)
                        self.reveal_opponent_card(player_key)
                    if not self.is_guess_correct(player_key, guess):
                        self.set_is_guess_correct(player_key, False)
                        self.swap_turn(player_key)
                        
                self.set_is_guessing(player_key, False)
                
        self.state_datas[player_key].input_invalid_reason = input_invalid_reason

    def swap_turn(self, player_key):
        print("Swapping turn")
        self.state_datas[player_key].is_turn = False
        self.state_datas[self.get_opponent_key(player_key)].is_turn = True
        if not self.state_datas[player_key].is_guess_correct:
            self.players[player_key].reveal_newest()
        else:
            self.state_datas[player_key].is_guess_correct = False
        self.draw_card(self.get_opponent_key(player_key))
        self.cursor_pos = 0
        player = self.get_player(player_key)
        opponent = self.get_opponent(player_key)
        self.players[player_key].look_at_opponents_hand(opponent.get_hand())
        self.players[self.get_opponent_key(player_key)].look_at_opponents_hand(player.get_hand())
        self.players[player_key].print_for_ai()

    def is_state_same(self, state, stateClass):
        return type(state) == stateClass or (type(state) == InputInvalidState and type(state.previous_state) == stateClass)

    def validate_username_input(self, input):
        banned_words = ["fuck"]
        if input == "":
            return "Name cannot be empty!"
        if input in banned_words:
            return "Name is a banned word!"
        return ""

    def validate_option_input(self, input, player_key):
        if input == "":
            return "Option cannot be empty!"
        if not input.isdigit():
            return "Option must be a number!"
        if input.isdigit() and input == "3" and self.is_opponent_card_already_revealed(player_key):
            return "Card that is not revealed must be chosen!"
        return ""

    def validate_guess_input(self, input):
        if input == "":
            return "Guess cannot be empty!"
        if not input.isdigit():
            return "Guess must be a number!"
        if input.isdigit() and not (0 <= int(input) and int(input) <= 11):
                return "Guess must be a number between 0 and 11!"
        return ""

    def is_guess_correct(self, player_key, guess):
        opponent = self.get_opponent(player_key)
        self.players[player_key].look_at_opponents_hand(opponent.get_hand())
        self.players[player_key].print_for_ai()
        opponent_hand = self.get_opponent(player_key).hand
        pos = len(opponent_hand) - self.cursor_pos - 1
        return opponent_hand[pos].number == guess

    def reveal_opponent_card(self, player_key):
        opponent_key = self.get_opponent_key(player_key)
        pos = len(self.get_opponent(player_key).hand) - self.cursor_pos - 1
        self.players[opponent_key].hand[pos].reveal()

    def is_opponent_card_already_revealed(self, player_key):
        opponent_key = self.get_opponent_key(player_key)
        pos = len(self.get_opponent(player_key).hand) - self.cursor_pos - 1
        return self.players[opponent_key].hand[pos].is_revealed

    # Functions that extracts stuff from the state
    def get_player(self, player_key):
        return self.players[player_key]

    def get_opponent(self, player_key):
        return self.players[self.get_opponent_key(player_key)]

    def get_opponent_key(self, player_key):
        return list(filter(lambda key: not key == player_key, list(self.players.keys())))[0]

    def is_player_turn(self, player_key):
        return self.state_datas[player_key].is_turn

    def get_player_hands(self, player_key):
        player = self.get_player(player_key)
        opponent = self.get_opponent(player_key)
        return player.get_hand(), opponent.get_hand()

    # Debug functions
    def debug_player_states(self, player_key):
        current_state = type(self.player_states[player_key])
        current_state_data = str(self.state_datas[player_key])
        if not player_key in self._debug_previous_player_states:
            print(self.state_datas[player_key].player_name)
            print(current_state)
            print(current_state_data)
            print()
            self._debug_previous_player_states[player_key] = self.player_states[player_key]
            self._debug_previous_state_datas[player_key] = self.state_datas[player_key]
        else:
            previous_state = type(self._debug_previous_player_states[player_key])
            previous_state_data = str(self._debug_previous_state_datas[player_key])
            if previous_state != current_state or current_state_data != previous_state_data:
                print(self.state_datas[player_key].player_name)
                print("Previous")
                print(previous_state)
                print(previous_state_data)
                print("Current")
                print(current_state)
                print(current_state_data)
                print()
                self._debug_previous_player_states[player_key] = self.player_states[player_key]
                self._debug_previous_state_datas[player_key] = self.state_datas[player_key]

