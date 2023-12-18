from server import start_server
from client import start_client


def main():
    while True:
        soc = input("Server or Client? (s/c): ")
        if soc == 's':
            start_server()
            break
        elif soc == 'c' or soc == '':
            start_client()
            break
        else:
            print("Invalid input")


if __name__ == "__main__":
    main()
