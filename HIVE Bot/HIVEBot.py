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
parser.add_argument('-H', '--hostname', default='192.168.44.109', help='Hostname to connect to')
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
        HHealth = HDat["Health"]
        OHealth = ODat["Health"]

        HAmmo = HDat["Ammo"]
        OAmmo = ODat["Ammo"]

        if HAmmo<OHealth:
                return(False)
        elif HHealth<OAmmo and HHealth == 1 and OHealth>1:
                return(False)
        else:
                return(True)

def goGoals(cur_x,cur_y):
        print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
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
        GameServer.sendMessage(ServerMessageTypes.TURNTURRETTOHEADING, {'Amount': direction})
        GameServer.sendMessage(ServerMessageTypes.FIRE)


#id 556


        
                                
# Main loop - read game messages, ignore them and randomly perform actions
targ_x = 0
targ_y = 0
snitch_present = 0
bank = 0
busy = False
nearestHPack = [0,0]
nearestAPack = [0,0]
ammo = 10
health = 5
nearest_enemy = 0
cur_x = 0
cur_y = 0
while True:

        

        data = GameServer.readMessage() 
        GameServer.sendMessage(ServerMessageTypes.TOGGLEFORWARD)

        if not(data == None):
                print(data)
                if(len(data)>1):
                        print(data)
                        if (data["Name"] == "HIVEbot"):
                                HiveID = data["Id"]
                                cur_x= data["X"]
                                cur_y = data["Y"]
                                ammo = data["Ammo"]
                                health = data["Health"]
                                if(cur_y> 100 or cur_y<-100):
                                        print("BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB")
                                        bank = False
                                
                        if len(data) == 1 and data["Id"] == HiveID:
                                GameServer.sendMessage(ServerMessageTypes.TURNTOHEADING,{'Amount':getAng(cur_x,cur_y,0,100)})
                                time.sleep(15)
                                targ_x = 0
                                targ_y = 0
                        if not(nearest_enemy == 0):
                                if nearest_enemy["Health"] == 0:
                                        print("HERERERERERERERERERRERERERERERERERER")
                                        bank = True
                                        nearest_enemy["Health"] = 5
                                        GameServer.sendMessage(ServerMessageTypes.TURNTOHEADING,{'Amount':getAng(cur_x,cur_y,0,100)})
                                        time.sleep(15)
                                        targ_x = 0
                                        targ_y = 0
                        if data["Type"] == "Tank" and not(data["Name"] == "HIVEbot"):
                                if not((nearest_enemy) == 0):
                                        if getDistance(cur_x,cur_y,nearest_enemy["X"],nearest_enemy["X"])>getDistance(cur_x,cur_y,data["X"],data["Y"]):
                                                nearest_enemy = data
                                else:
                                        nearest_enemy = data
                        if data["Type"] == "AmmoPickup":
                                nearestAPack[0] = (data["X"])
                                nearestAPack[1] = (data["Y"])
                                print(nearestAPack)
                        if data["Type"] == "HealthPickup":
                                nearestHPack[0] = (data["X"])
                                nearestHPack[1] =(data["Y"])

                                                
                                                

                                
                        
                                                
                                        


        

        if bank == True:
                GameServer.sendMessage(ServerMessageTypes.TURNTOHEADING,{'Amount':getAng(cur_x,cur_y,0,100)})
                goGoals(cur_x,cur_y)
        else:
                if ammo < 4 and health > 1:
                        if len(nearestAPack) > 0:
                                targ_x = nearestAPack[0]
                                targ_y = nearestAPack[1]
                elif not(nearest_enemy == 0):
                        if evalChance({"Health":health,"Ammo":ammo},nearest_enemy):
                                targ_x = nearest_enemy["X"]
                                targ_y = nearest_enemy["Y"]
                else:
                        if len(nearestHPack) > 0:
                                targ_x = nearestHPack[0]
                                targ_y = nearestHPack[1]
        print(targ_x,targ_y)
        
             
        GameServer.sendMessage(ServerMessageTypes.TURNTOHEADING,{'Amount':getAng(cur_x,cur_y,targ_x,targ_y)})                
        GameServer.sendMessage(ServerMessageTypes.FIRE)                       







	


    
