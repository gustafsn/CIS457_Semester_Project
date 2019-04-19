#!/usr/bin/env python

import socket
import os
from os import walk, mkdir
import sys
import json
import time

BUFFER_SIZE = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
isRunning = True
isConnected = False


def connect_to_server(ip, port):
    global isConnected
    global s

    try:
        s.connect((ip, port))
        s.settimeout(1)
        isConnected = True
    except ConnectionRefusedError:
        print("failed to establish a connection with: ", ip, "on port : ", port) 
        isConnected = False


def send_request(command):
    global s
    args = command.split(" ")

    if(command == "LIST"):
        s.send(command.encode())
        data = s.recv(BUFFER_SIZE)
        files = data.decode().split(",")
        print(*files, sep='\n')
        
    #NEW STUFF FOR SEMESTER PROJECT************************************************
    elif(args[0] == "USERNAME"):
        #updates the current user in the threaded connection on the server side
        s.send(command.encode())
        data = s.recv(BUFFER_SIZE)
        print(data.decode())
    elif(args[0] == "LISTPROJ"):
        s.send(command.encode())
        data = s.recv(BUFFER_SIZE)
        files = data.decode().split(",")
        print(*files, sep='\n')    
        
    elif args[0] == "LISTUSERS":
        s.send(command.encode())
        data = s.recv(BUFFER_SIZE)
        files = data.decode().split(",")
        print(*files, sep='\n')    
    elif(args[0] == "CHECKOUT"):
        print(command)
        s.send(command.encode())
        data = s.recv(BUFFER_SIZE)
        print(data.decode())
        #Select a project. must be a user of the project
    elif(args[0] == "ADDUSER"):
        print(command)
        s.send(command.encode())
        data = s.recv(BUFFER_SIZE)
        print(data.decode())
        #Add a user to a project. Current user must be a part of the project already
    elif(args[0] == "CREATE"):
        print(command)
        s.send(command.encode())
        data = s.recv(BUFFER_SIZE)
        print(data.decode())
        #Create a project. on the server side, add the current user to the list 
        #of users in this project
    elif(args[0] == "PULL"):
        s.send(command.encode())
        data = s.recv(BUFFER_SIZE)
        key = json.loads(data.decode())
        # test = json.loads(key)
        for something in key:
            for root, files in something.items():
                mkdir(root)
                for file in files:
                    path = root+"/"+file
                    # print("get"+file)
                    command = "RETRIEVE "+path
                    s.send(command.encode())
                    time.sleep(.5)
                    retr(path)

    elif(args[0] == "MODIFY"):
        print(command)
        s.send(command.encode())
        data = s.recv(BUFFER_SIZE)
        print(data.decode())
        #When a user wants to "check out" a file 
    elif(args[0] == "PUSH"):
        print(command)
        #Returning a Checked out file. Only if the current user is the one who 
        #checked it out with "MODIFY"
    #NEW STUFF FOR SEMESTER PROJECT************************************************
    elif(args[0] == "RETRIEVE"):
        print('command: RETRIEVE')
        s.send(command.encode())
        with open(args[1], 'wb') as f:
            print ('file opened')
            while True:
                print('receiving data...')
                try:
                    data = s.recv(BUFFER_SIZE)
                except socket.timeout:
                    data = "end"
                if (data == "end"):
                    f.close()
                    print('Successfully got the file')
                    break
                if (data.decode() == "requested file does not exist..."):
                    print(data.decode())
                    f.close()
                    os.remove(args[1])
                    break
                # write data to a file
                f.write(data)
        f.close()
    #STORE probably shouldnt be used
    elif(args[0] == "STORE"):
        print('command: STORE')
        try:
            f = open(args[1], "rb")
            s.send(command.encode())
            l = f.read(BUFFER_SIZE)
            while (l):
                s.send(l)
                l = f.read(BUFFER_SIZE)
            f.close()
            print('sent file...')
        except IOError:
            noFile = "requested file does not exist..."
            print(noFile)
            #s.send(noFile.encode())
    elif(args[0].upper() == "HELP"):
        print("\nPossible commands are: \nCONNECT <server name/IP address> <server port>,")
        print("LIST - to list file on this server")
        print("RETRIEVE <filename>")
        print("STORE <filename>")
        print("QUIT - to close the client")

def retr(file):
        with open(file, 'wb') as f:
            print ('file opened')
            while True:
                print('receiving data...')
                try:
                    data = s.recv(BUFFER_SIZE)
                except socket.timeout:
                    data = "end"
                if (data == "end"):
                    f.close()
                    print('Successfully got the file')
                    break
                if (data.decode() == "requested file does not exist..."):
                    print(data.decode())
                    f.close()
                    os.remove(file)
                    break
                # write data to a file
                f.write(data)
        f.close()

def main():
    global s 
    global isConnected
    global isRunning

    print("starting client...")

    while(isRunning):
        if(isConnected):
            command = input("enter a command: ")
            send_request(command)
            
        else:
            command = input("enter CONNECT followed by the ip and port in order to connect to the server: ")
            
    
            if (command.split(" ")[0] != "CONNECT"):
                print("must stablish connection first")
                continue
            else:
                args = command.split(" ")
                ip = args[1]
                port = int(args[2])
                connect_to_server(ip, port)
                username = input("enter your username (with no spaces): ")
                username = "USERNAME "+username
                send_request(username)
    
    
        if(command == "QUIT"):
            isRunning = False
    
    s.close()


main()
