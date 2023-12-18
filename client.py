import socket
import time

SERVER_HOST = 'localhost'
SERVER_PORT = 12345


def start_client():
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn_user = None

    print('Connecting to the server...', end='')
    while True:
        try:
            conn.connect((SERVER_HOST, SERVER_PORT))
            break
        except ConnectionRefusedError:
            print('.\n', end='')
            time.sleep(1)

    try:
        conn_user = login(conn)

        while True:
            conn.send(str(['users']).encode())
            users = eval(conn.recv(1024).decode())
            print('\nUsers:')
            for i, user in enumerate(users):
                print(f'{user[0]}. {user[1]}')
            chat_with(conn, conn_user, input('\nChat with: '))
    finally:
        conn.close()


def login(conn):
    while True:
        while True:
            loc = input('\nLogin or Create account? (l/c): ')

            if loc == 'l':
                mode = 'login'
                break
            elif loc == 'c':
                mode = 'register'
                break
            else:
                print('Invalid input.')

        conn.send(str([
            mode,
            input('Enter your username: '),
            input('Enter your password: ')
        ]).encode())
        response = conn.recv(1024).decode()

        print(response)
        if response.startswith('Logged in as'):
            return response.split(' ')[-1]


def chat_with(conn, conn_user, user):
    conn.send(str(['users', user]).encode())
    response = conn.recv(1024).decode()
    print(f'\nChat with {response[1]}:')
    while True:
        conn.send(
            str(['chat', conn_user, user]).encode()
        )
        chat = eval(conn.recv(1024).decode())
        for message in chat:
            print(f'{message.sender}: {message.message}')

        message = input('\nMessage: ')
        conn.send(
            str(['send', conn_user, user, message]).encode()
        )
