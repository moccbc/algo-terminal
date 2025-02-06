from __future__ import annotations
from abc import ABC, abstractmethod
from message import Message

class PlayerState(ABC):
    @abstractmethod
    def is_input_required(self):
        pass

    @abstractmethod
    def get_message(self):
        pass

    @abstractmethod
    def transition_to(self, state_data) -> PlayerState:
        pass

class StartState(PlayerState):
    def is_input_required(self):
        return False

    def get_message(self):
        return ["This should not be shown"]

    def transition_to(self, state_data):
        return AskUserNameState()

class AskUserNameState(PlayerState):
    def is_input_required(self):
        return True

    def get_message(self):
        return [Message.ASK_FOR_USER_NAME]

    def transition_to(self, state_data):
        next_state = AskUserNameState()
        if not state_data.input_invalid_reason == "":
            next_state = InputInvalidState(self, state_data.input_invalid_reason)
        elif state_data.input_invalid_reason == "":
            next_state = WaitForGameToStart(state_data.player_name)
            if state_data.is_game_running:
                if state_data.is_turn:
                    next_state = AskActionOptionState()
                else:
                    next_state = WaitForOpponentToMakeChoiceState()

        return next_state

class WaitForGameToStart(PlayerState):
    def __init__(self, player_name):
        self.player_name = player_name

    def is_input_required(self):
        return False

    def get_message(self):
        return [Message.WELCOME+self.player_name+"!", Message.WAIT_FOR_GAME_START]

    def transition_to(self, state_data):
        next_state = WaitForGameToStart(self.player_name)
        if state_data.is_game_running:
            if state_data.is_turn:
                next_state = AskActionOptionState()
            else:
                next_state = WaitForOpponentToMakeChoiceState()

        return next_state

class AskActionOptionState(PlayerState):
    def is_input_required(self):
        return True

    def get_message(self):
        return [Message.ASK_FOR_ACTION, Message.OPTION_1, Message.OPTION_2, Message.OPTION_3]

    def transition_to(self, state_data):
        next_state = AskActionOptionState()
        if not state_data.input_invalid_reason == "":
            next_state = InputInvalidState(self, state_data.input_invalid_reason)
        elif state_data.input_invalid_reason == "" and state_data.is_guessing:
            next_state = AskGuessState()

        return next_state

class AskActionOptionAfterCorrectGuessState(PlayerState):
    def is_input_required(self):
        return True

    def get_message(self):
        return [
            Message.ASK_FOR_ACTION, Message.OPTION_1, 
            Message.OPTION_2, Message.OPTION_3, Message.OPTION_4
        ]

    def transition_to(self, state_data):
        next_state = AskActionOptionAfterCorrectGuessState()
        if not state_data.input_invalid_reason == "":
            next_state = InputInvalidState(self, state_data.input_invalid_reason)
        elif state_data.input_invalid_reason == "":
            if state_data.is_turn and state_data.is_guessing:
                next_state = AskGuessState()
            elif not state_data.is_turn: # A player can quit their turn after they guess correctly
                next_state = WaitForOpponentToMakeChoiceState()

        return next_state

class AskGuessState(PlayerState):
    def is_input_required(self):
        return True

    def get_message(self):
        return [Message.ASK_FOR_GUESS]

    def transition_to(self, state_data):
        next_state = AskGuessState()
        if not state_data.input_invalid_reason == "":
            next_state = InputInvalidState(AskActionOptionState(), state_data.input_invalid_reason)
        else:
            if state_data.is_guess_correct:
                next_state = AskActionOptionAfterCorrectGuessState()            
            else:
                next_state = WaitForOpponentToMakeChoiceState()

        return next_state

class WaitForOpponentToMakeChoiceState(PlayerState):
    def is_input_required(self):
        return False

    def get_message(self):
        return [Message.WAITING_FOR_OPPONENT]

    def transition_to(self, state_data):
        next_state = WaitForOpponentToMakeChoiceState()
        if state_data.is_turn:
            next_state = AskActionOptionState()
        elif state_data.is_opponent_guessing:
            next_state = WaitForOpponentToGuessState()

        return next_state

class WaitForOpponentToMakeChoiceAfterCorrectGuessState(PlayerState):
    def is_input_required(self):
        return False

    def get_message(self):
        return [Message.OPPONENT_GUESSED_CORRECTLY, Message.OPPONENT_CONTINUING_TURN, Message.WAITING_FOR_OPPONENT]

    def transition_to(self, state_data):
        next_state = WaitForOpponentToMakeChoiceAfterCorrectGuessState()
        if state_data.is_turn: # Turn has swapped
            next_state = AskActionOptionState()
        elif state_data.is_guessing:
            next_state = WaitForOpponentToGuessState()

        return next_state

class WaitForOpponentToGuessState(PlayerState):
    def is_input_required(self):
        return False

    def get_message(self):
        return [Message.WAITING_FOR_OPPONENT_TO_GUESS]

    def transition_to(self, state_data):
        next_state = WaitForOpponentToGuessState()
        if state_data.is_turn:
            next_state = AskActionOptionState()
        elif not state_data.is_opponent_guessing:
            if state_data.is_opponent_guess_correct:
                next_state = WaitForOpponentToMakeChoiceAfterCorrectGuessState()
            else:
                next_state = WaitForOpponentToMakeChoiceState()

        return next_state

class InputInvalidState(PlayerState):
    def __init__(self, previous_state, input_invalid_reason):
        self.input_invalid_reason = input_invalid_reason
        self.previous_state = previous_state

    def is_input_required(self):
        return self.previous_state.is_input_required()

    def get_message(self):
        message = self.previous_state.get_message()
        message.insert(0, self.input_invalid_reason)
        return message

    def transition_to(self, state_data):
        return self.previous_state.transition_to(state_data)

