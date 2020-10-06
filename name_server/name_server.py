import os
import socket
from threading import Thread
import json
import random
import string
import shutil

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

def read_file(sock, params):
    print(f'Performing read_file on {params}')
    path = params[0]
    server_path = storage_directory + path
    if not os.path.exists(server_path):
        raise ValueError(f'{server_path}: No such file.')
    with open(server_path, 'r') as file:
        file_details = json.load(file)
        containing_storage_servers = file_details['containing_storage_servers']
        print(f'Containing storage servers: {containing_storage_servers}')
        for _ in range(5):
            chosen_server = random.choice(containing_storage_servers)
            print(f'Fetching from server {chosen_server}')
            request = {
                'command-type': '',
                'command': 'read',
                params: [
                    path
                ]
            }
            print(f'Creating socket.')
            with socket.socket() as storage_sock:
                storage_sock.connect(tuple(chosen_server))
                print(f'Connected. Sending request {request}')
                storage_sock.send(json.dumps(request).encode())
                storage_response = json.loads(storage_sock.read(1024).decode())
                print(f'Got response {storage_response}')
                if storage_response['message'] == 'OK':
                    sock.send(json.dumps({'message': 'OK', 'file_size': file_details['size']}))
                    while True:
                        data = storage_sock.recv(1024)
                        if data:
                            sock.write(data)
                        else:
                            break
        else:
            print(f'No storage servers could return the file.')
            response = {
                'message': 'NO',
                'details': 'No storage server could return the file.'
            }
            sock.send(json.dumps(response).encode())

def init(sock):
    print(f'Performing init.')
    for server in storage_servers:
        print(f'Connecting to server {server}.')
        with socket.socket() as storage_socket:
            storage_socket(json.dumps({'command_type': 'system', 'command': 'init'}).encode())
            response = json.loads(storage_socket.read(1024).decode())
            print(response)
    shutil.rmtree(storage_directory)

def write_file(sock, params):
    print(f'Performing write_file.')

class ClientHandler(Thread):
    def __init__(self, sock, address):
        super().__init__(daemon=True)
        self.sock = sock

    def run(self):
        request_header = json.loads(self.sock.recv(1024).decode())
        print(request_header)

        if request_header['command_type'] == 'system':
            if request_header['command'] == 'register-storage-server':
                pass
            if request_header['command'] == 'init':
                init(sock)
        if request_header['command_type'] == 'file':
            if request_header['command'] == 'create':
                create_file(self.sock, request_header['params'])
            if request_header['command'] == 'read':
                read_file(self.sock, request_header['params'])
            if request_header['command'] == 'write':
                write_file(self.sock, request_header['params'])

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
