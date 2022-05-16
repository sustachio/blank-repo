# pip install websocket-client
# pip install python-socketio

import socketio
import requests
import sys, os

# Thanks to https://stackoverflow.com/a/684344
def clear():
    os.system('cls' if os.name=='nt' else 'clear')

class App():
    def __init__(self):
        self.status=input("What should your starting status be? ")
        self.users = {}

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

app = App()
app.join()

sio = socketio.Client()

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

sio.connect('https://online-game-backend.sustachio.repl.co')
# sio.wait()
while True:
    clear()
    # print("\n")
    for name in app.users:
        print(f"{name}: {app.users[name]['status']}")
    status = input("status? ")
    app.update(status)
    