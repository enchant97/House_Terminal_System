from HomeTerminal import create_app, socketio

if __name__ == "__main__":
    socketio.run(create_app(), host="localhost", port=5050, debug=True)
    print("quit")