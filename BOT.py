import discord
from discord.ext import tasks
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
import time

client=discord.Client()
src=open(LAST_LINK.TXT,"r")                         #FILE WITH LATEST LINK
last_link=src.read()
src.close()

@tasks.loop(minutes=1)
async def main(id_channel=ID):
    def last_post(profile):
        LINK=profile
        options = Options()
        options.headless = True
        driver = webdriver.Firefox(options=options)
        driver.set_page_load_timeout(TIMEOUT)
        driver.get(LINK)
        code=driver.find_element_by_xpath(XPATH).get_attribute('outerHTML')     #WRITE HTML CODE
        blocks=code.split(sep="<")                  #SPLIT THE CODE
        link="https://www.instagram.com"+blocks[2].split()[1][6:-1]
        driver.close()
        return link

    channel=client.get_channel(id_channel)
    global last_link
    account=PROFILE

    link=last_post("https://www.instagram.com/"+account.replace("@","")+"/")                #@profile_name ---> profile_name

    if link!=last_link:
        last_link=link
        backup=open(LAST_LINK.TXT,"w")
        backup.write(last_link)
        backup.close()
        options=Options()
        options.headless=True
        driver = webdriver.Firefox(options=options)
        driver.set_page_load_timeout(180)
        driver.get(link)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        img = soup.find('img', class_='FFVAD')
        img_url = img['src']
        r = requests.get(img_url)
        name="file.png"
        with open(name,'wb') as f: 
            f.write(r.content)
        driver.close()
        await channel.send(f"@everyone Last post from {account}\n{link}", file=discord.File(name))          #Send message for everyone

@client.event
async def on_ready():
    print(f"Logged in as {client.user.name} [{client.user.id}]")
    main.start()
    return await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=PAGE))

client.run(TOKEN)