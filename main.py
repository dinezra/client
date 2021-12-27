from socket import *
from scapy.all import *
import select
import struct
import traceback
import sys
import warnings

class Client:
    def __init__(self, name):
        """
        :param name: Team name
        :return: None
        """
        self.teamName = name
        self.clientSocket = None
        self.serverSocket = None

    def start_client(self):
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        print("Client started, listening for offer requests")
        print(f'My IP: {get_if_addr("eth1")}')
        self.clientSocket.bind(("", 13117))
        while True:
            data_raw, addr = self.clientSocket.recvfrom(1024)
            try:
                print(f'got from {addr}')
                data = struct.unpack('Ibh', data_raw)
                if hex(data[0]) == "0xabcddcba" and hex(data[1]) == "0x2":
                    print(f'Received offer from {addr[0]}, attempting to connect...')
                    self.Start_client_tcp(addr[0], int(data[2]))
                    return
            except struct.error:
                pass
            except Exception as err:
                print(err)
    def wait_for_game(self):
        """
        Waiting for message from Server that start the game.
        :return: None
        """
        msg = ""
        self.serverSocket.setblocking(False)
        while len(msg) == 0:
            try:
                recive = self.serverSocket.recv(1024)
                msg = recive.decode("utf-8")
                if msg:
                    print(msg)

            except Exception as ex:
                if str(ex) == "[Errno 35] Resource temporarily unavailable":
                    time.sleep(0)
                    continue
                time.sleep(0.3)

    def Start_client_tcp(self, server_name, server_port):
        """
        Connecting to a server with TCP
        :param server_name: Server to connect name
        :param server_port: Server to connect port
        :return: None
        """
        print(f"connected to server {server_name} on port {server_port}")
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.connect((server_name, server_port))
        self.serverSocket.send(str(self.teamName).encode())
        self.wait_for_game()
        try:
            self.game_in_progress()
        except Exception as e:
            os.system("stty -raw echo")
            traceback.print_exc()
            print("Activate client_tcp")
        self.clodse()

    def game_in_progress(self):
        """
        Sends to Server the answer while game is on.
        Waiting for game to end.
        :return: None
        """
        message_ = ""
        os.system("stty raw -echo")
        while len(message_) == 0:
            try:
                message = self.serverSocket.recv(1024)
                message_ += message.decode("utf-8")
                if message_:
                    break
            except Exception as ex:
                # print("game_in_progress")
                if str(ex) == "[Errno 35] Resource temporarily unavailable":
                    time.sleep(0.01)
                    # continue
                time.sleep(0.01)
            data, _, _ = select.select([sys.stdin], [], [], 0)
            if data:
                data_to_send = sys.stdin.read(1)
                self.serverSocket.send(data_to_send.encode())
        os.system("stty -raw echo")
        print(message_)

    def clodse(self):
        """
        Closes the sockets in the end of the game.
        :return: None
        """
        print("Game Ended")

        time.sleep(1)
        self.serverSocket.close()
        self.clientSocket.close()

def main():
        while True:
            client = Client("DG-Hac")
            client.start_client()
            time.sleep(3)



if __name__ == "__main__":
        main()
        warnings.filterwarnings('ignore')
