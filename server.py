import argparse
import socket
import json
from bruteforceAttack import BruteForceAttack
from multiprocessing import Process, Manager

def main():
    params = parse_arguments()
    global targetInfo
    SERVER = socket.gethostbyname(socket.gethostname())
    # PORT = params.port
    # FILE = params.file
    # GROUP = params.group
    USERS = params.users
    # LIMIT = params.limit
    PORT = 8084
    LIMIT = 1000000
    GROUP = 50

    allUsers = read_file('shadow.txt')
    targetInfo = userFilter(allUsers, USERS)
    
    with Manager() as manager:
        pwList = manager.list()

        pg = Process(target=password_generation, args=[pwList, LIMIT, GROUP])
        pg.start()
        # pg.join()

        make_socket(SERVER, PORT, pwList)

def password_generation(list, limit, group):
    BA = BruteForceAttack(list, limit,  group)
    BA.initiateAttack()

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', help='location of shadow file')
    parser.add_argument('-g', '--group', help='Groups of passwords to try')
    parser.add_argument('-p', '--port', help='Open port')
    parser.add_argument('-l', '--limit', help='bruteforce limit')
    parser.add_argument('users', metavar='N', type=str, nargs='+', help='usernames')
    args = parser.parse_args()
    return args

def client_thread(conn, addr, pwList):
    section = pwList.pop(0)
    with conn:
        temp=''
        while True:
            data = conn.recv(1024)
            temp += data.decode('ascii')
            message = json.loads(temp)
            if not data:
                break
            else:
                status = int(message['status'])
                if status == 0:
                    # should send the userlist + first set of passwords
                    print('initial')
                    toSend = {'section': section, 'targets': targetInfo}
                    conn.sendall(json.dumps(toSend).encode())
                elif status == 1:
                    # should send next set of passwords
                    print('next_set')
                    toSend = {'section': section}
                    conn.sendall(json.dumps(toSend).encode())
                elif status == 2:
                    # should mark a boolean as true and ^ the about should indicate finish
                    print('found')
                    conn.sendall(json.dumps(section).encode())
                else:
                    conn.sendall('this is a temp message'.encode())
            
    print('[CONNECTION] Disconnected from {}'.format(addr))

def make_socket(server, port, pwList):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((server, port))
        s.listen(5)
        print('[CONNECTION] Listening on {}:{}'.format(server, port))
        while True:
            conn, addr = s.accept()
            print('[INFO] Starting Process for connection {}'.format(addr))
            thing = Process(target=client_thread, args=[conn, addr, pwList])
            thing.start()
            thing.join()

def read_file(filename='/etc/shadow'):
    try:
        f = open(filename)
    except PermissionError:
        print("ERROR: File Requires Additional Permissions To Read")
        exit(1)
    except:
        print("Something Went Wrong Reading File")
        exit(1)
    allUsers = f.read().split('\n')    
    return allUsers

def userFilter(usersList, targets):
    filterList = []
    for user in usersList:
        temp = user.split(':')
        try:
            targets.index(temp[0])
            salt = temp[1].rfind('$')
            info = {
                'user': temp[0],
                'hash': temp[1],
                'salt': temp[1][:salt],
                'found': False,
                'password': ''
            }
            filterList.append(info)
        except ValueError:
            continue
    return filterList

if __name__ == "__main__":
    main()

    # python server.py -f file -p 8080 -g 1000 user1 user2