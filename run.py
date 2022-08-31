from BeatstarsBot import BeatstarsBot
from datetime import datetime, date, timedelta
from Instrumentator import Instrumentator
from os import listdir, remove
from PIL import Image
from random import randint, sample
from time import sleep
from traceback import format_exc

#Make an object to access Instrumentator's methods and folders
mainInstrumentatorObject = Instrumentator(None)

#Delete all images under 500 x 500
imageFiles = listdir(mainInstrumentatorObject.imagesFolder)
for image in imageFiles:
    im = Image.open(mainInstrumentatorObject.imagesFolder+image)
    width, height = im.size
    im.close()
    if (width < 500) or (height < 500):
        remove(mainInstrumentatorObject.imagesFolder+image)
imageFiles = listdir(mainInstrumentatorObject.imagesFolder)

print('\n')
while(1):
    try:

        #Get some needed values
        today = date.today()
        currentDate = today.strftime("%d/%m/%Y")
        leave = False

        print("----------------------------------------------------\n")

        #Update user on status of folders
        melodies = listdir(mainInstrumentatorObject.inputFolder)
        print(str(len(melodies))+' melodies are left.')
        if len(melodies) == 0:
            mainInstrumentatorObject.sendNotificationToPhone('No melodies are left!', 'Get more melodies.')
            while(1):
                if currentDate == today.strftime("%d/%m/%Y"):
                    sleep(10)
                else:
                    leave = True
                    break
        if leave == True:
            continue  
        elif len(melodies) <= 5:
            mainInstrumentatorObject.sendNotificationToPhone(str(len(melodies))+' melodies are left.', 'Get more melodies soon.')

        #Choose a name for the beat
        possibleNames = open(mainInstrumentatorObject.beatNamesTextFile, 'r').readlines()
        print(str(len(possibleNames))+" names are left.")
        if len(possibleNames) == 0:
            mainInstrumentatorObject.sendNotificationToPhone('No beat names are left!', 'Get more beat names.')
            while(1):
                if currentDate == today.strftime("%d/%m/%Y"):
                    sleep(10)
                else:
                    leave = True
                    break
        if leave == True:
            continue  
        elif len(possibleNames) <= 5:
            mainInstrumentatorObject.sendNotificationToPhone(str(len(possibleNames))+' beat names are left.', 'Get more beat names soon.')
        beatName = possibleNames[0].strip()

        #Find and choose an image
        images = listdir(mainInstrumentatorObject.imagesFolder)
        print(str(len(images))+' images are left.')
        if len(images) == 0:
            mainInstrumentatorObject.sendNotificationToPhone('No images are left!', 'Get more images.')
            while(1):
                if currentDate == today.strftime("%d/%m/%Y"):
                    sleep(10)
                else:
                    leave = True
                    break
        if leave == True:
            continue  
        elif len(images) <= 5:
            mainInstrumentatorObject.sendNotificationToPhone(str(len(images))+' images are left.', 'Get more images soon.')
        chosenImage = mainInstrumentatorObject.imagesFolder+images[0]

        #Make a beat
        print("\n----------------------------------------------------\n")
        bot = Instrumentator(randint(1,6))
        usedMelody, beatLocation, beatFileName, stemZipLocation, beatBPM, beatKey = bot.makeBeat()
        print('Beat Created : '+beatFileName+'\n')
        print("----------------------------------------------------")

        #Choose three tags from the list of tags
        possibleTags = open(mainInstrumentatorObject.beatTagsTextFile, 'r').readlines()
        for counter1 in range(0, len(possibleTags)):
            possibleTags[counter1] = possibleTags[counter1].strip()
        listOfRandomNumbers1 = sample(range(0, len(possibleTags)), 3)
        beatTags = [possibleTags[listOfRandomNumbers1[0]], possibleTags[listOfRandomNumbers1[1]], possibleTags[listOfRandomNumbers1[2]]]

        #Get the beat description
        beatDescription = open(mainInstrumentatorObject.beatDescriptionTextFile, 'r').read()
        beatDescription = beatDescription.strip()

        #Get the genres for the beat
        possibleGenres = open(mainInstrumentatorObject.beatGenresTextFile, 'r').readlines()
        for counter2 in range(0, len(possibleGenres)):
            possibleGenres[counter2] = possibleGenres[counter2].strip()
        listOfRandomNumbers2 = sample(range(0, len(possibleGenres)), 3)
        beatGenres = [possibleGenres[listOfRandomNumbers2[0]], possibleGenres[listOfRandomNumbers2[1]], possibleGenres[listOfRandomNumbers2[2]]]
        
        #Get the moods for the beat 
        possibleMoods = open(mainInstrumentatorObject.beatMoodsTextFile, 'r').readlines()
        for counter3 in range(0, len(possibleMoods)):
            possibleMoods[counter3] = possibleMoods[counter3].strip()
        listOfRandomNumbers3 = sample(range(0, len(possibleMoods)), 5)
        beatMoods = [possibleMoods[listOfRandomNumbers3[0]], possibleMoods[listOfRandomNumbers3[1]], possibleMoods[listOfRandomNumbers3[2]], possibleMoods[listOfRandomNumbers3[3]], possibleMoods[listOfRandomNumbers3[4]]]

        uploadBot = BeatstarsBot('username', 'password', beatLocation, stemZipLocation, chosenImage, beatName, beatDescription, beatTags, beatGenres, beatMoods, str(beatKey).strip(), int(beatBPM))
        firstError = True
        while(1):
            try:
                print("\nLogging into BeatStars....\n")
                uploadBot.accessWebsite()
                uploadBot.login()
                uploadBot.makeNewTrack()
                print('\nUploading files....\n')
                uploadBot.uploadWav()
                uploadBot.uploadZip()
                print('\nUploading details....\n')
                uploadBot.uploadImage()
                uploadBot.uploadBasicInfo('[BUY 2 GET 1 FREE]', private=False)
                uploadBot.uploadMetadata()
                print('\nSettings leases and publishing....\n')
                uploadBot.activateLeases()
                uploadBot.publishBeat()
                break
            except Exception:
                print("\nError in Beatstars Bot. Waiting 10 minutes and restarting.\n")
                key = str(randint(1,1000000000))
                uploadBot.savePicture(key)
                if firstError == True:
                    mainInstrumentatorObject.sendNotificationToPhone('Beatstars Bot Error', 'Error key: '+key+'\nRestarting in 10 minutes.\n\n'+format_exc())
                if currentDate != today.strftime("%d/%m/%Y"):
                    break
                firstError = False
                print(format_exc())
                sleep(600)

        #Remove used image
        print('\nRemoving used details and files....\n')
        remove(chosenImage)
        print("    Removed "+str(chosenImage))
        
        #Remove used melody
        remove(usedMelody)
        print("    Removed "+str(usedMelody))
        
        #Remove the .wav and the .zip
        remove(beatLocation)
        print("    Removed "+str(beatLocation))
        remove(stemZipLocation)
        print("    Removed "+str(stemZipLocation))

        #Remove used beat name
        possibleNames = possibleNames[1:]
        with open(mainInstrumentatorObject.beatNamesTextFile, 'w') as f:
            for name in possibleNames:
                f.write(f"{name.strip()}\n")
        print("    Removed the name '"+str(beatName)+"'")

        print('\nEstimated Remaining Fuel:\n')
        print('    Melodies remaining: '+str(len(melodies)-1))
        print('    Names Remaining: '+str(len(possibleNames)))
        print('    Images Remaining: '+str(len(images)-1))

        print('\n-----------------------------------------------\n')

        #Calculate next upload time
        newTime = datetime(datetime.now().year, datetime.now().month, datetime.now().day, datetime.now().hour, datetime.now().minute) + timedelta(hours=12)

        #Alert phone of what has been done
        mainInstrumentatorObject.sendNotificationToPhone(str(beatName)+' has been uploaded.', 'Uploaded at: '+str(datetime.now().strftime("%Y-%m-%d %H:%M"))+'\nNext upload: '+str(newTime)[:-3]+'\nCurrent fuel levels: '+'\n    Melodies remaining: '+str(len(melodies)-1)+'\n    Names Remaining: '+str(len(possibleNames))+ '\n    Images Remaining: '+str(len(images)-1))

        #Wait for 12 hours
        print("Waiting 12 hours.... ("+str(newTime)[:-3]+')')
        sleep(43200)

    except Exception:
        print("\nError in run.py. Waiting 1 hour and restarting.\n")
        if firstError == True:
            mainInstrumentatorObject.sendNotificationToPhone('run.py Error', 'Restarting in 1 hour.\n\n'+format_exc())
        print(format_exc())
        sleep(3600)