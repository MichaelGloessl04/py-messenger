import datetime
import socket
from dbhandler import DBHandler
import threading

dbh = DBHandler()


def handle_client(conn, addr):
    try:
        with conn:
            print('Connected by', addr)
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                data = data.decode()
                request = data.split(',')

                if request[0] == 'register':
                    handle_register(conn, request[1], request[2])
                elif request[0] == 'login':
                    handle_login(conn, request[1], request[2])
                elif request[0] == 'send':
                    handle_new_message(request[1], request[2], request[3])
                elif request[0] == 'users':
                    handle_users(conn)
                elif request[0] == 'chat':
                    handler_chat(conn, request[1], request[2])
                else:
                    conn.send(str('Invalid request').encode())

    except ConnectionResetError:
        print(f'Connection to {addr} closed')


def handler_chat(conn, user1, user2):
    chat = dbh.get_chat(user1, user2)
    conn.send(str(chat).encode())


def handle_register(conn, username, password):
    user_id = dbh.new_user(username, password)
    if user_id == 0:
        conn.send(str(-1).encode())
    else:
        conn.send(str(user_id).encode())


def handle_login(conn, username, password):
    user_id = dbh.get_user_id(username)
    if user_id == 0:
        conn.send(str(-1).encode())
    elif not dbh.check_password(username, password):
        conn.send(str('Wrong Password').encode())
    else:
        conn.send(str(user_id).encode())


def handle_new_message(sender, recipient, message):
    dbh.new_message(sender, dbh.get_user_id(recipient),
                    message, datetime.datetime.now())


def handle_users(conn):
    users = dbh.get_users()
    ret = [[user.username, user.id] for user in users]
    conn.send(str(ret).encode())


def start_server():
    host = '172.31.180.253'
    port = 12345

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"Server started at {host}:{port}. Waiting for a connection...")

        while True:
            conn, addr = s.accept()
            client_thread = threading.Thread(target=handle_client,
                                             args=(conn, addr))
            client_thread.start()


if __name__ == "__main__":
    start_server()
