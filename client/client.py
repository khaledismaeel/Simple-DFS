import socket
import tqdm
import os
import sys
import json
import argparse

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 1024 # send 4096 bytes each time step


command_type = sys.argv[1]
command = sys.argv[2]
params = sys.argv[3:] if len(sys.argv) > 3 else None
print(type(params))


data = {}
data["command_type"] = command_type
data["command"] = command
data["params"] = params
json_data = json.dumps(data)


host = "10.91.53.24" # The IP of the instance
port = 8800

s = socket.socket()

print(f"[+] Connecting to {host}:{port}")
s.connect((host, port))
print("[+] Connected.")

s.send(json_data.encode())
print(json_data.encode())

received = s.recv(BUFFER_SIZE).decode()
print(received)

s.close()