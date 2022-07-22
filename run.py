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

    #Make a beat
    print("----------------------------------------------------\n")
    bot = Instrumentator(randint(1,4))
    beatLocation, beatFileName, stemZipLocation, stemZipFileName = bot.makeBeat()
    print('Beat Created : '+beatFileName+'\n')
    print("----------------------------------------------------\n")

    #Upload 
    exit()
    #Update user on status of folders

    #Make the beat and wait till the day changes
    print("Waiting until the next day to restart program....\n")
    while(currentDate == today.strftime("%d/%m/%Y")):
        sleep(10)