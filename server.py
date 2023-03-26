import argparse
import socket
from bruteforceAttack import BruteForceAttack
from multiprocessing import Process, Manager

def main():
    params = parse_arguments()
    SERVER = socket.gethostbyname(socket.gethostname())
    # PORT = params.port
    # FILE = params.file
    # GROUP = params.group
    # USERS = params.users
    # LIMIT = params.limit
    PORT = 8080
    LIMIT = 1000000
    GROUP = 50
    
    with Manager() as manager:
        pwList = manager.list()

        pg = Process(target=password_generation, args=[pwList, LIMIT, GROUP])
        pg.start()
        # pg.join()

        make_socket(SERVER, PORT)

        while True:
            print('hi')

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

def client_thread(conn, addr):
    with conn:
        print(''.format())
        while True:
            data = conn.recv(1024)
            if not data:
                break
            conn.sendall('[CONNECTION] Received {} from {}'.format(data, addr).encode())
    print('[CONNECTION] Disconnected from {}'.format(addr))

def make_socket(server, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((server, port))
        s.listen(5)
        print('[CONNECTION] Listening on {}:{}'.format(server, port))
        while True:
            conn, addr = s.accept()
            print('[INFO] Starting Process for connection {}'.format(addr))
            thing = Process(target=client_thread, args=[conn, addr])


if __name__ == "__main__":
    main()

    # python server.py -f file -p 8080 -g 1000 user1 user2