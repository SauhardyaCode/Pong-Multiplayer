import socket

def make_data(tup):
    return ','.join(list(map(str,tup)))

def read_data(txt):
    return [int(x) for x in txt.split(',')]

class Network():
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "192.168.1.4"
        self.port = 5556
        self.addr = (self.server,self.port)
        self.player = int(self.connect())
        self.flag = 0

        print(f"Player {self.player+1} joined")
    
    def connect(self):
        try:
            self.client.connect(self.addr)
            return self.client.recv(2048).decode()
        except Exception as e:
            print("[Connection Error]",e)
        
    def send(self, data):
        self.client.send(str.encode(data))
        try:
            data = read_data(self.client.recv(2048).decode())
            return data
        except socket.error as e:
            print("[No Data Received]",e)
