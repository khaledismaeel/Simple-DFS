import socket, sys, json, os, tqdm

BUFFER_SIZE = 1024 # send 4096 bytes each time step

host = "10.0.1.11"  # The IP of the instance
port = 8800


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


def receive_file(socket, filename, filesize):
    filepath = filename
    if not os.path.exists(os.path.dirname(filepath)):
        os.makedirs(os.path.dirname(filepath))
    progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
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
        return {"message": f"Could not download file: {filename}"}


if __name__ == '__main__':
    command_type = sys.argv[1]
    command = sys.argv[2]
    params = sys.argv[3:] if len(sys.argv) > 3 else None

    data = {"command_type": command_type, "command": command, "params": params}
    json_data = json.dumps(data)

    # Create socket and connect to nameserver
    s = socket.socket()
    print(f"[+] Connecting to {host}:{port}")
    s.connect((host, port))
    print("[+] Connected.")

    # send the command format to the nameserver
    s.send(json_data.encode())

    # dfs write filepath dir_in_dfs
    if data["command"] == "write":
        filename = data["params"][0]
        send_file(s, filename)

    # download a file from the dfs to the client
    # usage: dfs read filepath_in_dfs dir_in_client
    if data["command"] == "read":
        server_data = s.recv(BUFFER_SIZE).decode()
        server_data = json.loads(server_data)
        filepath = data["params"][0]
        filename = server_data["params"][1]
        dir_path, filename = os.path.split(filepath)
        received = receive_file(s, filename)
        s.send(json.dumps(data).encode())

    received = s.recv(BUFFER_SIZE).decode()
    print(received)

    s.close()