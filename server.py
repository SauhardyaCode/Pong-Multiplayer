import socket
from _thread import *

SERVER = "192.168.1.4"
PORT = 5556

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((SERVER,PORT))
except socket.error as e:
    print("[Connection Error]",e)

s.listen(2)
print("[Listening] Server started")

SCREEN_W = 1200
SCREEN_H = 600

pos = [0,0]
ball = [0,0]
pressed = 0
ended = 0
restarted = 0
scored = 0
score=[0,0] #host, joiner

def make_data(tup):
    return ','.join(list(map(str,tup)))

def read_data(txt):
    return [int(x) for x in txt.split(',')]

def threaded_client(conn, player):
    global pos, players, pressed, ball,score, ended, restarted, scored

    conn.send(str.encode(str(player)))
    while True:
        try:
            data = read_data(conn.recv(2048).decode())
            code = data[0]

            if not data:
                players-=1
                player = 1-player
                print("[Disconnected]")
                break
            else:
                if code==0:
                    pos[player]=data[1]
                    reply = [pos[1-player]]
                elif code==1:
                    if player==0:
                        ball = [data[1], data[2]]
                        reply=[0]
                    else:
                        reply = [SCREEN_W-ball[0], ball[1]]
                elif code==2:
                    if player==0:
                        pressed = data[1]
                        reply = [0]
                    else:
                        reply = [pressed]
                elif code==3:
                    if player==0:
                        score= [data[1],data[2]]
                        reply=[0]
                    else:
                        reply = score
                elif code==4:
                    if player==0:
                        ended = data[1]
                        reply=[0]
                    else:
                        reply = [ended]
                elif code==5:
                    if player==0:
                        restarted = data[1]
                        reply = [0]
                    else:
                        reply = [restarted]
                elif code==6:
                    if player==0:
                        scored = data[1]
                        reply=[0]
                    else:
                        reply = [scored]
                elif code==7:
                    reply = [players]
                

            conn.sendall(str.encode(make_data(reply)))

        except Exception as e:
            players-=1
            player = 1-player
            print("[Disconnected]",e)
            break

    conn.close()

player = 0
players = 0
while True:
    conn, addr = s.accept()
    print("[Connected]",addr)

    players+=1
    start_new_thread(threaded_client, (conn, player))
    player = 1-player
    if players>2:
        print("[Disconnected] Too many players")
        break