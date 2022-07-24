from Instrumentator import Instrumentator
import dawdreamer as daw
from os import listdir
from datetime import date
from time import sleep
from random import randint

#Make an object solely for getting the input folder
forInputFolder = Instrumentator(None)

while(1):
    
    #Get current date
    today = date.today()
    currentDate = today.strftime("%d/%m/%Y")

    #Make a instrumental
    print("----------------------------------------------------\n")
    bot = Instrumentator(randint(1,4))
    instrumentalLocation, instrumentalFileName, stemZipLocation, stemZipFileName = bot.makeinstrumental()
    print('instrumental Created : '+instrumentalFileName+'\n')
    print("----------------------------------------------------\n")

    ########THIS PART STILL IN DEVELOPMENT

    #Make the instrumental and wait till the day changes
    print("Waiting until the next day to restart program....\n")
    while(currentDate == today.strftime("%d/%m/%Y")):
        sleep(10)