import os
import socket
from threading import Thread
import json
import random


class StorageServerHandler(Thread):
    def __init__(self, sock, request):
        super().__init__(daemon=True)
        self.sock = sock
        self.request = request


def create_file(sock, params):
    path = params[0]
    server_path = storage_directory + path
    if os.path.exists(server_path):
        raise ValueError(f'{server_path}: File already exists.')
    if not os.path.exists(os.path.dirname(server_path)):
        os.makedirs(os.path.dirname(server_path))
    with open(server_path, 'w') as file:
        if replication_level > len(storage_servers):
            print(
                f'Not enough storage servers, current: {len(storage_servers)}, needed: {replication_level}.')
            print(f'will replicate to the available ones for now.')
        containing_storage_servers = random.sample(
            storage_servers, min(replication_level, len(storage_servers)))
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


def add_storage_server(sock, address):
    storage_servers.append(list(address))


class ClientHandler(Thread):
    def __init__(self, sock, address):
        super().__init__(daemon=True)
        self.sock = sock

    def run(self):
        request_header = json.loads(self.sock.recv(1024).decode())

        if request_header['command_type'] == 'system':
            if request_header['command'] == 'add-storage-server':
                add_storage_server(sock, address)

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
        connection, address = sock.accept()
        print(f'Accepted')
        ClientHandler(connection, address).start()

    sock.close()
