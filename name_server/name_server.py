import os
import socket
from threading import Thread
import json
import random
import string
import shutil

def init(sock):
    print(f'Performing init.')
    for server in storage_servers:
        print(f'Connecting to server {server}.')
        with socket.socket() as storage_socket:
            storage_socket(json.dumps({'command_type': 'system', 'command': 'init'}).encode())
            response = json.loads(storage_socket.read(1024).decode())
            print(response)
    shutil.rmtree(storage_directory)

def create_file(sock, params):
    path = params[0]
    abs_path = current_directory + '/' + path
    server_path = storage_directory + abs_path

    if os.path.exists(server_path):
        raise ValueError(f'{server_path}: File already exists.')
        
    if not os.path.exists(os.path.dirname(server_path)):
        os.makedirs(os.path.dirname(server_path))
    
    with open(server_path, 'wb') as file:
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
            with socket.socket() as storage_sock:
                storage_sock.connect(tuple(server))
                storage_sock.send(json.dumps(request).encode())
                response = json.loads(storage_sock.recv(1024).decode())
                print(response)
        file.write(json.dumps({'size': 0, 'containing_storage_servers': containing_storage_servers}))
    response = {
        'message': 'OK',
        'details': 'File created successfully.'
    }
    sock.send(json.dumps(response).encode())

def read_file(sock, params):
    print(f'Performing read_file on {params}')
    path = params[0]
    server_path = storage_directory + '/' + path
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

def write_file(sock, params):
    print(f'Performing write_file.')
    path = params[1]
    if path[0] == '/':
        abs_path = path
    else:
        abs_path = current_directory + '/' + path
    server_path = storage_directory + abs_path
    tmp_file_path = '/tmp/' + ''.join(random.choices(string.ascii_lowercase, k = 16))
    print(f'Writing to file {tmp_file_path}')
    with open(tmp_file_path, 'wb') as tmp_file:
        while True:
            data = sock.rec(1024)
            if data:
                tmp_file.write(data)
            else:
                break
    with open(server_path, 'rb') as details_file:
        details = json.load(details_file)
        details['size'] = os.path.getsize(tmp_file_path)
    print(f'New file details {details}')
    with open(server_path, 'wb') as details_file:
        details_file.write(json.dumps(details))
    if replication_level > len(storage_servers):
        print(f'Not enough storage servers, need {replication_level}, found {len(storage_servers)}')
    print(f'Sending to servers {details["containing_storage_servers"]}')
    for server in details['containing_storage_servers']:
        print(f'Sending to server {server}')
        request = {
            'command_type': 'file',
            'command': 'write',
            'params': [
                abs_path,
                details['size']
            ]
        }
        with socket.socket() as storage_socket:
            print(f'Connected to server')
            storage_socket.connect(tuple(server))
            storage_socket.send(json.dumps(request).encode())
            with open(tmp_file_path, 'rb') as tmp_file:
                storage_socket.sendfile(tmp_file)

def delete_file(sock, params):
    print(f'Performing delete_file on {params}')
    path = params[0]
    abs_path = path if path[0] == '/' else current_directory + '/' + path
    server_path = storage_directory + abs_path
    with open(abs_path) as details_file:
        details = json.load(details_file)
    print(f'Iteraing over {details["containing_storage_servers"]}')
    for server in details['containing_storage_servers']:
        request = {
            'command_type': 'file',
            'command': 'delete',
            'params': [
                abs_path
            ]
        }
        with socket.socket() as storage_sock:
            print(f'Connected to {server}')
            storage_sock.connect(tuple(server))
            storage_sock.send(json.dumps(request).encode())
            response = json.loads(storage_sock.recv(1024).decode())
            print(f'{response}')
    os.remove(server_path)

def info_file(sock, params):
    print(f'Performing info_file on {params}.')
    path = params[0]
    abs_path = path if path[0] == '/' else current_directory + path
    server_path = storage_directory + abs_path
    with open(server_path, 'rb'):
        sock.sendfile(server_path)

def copy_file(sock, params):
    print(f'Performing copy_file on {params}')
    src_path = params[0]
    src_abs_path = src_path if src_path[0] == '/' else current_directory + '/' + src_path
    src_server_path = storage_directory + src_abs_path
    dst_path = params[1]
    dst_abs_path = dst_path if dst_path[0] == '/' else current_directory + '/' + dst_path
    dst_server_path = storage_directory + dst_abs_path
    
    shutil.copy(src_server_path, dst_server_path)
    
    with open(src_server_path, 'rb') as details_file:
        details = json.load(details_file)
    
    for server in details['containing_storage_servers']:
        request = {
            'command_type': 'file',
            'command': 'copy',
            'params': [
                src_abs_path,
                dst_abs_path
            ]
        }
        with socket.socket() as storage_socket:
            storage_socket.connect(tuple(server))
            storage_socket.send(json.dumps(request).encode())
            response = storage_socket.recv(1024)
            print(response)

def move_file(sock, params):
    print(f'Performing copy_file on {params}')
    src_path = params[0]
    src_abs_path = src_path if src_path[0] == '/' else current_directory + '/' + src_path
    src_server_path = storage_directory + src_abs_path
    dst_path = params[1]
    dst_abs_path = dst_path if dst_path[0] == '/' else current_directory + '/' + dst_path
    dst_server_path = storage_directory + dst_abs_path
    
    shutil.move(src_server_path, dst_server_path)
    
    with open(src_server_path, 'rb') as details_file:
        details = json.load(details_file)
    
    for server in details['containing_storage_servers']:
        request = {
            'command_type': 'file',
            'command': 'move',
            'params': [
                src_abs_path,
                dst_abs_path
            ]
        }
        with socket.socket() as storage_socket:
            storage_socket.connect(tuple(server))
            storage_socket.send(json.dumps(request).encode())
            response = storage_socket.recv(1024)
            print(response)

def change_directory(sock, params):
    path = params[0]
    abs_path = path if path[0] == '/' else current_directory + '/' + path
    current_directory = abs_path

def list_directory(sock, params):
    path = params[0]
    abs_path = path if path[0] == '/' else current_directory + '/' + path
    server_path = storage_directory + abs_path
    sock.send(json.dumps(os.listdir(server_path)).encode())

def make_directory(sock, params):
    path = params[0]
    abs_path = path if path[0] == '/' else current_directory + '/' + path
    server_path = storage_directory + abs_path
    os.makedirs(server_path)

def delete_directory(sock, params):
    path = params[0]
    abs_path = path if path[0] == '/' else current_directory + '/' + path
    server_path = storage_directory + abs_path
    if not os.path.exists(server_path):
        response = {
            'message': 'NO',
            'details': 'No such path.'
        }
        sock.send(json.dumps(response).encode())
        return
    if not os.path.isdir(server_path):
        response = {
            'message': 'NO',
            'details': 'Not a directory.'
        }
        sock.send(json.dumps(response).encode())
        return
    for server in storage_servers:
        request = {
            'command_type': 'directory',
            'command': 'delete',
            'params': [
                abs_path
            ]
        }
        with socket.socket as storage_socket:
            storage_socket.connect(tuple(server))
            storage_socket.send(json.dumps(request).encode())
            response = json.loads(storage_socket.recv(1024)).decode()
            print(response)
    

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
            if request_header['command'] == 'delete':
                delete_file(self.sock, request_header['params'])
            if request_header['command'] == 'info':
                info_file(self.sock, request_header['params'])
            if request_header['command'] == 'copy':
                copy_file(self.sock, request_header['params'])
            if request_header['command'] == 'move':
                move_file(self.sock, request_header['params'])
        if request_header['command_type'] == 'directory':
            if request_header['command'] == 'cd':
                change_directory(self.sock, request_header['params'])
            if request_header['command'] == 'ls':
                list_directory(self.sock, request_header['params'])
        self.sock.close()


if __name__ == '__main__':
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)

    storage_directory = config['storage_directory']
    current_directory = config['current_directory']
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
