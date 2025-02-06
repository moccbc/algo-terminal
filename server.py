import sys
import socket
from threading import Thread, Lock
import json
from method import Method
from game import GameManager
import traceback

CLIENT_NAME_KEY = "client_name"
CLIENT_SOCKET_KEY = "client_socket"
CLIENT_ADDRESS_KEY = "client_address"
GAME_ID_KEY = "game_id"

lock = Lock()
class Server:
    Clients = []
    Games = {} # Mapping of int: game_id to a game instance

    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((host, port))
        self.socket.listen()
        self.clients_connected_count = 0;
        print(f"Listening on {(host, port)}")

    def listen(self):
        while True:
            client_socket, address = self.socket.accept()
            print("Accepted connection from: " + str(address))
            self.clients_connected_count += 1
            game_id = self.get_open_game_room_id()

            client = {
                CLIENT_SOCKET_KEY: client_socket,
                CLIENT_ADDRESS_KEY: address,
                GAME_ID_KEY: game_id 
            }

            if game_id not in Server.Games:
                Server.Games[game_id] = GameManager()
            Server.Games[game_id].add_player(address)
            Server.Clients.append(client)
            print("Number of active games:", len(Server.Games))

            Thread(target = self.client_thread, args = (client,)).start()

    def send(self, socket, state):
        serialized_state = json.dumps(state)
        socket.send(serialized_state.encode())

    def get_open_game_room_id(self):
        # If there are no games at all
        if len(Server.Games) == 0:
            return 0

        # First check to see if there are any single player rooms.
        smallest_non_existing_id = 0
        for game_id, game in Server.Games.items():
            if smallest_non_existing_id == game_id:
                smallest_non_existing_id += 1
            if not game.has_enough_players():
                return game_id

        # All rooms have 2 players, so a new room must be created.
        return smallest_non_existing_id

    # This function should not react to the game state. It is just passing information between the
    # client(s) and the Game instance. The Game instance is the one that will decide on what the
    # current state is.
    # Listens to requests coming in from the client and decides what to respond 
    # with based on it.
    def client_thread(self, client):
        client_socket = client[CLIENT_SOCKET_KEY]
        client_address = client[CLIENT_ADDRESS_KEY]
        game_id = client[GAME_ID_KEY]
        print("Started thread for", client[CLIENT_ADDRESS_KEY])
        try:
            while True:
                encoded_requested_method = client_socket.recv(30)
                if not encoded_requested_method:
                    break
                requested_method = encoded_requested_method.decode()

                if requested_method == Method.GET_GAME_STATE:
                    state = self.get_game_state(client)
                    self.send(client_socket, state)
                elif Method.SEND in requested_method:
                    input = ''.join(requested_method[len(Method.SEND):])
                    #print(input)
                    with lock:
                        Server.Games[game_id].handle_input(client_address, input)
                    self.send(client_socket, "Completed")

        except Exception as err:
            print("Unexpected exception!:", err)
            print(traceback.format_exc())
            self.close_client(client)

        #if not exception:
        #    self.close_client(client)

    def get_game_state(self, client):
        with lock:
            game_id = client[GAME_ID_KEY]
            client_address = client[CLIENT_ADDRESS_KEY]
            return Server.Games[game_id].get_state_for_client(client_address)

    def close_client(self, client):
        client_socket = client[CLIENT_SOCKET_KEY]
        client_address = client[CLIENT_ADDRESS_KEY]
        game_id = client[GAME_ID_KEY]
        Server.Games[game_id].remove_player(client_socket)
        if Server.Games[game_id].has_no_players():
            del Server.Games[game_id]
        else:
            Server.Games[game_id].reset()
        print("Closing socket to:", client_address)
        print("Number of active games:", len(Server.Games))
        client_socket.close()
        Server.Clients.remove(client)
        self.clients_connected_count -= 1


host, port = sys.argv[1], int(sys.argv[2])
try:
    server = Server(host, port)
    server.listen()
except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
