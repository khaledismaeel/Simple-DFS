# DS Project 2 Report

## Introduction

In this document we shall summarize our distributed file system (DFS) implementation. Note that we merged both the GitHub `README` file and the project report into this document.

The GitHub repository for our project is available here:

https://github.com/khaledismaeel/Simple-DFS

The DockerHub repositories for our client, name server, and storage server images are available here:

https://hub.docker.com/r/hussein987/client
https://hub.docker.com/r/hussein987/name_server
https://hub.docker.com/r/hussein987/storage_server

First, we shall introduce the overall architecture of our DFS. Then, we provide a brief usage manual for our client application. We then summarize the work each one of our team members accomplished on the project. We finally  conclude our project report and briefly list some room for improvement.

## Architecture

### General Overview

In our implementation, an instance of the DFS roughly corresponds to an empty partition on a disk; end users create, read, and write files and directories on this DFS as they would do on their local disk partitions. Operations on an instance of the DFS are accomplished through our client application docker container. With that said, we shall now present the architecture of such an instance of the DFS.

An instance of the DFS consists of name server and storage server network nodes implemented as docker containers. One instance of the DFS consists of exactly one name server container and several storage server containers. While the storage servers store the actual files, the name server stores general information about the distributed file system, such as its file system tree, connected storage servers, file locations on storage servers, and others.

The client application accepts operations from the end user and communicates with the name server directly. The name server performs the operations (possibly communicating with storage servers in the process) and returns a response and the result (if needed) to the client.

Note that the client does not communicate with the storage server in the process, that is, file resolution is done recursively rather than iteratively. Although this architecture creates a networking bottleneck at the name server, it greatly simplifies the networking architecture and communication protocols. We decided that this is a winning trade off and we implemented our file resolution recursively.

All connections in the DFS (client and name server, name server and storage server) are implemented on top of TCP. We decided to use TCP because our application does not really require any of the higher level protocol constructs such as security and others; it was high enough to encapsulate our needs and low enough to simplify our implementation. Besides raw file data, the nodes in the network do share report messages of fixed length (1024 bytes). These messages are `.json` files that initiate and terminate operations.

Below is a diagram representing the overall structure of our DFS.

![](https://i.imgur.com/5G79sQV.png)


### Name Server

The name server essentially performs the following operations:
- Track the DFS networks structure (which may be dynamically changing).
- Maintain the file system tree.
- Track which files are located on which storage servers.

Storage servers are tracked by maintaining `.json` configuration file that gets backed up periodically. In case the name server goes down, it can restore the storage servers status from the configuration file.

The file system tree is maintained on the disk storage of the name server at the `/simple-dfs/` directory. The contents of `/simple-dfs/` is an exact mirror of the file system tree, except that it is not the actual files that are stored, but rather a `.json` file containing a list of storage servers that contain this file along with other file metadata.

The name server has a TCP socket listening on port `8800`. Whenever a client attempts to send a request to the server a thread is dispatched to process the client operation. This thread communicates with storage servers if necessary (possibly creating other threads in the process) and returns the result to the client.

A DFS-wide level of replication is maintained and is set by the system administrator upon creation of the DFS. In the case of file creation and file writing, the name server *randomly* selects storage servers to replicate the file to. The random assignment keeps the loads balanced among storage servers.

### Storage Server

The storage server is where the actual files are stored. In a similar manner to the name server, the storage server has a local storage directory at `/simple-dfs/`. Unlike the name server, the storage server's storage directory is not a mirror of the file system tree. Instead, each storage server contains a subset of the file system files dictated by the name server.

When a file is written on the storage server the whole path to the file is created. Therefore, the directory structure of the storage directory on the storage server is a subset of the file system directory tree.

The name server also has a TCP socket listening on port `8800`. This port is exposed and the mapped host port number is maintained in the name server's list of storage servers.

### Client Application

The client application is the simplest portion of our architecture. The application accepts commands from the user and sends the corresponding request to the specified name server. The name server then sends the response on and returned data (if any) through the same TCP socket.

It is worth noting, however, that it perhaps would have been more convenient to implement the client application as a standalone program/script rather than a docker container. Having a docker container sending and receiving files leads to one of two scenarios:

1. Data needs to be loaded and unloaded into and from the docker container, which is kind of tedious to the end user.
2. The docker container is going to have access to the host machine's file system, which is an unusual way for deploying container applications.

Our application was originally developed as a Python script which very closely resembles the way ordinary file system commands are done. We later wrapped it in a docker image to conform to the project specification.

## Usage Manual
### Environment setup
To use the DFS, the following requirements should be met:
- Having docker installed on the host instances.
- Having a private network connecting the instances.


### Deployment
#### Name Server
To run the name server, we have to pull the `name_server` image from DockerHub using the following command 
```
$ docker pull hussein987/name_server
```
Now, we can run the name server as follows
```
$ docker run --name name_server -p <PUBLISH_TO>:8800 hussein987/name_server
```
Where `PUBLISH_TO` is any unallocated port that will be exposed to the outside world. And `8800` is the already exposed port from the Dockerfile.

#### Storage Server
To run the storage server, we have to pull the `storage_server` image from DockerHub using the following command
```
$ docker pull hussein987/storage_server
```
Now, we can run the storage server as follows
```
$ docker run --name storage_server -p <PUBLISH_TO>:8800 hussein987/storage_server
```
Where `PUBLISH_TO` is any unallocated port that will be exposed to the outside world. And `8800` is the already exposed port from the Dockerfile.
- Please note that if multiple servers are running on the same instance, you have to publish their ports from `8800` to different unallocated prots. For example, if two storage servers are running on the same instance, the first one might be prublished as `-p 8800:8800` and the second one as `-p 8801:8800`.
- Moreover, the option `--name` should be different for each running server on the same instance.

#### Client
To run the client side, we have to pull the `client` image from DockerHub using the following command
```
$ docker pull hussein987/client
```
After pulling the image, we can run it as follows
```
$ docker run --name client hussein987/client
```
To execute commands on the DFS, we have to execute the python scipt that is inside the container passing the corresponding arguments.

This is the general form of the command
```
$ python client.py command_type command [params]
```

### Simple-DFS CLI Command Types

#### `system`

The commands of this type has nothing to do with a specific file or directory, instead, they will modify the structure of the DFS (like initializing the system storage) and get relevant information.

#### `file`

The commands of this type will operate on files by creating, writing, reading, moving, copying, or deleting files on the DFS.

#### `directory`
The commands of this type will operate on directories by changing, listing, creating, and deleting directories.

### Simple-DFS CLI Commands

#### `init`

Initializes the system storage by deleting all the files and directories in the root directory, and returns the available space to the user.

```
$ python client.py system init
```

#### `create <file_path>`

Creates a file on the DFS

**Parameters**

- `file_path`: the path of the file that we need to put on the DFS.
  

**Example**

```
$ python client.py file create /test.py
```

#### `read <src_file_path>`

Downloads a file from the DFS to the client's file system. 

**Parameters**

- `src_file_path`: the path of the file that we need to read from the DFS.

**Example**

```
$ python client.py file read /test.py
```


#### `write <src_file_path> <dst_dir>`

uploads a file from the client's host machine to the DFS.

**Parameters**
- `src_file_path`: the path of the file that we need to put on the DFS. 
- `dst_dir`: the directory where the file should be put on the DFS.

**Example**

```
$ python client.py file write /test.py /usr/var/
```

#### `delete <file_path>`

Deletes a file from the DFS.

**Parameters**

- `file_path`: the path of the file that we need to delete from the DFS.

**Example**

```
$ python client.py file delete /use/var/test.py
```

#### `info <file_path>`

Prints the info about the file.

**Paramters**

- `file_path`: the path of the file tat need to get info about.

**Example**

```
$ python client.py file info /usr/var/test.py
```

#### `copy <src_file_path> <dst_file_path>`

Copies a file in the file system.

**Parameters**

- `src_file_path`: the file to copy.
- `dst_file_path`: the location to copy the file to.

**Example**

```
$ python client.py system init
```

#### `move <src_path> <dst_path>`

Moves a file from the source path to the destination path

**Parameters**
- `src_path`: The path of the file that we need to move. 
- `dst_path`: The destination path

**Example**
```
$ python client.py file move /usr/loacl/test.py /test.py
```
#### `ch <dir_path>`
Changes the current working directory to the specified directory.

**Parameters**
- `dir_path`: The directory to be set as a current directory. 

**Example**
```
$ python client.py directory ch /usr/local/
```
#### `ls`

lists the contents of the current working directory.

**Example**

```
$ python client.py directory ls
```
#### `mkdir <dir_path>`

creating the specified directory on the DFS.

**Paramters**:
- `dir_path`: the directory path to create.

**Example**

```
$ python client.py directory mkdir /usr/local/
```

#### `delete <dir_path>`
Deletes the given directory.

**Paramters**:
- `dir_path`: the directory path to delete.

**Example**
```
$ python client.py directory delete /usr/local/
```
## Team Work

Our team consists of Khaled Ismaeel from `BS18-SB-01` and Hussein Younes from `BS18-DS-02`. After spending some time to agree on the overall DFS architecture and request-response formats between its nodes, we evenly divided the work among us as follows.

- Khaled Ismaeel shall be responsible for the central point of the DFS: the name server. He wrote the entire code for the name server and built its docker image.
- Hussein Younes shall be responsible for the client and storage server applications. Again, he wrote the entire source for both of them and built their docker images.

With that division we had almost half of the project code for each of us to code (each had two communication channels to write). Our commit history on GitHub provides all the relevant statistics.

It is worth noting that we were in a continuous testing loop throughout development. That is, we were constantly present together while writing and testing the code.

## Conclusion

In this project we implemented a simple distributed file system (DFS). The system consisted of three parts: client application, name server, and storage server. All three parts were deployed as docker containers.

A lot room for improvement exists for this project, such as:
- Using higher level communication protocols and services (HTTPS, TLS, FTP, etc).
- Using more intelligent file replication algorithms.
- Gathering more usage statistics.
- Employing a DBMS to support persistent structures.

Our team's contribution was pretty evenly divided and is available through our GitHub commit history.