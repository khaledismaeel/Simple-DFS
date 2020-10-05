import os
import socket
from threading import Thread
import json

class ClientHandler(Thread):
    def __init__(self, sock):
        super().__init__(daemon = True)
    
    def run(self):
        pass

if __name__ == '__main__':
    with open('config.json', 'r') as config_file:
        config = 

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', 8800))
    sock.listen()

    while True:
        connection, addr = sock.accept()
        print(connection)
    
    sock.close()
