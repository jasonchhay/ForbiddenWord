# https://github.com/Rapptz/discord.py/blob/async/examples/reply.py
import discord
from discord import Permissions
import asyncio
import copy
from generate_dictionary import generate_dictionary
TOKEN = 'NDcxODM3MTMzMzA5NDc2ODc1.Djqo_Q.nNu8BNi1MkVVlYf565qALkUj3s4'

client = discord.Client()


dictionary = generate_dictionary()
wordBank = dictionary[:1000]
cursedBank = dictionary[1000:1050]
blessedBank = dictionary[1050:]
print(wordBank)
print(cursedBank)
print(blessedBank)

role = None

blessed_role = None
cursed_role = None
timeout_role = None
@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    message_space = message.content.split(" ")

    if message.content == "~rules":
        msg = open("rules.txt", 'r').read()
        await client.send_message(message.channel, msg)

    if message.content == "~reshuffle":
        global dictionary
        dictionary = generate_dictionary()

        global wordBank
        wordBank = dictionary[:1000]

        global cursedBank
        cursedBank = dictionary[1000:1050]

        global blessedBank
        blessedBank = dictionary[1050:]
        print(wordBank)
        print(cursedBank)
        print(blessedBank)

        msg = "The word bank has been reshuffled. Good luck ;)"
        await client.send_message(message.channel, msg)
    print(message.content)

    forbidden = 0
    timeout = 0
    plural = 'minute'
    wordType = 'forbidden'

    cursedCounter = 0
    forbiddenCounter = 0
    cursedPlural = 'word'
    forbiddenPlural = 'word'

    roles = []

    for word in message_space:
        if word == "~rules" or word == "~reshuffle":
            return
        word = "".join(list(filter(lambda c: c.isalpha(), word)))

        if word.lower() in blessedBank:
            forbidden = 1
            timeout = 0

            blessedBank.remove(word.lower())
            wordBank.remove(word.lower())
            await client.add_roles(message.author, blessed_role)
            msg = "Congratulations <@{}>, you have said a blessed word. From here on out, you'll be immune to any forbidden or cursed words.".format(message.author.id)
            await client.send_message(message.channel, msg)
            return

        elif word.lower() in cursedBank:
            forbidden = 2
            timeout += 600
            cursedCounter += 1
            roles.append(cursed_role)

        if blessed_role not in message.author.roles and word.lower() in wordBank:
            forbidden = 3
            timeout += 60
            forbiddenCounter += 1
            roles.append(timeout_role)


    if forbidden > 1:
        currentRoles = copy.copy(message.author.roles)
        print(currentRoles)
        if timeout / 60 > 1:
            plural = 'minutes'

        msg = "<@{}> You have said ".format(message.author.id)
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

        msg += '. You will be on timeout for {} {}.'.format(int(timeout / 60),plural)
        await client.send_message(message.channel, msg)

        for r in currentRoles:
            await client.remove_roles(message.author, r)
        for role in roles:
            await client.add_roles(message.author, role)

        await asyncio.sleep(timeout)

        for role in roles:
            await client.remove_roles(message.author, role)
        for r in currentRoles:
            await client.add_roles(message.author, r)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

    for server in client.servers:
        if 'Blessed' not in [r.name for r in server.roles]:
            await client.create_role(server, name="Blessed", color=discord.Color(0xfcfbb8))
        global blessed_role
        blessed_role = discord.utils.get(server.roles, name='Blessed')
        print(blessed_role)

        if 'Cursed' not in [r.name for r in server.roles]:
            await client.create_role(server, name="Cursed", color=discord.Color(0x440d0d))
        global cursed_role
        cursed_role = discord.utils.get(server.roles, name='Cursed')
        print(cursed_role)

        if 'Time-Out' not in [r.name for r in server.roles]:
            await client.create_role(server, name='Time-Out', color=discord.Color(0x826987))
        global timeout_role
        timeout_role = discord.utils.get(server.roles, name='Time-Out')
        print(timeout_role)


client.run(TOKEN)