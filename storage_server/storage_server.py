import socket, os, json, tqdm

SERVER_PORT = 8800
SERVER_HOST = "0.0.0.0"
BUFFER_SIZE = 1024

root_dir = "/home/hussein/dfs_dir"


def connect_to_name_server(sock, command, name_server):
    print(f"[+] Connecting to {name_server[0]}:{name_server[1]}")
    sock.connect(name_server)
    print("[+] Connected.")

    data = {"command_type": "system", "command": command, "params": []}
    json_data = json.dumps(data)
    registration_sock.send(json_data.encode())

    # receive response from the name server
    received_msg = sock.recv(BUFFER_SIZE).decode()
    print(received_msg)


def create_file(path):
    filepath = root_dir + path
    if not os.path.exists(os.path.dirname(filepath)):
        os.makedirs(os.path.dirname(filepath))
    try:
        with open(filepath, "w") as file:
            pass
        return {"message": "File Created Successfully"}
    except:
        return {"message": f"Could not create file: {filepath}"}


def receive_file(socket, path, filesize):
    filepath = root_dir + path
    progress = tqdm.tqdm(range(filesize), f"Receiving {path}", unit="B", unit_scale=True, unit_divisor=1024)
    try:
        with open(filepath, "wb") as f:
            for _ in progress:
                bytes_read = socket.recv(BUFFER_SIZE)
                if not bytes_read:
                    break

                f.write(bytes_read)
                progress.update(len(bytes_read))
        return {"message": "File Dowonloaded Successfully"}
    except:
        return {"message": f"Could not download file: {path}"}


def send_file(socket, filename):
    filesize = os.path.getsize(filename)
    progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "rb") as f:
        for _ in progress:
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                break

            socket.sendall(bytes_read)
            progress.update(len(bytes_read))


def delete_file(path):
    filepath = path + root_dir
    os.remove(filepath)


def get_file_info(path):
    filepath = path + root_dir
    os.path.getsize(filepath)


if __name__ == '__main__':
    # command = 'register-storage-server'
    # param = (input('Enter name server IP: '), int(input('Enter name server port: ')))
    # registration_sock = socket.socket()
    # connect_to_name_server(registration_sock, command, param)
    # registration_sock.close()

    s = socket.socket()
    s.bind((SERVER_HOST, SERVER_PORT))
    s.listen(5)
    while True:
        print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")
        client_socket, address = s.accept()
        print(f"[+] {address} is connected.")

        data = client_socket.recv(BUFFER_SIZE).decode()
        data = json.loads(data)

        if data["command"] == "create":
            print(data["params"][0])
            print(json.dumps(create_file(data["params"][0])))
            client_socket.send(json.dumps(create_file(data["params"][0])).encode())

        if data["command"] == "put":
            filepath = data["params"][0]
            filesize = data["params"][1]
            receive_file(client_socket, filepath, filesize)

        if data["command"] == "delete":
            filepath = data["params"][0]
            delete_file(filepath)

        if data["command"] == "info":
            filepath = data["params"][0]
            get_file_info(filepath)

        if data["command"] == "read":
            filepath = data["params"][0]
            send_file(client_socket, filepath)


        client_socket.close()
    s.close()
