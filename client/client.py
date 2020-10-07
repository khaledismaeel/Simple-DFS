import socket, sys, json, os, tqdm

BUFFER_SIZE = 1024 # send 4096 bytes each time step

host = "10.0.1.11"  # The IP of the instance
port = 8800


def send_file(socket, filename):
    filesize = os.path.getsize(filename)
    # progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "rb") as f:
        read_so_far = 0
        while read_so_far < filesize:
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                break
            socket.sendall(bytes_read)
            read_so_far += len(bytes_read)
            # progress.update(len(bytes_read))


def receive_file(socket, filename, filesize):
    filepath = filename
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
    s.bind(('', 8800))
    print(f"[+] Connecting to {host}:{port}")
    s.connect((host, port))
    print("[+] Connected.")


    # dfs write filepath dir_in_dfs
    if data["command"] == "write":
        filename = data["params"][0]
        data["params"].append(os.path.getsize(filename))
        json_data = json.dumps(data)
        s.send(json_data.encode())
        s.send((' '*(1024 - len(json_data.encode()))).encode())
        send_file(s, filename)

    # download a file from the dfs to the client
    # usage: dfs read filepath_in_dfs dir_in_client
    elif data["command"] == "read":
        s.send(json_data.encode())
        server_data = s.recv(BUFFER_SIZE).decode()
        print(server_data)
        server_data = json.loads(server_data)
        filepath = data["params"][0]
        filesize = server_data["file_size"]
        dir_path, filename = os.path.split(filepath)
        print(dir_path, filename)
        received = receive_file(s, filename, filesize)


    else:
        s.send(json_data.encode())



    received = s.recv(BUFFER_SIZE).decode()
    print("Server response:")
    print(received)

    s.close()