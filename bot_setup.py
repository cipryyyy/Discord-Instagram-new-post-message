import discord
from termcolor import colored
import time

client=discord.Client()
exit=False

@client.event
async def on_message(message):
    global exit
    if exit==False:
        if message.author==client.user:
            return
        if message.content.lower()=="config":
            chid=str(message).split()[3][3:]
            name=str(message).split()[4].replace("'","").split("=")[1].replace(" ","")
            print(colored(chid,"green"))
            print(colored(name,"green"))
            msg=str("\n\nID: "+chid+"\nChannel: "+name)
            f=open("channel_id.txt","w")
            f.write(str(chid))
            f.close()
            print(colored("ID SAVED\n","cyan"))
            await message.channel.send(msg)
        if message.content.lower().startswith("close"):
            print(colored("QUITTING","red"))
            exit=True
            await message.channel.send("Goodbye")
    else:
        return await client.close()
        return await quit()

@client.event
async def on_ready():
    print('Logged in as:')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(TOKEN)
