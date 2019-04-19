import socket 
from _thread import *
import threading 
import os
import sys
from os import listdir
from os.path import isfile, join
import json

BUFFER_SIZE = 1024 
# Projects store all of the projects as a json/dict with their files, users. 
# Projects should be stored locally on the server as a folder containing the files
# JSON/DictStructure like:
# # projects = {
# 	'proj1' : {
# 		'users' : ['tim', 'tom', 'toom'],
# 		'file1' : {
# 			'isCheckedOut' : False,
# 			'isModifying' : False,
# 			'version' : 1
# 		}
# 	}
# # 	<projName2> : {...}
# # }
Projects = {}

#print_lock = threading.Lock() 

#The threaded function that will handle most of the parsing
def threaded(connection): 
	global Projects
	currentUser = "" #the username for the client.py in this thread
	selectedProj = "" #project the user wants to do stuff with
	while True: 

		# data received from client 
		incMessage = connection.recv(BUFFER_SIZE) 
		if not incMessage:
			print('Bye ', connection.getpeername()) 
			#print_lock.release()
			break
			
		#split the data into a list
		incStr = incMessage.decode()
		incList= incStr.split(" ")

		
		#check which function is requested
		if incList[0] == "LIST":
			files = List()
			filesStr = ",".join(files)
			connection.send(filesStr.encode())
		# some semester project stuff in here******************************************************************************************
		elif incList[0] == "USERNAME":
			currentUser = incList[1]
			response = currentUser+" successfully signed in."
			connection.send(response.encode())
		elif incList[0] == "LISTPROJ":
			projs = list(Projects.keys())
			projsStr = ",".join(projs)
			connection.send(projsStr.encode())
		elif incList[0] == "LISTUSERS":
			desProj = incList[1]
			projUsers = Projects[desProj]['users']
			usersStr = ",".join(projUsers)
			connection.send(usersStr.encode())
		elif incList[0] == "CHECKOUT":
			desProj = incList[1]
			projUsers = Projects[desProj]['users']
			if currentUser in projUsers:
				selectedProj = desProj
				msg = "You have checked out " + desProj
				connection.send(msg.encode())
			else:
				msg = "You cannot check out a project you are not a user of."
				connection.send(msg.encode())
			#Select a project. must be a user of the project. update 'selectedProj'
		elif(incList[0] == "ADDUSER"):
			print(incStr)
			userName = incList[1]
			if (userName not in Projects[selectedProj]['users']):
				Projects[selectedProj]['users'].append(userName)
				msg = "the user has been added"
			else:
				msg = "the user already exist as a contributing memeber"

			connection.send(msg.encode())
			#Add a user to a project. Current user must be a part of the project already
		elif(incList[0] == "CREATE"):
			print(incStr)
			projName = incList[1]
			print(list(Projects.keys()))
			print(projName)
			if projName in list(Projects.keys()):
				
				msg = projName + " already exists."
			else:
				print("hello")
				Projects[projName] = {'users' : [currentUser]}
				print("PLEASE")
				print(Projects)
				msg = "You have created " + projName
				StoreProject()
				projNameParam = "./" +projName + "/"
				MakeFolder(projName)
			connection.send(msg.encode())
			#Create a project. on the server side, add the current user to the list 
			#of users in this project
		elif(incList[0] == "PULL"):
			print(incStr)
			
		elif(incList[0] == "MODIFY"):
			print(incStr)
			#When a user wants to "check out" a file 
		elif(incList[0] == "PUSH"):
			print(incStr)
			#Returning a Checked out file. Only if the current user is the one who 
			#checked it out with "MODIFY"
		# ******************************************************************************************
		elif incList[0] == "RETRIEVE":
			print('command: RETRIEVE')
			try:
				f = open(incList[1], "rb")
				l = f.read(BUFFER_SIZE)
				while (l):
					connection.send(l)
					l = f.read(BUFFER_SIZE)
				f.close()
				print('sent file...')
			except IOError:
				noFile = "requested file does not exist..."
				print(noFile)
				connection.send(noFile.encode())
		elif incList[0] == "STORE":
			print('command: STORE')
			with open(incList[1], 'wb') as f:
				print ('file opened')
				connection.settimeout(2)
				#endlessly loops on .recv() if there is nothing in the socket, and you don't set a timeout. 
				#changed back to None after this loop, so other commands don't break. Probably a better way to avoid this problem..
				while True:
					print('receiving data...')
					try:
						data = connection.recv(BUFFER_SIZE)
					except socket.timeout:
						data = "end"
					if (data == "end"):
						f.close()
						print('Successfully got the file')
						break
					if (data.decode() == "requested file does not exist..."):
						print(data.decode())
						f.close()
						break
					# write data to a file
					f.write(data)
			f.close()
			connection.settimeout(None)
		elif incList[0] == "QUIT":
			connection.close()
			break
		else:
			connection.send("Invalid Message".encode())
		

	# connection closed 
	connection.close()


def RetrieveProject():
	"""Stores the Projects dict on a local file """
	with open('projects.json') as json_file:  
		Projects = json.load(json_file)
	return Projects

def MakeFolder(directory):
	try:
		if not os.path.exists(directory):
			os.makedirs(directory)
	except OSError:
		print ('Error: Creating directory. ' +  directory)

def StoreProject():
	"""Retrieves the Projects JSON from a local file """
	with open('projects.json', 'w') as outfile:  
		json.dump(Projects, outfile)

def List():
	files = []
	root = "."
	for item in os.listdir(root):
		if os.path.isfile(os.path.join(root, item)):
			files.append(item)
	return files

def Main():
	# StoreProject()
	global Projects
	Projects = RetrieveProject()
	print(Projects)
	host = "127.0.0.1" 


	# reverse a port on your computer 
	# in our case it is 8080 but it 
	# can be anything 
	port = 8080
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
	sock.bind((host, port)) 
	print("socket binded to post", port) 

	# put the socket into listening mode 
	sock.listen(5) 
	print("socket is listening") 

	# a forever loop until client wants to exit 
	while True: 

		# establish connection with client 
		connection, addr = sock.accept() 

		# lock acquired by client 
		#print_lock.acquire() 
		print('Connected to :', addr[0], ':', addr[1]) 

		# Start a new thread and return its identifier 
		start_new_thread(threaded, (connection,)) 
	sock.close() 


if __name__ == '__main__': 
	Main() 
