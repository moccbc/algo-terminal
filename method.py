from enum import Enum

class Method(str, Enum):
    GET_GAME_STATE = "getGameState"
    CLOSE = "close"
    ACCEPT_GAME = "acceptGame"
    REJECT_GAME = "rejectGame"
    MOVE_CURSOR_LEFT = "moveCursorLeft"
    MOVE_CURSOR_RIGHT = "moveCursorRight"
    GUESS_NUMBER = "guessNumber"
    UNDEFINED_SELECTION = "undefinedSelection"
    SEND = "send:"
