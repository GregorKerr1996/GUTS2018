#!/usr/bin/python

import json
import socket
import logging
import binascii
import struct
import argparse
import random
import time
import math


class ServerMessageTypes(object):
	TEST = 0
	CREATETANK = 1
	DESPAWNTANK = 2
	FIRE = 3
	TOGGLEFORWARD = 4
	TOGGLEREVERSE = 5
	TOGGLELEFT = 6
	TOGGLERIGHT = 7
	TOGGLETURRETLEFT = 8
	TOGGLETURRETRIGHT = 9
	TURNTURRETTOHEADING = 10
	TURNTOHEADING = 11
	MOVEFORWARDDISTANCE = 12
	MOVEBACKWARSDISTANCE = 13
	STOPALL = 14
	STOPTURN = 15
	STOPMOVE = 16
	STOPTURRET = 17
	OBJECTUPDATE = 18
	HEALTHPICKUP = 19
	AMMOPICKUP = 20
	SNITCHPICKUP = 21
	DESTROYED = 22
	ENTEREDGOAL = 23
	KILL = 24
	SNITCHAPPEARED = 25
	GAMETIMEUPDATE = 26
	HITDETECTED = 27
	SUCCESSFULLHIT = 28
    
	strings = {
		TEST: "TEST",
		CREATETANK: "CREATETANK",
		DESPAWNTANK: "DESPAWNTANK",
		FIRE: "FIRE",
		TOGGLEFORWARD: "TOGGLEFORWARD",
		TOGGLEREVERSE: "TOGGLEREVERSE",
		TOGGLELEFT: "TOGGLELEFT",
		TOGGLERIGHT: "TOGGLERIGHT",
		TOGGLETURRETLEFT: "TOGGLETURRETLEFT",
		TOGGLETURRETRIGHT: "TOGGLETURRENTRIGHT",
		TURNTURRETTOHEADING: "TURNTURRETTOHEADING",
		TURNTOHEADING: "TURNTOHEADING",
		MOVEFORWARDDISTANCE: "MOVEFORWARDDISTANCE",
		MOVEBACKWARSDISTANCE: "MOVEBACKWARDSDISTANCE",
		STOPALL: "STOPALL",
		STOPTURN: "STOPTURN",
		STOPMOVE: "STOPMOVE",
		STOPTURRET: "STOPTURRET",
		OBJECTUPDATE: "OBJECTUPDATE",
		HEALTHPICKUP: "HEALTHPICKUP",
		AMMOPICKUP: "AMMOPICKUP",
		SNITCHPICKUP: "SNITCHPICKUP",
		DESTROYED: "DESTROYED",
		ENTEREDGOAL: "ENTEREDGOAL",
		KILL: "KILL",
		SNITCHAPPEARED: "SNITCHAPPEARED",
		GAMETIMEUPDATE: "GAMETIMEUPDATE",
		HITDETECTED: "HITDETECTED",
		SUCCESSFULLHIT: "SUCCESSFULLHIT"
	}
    
	def toString(self, id):
		if id in self.strings.keys():
			return self.strings[id]
		else:
			return "??UNKNOWN??"


class ServerComms(object):
	'''
	TCP comms handler
	
	Server protocol is simple:
	
	* 1st byte is the message type - see ServerMessageTypes
	* 2nd byte is the length in bytes of the payload (so max 255 byte payload)
	* 3rd byte onwards is the payload encoded in JSON
	'''
	ServerSocket = None
	MessageTypes = ServerMessageTypes()
	
	
	def __init__(self, hostname, port):
		self.ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.ServerSocket.connect((hostname, port))
	
	def readMessage(self):
		'''
		Read a message from the server
		'''
		messageTypeRaw = self.ServerSocket.recv(1)
		messageLenRaw = self.ServerSocket.recv(1)
		messageType = struct.unpack('>B', messageTypeRaw)[0]
		messageLen = struct.unpack('>B', messageLenRaw)[0]
		
		if messageLen == 0:
			messageData = bytearray()
			messagePayload = None
		else:
			messageData = self.ServerSocket.recv(messageLen)
			logging.debug("*** {}".format(messageData))
			messagePayload = json.loads(messageData.decode('utf-8'))
			
		logging.debug('Turned message {} into type {} payload {}'.format(
			binascii.hexlify(messageData),
			self.MessageTypes.toString(messageType),
			messagePayload))
		return messagePayload
		
	def sendMessage(self, messageType=None, messagePayload=None):
		'''
		Send a message to the server
		'''
		message = bytearray()
		
		if messageType is not None:
			message.append(messageType)
		else:
			message.append(0)
		
		if messagePayload is not None:
			messageString = json.dumps(messagePayload)
			message.append(len(messageString))
			message.extend(str.encode(messageString))
			    
		else:
			message.append(0)
		
		logging.debug('Turned message type {} payload {} into {}'.format(
			self.MessageTypes.toString(messageType),
			messagePayload,
			binascii.hexlify(message)))
		return self.ServerSocket.send(message)


# Parse command line args
parser = argparse.ArgumentParser()
parser.add_argument('-d', '--debug', action='store_true', help='Enable debug output')
parser.add_argument('-H', '--hostname', default='127.0.0.1', help='Hostname to connect to')
parser.add_argument('-p', '--port', default=8052, type=int, help='Port to connect to')
parser.add_argument('-n', '--name', default='HIVEbot', help='Name of bot')
args = parser.parse_args()

# Set up console logging
if args.debug:
	logging.basicConfig(format='[%(asctime)s] %(message)s', level=logging.DEBUG)
else:
	logging.basicConfig(format='[%(asctime)s] %(message)s', level=logging.INFO)


# Connect to game server
GameServer = ServerComms(args.hostname, args.port)

# Spawn our tank
logging.info("Creating tank with name '{}'".format(args.name))
GameServer.sendMessage(ServerMessageTypes.CREATETANK, {'Name': args.name})
            

def getDistance(x1,y1,x2,y2):
        heading_x = x2-x1
        heading_y = y2-y1
        return(math.sqrt((heading_x*heading_x) + (heading_y*heading_y)))

def getAng(x1,y1,x2,y2):
        t1 = math.atan2(y2-y1,x2-x1)
        t1 = (t1*180)/math.pi
        t1 = (t1-360)%360
        return(360-t1)


def evalChance(HDat,ODat):
        HHealth = HData["Health"]
        OHealth = ODat["Health"]

        HAmmo = HData["Ammo"]
        OAmmo = ODat["Ammo"]

        if HAmmo<OHealth:
                return(False)
        elif HHealth<OAmmo and HHealth == 1 and OHealth>1:
                return(False)
        else:
                return(True)

def goGoals(cur_x,cur_y):
        targ_x = 0
        if getDistance(cur_x,cur_y,0,100)>122:
                targ_y = -100
        else:
                targ_y = 100


def shoot(cur_x,cur_y,tar_x,tar_y):
    #Turn turret to tar x tary
    #shoot

    distance = getDistance(cur_x,cur_y,tar_x,tar_y)

    if (distance < 50):
        direction = getAng(cur_x, cur_y, targ_x, targ_y)
        GameServer.sendMessage(ServerMessageTypes.TURNTOHEADING, {'Amount': direction})
        GameServer.sendMessage(ServerMessageTypes.FIRE)


#id 556


        
                                
# Main loop - read game messages, ignore them and randomly perform actions
targ_x = 0
targ_y = 0
snitch_present = 0
bank = 0
busy = False
nearestHPack = []
nearestAPack = []
while True:

        

        data = GameServer.readMessage() 
        GameServer.sendMessage(ServerMessageTypes.TOGGLEFORWARD)

        if not(data == None):
                print(data)
                if(len(data)>1):
                        print(data)
                        if (data["Name"] == "HIVEbot"):
                                cur_x= data["X"]
                                cur_y = data["Y"]
                                ammo = data["Ammo"]
                                health = data["Health"]
                        if data["Type"] == "AmmoPickup":
                                if len(nearestAPack)<1:
                                        nearestAPack.append(data["X"])
                                        nearestAPack.append(data["Y"])
                                else:
                                        if getDistance(cur_x,cur_y,nearestAPack[0],nearestAPack[1])>getDistance(cur_x,cur_y,data["X"],data["Y"]):
                                                nearestAPack[0] = data["X"]
                                                nearestAPack[1] = data["Y"]
                        if data["Type"] == "HealthPickup":
                                if len(nearestHPack)<1:
                                        nearestHPack.append(data["X"])
                                        nearestHPack.append(data["Y"])
                                else:
                                        if getDistance(cur_x,cur_y,nearestHPack[0],nearestHPack[1])>getDistance(cur_x,cur_y,data["X"],data["Y"]):
                                                nearestHPack[0] = data["X"]
                                                nearestHPack[1] = data["Y"]
                        
                                                
                                        




        if bank:
                busy = True
                goGoals(cur_x,cur_y)

                if not(busy):
                        if ammo < 6  and health > 1:
                                targ_x = nearestAPack[0]
                                targ_y = nearestAPack[1]
                else:
                        targ_x = nearestHPack[0]
                        targ_y = nearestHPack[1]
                
                                
                                

                        #if data["Type"] == "AmmoPickup":
                         #       targ_x = data["X"]
                          #      targ_y = data["Y"]
                                
                        #if data["Type"] == "HealthPickup":
                         #       targ_x = data["X"]
                          #      targ_y = data["Y"]

                        #if data["Type"] == "Snitch":
                         #       snitch_present = 1
                          #      print(data)
                           #     targ_x = data["X"]
                            #    targ_y = data["Y"]

                        #if GameServer.sendMessage(ServerMessageTypes.SNITCHPICKUP):
                                #targ_x = 0
                                #if getDistance(cur_x,cur_y,0,100)>122:
                                        #targ_y = -100
                                #else:
                                        #targ_y = 100

        
                        ##GET A DIRECTION TO TRAVEL IN
                        ##CHANGE DIRECTION UNTIL FACINGgit 
                        #print(targ_x,targ_y)
                        GameServer.sendMessage(ServerMessageTypes.TURNTOHEADING,{'Amount':getAng(cur_x,cur_y,targ_x,targ_y)})

                        if cur_x == 0.0 and cur_y == 0.0:
                                GameServer.sendMessage(ServerMessageTypes.STOPMOVE)
                                GameServer.sendMessage(ServerMessageTypes.STOPTURN)
                        #GameServer.sendMessage(ServerMessageTypes.FIRE)
                        #GameServer.sendMessage(ServerMessageTypes.MOVEFORWARDDISTANCE, {'Amount': 100})
                        #GameServer.sendMessage(ServerMessageTypes.TOGGLELEFT,{'Amount':50})
                        #print("HERE")
                        #GameServer.sendMessage(ServerMessageTypes.FIRE)





	


    
