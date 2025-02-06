import socket
from threading import Thread
import os
import sys
import json
from method import Method

GAME_IS_READY_KEY = "is_ready"
GAME_HAS_ENOUGH_PLAYERS_KEY = "has_enough_players"
GAME_BOARD_KEY = "board"
GAME_IS_PLAYER_TURN_KEY = "is_player_turn"
GAME_GUESSING_KEY = "guessing"
GAME_INPUT_REQUIRED_KEY = "input_required"

# TODO: Add functionality for rejecting game
class Client:
  
    def __init__(self, HOST, PORT):
        self.socket = socket.socket()
        self.socket.connect((HOST, PORT))
        self.board = ""
        
        try:
            self.client_loop()
            self.send(Method.CLOSE)
            print("close")
        except Exception as err:
            self.send(Method.CLOSE)
            print(f"Unexpected {err=}, {type(err)=}")

    def client_loop(self):
        while True:
            state = self.get_game_state()
            self.print_board(state[GAME_BOARD_KEY])
            if state[GAME_INPUT_REQUIRED_KEY]:
                user_input = self.get_user_input()
                self.send_input(user_input)

    def get_game_state(self):
        self.send(Method.GET_GAME_STATE)
        return self.receive()

    def send_input(self, input):
        input_to_send = Method.SEND+input
        self.socket.send(input_to_send.encode())
        res = self.receive()
        #print(res)

    def get_user_input(self):
        return input("Enter input here: ")

    def send(self, message):
        self.socket.send(message.encode())

    def print_board(self, new_board, force=False):
        if new_board != "" and (force or self.board != new_board):
            self.board = new_board
            print(self.board)

    def receive(self):
        return json.loads(self.socket.recv(1024*11).decode())

    def close_connection(self):
        self.socket.close()
      
host, port = sys.argv[1], int(sys.argv[2])
try:
    Client(host, port)
except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
