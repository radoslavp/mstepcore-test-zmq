#!/usr/bin/env python3

import os
import time
import zmq
import importlib
import pickle
import datetime
import sys
import inspect
import json
from mstepcore_test_zmq.common import *
from pathlib import Path
from threading import Thread, Timer
# from multiprocessing import Process

SAVED_FILE = "vars.saved"
USER_MODULES_DIR = "/home/root/modules/"

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")
socket2 = context.socket(zmq.PUB)
socket2.bind("tcp://*:5556")

root = Path().cwd()

###########################

# API backend
# vars
def getVar(vars, var_name):
    if var_name in vars:
        debugPrint(f"'{var_name}' value '{vars[var_name]}' sent.")
        return vars[var_name]
    return False

def setVar(vars, var_name, value):
    vars[var_name] = value
    debugPrint(f"'{var_name}' set to '{value}'.")
    return True

# dirs
def mkDir(dir_path):
    p = Path(root / dir_path)
    if not p.exists():
        p.mkdir()
        debugPrint(f"crated dir '{root}/{dir_path}'.")
        return True
    return False

def rmDir(dir_path):
    p = Path(root / dir_path)
    if p.exists():
        p.rmdir()
        debugPrint(f"removed dir '{root}/{dir_path}'.")
        return True
    return False

def lsDir(dir_path):
    p = Path(root / dir_path)
    if p.exists():
        dir_list = []
        
        for p in p.iterdir():
            dir_list.append(p.as_posix())

        debugPrint(f"listed '{root}/{dir_path}'.")
        return dir_list
    return False

# files
def mkFile(file_path):
    p = Path(root / file_path)
    if not p.exists():
        p.touch()
        debugPrint(f"created file '{root}/{file_path}'.")
        return True
    return False

def rmFile(file_path):
    p = Path(root / file_path)
    if p.exists():
        p.unlink()
        debugPrint(f"removed file '{root}/{file_path}'.")
        return True
    return False

def rdFile(file_path):
    try:
        p = Path(root / file_path)
        with p.open(mode = "r") as file:
            debugPrint(f"sent content of '{root}/{file_path}'.")
            return file.read()
    except Exception as error:
        errorPrint(f"Error: {error}")
        return False

def wrFile(file_path, content):
    try:
        p = Path(root / file_path)
        with p.open(mode = "a") as file:
            file.write(content + "\n")
            # file.close()
            debugPrint(f"written '{content}' to '{root}/{file_path}'.")
            return True
    except Exception as error:
        errorPrint(f"Error: {error}")
        return False

# callbacks
def regCback(callbacks, event, module, callback):
    if event in callbacks:
        for cback in callbacks[event]:
            if cback[0] == module and cback[1] == callback:
                return False	# already registered
    
    callbacks[event] = []
    callbacks[event].append([module, callback])
    print(f"Callback '{callback}' from module '{module}' registered to event '{event}'.")
    return True
    
###########################

# internal thread functions
def saver(vars):
    print("Saver")
    # global vars

    while True:
        with open(SAVED_FILE, "wb") as file:
            debugPrint(f"vars: {vars}")
            pickle.dump(vars, file)
            debugPrint("saved")
        time.sleep(5)

def modulesInitializer(callbacks):
    print("modulesInitializer")
    
    p = Path(USER_MODULES_DIR)

    if p.exists():
        for p in p.iterdir():
            path_parts = p.as_posix().split(".")
            
            if len(path_parts) == 2 and path_parts[1] == "py":
                module_name = path_parts[0].split("/")[-1]
                print(f"module_name: {module_name}")
            
                module = importlib.import_module(module_name, package="modules")
                module.initModule(context)
        
def scheduler(events, callbacks):
    print("Scheduler")
    sys.path.append(USER_MODULES_DIR)
    
    print(f"Changing to {USER_MODULES_DIR}")
    os.chdir(USER_MODULES_DIR)
    
    sched_table = {}

    for name,e in events.items():
        x = time.strptime(e["interval"],'%H:%M:%S')
        y = time.strptime(e["shift"],'%H:%M:%S')
        interval_secs = int(datetime.timedelta(hours=x.tm_hour,minutes=x.tm_min,seconds=x.tm_sec).total_seconds())
        shift_secs = int(datetime.timedelta(hours=y.tm_hour,minutes=y.tm_min,seconds=y.tm_sec).total_seconds())
        
        sched_table[name] = [interval_secs, shift_secs]
        
    while True:
        curr_secs = int(time.time())
        
        for name,times in sched_table.items():            
            interval_secs = times[0]
            shift_secs = times[1]
            
            if curr_secs % interval_secs == 0:
                for event,cbacks in callbacks.items():
                    for cback in cbacks:
                        if event == name:
                            print(time.strftime("%H:%M:%S") + f" {name}: Scheduling callback {cback[0]}.{cback[1]} in {shift_secs} s")
                            module = importlib.import_module(cback[0], package="modules")
                    
                            c = None
                            funcs = inspect.getmembers(module, inspect.isfunction)
                            for f in funcs:
                                if f[0] == cback[1]:
                                    c = f[1]
                            if c:
                                Timer(shift_secs, c).start()
                            else:
                                print(f"Callback {cback[1]} not found.")
        
        time.sleep(1)

def publisher(vars):
    while True:
        if len(vars) > 0:
            if vars["temp"]:
                socket2.send_string(f"TEMP {vars['temp']}")
            if vars["hum"]:
                socket2.send_string(f"HUMI {vars['hum']}")
            if vars["pres"]:
                socket2.send_string(f"PRES {vars['pres']}")
                
            time.sleep(1)

###########################

def parseConfig():
    with open(os.path.dirname(__file__) + "/default_config.json", "r") as cfg_file:
        config = json.load(cfg_file)
        return config
    
    return False

def main():
    config = parseConfig()
    
    if not config:
        errorPrint("Failed to parse default config.")
        return False

    vars = {}
    callbacks = {}
    events = config["events"]    

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
    Thread(target = modulesInitializer, daemon = True, args=(callbacks, )).start()
    Thread(target = scheduler, daemon = True, args=(events, callbacks, )).start()
    Thread(target = publisher, daemon = True, args=(vars, )).start()
    
    print("Running modules.")
    project_dir = os.path.dirname(__file__)
    modules_list = os.listdir(f"{project_dir}/modules")
    modules_threads = {}
    for module_name in modules_list:
        if module_name == "__init__.py":
            continue

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
        elif message_len == 4:
            arg1 = message[1]
            arg2 = message[2]
            arg3 = message[3]
            if message[0] == "regCback":
                res = regCback(callbacks, arg1, arg2, arg3)
                
        socket.send_string(str(res))

if __name__ == "__main__":
    main()
