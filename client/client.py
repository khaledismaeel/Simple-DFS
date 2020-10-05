import sys
import os
import json

if __name__ == '__main__':
    print(f'Running client.')
    
    os.chdir(sys.path[0])
    
    with open('./config.json', 'r') as config_file:
        config = json.load(config_file)
    
    try:
        name_server = sys.argv[sys.argv.index('--name-server') + 1]
    except ValueError:
        name_server = config['default_name_server']
    except IndexError:
        print(f'No value for --name-server')
        exit(1)
    
    