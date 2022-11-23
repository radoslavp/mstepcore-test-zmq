#!/usr/bin/env python3

import os
import time
import zmq
import importlib
import pickle
from pathlib import Path
from threading import Thread
# from multiprocessing import Process

SAVED_FILE = "vars.saved"

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

root = Path().cwd()

# API backend
# vars
def getVar(vars, var_name):
    if var_name in vars:
        print(f"'{var_name}' value '{vars[var_name]}' sent.")
        return vars[var_name]
    return False

def setVar(vars, var_name, value):
    vars[var_name] = value
    print(f"'{var_name}' set to '{value}'.")
    return True

# dirs
def mkDir(dir_path):
    p = Path(root / dir_path)
    if not p.exists():
        p.mkdir()
        print(f"crated dir '{root}/{dir_path}'.")
        return True
    return False

def rmDir(dir_path):
    p = Path(root / dir_path)
    if p.exists():
        p.rmdir()
        print(f"removed dir '{root}/{dir_path}'.")
        return True
    return False

def lsDir(dir_path):
    p = Path(root / dir_path)
    if p.exists():
        dir_list = []
        
        for p in p.iterdir():
            dir_list.append(p.as_posix())

        print(f"listed '{root}/{dir_path}'.")
        return dir_list
    return False

# files
def mkFile(file_path):
    p = Path(root / file_path)
    if not p.exists():
        p.touch()
        print(f"created file '{root}/{file_path}'.")
        return True
    return False

def rmFile(file_path):
    p = Path(root / file_path)
    if p.exists():
        p.unlink()
        print(f"removed file '{root}/{file_path}'.")
        return True
    return False

def rdFile(file_path):
    try:
        p = Path(root / file_path)
        with p.open(mode = "r") as file:
            print(f"sent content of '{root}/{file_path}'.")
            return file.read()
    except Exception as error:
        print(f"Error: {error}")
        return False

def wrFile(file_path, content):
    try:
        p = Path(root / file_path)
        with p.open(mode = "a") as file:
            file.write(content + "\n")
            # file.close()
            print(f"written '{content}' to '{root}/{file_path}'.")
            return True
    except Exception as error:
        print(f"Error: {error}")
        return False

def saver(vars):
    print("Saver")
    # global vars

    while True:
        with open(SAVED_FILE, "wb") as file:
            print(f"vars: {vars}")
            pickle.dump(vars, file)
            print("saved")
        time.sleep(5)

def main():
    vars = {}

    print("Loading saved variables from file.")
    try:
        with open(SAVED_FILE, "rb") as file:
            vars = pickle.load(file)
            print("loaded")
    except EOFError:
        print("nothing was saved.")
    print(f"vars: {vars}")

    print("Running internal threads:")
    Thread(target = saver, daemon = True, args=(vars, )).start()


    print("Running modules.")
    project_dir = os.path.dirname(__file__)
    modules_list = os.listdir(f"{project_dir}/modules")
    modules_threads = {}
    for module_name in modules_list:
        if ".py" in module_name:
            module_name = module_name.strip(".py")
            print(f"Loading module: {module_name}")
            module = f".modules.{module_name}"
            module = importlib.import_module(module, package = "mstepcore_test_zmq")
            modules_threads[module_name] = Thread(target = module.module_run, args = (context,), daemon = True)
            print(f"Running module: {module_name}")
            modules_threads[module_name].start()

    print("Running main loop.")
    while True:
        res = False
        message = socket.recv_string()
        message = message.split("<delim>")
        message_len = len(message)

        if message_len == 1:
            pass
        elif message_len == 2:
            arg = message[1]
            if message[0] == "getVar":
                res = getVar(vars, arg)
            elif message[0] == "mkDir":
                res = mkDir(arg)
            elif message[0] == "rmDir":
                res = rmDir(arg)
            elif message[0] == "lsDir":
                res = lsDir(arg)
            elif message[0] == "mkFile":
                res = mkFile(arg)
            elif message[0] == "rmFile":
                res = rmFile(arg)
            elif message[0] == "rdFile":
                res = res = rdFile(arg)
        elif message_len == 3:
            arg1 = message[1]
            arg2 = message[2]
            if message[0] == "setVar":
                res = setVar(vars, arg1, arg2)
            elif message[0] == "wrFile":
                res = wrFile(arg1, arg2)

        socket.send_string(str(res))

if __name__ == "__main__":
    main()