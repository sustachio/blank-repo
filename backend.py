# TO FIX:
# - never sending update to client

from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key_123456789_10'
socketio = SocketIO(app)

rooms = {
    "room1": {
        "user123": {"status": "foo"}
    }
}

# when a user tries to join a room
@app.route("/join", methods=["GET", "POST"])
def join():
  name = request.args["name"]
  status = request.args["status"]
  room = request.args["room"]
  
  try:
    users = rooms[room]

  # make the room
  except KeyError:
    rooms[room] = {}
    users = rooms[room]

  # if the name is used
  if name in users:
    return {"data" : "name used"}

  # add user to room
  users[name] = {"status": status}
  print(f"{name} has joined the room: {room}")
  
  return {"status" : "succsess", "data" : users} 

@socketio.on("join")
def joinroom(data):
  room = data["room"]
  status = data["status"]
  name = data["name"]

  join_room(room)
  emit("update", 
      {name : {"status":status}}, 
      to=room)

@socketio.on("leave")
def leave(data):
  room = data["room"]
  name = data["name"]
  
  leave_room(room)
  emit("leave", name)
  del rooms[room][name]

@socketio.on("update")
def update(data):
  print("recieved update", data)
  room = data["room"]
  name = data["name"]
  status=data["status"]
  
  # update in server
  rooms[room][name] = {"status": status}
  # update in clients
  emit("update", 
        {name : {"status" : status}}
        , to=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    print(f"{username} has left the room: {room}")
    emit("message", username + ' has left the room.', to=room)

@socketio.on('message')
def handle_message(data):
    print('received message: ' + data["data"])

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", debug=True)