from Instrumentator import Instrumentator
from os import listdir

mainInstrumentatorObject = Instrumentator(None)

print("Fuel status:")

#Update user on status of folders
melodies = listdir(mainInstrumentatorObject.inputFolder)
print('    '+str(len(melodies))+' melodies are left.')

#Choose a name for the beat
possibleNames = open(mainInstrumentatorObject.beatNamesTextFile, 'r').readlines()
print('    '+str(len(possibleNames))+" names are left.")

#Find and choose an image
images = listdir(mainInstrumentatorObject.imagesFolder)
print('    '+str(len(images))+' images are left.')