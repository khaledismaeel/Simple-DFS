import socket
import tqdm
import os
import sys

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096 # send 4096 bytes each time step

command_type = sys.argv[1]
command = sys.argv[2]
params = map(float, sys.argv[3].strip('[]').split(','))
    
'''
# the ip address or hostname of the receiver, AWS instance in this case
host = sys.argv[2] # The IP of the instance

# the port, specified as a paramter
port = int(sys.argv[3])

# the name of file we want to send
filename = sys.argv[1]

# get the file size
filesize = os.path.getsize(filename)
'''

# create the client socket, TCP socket
s = socket.socket()

print(f"[+] Connecting to {host}:{port}")
s.connect((host, port))
print("[+] Connected.")

# send the filename and filesize
s.send(f"{filename}{SEPARATOR}{filesize}".encode())
filename = "hussein"
filesize = "younes"
print(f"{filename}{SEPARATOR}{filesize}")

# start sending the file
progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
with open(filename, "rb") as f:
    for _ in progress:
        # read the bytes from the file
        bytes_read = f.read(BUFFER_SIZE)
        if not bytes_read:
            # file transmitting is done
            break
        # we use sendall to assure transimission in
        # busy networks
        s.sendall(bytes_read)
        # update the progress bar
        progress.update(len(bytes_read))
# close the sockets
s.close()