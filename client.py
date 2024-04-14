import pygame, random, os
from pygame.locals import *
import pygame.mixer as mixer
from network import Network

pygame.init()
mixer.init()
clock = pygame.time.Clock()
PATH = os.path.dirname(__file__)
FPS = 60

SCREEN_W = 1200
SCREEN_H = 600
BG_COLOR = (30,30,30)
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("PONG")
flag = 0

player_dim = (10, 110)
ball_rad = 12
ball_rad_l = ball_rad
ball_rad_r = ball_rad
boundary = pygame.Rect(0,0,SCREEN_W,SCREEN_H)
opponent = pygame.Rect(0,0,*player_dim)
opponent.center = (10,SCREEN_H/2)
player = pygame.Rect(0,0,*player_dim)
player.center = (SCREEN_W-10,SCREEN_H/2)
ball = pygame.Rect(0,0,ball_rad*2, ball_rad*2)
ball.center = (SCREEN_W/2, SCREEN_H/2)

speed = 11
p_speed_r = 0
b_speed_x = 0
b_speed_y = 0
score = [0,0]
TARGET = 11
target = TARGET

verdana = pygame.font.SysFont("verdana", 40)
comicsans = pygame.font.SysFont("comicsans", 30)
comics = pygame.font.SysFont("comicsans", 20)

mute=False
players = 0

def draw_screen():
    global ball
    pygame.draw.rect(screen, (200,200,0), boundary, 1)
    pygame.draw.aaline(screen, (255,255,255), (SCREEN_W/2, 0), (SCREEN_W/2, SCREEN_H))
    pygame.draw.rect(screen, (0,200,100), ball, 0, ball_rad)
    pygame.draw.rect(screen, (100,100,100), opponent)
    pygame.draw.rect(screen, (100,100,100), player)
    left = comics.render("LEFT", 1, (50,200,150), BG_COLOR)
    right = comics.render("RIGHT", 1, (50,200,150), BG_COLOR)
    match = comics.render(f"Target: {target}", 1, (50,200,150), BG_COLOR)
    screen.blit(left, (10,10))
    screen.blit(match, ((SCREEN_W-match.get_width())/2, SCREEN_H-match.get_height()-20))
    screen.blit(right, (SCREEN_W-right.get_width()-10,10))

def reset_ball():
    global b_speed_x,b_speed_y
    b_speed_x = speed*random.choice((-1,1))
    b_speed_y = speed*random.choice((-1,1))

def bounce():
    global b_speed_x, b_speed_y
    ball.centerx+=b_speed_x
    ball.centery+=b_speed_y

    if client.player==0:
        if ball.centerx>=SCREEN_W or ball.centerx<=0:
            code=6
            client.send(make_data([code,1]))

            if ball.centerx<=0:
                score[1]+=1
            else:
                score[0]+=1
            ball.center = (SCREEN_W/2, SCREEN_H/2)
            reset_ball()
            host_permit = 1  
        else:
            code=6
            client.send(make_data([code,0]))
            host_permit = 0
    else:
        code=6
        scored = client.send(make_data([code]))[0]


    if (client.player==1 and scored) or (client.player==0 and host_permit):
        mixer.music.load(PATH+"/miss.mp3")
        if not mute:
            mixer.music.play()
        screen.fill((255,0,0))

    if ball.centery>=SCREEN_H or ball.centery<=0:
        b_speed_y*=-1
        mixer.music.load(PATH+"/bounce.mp3")
        if not mute:
            mixer.music.play()
    if ball.colliderect(opponent) or ball.colliderect(player):
        b_speed_x*=-1
        mixer.music.load(PATH+"/hit.mp3")
        if not mute:
            mixer.music.play()

def move():
    global p_speed_r
    player.y+=p_speed_r
    if player.y>=(SCREEN_H-player.height):
        p_speed_r=0
        player.y=SCREEN_H-player.height-1
    if player.y<=0:
        p_speed_r=0
        player.y=0

def show_score():
    l = str(score[0])
    r = str(score[1])
    while len(l)<len(r):
        l='0'+l
    while len(l)>len(r):
        r='0'+r
    text = verdana.render(f"{l}  :  {r}", 1, (200,100,100), BG_COLOR)
    screen.blit(text, ((SCREEN_W-text.get_width())/2,10))

def winner():
    global b_speed_x, b_speed_y, p_speed_l, p_speed_r, flag

    code=4
    if client.player==0:
        if score[0]==target or score[1]==target:
            flag = 2
            client.send(make_data([code, 1]))
        else:
            client.send(make_data([code, 0]))
    else:
        ended = client.send(make_data([code]))[0]
        if ended:
            flag = 2
    
    
    if flag==2:
        b_speed_x, b_speed_y, p_speed_l, p_speed_r = 0,0,0,0
        screen.fill(BG_COLOR)
        if score[0]>score[1]:
            msg = "Oops! You lost the game!"
        else:
            msg = "Hooray! You won the game!"
        
        _scorel = score[0]
        _scorer = score[1]

        if client.player==1:
            if score[0]>score[1]:
                _scorel = score[0]+1
            else:
                _scorer = score[1]+1

        text = comicsans.render(msg, 1, (255,255,255), BG_COLOR)
        text2 = verdana.render(f"{_scorel}  :  {_scorer}", 1, (200,100,100), BG_COLOR)
        if client.player==0:
            text3 = comics.render(f"(Press SPACEBAR to Replay)", 1, (200,200,100), BG_COLOR)
        else:
            text3 = comics.render(f"(Wait for your Opponent to Replay)", 1, (200,200,100), BG_COLOR)
        screen.blit(text, ((SCREEN_W-text.get_width())/2, (SCREEN_H-text.get_height())/2))
        screen.blit(text2, ((SCREEN_W-text2.get_width())/2, 20))
        screen.blit(text3, ((SCREEN_W-text3.get_width())/2, (SCREEN_H-text.get_height())/2+text3.get_height()*5))

def lift_target():
    global target
    if score[0] == score[1] and score[0] == target-1:
        target+=1

def instruct():
    if client.player==0:
        text = comics.render("(Press SPACEBAR to Start)", 1, (200,200,100), BG_COLOR)
    else:
        text = comics.render("(Wait for your Opponent to start)", 1, (200,200,100), BG_COLOR)
    if flag == 0:
        screen.blit(text, ((SCREEN_W-text.get_width())/2, SCREEN_H-text.get_height()-20))

def make_data(tup):
    return ','.join(list(map(str,tup)))

def read_data(txt):
    return [int(x) for x in txt.split(',')]


client = Network()
pressed=0
while True:
    screen.fill(BG_COLOR)
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            pygame.quit()
            exit()

        elif ev.type == KEYDOWN:
            if ev.key==K_UP or ev.key==K_w:
                p_speed_r=-speed-1
            if ev.key==K_DOWN or ev.key==K_s:
                p_speed_r=speed+1
        elif ev.type == KEYUP:
            if (ev.key==K_UP or ev.key==K_DOWN or ev.key==K_w or ev.key==K_s):
                p_speed_r=0
            elif ev.key == K_SPACE and client.player==0 and players==2:
                if flag == 2:
                    flag = 0
                    code=5
                    client.send(make_data([code, 1]))
                    score = [0,0]
                    target = TARGET
                elif flag == 0 and client.player==0:
                    flag = 1
                    code=2
                    client.send(make_data([code, 1]))
                    reset_ball()
                    pygame.time.delay(1000)
            elif ev.key==K_m:
                mute=not mute

    '''code
    0 --> player position
    1 --> ball position
    2 --> game state (started 0-->1)
    3 --> score
    4 --> game state (ended 1-->2)
    5 --> game state (restart 2-->0)
    6 --> someone scored
    7 --> player count
    '''

    code=0
    reply=client.send(make_data([code, player.centery]))
    opponent.centery=reply[0]

    code=7
    players=client.send(make_data([code]))[0]

    if client.player==0:
        code=2
        client.send(make_data([code, 0]))
            
        if flag==1 or flag==0:
            code=1
            client.send(make_data([code, *ball.center]))

            code=3
            client.send(make_data([code,*score]))

        if flag==1:
            code=5
            client.send(make_data([code, 0]))

    else:
        code=2
        pressed = client.send(make_data([code]))[0]
        if pressed:
            flag = 1

        if flag==2:
            code=5
            restarted = client.send(make_data([code]))[0]
            if restarted:
                flag = 0
                score = [0,0]
                target = TARGET

        if flag==1 or flag==0:
            code=1
            ball.center = client.send(make_data([code]))

            code=3
            reply = client.send(make_data([code]))
            score = [reply[1], reply[0]]

    show_score()
    draw_screen()
    bounce()
    move()
    lift_target()
    instruct()
    winner()
    pygame.display.update()
    clock.tick(FPS)