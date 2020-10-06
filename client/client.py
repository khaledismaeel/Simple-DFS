import socket, sys, json, os, tqdm

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 1024 # send 4096 bytes each time step

host = "10.91.53.24"  # The IP of the instance
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


if __name__ == '__main__':
    command_type = sys.argv[1]
    command = sys.argv[2]
    params = sys.argv[3:] if len(sys.argv) > 3 else None
    print(type(params))

    data = {"command_type": command_type, "command": command, "params": params}
    json_data = json.dumps(data)

    # Create socket and connect to nameserver
    s = socket.socket()
    print(f"[+] Connecting to {host}:{port}")
    s.connect((host, port))
    print("[+] Connected.")

    # send the command format to the nameserver
    s.send(json_data.encode())

    # dfs put filepath dir_in_dfs
    if data["command"] == "put":
        filename = data["params"][0]
        send_file(s, filename)

    received = s.recv(BUFFER_SIZE).decode()
    print(received)

    s.close()