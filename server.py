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
                data = conn.recv(1024).decode()
                if not data:
                    break
                print(data)
                request = list(eval(data))

                if request[0] == 'register':
                    handle_register(conn, request[1], request[2])
                elif request[0] == 'login':
                    handle_login(conn, request[1], request[2])
                elif request[0] == 'send':
                    handle_new_message(
                        dbh.get_user_id(request[1]), request[2], request[3]
                    )
                elif request[0] == 'users':
                    if len(request) >= 2:
                        handle_users(conn, request[1])
                    else:
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
        conn.send(
            str(f'Logged in as {dbh.get_users(user_id).username}').encode()
        )


def handle_login(conn, username, password):
    user_id = dbh.get_user_id(username)
    if user_id == 0:
        conn.send(str('User does not exist').encode())
    elif not dbh.check_password(username, password):
        conn.send(str('Wrong Password').encode())
    else:
        conn.send(
            str(f'Logged in as {dbh.get_users(user_id).username}').encode()
        )


def handle_new_message(sender, recipient, message):
    dbh.new_message(sender, dbh.get_user_id(recipient),
                    message, datetime.datetime.now())


def handle_users(conn, user_id=None):
    if user_id:
        user = dbh.get_users(user_id)
        ret = [user[0].id, user[0].username]
        conn.send(str(ret).encode())
    else:
        users = dbh.get_users()
        ret = [[user.id, user.username] for user in users]
        conn.send(str(ret).encode())


def start_server():
    host = 'localhost'
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
