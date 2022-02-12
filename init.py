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
    for result in collection.find({"name":str(name)}):
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

    for resultCallback in collection.find({f"{dataType}": str(member) }):
        return resultCallback[str(searchQuery)]


def massDumpUsers(member,server_id):
    if isUser(member,server_id) == None:

        collection = MongoDBConnect(str(member.guild.id))
        date = getDate()
        userToken = generateToken()
        insert_block = {"name": str(member),"join_date": date,"tsiv": 0,"xp": 0,"userUniToken": userToken}
        collection.insert_one(insert_block)
        print(f"[DEBUG] Dumped users to {member.guild.name}")
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
    collection.update_one({"name": str(member)},{"$set":{"tsiv": tsivp}})


def calculateTime(member):
    cwd = os.getcwd()
    with open(f"{cwd}/vcTEMP/{member.id}.txt","r") as tempVC:
        time_spent = tempVC.read()
        date_time_obj = datetime.strptime(time_spent, '%Y-%m-%d %H:%M:%S.%f')
        timeNow = getDate()
        elapsed = timeNow - date_time_obj
        elapsed_new = round(elapsed.total_seconds())
        tsiv = getdataonUser("name",member,"tsiv")
        new_tsiv = elapsed_new + tsiv


        addTsivp(member,member.guild.id,new_tsiv)

    os.remove(f"{cwd}/vcTEMP/{member.id}.txt")


def getUserTSIV(user,server_id):
    collection = MongoDBConnect(server_id)
    for resultCallback in collection.find({"name":str(user)}):
        return resultCallback["tsiv"]



def addMeMongo(member,server_id):

    if isUser(str(member),server_id) == None:
        collection = MongoDBConnect(server_id)
        date = getDate()
        userToken = generateToken()
        insert_block = {"name": str(member),"join_date": date,"tsiv": 0,"xp": 0,"userUniToken": userToken}
        collection.insert_one(insert_block)
    else:
        print("User already in db")

#

#Client events

@client.event
async def on_ready():
    print("[DEBUG] Client up...")
    await client.change_presence(status=discord.Status.offline)


@client.event
async def on_member_join(member):
    print(member)
    print(f"[DEBUG] Performing user check on {member}")
    if isUser(member) == None:
        print("Imporing user to database")
        insertMongoDB(member)


@client.event
async def on_voice_state_update(member,before,after):
    if before.channel is None and after.channel is not None:
        print(f"[DEBUG] {str(member)} has joined voice channel")
        createTrackerfile(member.id)

    if before.channel is not None and after.channel is None:
        print(f"[DEBUG] {str(member)} has left voice channel")
        calculateTime(member)


@client.command()
async def addUsers(ctx):
    for member in ctx.guild.members:
        massDumpUsers(member,ctx.guild.id)
        


@commands.has_role('Savitar')
@client.command()
async def addMe(ctx):
    addMeMongo(ctx.message.author,ctx.guild.id)

@commands.has_role('Savitar')
@client.command()
async def userstats(ctx,member: discord.Member):
    member_status = member.status
    member_pfp = member.avatar_url
    member_TSIV = getUserTSIV(member,ctx.guild.id)
    member_TSIV =  str(timedelta(seconds=member_TSIV))
    color_scheme = {"offline":0x808080,"online":0x00ff00,"dnd":0xff0000,"idle":0xffff00}
    colorChoice = color_scheme[str(member_status)]
    embed=discord.Embed(title=f"$~User@{member}", description=f"User is currently { member_status }", color=colorChoice)
    embed.set_image(url=member_pfp)
    embed.add_field(name="User TSIV", value=f"{member_TSIV}", inline=True)
    embed.add_field(name="User CS", value="undefined", inline=True)
    embed.set_footer(text="//END")
    await ctx.send(embed=embed)



@client.event
async def on_message(package):

    print(package.author.guild)

    await client.process_commands(package)


client.run("ODUyOTQ0OTkzMDU2MzI1NzE1.YMOM7Q.MJ6yAmQB0-_3WW1pPTxQAKJndJ8")

##