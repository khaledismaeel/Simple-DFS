import os
import socket
from threading import Thread
import json
import random

class StorageServerHandler(Thread):
    def __init__(self, sock):
        super().__init__(daemon = True)
        self.sock = sock

    def run(self):
        pass

def create_file(sock, params):
    path = params[0]
    server_path = storage_directory + path
    if os.path.exists(server_path):
        raise ValueError(f'{server_path}: File already exists.')
    if not os.path.exists(os.path.dirname(server_path)):
        os.makedirs(os.path.dirname(server_path))
    with open(server_path, 'w') as file:
        containing_storage_servers = random.sample(storage_servers, replication_level)
        for server in containing_storage_servers:
            request = {
                'command_type': 'file',
                'command': 'create',
                'params': [path]
            }
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as storage_sock:
                storage_sock.connect(tuple(server))
                storage_sock.send(json.dumps(request).encode())
                response = json.loads(storage_sock.recv(1024).decode())
                print(response)
        file.write(json.dumps(containing_storage_servers))

class ClientHandler(Thread):
    def __init__(self, sock):
        super().__init__(daemon = True)
        self.sock = sock
    
    def run(self):
        request_header = json.loads(self.sock.recv(1024).decode())
        
        if request_header['command_type'] == 'file':
            if request_header['command'] == 'create':
                create_file(sock, request_header['params'])
        
        self.sock.close()

if __name__ == '__main__':
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)

    storage_directory = config['storage_directory']
    replication_level = config['replication_level']
    storage_servers = config['storage_servers']

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', 8800))
    sock.listen()

    while True:
        print('listening now...')
        connection, addr = sock.accept()
        print(connection)
        ClientHandler(connection).start()
    
    sock.close()