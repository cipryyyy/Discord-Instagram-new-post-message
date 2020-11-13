import discord
from discord.ext import tasks
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from termcolor import colored
import time
import datetime
import os
import traceback
import sys

client=discord.Client()
account=#############

pth="path"                          #Main folder

BCP=pth+"bcp.txt"
IDF=pth+"channel_id.txt"
BLG=pth+"bots_log.txt"

if os.path.isfile(BCP)==True:                   #Check if files exist
    src=open(BCP,"r")
    last_link=src.read()
    src.close()
else:
    print("No backup file, quitting")
    quit()
if os.path.isfile(IDF)==True:
    id_src=open(IDF,"r")
    id_channel=int(id_src.read())
    id_src.close()
else:
    print("No ID file, quitting")
    quit()
if os.path.isfile(BLG)==True:
    BL=open(BLG,"a")
else:
    print("No log file, quitting")
    quit()

@tasks.loop(minutes=1) 
async def main(id_channel=id_channel):
    global last_link                            #link of the last post
    global pth

    def DataGen(source):                        #Generate name
        AW=None
        author=""

        words=source.split()
        for word in words:
            if word=="by":
                AW=True
            if word=="in" or word=="on":
                AW=False
            if AW==True:
                author+=word+" "

        author=author.replace("by ","")                 #"by user"--->"user"
        return author

    def LinkGen(source):
        href=source.split()[1]
        partial_link=href[6:-1]                         #partial link = /p/1a2bc3d4e5f
        return partial_link

    global account
    page_link="https://www.instagram.com/{}/".format(account.replace("@",""))       #link of the account
    options=Options()
    options.add_argument("--headless")
    browser=webdriver.Firefox(options=options)
    browser.get(page_link)

    code=browser.find_element_by_class_name("v1Nh3.kIKUG._bz0w").get_attribute('outerHTML')         #class of the last post
    tags=code.replace("><",">(SEP)<").split(sep="(SEP)")                                            #splits tag
    for tag in tags:
        if tag.startswith("<img"):                                                          #in the img tag you can find username
            author=DataGen(tag)
        if tag.startswith("<a"):
            link="https://www.instagram.com"+LinkGen(tag)                   #full link = https://www.instagram.com/p/1a2bc3d4e5f
    browser.get(link)
    caption_code=browser.find_element_by_class_name("C4VMK").get_attribute('outerHTML')
    caption_blocks=(caption_code.replace("<br>","\n")).replace("><",">(SEP)<").split(sep="(SEP)")   #<br> in HTML == \n in python
    for tag in caption_blocks:
        if tag.startswith("<span"):
            caption=(tag.split(sep="<")[1].split(sep=">")[1])                           #keeps inly the caption
    browser.close()

    captions_text=caption.split("\n")
    caption=captions_text[0]
    if len(captions_text)>20:                                                           #shows noly the firsts twenty words
        caption=" ".join(captions_text[:20])+"..."

    if link!=last_link:
        news="["+str(datetime.datetime.now())+"] "+"New post: "+str(link)+"\n"
        BL.write(news)
        print(colored(f"[{datetime.datetime.now()}]###!NEW POST!###","green"))
        last_link=link
        backup=open(BCP,"w")                                        #backup of the last post
        backup.write(last_link)
        backup.close()
        options=Options()
        options.headless=True
        driver = webdriver.Firefox(options=options)
        driver.set_page_load_timeout(TIMEOUT)
        driver.get(link)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        img = soup.find('img', class_='FFVAD')
        img_url = img['src']
        r = requests.get(img_url)
        name="file.png"
        with open(pth+name,'wb') as f:
            f.write(r.content)
        driver.close()

        comm=f"@everyone NUOVO POST\n{author}\n{caption}\n\nLINK:\n{link}"          #message to send
        await channel.send(comm, file=discord.File(pth+name))

@client.event
async def on_ready():
    global id_channel
    start_log="["+str(datetime.datetime.now())+"] "+"BOT ONLINE ("+str(id_channel)+")\n"
    BL.write(start_log)
    print(colored(f"Logged in as {client.user.name} [{client.user.id}]","cyan"))
    try:
        main.start()
    except Exception:
        exc_info=sys.exc_info()                                                     #Logs error
        err=traceback.format_exception(*exc_info)
        error_log="["+str(datetime.datetime.now())+"] "+str(err[-1])
        BL.write(error_log)
        BL.close()
        quit()
    return await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name=account))

client.run(TOKEN) 