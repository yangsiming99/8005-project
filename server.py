import argparse
import socket
import json
from bruteforceAttack import BruteForceAttack
from multiprocessing import Process, Manager
import os

def main():
    params = parse_arguments()
    global targetInfo
    SERVER = socket.gethostbyname(socket.gethostname())
    PORT = int(params.port)
    FILE = params.file
    USERS = params.users
    LIMIT = int(params.limit)
    # PORT = 8082
    # LIMIT = 1000000
    GROUP = 50

    global found
    found = False

    allUsers = read_file(FILE)
    targetInfo = userFilter(allUsers, USERS)
    
    with Manager() as manager:
        pwList = manager.list()
        status = manager.dict()
        status['found'] = False

        pg = Process(target=password_generation, args=[pwList, LIMIT, GROUP, status])
        pg.start()
        # pg.join()

        make_socket(SERVER, PORT, pwList, status)

def password_generation(list, limit, group, status):
    BA = BruteForceAttack(list, limit,  group, status)
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

def client_thread(conn, addr, pwList, pwstatus):
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
                if pwstatus['found'] == True:
                    print("1")
                    conn.sendall(json.dumps({'found': True}).encode())
                elif status == 0:
                    # should send the userlist + first set of passwords
                    print("2")
                    toSend = {'section': section, 'targets': targetInfo}
                    conn.sendall(json.dumps(toSend).encode())
                elif status == 1:
                    print("3")
                    # should send next set of passwords
                    toSend = {'section': section}
                    conn.sendall(json.dumps(toSend).encode())
                elif status == 2:
                    print("4")
                    # should mark a boolean as true and ^ the about should indicate finish
                    userInfo = message['data'][0]
                    print('=========================================')
                    print('Username: {}'.format(userInfo['user']))
                    print('Password: {}'.format(userInfo['password']))
                    print('=========================================')
                    pwstatus['found'] = True
                    conn.sendall(json.dumps(section).encode())
                else:
                    conn.sendall('this is a temp message'.encode())
            
    # print('[CONNECTION] Disconnected from {}'.format(addr))

def make_socket(server, port, pwList, status):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((server, port))
        s.listen(5)
        print('[CONNECTION] Listening on {}:{}'.format(server, port))
        while True:
            conn, addr = s.accept()
            print('[INFO] Starting Process for connection {}'.format(addr))
            thing = Process(target=client_thread, args=[conn, addr, pwList, status])
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

    # python server.py -f shadow.txt -p 8080 -l 10000 -g 1000 user7