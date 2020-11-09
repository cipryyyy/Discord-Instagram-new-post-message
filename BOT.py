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

BCP=backup_file
ID=id_of_the_channel
LOG=log_file
XPATH=full_xpath_of_last_post_from_user_page

if os.path.isfile(BCP)==True:
    src=open(BCP,"r")
    last_link=src.read()
    src.close()
else:
    print("No backup file found, quitting")
    quit()
if os.path.isfile(ID)==True:
    id_src=open(ID,"r")
    id_channel=int(id_src.read())
    id_src.close()
else:
    print("No ID found, quitting")
    quit()

if os.path.isfile(LOG)==True:
    BL=open(LOG,"a")
else:
    print("No log file found, quitting")
    quit()

@tasks.loop(minutes=1)
async def main(id_channel=id_channel):
    def last_post(profile):
        LINK=profile
        options = Options()
        options.headless = True
        driver = webdriver.Firefox(options=options)
        driver.set_page_load_timeout(180)
        driver.get(LINK)
        code=driver.find_element_by_xpath(XPATH).get_attribute('outerHTML')
        blocks=code.split(sep="<")
        link="https://www.instagram.com"+blocks[2].split()[1][6:-1]
        driver.close()
        return link

    channel=client.get_channel(id_channel)
    global last_link
    START=time.time()
    account=#############

    link=last_post(f"https://www.instagram.com/{account}/")

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
        with open("/path/"+name,'wb') as f:
            f.write(r.content)
        driver.close()
        await channel.send(f"@everyone Ultimo post di {account}\n{link}", file=discord.File("/path/"+name))
@client.event
async def on_ready():
    BL.write(str(datetime.datetime.now()))
    BL.write(" Started\n")
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
    return await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=))

client.run(TOKEN)