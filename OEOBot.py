import threading
import time
import os
import random
import json
import discord
import socket
from datetime import datetime
from dotenv import load_dotenv
from nested_lookup import nested_lookup
#from discord.ext.commands import Bot
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
client = discord.Client()
UDP_IP = "127.0.0.1"
UDP_PORT = 8095
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
heartbeatTimeout = 120
heart_dict = 0
missionInfo_dict = 0
playerInfoSt_dict = 0
playerInfoCont_dict = 0
playersOnline = 0
slotInfoSt_dict = 0
slotInfoCont_dict = 0
servState = 0
lastHeartbeat = 0

def toGo():
    timeRaw = heart_dict.get('time_left')
    return conversion(timeRaw)
 
def conversion(sec):
   sec_value = sec % (24 * 3600)
   hour_value = sec_value // 3600
   sec_value %= 3600
   mins = sec_value // 60
   sec_value %= 60
   strRetunrn ="{} hrs and {} mins.".format(hour_value, mins)
   return strRetunrn

def getMisTime():
    timeRaw = heart_dict.get('time')
    ServHour = timeRaw.get('hour')
    hourInS = ServHour * 3600
    ServMin =  timeRaw.get('min')
    return "{:02d}:{:02d}".format(ServHour, ServMin)

def checkType(recvMessage_dict):
    global heart_dict, missionInfo_dict, playerInfoSt_dict, playerInfoCont_dict, slotInfoSt_dict, slotInfoCont_dict, servState, lastHeartbeat, playersOnline
    type = recvMessage_dict.get("type")
    print('Message type: {}'.format(type))
    if type == 1:
        heart_dict = recvMessage_dict.get("data", "Please wait for this information to be intialised and try again soon")
        lastHeartbeat = time.time()
    elif type == 2:
        missionInfo_dict = recvMessage_dict.get("data", "Please wait for this information to be intialised and try again soon")
    elif type == 3:
        playerInfoSt_dict = recvMessage_dict.get("data", "Please wait for this information to be intialised and try again soon")
        player_dict = playerInfoSt_dict.get('players')
        playerList = nested_lookup('name', player_dict)
        playersOnline = playerList
        #bot.change_presence(game.discord.Game(name='P = {}/60, Status: = {}'.format(playersOnline, servState)))

    elif type == 4:
        playerInfoCont_dict = recvMessage_dict.get("data" , "Please wait for this information to be intialised and try again soon")
    elif type == 5:
        slotInfoSt_dict = recvMessage_dict.get("data", "Please wait for this information to be intialised and try again soon")
    elif type == 6:
        slotInfoCont_dict = recvMessage_dict.get("data", "Please wait for this information to be intialised and try again soon")
    elif type == 7:
        numState = recvMessage_dict.get("data", "Please wait for this information to be intialised and try again soon")
        if numState == 1:
            servState = "Running"
        elif numState == 2:
            servState = "Stopped"
        elif numState == 3:
            servState = "Paused"

def checkTime():
    if 'heart_dict' in globals() and type(heart_dict) is dict:
        info = "```Time: {} local.\nThe server will restart in {} ```".format(getMisTime(), toGo())
    else:
        info = "Please wait for this information to be intialised and try again soon"
    return info

def checkStatus():
    if 'servState' in globals():
        info = "OEO is currently: {}".format(servState)
    else:
        info = "Please wait for this information to be intialised and try again soon"
    HBDiffTime = time.time() - lastHeartbeat
    if HBDiffTime > heartbeatTimeout:
        info = "Server might not be running, contact an admin"
    return info

def checkPlayers():
    if 'playerInfoSt_dict' in globals() and type(playerInfoSt_dict) is dict:
        info = 'Players currently online: {}/60'.format(len(playersOnline))
    else:
        info = "Please wait for this information to be intialised and try again soon"
    return info

def gen_dict_extract(key, var):
    if hasattr(var,'iteritems'):
        for k, v in var.iteritems():
            if k == key:
                yield v
            if isinstance(v, dict):
                for result in gen_dict_extract(key, v):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    for result in gen_dict_extract(key, d):
                        yield result

def checkRestart():
    if 'heart_dict' in globals() and type(heart_dict) is dict:
        info = " ```The server will restart in {} ```".toGo())
    else:
        info = "Please wait for this information to be intialised and try again soon"
    return info

def checkInfo():
    if 'missionInfo_dict' in globals() and type(missionInfo_dict) is dict:
        theater = missionInfo_dict.get('theater')
        mission = missionInfo_dict.get('mission')
        if type('heart_dict') is dict:
            time = getMisTime()
            restart = toGo()
        else:  
            time = "Please wait for this information to be intialised and try again soon"   
            restart = "Please wait for this information to be intialised and try again soon"
        info = "Server: Operation Enduring Oddysey\nMission: {}\nTheater: {}\nLocal Time: {}\nRestart: {}".format(mission, theater, time, restart)
    else:
        info = "Please wait for this information to be intialised and try again soon"
    if info:
            await message.channel.send(info)

def thread_recieve():
    while True:
        dataUDP, addr = sock.recvfrom(2**16)
        recvMessage_dict = json.loads(dataUDP)
        if "recvMessage_dict" in locals():
            checkType(recvMessage_dict)

def thread_message():
    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        if message.content == '!help':
            info = '``!Server Info`` - returns a summary of server information.``\n``!Time`` or ``!Mission Time`` - returns in-game time and time to next restart.\n ``!Status`` or ``!Server Status`` returns server status.\n``!Players`` or ``!List Players`` returns number of players online.\n``!Reset`` or ``!Restart`` returns time to next server reset.'
            if info:
                await message.channel.send(info)

        if message.content == '!Time' or message.content == '!Mission Time':
            info = checkTime()
            if info:
                await message.channel.send(info)
                

        if message.content == '!Status' or message.content ==  '!Server Status':
            info = checkStatus()
            if info:
                await message.channel.send(info)

        if message.content == '!Players' or message.content ==  '!List Players':
            info = checkPlayers()
            if info:
                await message.channel.send(info)
                
        if message.content == "!Reset" or message.content == "!Restart":
            info = checkRestart()
            if info:
                await message.channel.send(info)
                
        if message.content == '!Server Info' or message.content == '!Info':
            info = checkInfo()
            if info:
                await message.channel.send(info)
                
    client.run(TOKEN)

if __name__ == "__main__":
    x = threading.Thread(target=thread_recieve, args=(),)
    y = threading.Thread(target=thread_message, args=(),)
    x.start()
    y.start()

