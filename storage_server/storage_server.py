import socket, os, json, tqdm
import shutil

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
    sock.send(json_data.encode())

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
        return {"status": "OK",
                "details": "File created Successfully"}
    except Exception as e:
        return {"message": {"status": "FAILED",
                "details": 'Failed to create %s. Reason: %s' % (filepath, e)}}


def receive_file(sock, path, filesize):
    filepath = root_dir + path
    # progress = tqdm.tqdm(range(filesize), f"Receiving {path}", unit="B", unit_scale=True, unit_divisor=1024)
    try:
        with open(filepath, "wb") as f:
            bytes_read = sock.recv(filesize)
            f.write(bytes_read)
        return {"status": "OK",
                "details": "File Dowonloaded Successfully"}
    except Exception as e:
        return {"status": "FAILED",
                "details": 'Failed to download %s. Reason: %s' % (path, e)}


def send_file(sock, filename):
    filename = root_dir + filename
    try:
        filesize = os.path.getsize(filename)
        response = {"status": "OK",
                "details": "File Found",
                "size": filesize}
    except Exception as e:
        response =  {"status": "FAILED",
                "details": 'Failed to find file %s. Reason: %s' % (filename, e)}
    sock.send((json.dumps(response) + ' ' * (1024 - len(json.dumps(response).encode()))).encode())
    # sock.send((' ' * (1024 - len(json.dumps(response).encode()))).encode())
    with open(filename, "rb") as f:
        sock.send(f.read())

def delete_file(path):
    filepath = root_dir + path
    try:
        os.remove(filepath)
        return {"message": "File deleted Successfully"}
    except:
        return {"message": "Failed to delete file"}


def get_file_info(path):
    filepath = path + root_dir
    os.path.getsize(filepath)


def copy_file(src, dst):
    try:
        shutil.copyfile(root_dir + src, root_dir + dst)
        return {"message": "File copied Successfully"}
    except:
        return {"message": "Failed to copy file"}


def move_file(src, dst):
    try:
        shutil.move(root_dir + src, root_dir + dst)
        return {"message": "File moved Successfully"}
    except:
        return {"message": "Failed to move file"}


def delete_directory(dir_path):
    dir_path = root_dir + dir_path
    if not os.path.isdir(dir_path):
        return {"message": 'No such file or directory'}
    for filename in os.listdir(dir_path):
        file_path = os.path.join(dir_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
            return {"message": f"The storage is initialized"}
        except Exception as e:
            return {"message": 'Failed to delete %s. Reason: %s' % (file_path, e)}


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

        if data["command_type"] == "file":
            if data["command"] == "create":
                print(data["params"][0])
                print(json.dumps(create_file(data["params"][0])))
                client_socket.send(json.dumps(create_file(data["params"][0])).encode())

            if data["command"] == "write":
                filepath = data["params"][0]
                filesize = data["params"][1]
                received = receive_file(client_socket, filepath, filesize)
                client_socket.send(json.dumps(received).encode())

            if data["command"] == "delete":
                filepath = data["params"][0]
                deleted = delete_file(filepath)
                client_socket.send(json.dumps(deleted).encode())

            if data["command"] == "info":
                filepath = data["params"][0]
                get_file_info(filepath)

            if data["command"] == "read":
                filepath = data["params"][0]
                send_file(client_socket, filepath)

            if data["command"] == "copy":
                source = data["params"][0]
                destination = data["params"][1]
                copied = copy_file(source, destination)
                client_socket.send(json.dumps(copied).encode())

            if data["command"] == "move":
                current_path = data["params"][0]
                new_path = data["params"][1]
                moved = move_file(current_path, new_path)
                client_socket.send(json.dumps(moved).encode())

        if data["command_type"] == "directory":
            if data["command"] == "delete":
                dir_path = data["params"][0]
                deleted = delete_directory(dir_path)
                client_socket.send(json.dumps(deleted).encode())

        if data["command_type"] == "system":
            if data["command"] == "init":
                if os.path.exists(root_dir):
                    shutil.rmtree(root_dir)
                response = {
                    "status": "OK",
                    "details": f"The storage is initialized"
                }
                client_socket.send(json.dumps(response).encode())


        client_socket.close()
    s.close()
