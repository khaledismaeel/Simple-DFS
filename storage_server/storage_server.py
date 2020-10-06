import socket, os, json, sys, tqdm

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8800

BUFFER_SIZE = 1024
SEPARATOR = "<SEPARATOR>"

root_dir = "/home/hussein/dfs_dir"


def connect_to_name_server(socket):
    print(f"[+] Connecting to {SERVER_HOST}:{SERVER_HOST}")
    socket.connect((SERVER_HOST, SERVER_PORT))
    print("[+] Connected.")
    command = sys.argv[1]
    param = sys.argv[2]
    data = {"command": command, "param": param}
    json_data = json.dumps(data)
    s.send(json_data.encode())

    # receive response from the name server
    received_msg = s.recv(BUFFER_SIZE).decode()
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


if __name__ == '__main__':
    registration_sock = socket.socket()
    connect_to_name_server(registration_sock)
    registration_sock.close()

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

        if data["command"] == "write":
            file = data["params"][0]

        client_socket.close()
    s.close()
