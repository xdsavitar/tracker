import discord
from discord.ext import commands
import requests
import json
import pymongo
from pymongo import MongoClient
from datetime import datetime
from datetime import timedelta
import string
import random
import os
import colorama
from colorama import Fore,Back,Style
import threading
import time
from discord.ext import tasks

#Global Variables

Server_Id_List = []

#



colorama.init()


intents = discord.Intents.all()
client = discord.Client(intents=intents)
client = commands.Bot(command_prefix=">",intents=intents)

#Functions

def MongoDBConnect(server_id):
    cluster = pymongo.MongoClient("mongodb+srv://woe87:bottlecap87@cluster0.3iebv.mongodb.net/discordatastorage?retryWrites=true&w=majority")
    dataBase = cluster["discordatastorage"]
    collection = dataBase[str(server_id)]
    return collection


def isUser(name,server_id):
    collection = MongoDBConnect(server_id)
    for result in collection.find({"name":name}):
        return result


def insertMongoDB(member):
    collection = MongoDBConnect(str(member.guild.id))
    date = getDate()
    userToken = generateToken()

    insert_block = {"_id": 0,"name": member.name,"join_date": date,"tsiv": 0,"xp": 0,"userUniToken": userToken}
    collection.insert_one(insert_block)

def getdataonUser(dataType,member,searchQuery):
    print(member)
    collection = MongoDBConnect(str(member.guild.id))

    for resultCallback in collection.find({f"{dataType}": member.id }):
        return resultCallback[str(searchQuery)]


def massDumpUsers(member,server_id):
    if isUser(member,server_id) == None:

        collection = MongoDBConnect(str(server_id))
        date = getDate()
        userToken = generateToken()
        insert_block = {"name": member,"join_date": date,"tsiv": 0,"xp": 0,"userUniToken": userToken}
        collection.insert_one(insert_block)
        print(f"[DEBUG] Dumped users")
    else:
        print("Already in database")


def generateToken():
    res = ''.join(random.choices(string.ascii_uppercase+string.digits, k = 9))
    return res

def getDate():
    now = datetime.now()
    return now

def createTrackerfile(member):
    cwd = os.getcwd()
    with open(f"{cwd}/vcTEMP/{member}.txt","w") as tempVC:
        tempVC.write(str(getDate()))
        tempVC.close()


def addTsivp(member,guild,tsivp):
    collection = MongoDBConnect(guild)
    collection.update_one({"name": member.id},{"$set":{"tsiv": tsivp}})


def ElapseTimes(voiceLastDelta):
        date_time_obj = datetime.strptime(voiceLastDelta, '%Y-%m-%d %H:%M:%S.%f')
        timeNow = getDate()
        elapsed = timeNow - date_time_obj
        elapsed_new = round(elapsed.total_seconds())
        return elapsed_new



def calculateTime(member):
    cwd = os.getcwd()


    with open(f"{cwd}/vcTEMP/{member.id}.txt","r") as tempVC:
        time_spent = tempVC.read()
        elapsed_new = ElapseTimes(time_spent)

        addTsivp(member,member.guild.id,elapsed_new)

 
    #os.remove(f"{cwd}/vcTEMP/{member.id}.txt")



def fetchLast(member):

    try:
        with open(f"vcTEMP/{member}.txt","r") as readVC:
            print(member)
            time_spent = readVC.read()
            elapsed = ElapseTimes(time_spent)
            return elapsed

    except FileNotFoundError:
        return "Unknown"


def getUserTSIV(user,server_id):
    collection = MongoDBConnect(server_id)
    for resultCallback in collection.find({"name":user}):
        return resultCallback["tsiv"]



def addMeMongo(member,server_id):

    if isUser(member.id,server_id) == None:
        print(member.id)
        collection = MongoDBConnect(server_id)
        date = getDate()
        userToken = generateToken()
        insert_block = {"name": member.id,"join_date": date,"tsiv": 0,"xp": 0,"userUniToken": userToken}
        collection.insert_one(insert_block)
    else:
       
        print("User already in db")



def createDailyData():
    with open(f"DataOnUsers/{str(getDate)}.txt","w+") as writableData:
        write_block = f"{user_name}: {TSIV}\n"
        writableData.write(write_block)

def loadAllServers():
    active_servers = client.guilds
    for guild in active_servers:
        Server_Id_List.append(guild.id)


@tasks.loop(seconds=2)
async def job():
    
    for guild_id in Server_Id_List:
        collection = MongoDBConnect(guild_id)
        



#

#Client events

@client.event
async def on_ready():
    print(Fore.GREEN + "[DEBUG]: Key Accepted, Prompting")
    print(Fore.GREEN + "[DEBUG] Client up...")
    print(Fore.YELLOW + "[PROCCESS]: Ateempting to start a job.")
    job.start()
    print(Fore.GREEN + "[PROCCESS]: Job started Successfully.")
    print(Fore.GREEN + "[PROCCESS]: Loading active servers...")
    loadAllServers()
    print(Fore.GREEN + "[PROCCESS]: Servers loaded.")
    await client.change_presence(status=discord.Status.offline)


@client.event
async def on_member_join(member):
    print(member)
    print(f"{Fore.YELLOW}[DEBUG] Performing user check on {member}")
    if isUser(member.id,member.guild.id) == None:
        print(Fore.RED + "Imporing user to database")
        insertMongoDB(member)




@client.event
async def on_guild_channel_delete(channel):
    print(channel)



@client.event
async def on_voice_state_update(member,before,after):
    if before.channel is None and after.channel is not None:
        print(f"{Fore.GREEN} [DEBUG] {str(member)} has joined voice channel")
        createTrackerfile(member.id)

    if before.channel is not None and after.channel is None:
        print(f"{Fore.RED}[DEBUG] {str(member)} has left voice channel")
        calculateTime(member)


@commands.has_role('Savitar + SOC')
@client.command()
async def addUsers(ctx):
    for member in ctx.guild.members:
        massDumpUsers(member.id,ctx.guild.id)


@commands.has_role('Savitar + SOC')
@client.command()
async def addMe(ctx):
    addMeMongo(ctx.message.author,ctx.guild.id)

@client.command()
async def userstats(ctx,member: discord.Member):
    member_status = member.status
    member_pfp = member.avatar_url
    member_TSIV = getUserTSIV(member.id,ctx.guild.id)
    member_TSIV =  str(timedelta(seconds=member_TSIV))
    last_activity = fetchLast(str(member.id))
    print(last_activity)

    if last_activity == "Unknown":
        last_activity = "Unknown"
    else:
        last_activity = str(timedelta(seconds=last_activity))

    color_scheme = {"offline":0x808080,"online":0x00ff00,"dnd":0xff0000,"idle":0xffff00}
    colorChoice = color_scheme[str(member_status)]
    embed=discord.Embed(title=f"$~User@{member}", description=f"User is currently { member_status }", color=colorChoice)
    embed.set_image(url=member_pfp)
    embed.add_field(name="User TSIV", value=f"{member_TSIV}", inline=True)
    embed.add_field(name="User last voice activity", value=f"T- {last_activity}", inline=True)
    embed.set_footer(text="//END")
    await ctx.send(embed=embed)



@client.command()
async def meme(ctx):
    request = requests.get("https://meme-api.herokuapp.com/gimme")
    data = request.json()
    meme_url = data["url"]
    title = data["title"]
    ups = data["ups"]
    embed=discord.Embed(title=f"{title}")
    embed.set_image(url=meme_url)
    embed.set_footer(text=f"Upvotes: {ups}")
    await ctx.send(embed=embed)


##Joke commands

@client.command()
async def whoasked(ctx,user):
    await ctx.send(f"No one asked {user}")


##





@client.event
async def on_message(package):

    print(package.author.guild)

    await client.process_commands(package)

CORE_KEY = input("CORE_KEY: ")
client.run(CORE_KEY)

##