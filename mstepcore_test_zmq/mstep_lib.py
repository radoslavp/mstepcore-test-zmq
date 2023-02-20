import zmq

class MstepLib():
    def __init__(self, context):
        self.context = context
        #  Socket to talk to server
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect("tcp://localhost:5555")

    # helpers
    def processCommand(self, command):
        command = "<delim>".join(command)
        self.socket.send_string(command)
        rep = self.socket.recv_string()
        return rep

    # API frontend - commands
    # vars
    def getVar(self, var_name):
        command = ["getVar", var_name]
        return self.processCommand(command)

    def setVar(self, var_name, value):
        command = ["setVar", var_name, str(value)]
        self.processCommand(command)

    # dirs
    def lsDir(self, dir_path):
        command = ["lsDir", dir_path]
        self.processCommand(command)

    def mkDir(self, dir_path):
        command = ["mkDir", dir_path]
        self.processCommand(command)

    def rmDir(self, dir_path):
        command = ["rmDir", dir_path]
        self.processCommand(command)

    # files
    def mkFile(self, file_path):
        command = ["mkFile", file_path]
        self.processCommand(command)

    def rmFile(self, file_path):
        command = ["rmFile", file_path]
        self.processCommand(command)

    def rdFile(self, file_path):
        command = ["rmdFile", file_path]
        self.processCommand(command)

    def wrFile(self, file_path, content):
        command = ["wrFile", file_path, str(content)]
        self.processCommand(command)
    
    # callbacks
    def regCback(self, event, module, callback):
        command = ["regCback", event, module, callback]
        self.processCommand(command)
