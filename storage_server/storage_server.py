import socket
import os
import json

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8800

BUFFER_SIZE = 1024
SEPARATOR = "<SEPARATOR>"

root_dir = "/home/hussein/dfs_dir"


def create(path):
    filepath = root_dir + path
    if not os.path.exists(os.path.dirname(filepath)):
        os.makedirs(os.path.dirname(filepath))
    try:
        with open(filepath, "w") as file:
            pass
        return {"message": "File Created Successfully"}
    except:
        return {"message": f"Could not create file: {filepath}"}


if __name__ == '__main__':
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
            print(json.dumps(create(data["params"][0])))
            client_socket.send(json.dumps(create(data["params"][0])).encode())

        client_socket.close()
    s.close()
