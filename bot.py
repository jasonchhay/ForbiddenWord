# https://github.com/Rapptz/discord.py/blob/async/examples/reply.py
import discord
from discord import PermissionOverwrite
import asyncio
import copy
from generate_dictionary import generate_dictionary
TOKEN = ''

client = discord.Client()

global wordBank
global cursedBank
global blessedBank

wordBank = {}
cursedBank = {}
blessedBank = {}

global blessed_role
global cursed_role
global timeout_role

blessed_role = None
cursed_role = None
timeout_role = None

def reshuffle(server):
    dictionary = generate_dictionary()

    wordBank[server] = dictionary[:1000]

    cursedBank[server] = dictionary[1000:1050]

    blessedBank[server] = dictionary[1050:]

async def check_message(message, message_space):

    server = message.server

    role = None

    forbidden = 0
    timeout = 0
    plural = 'minute'
    wordType = 'forbidden'

    cursedCounter = 0
    forbiddenCounter = 0
    cursedPlural = 'word'
    forbiddenPlural = 'word'

    roles = []

    if blessed_role not in message.author.roles:
        #Check each word in the message for blessed, cursed, or forbidden words
        for word in message_space:
            word = "".join(list(filter(lambda c: c.isalpha(), word)))

            if word.lower() in blessedBank[server]:
                forbidden = 1
                timeout = 0

                blessedBank[server].remove(word.lower())
                await client.add_roles(message.author, discord.utils.get(server.roles, name='Blessed'))
                msg = "Congratulations <@{}>, you have said a blessed word: **\"{}\"**. From here on out, you'll be immune to any forbidden or cursed words.".format(message.author.id, word.lower())
                await client.send_message(message.channel, msg)
                return

            elif word.lower() in cursedBank[server]:
                forbidden = 2
                timeout += 600
                cursedCounter += 1
                roles.append(discord.utils.get(server.roles, name='Cursed'))

            if blessed_role not in message.author.roles and word.lower() in wordBank[server]:
                forbidden = 3
                timeout += 60
                forbiddenCounter += 1
                roles.append(discord.utils.get(server.roles, name='Time-Out'))

        #Provide appropriate punishment if a forbidden word is said.
        if forbidden > 1:
            currentRoles = copy.copy(message.author.roles)
            if timeout / 60 > 1:
                plural = 'minutes'
            msg = "<@{}> said ".format(message.author.id)
            if cursedCounter > 0:
                if cursedCounter > 1:
                    cursedPlural = "words"
                msg += "{} cursed {}".format(cursedCounter, cursedPlural)

            if cursedCounter > 0 and forbiddenCounter > 0:
                msg += " and "

            if forbiddenCounter > 0:
                if forbiddenCounter > 1:
                    forbiddenPlural = "words"
                msg += "{} forbidden {}".format(forbiddenCounter, forbiddenPlural)

            msg += '. They will be on timeout for {} {}.'.format(int(timeout / 60), plural)
            await client.send_message(message.channel, msg)

            for r in currentRoles:
                await client.remove_roles(message.author, r)
            for role in roles:
                print(role)
                await client.add_roles(message.author, role)

            await asyncio.sleep(timeout)

            for role in roles:
                await client.remove_roles(message.author, role)
            for r in currentRoles:
                await client.add_roles(message.author, r)

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content == "~rules":
        msg = open("rules.txt", 'r').read()
        await client.send_message(message.channel, msg)
        return

    if message.content == "~reshuffle":
        reshuffle(message.server)
        msg = "The word bank has been reshuffled. Good luck ;)"
        await client.send_message(message.channel, msg)
        return

    print(message.content)

    await check_message(message, message.content.split(" "))

@client.event
async def on_message_edit(before, after):
    await check_message(before, before.content.split(" "))

@client.event
async def on_server_join(server):
    print("Joined server:",server)
    if 'Blessed' not in [r.name for r in server.roles]:
        await client.create_role(server, name="Blessed", color=discord.Color(0xfcfbb8))

    if 'Cursed' not in [r.name for r in server.roles]:
        await client.create_role(server, name="Cursed", color=discord.Color(0x440d0d))

    if 'Time-Out' not in [r.name for r in server.roles]:
        await client.create_role(server, name='Time-Out', color=discord.Color(0x826987))

    cursed_role = discord.utils.get(server.roles, name='Cursed')
    timeout_role = discord.utils.get(server.roles, name='Time-Out')
    mute_permissions = PermissionOverwrite(read_messages = True, read_message_history=True, send_messages = False, connect=False, speak=False)

    for channel in server.channels:
        await client.edit_channel_permissions(channel, cursed_role, mute_permissions)
        await client.edit_channel_permissions(channel, timeout_role, mute_permissions)
    dictionary = generate_dictionary()
    wordBank[server] = dictionary[:1000]
    cursedBank[server] = dictionary[1000:1050]
    blessedBank[server] = dictionary[1050:]

    print(wordBank[server])
    print(cursedBank[server])
    print(blessedBank[server])

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

    for server in client.servers:
        await on_server_join(server)


client.run(TOKEN)
