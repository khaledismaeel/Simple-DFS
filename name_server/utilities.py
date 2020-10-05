import random
import string

class Directory:
    def __init__(self, parent = None, name = None):
        if name is None:
            self.name = ''.join(random.choices(string.ascii_letters + string.digits, k = 32))
        elif name == '':
            raise ValueError('Empty names are not allowed.')
        else:
            self.name = name
        
        if parent is not None:
            for sibling in parent.children:
                if sibling.name == name:
                    raise ValueError(f'{name}: File or directory already exist.')
            
            self.parent = parent
            parent.children.append(self)

        self.children = []


class File:
    def __init__(self, parent, name = None):
        if name is None:
            self.name = ''.join(random.choices(string.ascii_letters + string.digits, k = 32))
        elif name == '':
            raise ValueError('Empty names are not allowed.')
        else:
            self.name = name
        
        for sibling in parent.children:
            if sibling.name == name:
                raise ValueError(f'{name}: File or directory already exist.')

        self.parent = parent
        parent.children.append(self)

class FileSystem:
    def __init__(self):
        self.root = Directory(name = '')
    
    def print_tree(self, dir = None, spaces = 0):
        if dir is None:
            dir = self.root
        
        print(f' ' * spaces + dir.name)

        for child in dir.children:
            if isinstance(child, File):
                print(f' ' * (spaces + 1) + child.name)
            else:
                self.print_tree(child, spaces + 1)
    
    def create_file(self, path):
        path_segments = path.split('/')
        
        if path_segments[0] != '' or path_segments[-1] == '':
            raise ValueError(f'{path}: Invalid path.')
        
        current_directory = self.root
        for seg in path_segments[1:-1]:
            for child in current_directory.children:
                if child.name == seg:
                    current_directory = child
                    break
            else:
                new_directory = Directory(current_directory, seg)
                current_directory = new_directory
        
        for child in current_directory.children:
            if child.name == path_segments[-1]:
                raise ValueError(f'{path}: File already exists.')
                
        File(current_directory, path_segments[-1])
    