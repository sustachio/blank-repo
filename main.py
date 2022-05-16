import pygame
import socketio
import requests
import sys, os
from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

pygame.init()

sio = socketio.Client()
class App():
    def __init__(self):
        self.users = {}
        self.status = [25,25]

    def join(self):
        self.room = input("What room would you like to join? ")
        self.name = input("What would you like to be called? ")

        r = requests.get("https://online-game-backend.sustachio.repl.co/join", {
            "room": self.room,
            "name": self.name,
            "status": self.status,
        })

        # get json response
        try:
            response = r.json()
        except:
            print("internal server error")
            print(r.text)
            sys.exit()

        # name used exception
        if response["data"] == "name used":
            print("name used")
            self.join()
        else:
            print(response["data"])
            self.users = response["data"]

    def update(self, data):
        self.status = data
        sio.emit("update", {
            "room": self.room,
            "name": self.name,
            "status": data,
        })
        
    def leave(self):
      sio.emit("leave", {
        "name": self.name,
        "room": self.room
      })

app = App()
app.join()

@sio.event
def connect():
    # connect to websocket room
    print('connection established') 
    sio.emit("join", {
            "room": app.room,
            "name": app.name,
            "status": app.status,
        })

@sio.event
def update(data):
    print("recevied update", data)
    app.users.update(data)

@sio.event
def disconnect():
    print('disconnected from server')
    sys.exit()
    
@sio.event
def leave(data):
  del app.users[data]

sio.connect('https://online-game-backend.sustachio.repl.co')


class Player(pygame.sprite.Sprite):
  def __init__(self, app):
    super(Player, self).__init__()
    self.app = app
    
    self.surf = pygame.Surface((25,25))
    self.rect = self.surf.get_rect()
    
    self.surf.fill((255,0,0))
    
  def update(self, pressed_keys):
    if pressed_keys[K_UP]:
        self.rect.move_ip(0, -5)
    elif pressed_keys[K_DOWN]:
        self.rect.move_ip(0, 5)
    elif pressed_keys[K_LEFT]:
        self.rect.move_ip(-5, 0)
    elif pressed_keys[K_RIGHT]:
        self.rect.move_ip(5, 0)
    else:   return
    
    self.app.update(self.rect.topleft)
        
        
    # Keep player on the screen
    if self.rect.left < 0:
        self.rect.left = 0
    if self.rect.right > screen_width:
        self.rect.right = screen_width
    if self.rect.top <= 0:
        self.rect.top = 0
    if self.rect.bottom >= screen_height:
        self.rect.bottom = screen_height

screen_height = 600
screen_width = 800
pygame.display.set_caption('best game')

screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()

player = Player(app)


# ------ sprite groups -------
all_sprites = pygame.sprite.Group()

all_sprites.add(player)


running = True

while running:

  for event in pygame.event.get():
    if event.type == KEYDOWN:

      if event.key == K_ESCAPE:
        app.leave()
        running = False

    elif event.type == QUIT:
      app.leave()
      running = False 
      
  pressed_keys = pygame.key.get_pressed()
  player.update(pressed_keys)
  
  screen.fill((0,255,0))
  
  # display other players
  for i in app.users:
    if app.users[i] == app.name:  continue
    x = app.users[i]["status"][0]
    y = app.users[i]["status"][1]
    pygame.draw.rect(screen, (255,0,0), pygame.Rect(x, y, 25, 25))
      
  screen.blit(player.surf, player.rect)
  
  pygame.display.flip()
  clock.tick(30)

