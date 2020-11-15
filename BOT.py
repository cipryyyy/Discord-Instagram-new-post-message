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
import urllib.request
import asyncio

client=discord.Client()
account=############
cnt=0
pth="/home/server/bots_file/"

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
if os.path.isfile(BLG)==False:
    print("No log file, quitting")
    quit()

async def main(id_channel=id_channel):
    global last_link
    global pth
    global cnt

    channel=client.get_channel(id_channel)

    def DataGen(source):
        TW=None
        AW=None
        author=""
        text=[]
        hashtags=[]

        words=source.split()
        for word in words:
            if word[0]=="#":
                hashtags.append(word)
            if "quot" in word:
                if TW==True:
                    TW=False
                else:
                    TW=True
            if TW==True:
                text.append(word.replace("&quot;"," "))
            if word=="by":
                AW=True
            if word=="in" or word=="on":
                AW=False
            if AW==True:
                author+=word+" "

        author=author.replace("by ","")
        text=" ".join(text)
        if len(hashtags)==0:
            hashtags=["No hashtags used"]
        if text=="":
            text="No text in the image"
        return author, hashtags, text

    def LinkGen(source):
        href=source.split()[1]
        partial_link=href[6:-1]
        return partial_link
    global BLG
    global account

    try:
        while True:
            cnt+=1
            page_link="https://www.instagram.com/{}/".format(account.replace("@",""))
            options=Options()
            options.add_argument("--headless")
            browser=webdriver.Firefox(options=options)
            browser.get(page_link)

            code=browser.find_element_by_class_name("v1Nh3.kIKUG._bz0w").get_attribute('outerHTML')
            tags=code.replace("><",">(SEP)<").split(sep="(SEP)")
            for tag in tags:
                if tag.startswith("<img"):
                    author, htag, text=DataGen(tag)
                if tag.startswith("<a"):
                    link="https://www.instagram.com"+LinkGen(tag)
            browser.get(link)
            caption_code=browser.find_element_by_class_name("C4VMK").get_attribute('outerHTML')
            caption_blocks=(caption_code.replace("<br>","\n")).replace("><",">(SEP)<").split(sep="(SEP)")
            for tag in caption_blocks:
                if tag.startswith("<span"):
                    caption=(tag.split(sep="<")[1].split(sep=">")[1])
            browser.quit()

            captions_text=caption.split("\n")
            caption=captions_text[0]
            if len(caption.split())>40:
                caption=" ".join(caption.split()[:40])+"..."

            if link!=last_link:
                client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name=account))
                news="["+str(datetime.datetime.now())+"] "+"New post: "+str(link)+"\n"
                BL=open(BLG,"a")
                BL.write(news)
                BL.close()
                print(colored(f"[{datetime.datetime.now()}]###!NEW POST!###","green"))
                last_link=link
                backup=open(BCP,"w")
                backup.write(last_link)
                backup.close()

                options=Options()
                options.headless=True
                driver = webdriver.Firefox(options=options)
                driver.set_page_load_timeout(180)

                name="file.png"

                try:
                    driver.get(link)
                    soup = BeautifulSoup(driver.page_source, 'lxml')
                    img = soup.find('img', class_='FFVAD')
                    img_url = img['src']
                    r = requests.get(img_url)
                    with open(pth+name,'wb') as f:
                        f.write(r.content)

                except TypeError:
                    driver.get(link)
                    code=driver.find_element_by_class_name("tWeCl").get_attribute("outerHTML")
                    url=code.split()[-4].replace("&amp;","&")[8:-1]
                    r = urllib.request.urlopen(url)
                    with open(pth+name,"wb") as f:
                        f.write(r.read())
                driver.quit()
                comm=f"@everyone NUOVO POST\n{account}\n{caption}\n\nLINK AL POST:\n{link}"
                await channel.send(comm, file=discord.File(pth+name))
            if cnt==20:
                BL=open(BLG,"a")
                report="["+str(datetime.datetime.now())+"] "+"ACCOUNT CHECKED\n"
                cnt=0
                BL.write(report)
                BL.close()
            await asyncio.sleep(60)

    except Exception:
        print(colored("An error occured, check logs for further infos","red"))
        exc_info=sys.exc_info()
        err=traceback.format_exception(*exc_info)
        error_log="["+str(datetime.datetime.now())+"] "+str(err[-1])+"\n"
        BL=open(BLG,"a")
        BL.write(error_log)
        BL.close()
        quit()

def starter():
    client.loop.create_task(main())


@client.event
async def on_ready():
    global id_channel
    BL=open(BLG,"a")
    start_log="["+str(datetime.datetime.now())+"] "+"BOT ONLINE ("+str(id_channel)+")\n"
    BL.write(start_log)
    BL.close()
    print(colored(f"Logged in as {client.user.name} [{client.user.id}]","cyan"))
    starter()
    return await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name=account))

client.run(TOKEN)