  GNU nano 4.8                                                                                                      DeBug.py
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

pth="path"

BCP=pth+"bcp.txt"
IDF=pth+"channel_id.txt"
BLG=pth+"bots_log.txt"

if os.path.isfile(BCP)==True:
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

    global last_link
    global pth

    def DataGen(source):
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

        author=author.replace("by ","")
        return author

    def LinkGen(source):
        href=source.split()[1]
        partial_link=href[6:-1]
        return partial_link

    global account
    page_link="https://www.instagram.com/{}/".format(account.replace("@",""))
    options=Options()
    options.add_argument("--headless")
    browser=webdriver.Firefox(options=options)
    browser.get(page_link)

    code=browser.find_element_by_class_name("v1Nh3.kIKUG._bz0w").get_attribute('outerHTML')
    tags=code.replace("><",">(SEP)<").split(sep="(SEP)")
    for tag in tags:
        if tag.startswith("<img"):
            author=DataGen(tag)
        if tag.startswith("<a"):
            link="https://www.instagram.com"+LinkGen(tag)
    browser.get(link)
    caption_code=browser.find_element_by_class_name("C4VMK").get_attribute('outerHTML')
    caption_blocks=(caption_code.replace("<br>","\n")).replace("><",">(SEP)<").split(sep="(SEP)")
    for tag in caption_blocks:
        if tag.startswith("<span"):
            caption=(tag.split(sep="<")[1].split(sep=">")[1])
    browser.close()

    captions_text=caption.split("\n")
    caption=captions_text[0]
    if len(captions_text)>20:
        caption=" ".join(captions_text[:20])+"..."

    if link!=last_link:
        news="["+str(datetime.datetime.now())+"] "+"New post: "+str(link)+"\n"
        BL.write(news)
        print(colored(f"[{datetime.datetime.now()}]###!NEW POST!###","green"))
        last_link=link
        backup=open(BCP,"w")
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

        comm=f"@everyone NUOVO POST\n{author}\n{caption}\n\nLINK:\n{link}"
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
        exc_info=sys.exc_info()
        err=traceback.format_exception(*exc_info)
        error_log="["+str(datetime.datetime.now())+"] "+str(err[-1])
        BL.write(error_log)
        BL.close()
        quit()
    return await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name=account))

client.run(TOKEN)