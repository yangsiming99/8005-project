import argparse
import socket
import json
import crypt

status_codes = {
    'initial': 0,
    'next_set': 1,
    'found': 2
}

def main():
    # params = parse_arguments()
    global SERVER 
    global PORT 
    global targets
    global STOP
    STOP = False
    # SERVER = params.server
    # PORT = params.PORT
    SERVER= '10.0.0.45'
    PORT = 8084

    count = 0

    while True:
        if (count == 0): 
            resp = send(status_codes['initial'])
            targets = resp['targets']
            print(targets)
        else:
            resp = send(status_codes['next_set'])

        guessPasswords(resp['section'])
        if STOP == True:
            break
        count += 1
    
    print(targets)

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--server', help='IP address of server')
    parser.add_argument('-p', '--port', help='Open port of server')

    args = parser.parse_args()
    return args

def send(status):
    # Should be used to get the first set of passwords + the shadow file info
    to_send = {"status": "{}".format(status)}
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((SERVER, PORT))
    s.send(json.dumps(to_send).encode())
    data = s.recv(1024)
    temp = ''
    temp += data.decode('ascii')
    resp = json.loads(temp)
    return resp

def guessPasswords(pwList):
    global STOP
    global targets

    for guess in pwList:
        for user in targets:
            if(user['found'] == False):
                encrypted = crypt.crypt(guess, user['salt'])
                if encrypted == user['hash']:
                    STOP = True
                    user['found'] = True
                    user['password'] = guess

if __name__ == '__main__':
    main()
    