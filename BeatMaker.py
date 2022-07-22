from librosa import load
from moviepy.editor import AudioFileClip, CompositeAudioClip
from os import chdir, getcwd, path, listdir, remove, stat, rename
from pydub import AudioSegment
from pyloudness import get_loudness
from random import randint
from shutil import move, make_archive, copy
from time import sleep
import dawdreamer as daw
import numpy as np
import scipy.io.wavfile

class BeatMaker:
    def __init__(
            self,
            templateSeed,
            sampleRate = 44100,
            bufferSize = 512,
        ):

        #Find BeatMaker's location so we can find where our directories are located
        fileLocation = path.abspath(__file__)

        #Set variables
        self.sampleRate = sampleRate
        self.bufferSize = bufferSize
        self.templateSeed = templateSeed
        self.engine = daw.RenderEngine(self.sampleRate, self.bufferSize)
        self.majorKeys = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']
        self.minorKeys = ['Am', 'A#m', 'Bm', 'Cm', 'C#m', 'Dm', 'D#m', 'Em', 'Fm', 'F#m', 'Gm', 'G#m']
        self.trapMajorKeysList = []
        self.trapMinorKeysList = []

        #Path conjoiner is dependant on OS
        if fileLocation.rfind('/') >= 0:
            self.pathConjoiner = '/'
        else:
            self.pathConjoiner = '\\'

        #Find the directory the program files are in
        instance = fileLocation.rfind(self.pathConjoiner)
        fileLocation = fileLocation[0:instance+1]
        self.currentDirectory = fileLocation
        
        #Make paths from constructor information
        self.pluginFolder = self.currentDirectory+'Plugins'+self.pathConjoiner
        self.majorKeyFolder = self.currentDirectory+'Drum Loops'+self.pathConjoiner+'Major'+self.pathConjoiner
        self.minorKeyFolder = self.currentDirectory+'Drum Loops'+self.pathConjoiner+'Minor'+self.pathConjoiner
        self.processFolder = self.currentDirectory+'Process'+self.pathConjoiner
        self.inputFolder = self.processFolder+'Input'+self.pathConjoiner
        self.outputFolder = self.processFolder+'Output'+self.pathConjoiner
        self.usedMajorKeysTextFile = self.processFolder+'usedMajorKeys.txt'
        self.usedMinorKeysTextFile = self.processFolder+'usedMinorKeys.txt'
        self.finalBeatsFolder = self.currentDirectory+'Final Beats'+self.pathConjoiner
        self.risersFolder = self.currentDirectory+'FX'+self.pathConjoiner+'Risers'+self.pathConjoiner
        self.crashesFolder = self.currentDirectory+'FX'+self.pathConjoiner+'Crashes'+self.pathConjoiner

        #Get list of keys
        for file in listdir(self.majorKeyFolder):
            self.trapMajorKeysList.append(file[:file.find('-')].strip())
        for file in listdir(self.minorKeyFolder):
            self.trapMinorKeysList.append(file[:file.find('-')].strip())

    def loadAudioFile(self, song):
        sig, rate = load(song, duration=None, mono=False, sr=self.sampleRate)
        assert(rate == self.sampleRate)
        return sig
    
    def getMelodyAndDrums(self):

        #Get melody file and its key
        chdir(self.inputFolder)
        melodyFile = (sorted(listdir(self.inputFolder), key=lambda t: stat(t).st_mtime))[0]
        melodyFileKey = melodyFile[:melodyFile.find('-')].strip()
        initialKey = melodyFileKey

        #How much the melody will be transposed by
        leave = False
        if melodyFileKey in self.trapMajorKeysList:
            allLoops = listdir(self.majorKeyFolder)
            chdir(self.majorKeyFolder)
        else:
            allLoops = listdir(self.minorKeyFolder)
            chdir(self.minorKeyFolder)

        counter = 0

        #Keep doing until told to leave the loop
        while(leave == False):

            #Loop over all the trap loops
            for loop in allLoops:

                #Get the key of the current loop in scope
                currentLoopKey = loop[:loop.find('-')].strip()

                #If this trap loop key is the same as our melody's key (or the updated melody's key), continue
                if currentLoopKey == melodyFileKey:
                    
                    #Get the used trap loops. This textfile resets once all the trap loops have been used.
                    usedFiles = []
                    if melodyFileKey in self.trapMajorKeysList:
                        for file in open(self.usedMajorKeysTextFile, 'r').readlines():
                            usedFiles.append(file.strip())
                    if melodyFileKey in self.trapMinorKeysList:
                        for file in open(self.usedMinorKeysTextFile, 'r').readlines():
                            usedFiles.append(file.strip())
                        
                    #If the loop hasn't been used yet, use it and add it to used.txt
                    if (loop not in usedFiles):
                        if melodyFileKey in self.trapMajorKeysList:
                            chosenTrapBeat = loop
                            leave = True
                            open(self.usedMajorKeysTextFile, 'a').write('\n'+str(loop))
                            break
                        if melodyFileKey in self.trapMinorKeysList:
                            chosenTrapBeat = loop
                            leave = True
                            open(self.usedMinorKeysTextFile, 'a').write('\n'+str(loop))
                            break
            
            #When no loop in the current melody key is found, increment to the next key 
            if melodyFileKey in self.trapMajorKeysList:
                instance = self.majorKeys.index(melodyFileKey)
                melodyFileKey = self.majorKeys[(instance+1) % len(self.majorKeys)]
            else:
                instance = self.minorKeys.index(melodyFileKey)
                melodyFileKey = self.minorKeys[(instance+1) % len(self.minorKeys)]

            counter = counter + 1

            if counter == len(allLoops):
                break

        #If counter == allLoops then we've seen all the loops and haven't found one. So reset the used.txt so we can re-use beats
        if counter == len(allLoops) and (melodyFileKey in self.majorKeys):
            open(self.usedMajorKeysTextFile, 'w').write('PLACEHOLDER')
            return False
        if counter == len(allLoops) and (melodyFileKey in self.minorKeys):
            open(self.usedMinorKeysTextFile, 'w').write('PLACEHOLDER')
            return False
        else:
            
            #Get bpms
            melodyFileBpm = melodyFile[melodyFile.find('-')+1:melodyFile.rfind('B')].strip()
            trapFileBpm = chosenTrapBeat[chosenTrapBeat.find('-')+1:chosenTrapBeat.rfind('B')].strip()

            print('Chosen Trap Loop   : '+chosenTrapBeat)
            print('Chosen Melody Loop : '+melodyFile+'\n')

            if (melodyFileKey in self.trapMajorKeysList):
                keyGenre = 'Major'
                return chosenTrapBeat, melodyFile, self.majorKeys[(instance) % len(self.minorKeys)], initialKey, keyGenre, melodyFileBpm, trapFileBpm
            else:
                keyGenre = 'Minor'
                return chosenTrapBeat, melodyFile, self.minorKeys[(instance) % len(self.minorKeys)], initialKey, keyGenre, melodyFileBpm, trapFileBpm

    def transposeMelodyAndBpm(self, file, newKey, oldKey, name, melodyBpm=1, trapBpm=1, justTranspose=False, setTransposeValue=0, stringValue=''):
        
        graph = []

        if justTranspose == True:
            changekey_processor = self.engine.make_playbackwarp_processor("change_key", self.loadAudioFile(file))
            changekey_processor.transpose = setTransposeValue
            graph.append((changekey_processor, []))
            self.exportGraphAsWav(graph, file, name, melodyBpm, trapBpm)
            return (self.outputFolder+name+'.wav')
        
        #Set engine plugin
        changekey_processor = self.engine.make_playbackwarp_processor("change_key", self.loadAudioFile(file))

        #Find the difference between the two keys
        if oldKey in self.minorKeys:
            transposeValue = self.minorKeys.index(newKey)-self.minorKeys.index(oldKey)
        else:
            transposeValue = self.majorKeys.index(newKey)-self.majorKeys.index(oldKey)
        
        #If increase if larger than 6 or decrease is smaller than 6, flip the sign and change the number
        if transposeValue < -6:
            transposeValue = transposeValue+12
        if transposeValue > 6:
            transposeValue = transposeValue-12

        #Transpose the audio clip
        changekey_processor.transpose = transposeValue
        changekey_processor.time_ratio = int(melodyBpm)/int(trapBpm)

        graph.append((changekey_processor, []))
        self.exportGraphAsWav(graph, file, name, melodyBpm, trapBpm)

        #Return the change graph and the new element's key
        return (self.outputFolder+name+'.wav')

    def exportGraphAsWav(self, graph, file, name, bpm1=1, bpm2=1):
        self.engine.load_graph(graph)
        durationOfClip = AudioFileClip(file)
        self.engine.render(durationOfClip.duration * int(bpm1)/int(bpm2))
        durationOfClip.close()

        audio = self.engine.get_audio()
        scipy.io.wavfile.write(self.outputFolder+name+'.wav', self.sampleRate, audio.transpose())

    def makeBeat(self):

        print("Constructing beat....\n")

        #Get the melody and drum file
        returnValue = False
        while(returnValue == False):
            returnValue = self.getMelodyAndDrums()
        
        #Get the variables
        trapBeat, melody, keyTheMelodyShouldBeTurnedInto, initialMelodyKey, keyGenre, melodyFileBpm, trapFileBpm = returnValue
        
        #Set the variables
        trapBeatFile = trapBeat
        trapBeat = self.currentDirectory+'Drum Loops'+self.pathConjoiner+keyGenre+self.pathConjoiner+trapBeat
        newTrapBeat = self.outputFolder+'Trap Beat - '+trapBeatFile
        melody = self.inputFolder+melody

        #Copy trap beat into folder where we'll be doing our work
        copy(trapBeat, self.outputFolder)
        rename(self.outputFolder+trapBeatFile, newTrapBeat)

        #Set trap beat to 1, trim it and cut off any clicks that may be there
        newTrapBeat = self.checkAndChangeVolume(newTrapBeat, wantedVolume=0.8)
        newTrapBeat = self.cutAndOrFade(newTrapBeat, trapFileBpm)

        #Transpose, mix, clip, and fade melody
        transposedMelody = self.transposeMelodyAndBpm(melody, keyTheMelodyShouldBeTurnedInto, initialMelodyKey, 'Melody - '+keyTheMelodyShouldBeTurnedInto+' '+trapFileBpm+' BPM', melodyBpm=melodyFileBpm, trapBpm=trapFileBpm,)
        transposedMelody = self.checkAndChangeVolume(transposedMelody, volumeRange=(-7,-9))
        transposedMelody = self.cutAndOrFade(transposedMelody, trapFileBpm)

        #Make and export clip with melody and beat playing
        transposedMelodyAndTrapBeat = self.mergeAudioFiles([transposedMelody, newTrapBeat], 'Melody + Trap Beat')

        if self.templateSeed == 1:

            #Tranpose the melody 12 semitones up and export the clip
            raisedTransposedMelody = self.transposeMelodyAndBpm(transposedMelody, keyTheMelodyShouldBeTurnedInto, keyTheMelodyShouldBeTurnedInto, 'Melody Raised 12 Semitones', justTranspose=True, setTransposeValue=12)

            #Make and export clip with melody and beat playing
            raisedMelodyAndTrapBeat = self.mergeAudioFiles([raisedTransposedMelody, newTrapBeat], 'Melody Raised 12 Semitones + Trap Beat')

            #Add riser to end of melody
            transposedMelodyWithRiser = self.addFX(transposedMelody, sound='Riser', position='Back')

            #Add crash to beginning of raised melody
            raisedTransposedMelodyWithCrash = self.addFX(raisedTransposedMelody, sound='Crash', position='Front')

            #Concatenate clips in a particular order to make the beat structure (export this file)
            preCompressionFinalBeat = self.beatStructure([transposedMelodyWithRiser, transposedMelodyAndTrapBeat, raisedMelodyAndTrapBeat, transposedMelodyWithRiser, transposedMelodyAndTrapBeat, raisedMelodyAndTrapBeat, raisedTransposedMelodyWithCrash], 'Pre-Compression Beat', trapFileBpm)
            
            #Take final beat structure and compress it. Beat has been made.
            self.compressAudio(preCompressionFinalBeat, trapBeatFile[:-4]+' FINAL BEAT')
        
        if self.templateSeed == 2:

            #Tranpose the melody 12 semitones down
            loweredTransposedMelody = self.transposeMelodyAndBpm(transposedMelody, keyTheMelodyShouldBeTurnedInto, keyTheMelodyShouldBeTurnedInto, 'Melody Lowered 12 Semitones', justTranspose=True, setTransposeValue=-12)
            loweredTransposedMelody = self.checkAndChangeVolume(loweredTransposedMelody, volumeRange=(-7,-9))
            loweredTransposedMelody = self.cutAndOrFade(loweredTransposedMelody, trapFileBpm)
            
            #Transpose the melody 12 semitones up
            raisedTransposedMelody = self.transposeMelodyAndBpm(transposedMelody, keyTheMelodyShouldBeTurnedInto, keyTheMelodyShouldBeTurnedInto, 'Melody Raised 12 Semitones', justTranspose=True, setTransposeValue=12)
            raisedTransposedMelody = self.cutAndOrFade(raisedTransposedMelody, trapFileBpm)

            #Make and export clip with melody and beat playing
            raisedMelodyAndTrapBeat = self.mergeAudioFiles([raisedTransposedMelody, newTrapBeat], 'Melody Raised 12 Semitones + Trap Beat')

            #Add riser to end of lowered melody
            loweredTransposedMelodyWithRiser = self.addFX(loweredTransposedMelody, sound='Riser', position='Back')

            #Add riser to end of normal melody
            transposedMelodyWithRiser = self.addFX(transposedMelody, sound='Riser', position='Back')

            #Add fx to beat
            trapBeatWithFX = self.addFX(newTrapBeat, sound='Crash', position='Front')

            #Concatenate clips in a particular order to make the beat structure (export this file)
            preCompressionFinalBeat = self.beatStructure([loweredTransposedMelodyWithRiser, transposedMelodyAndTrapBeat, raisedMelodyAndTrapBeat, transposedMelodyWithRiser, transposedMelodyAndTrapBeat, raisedMelodyAndTrapBeat, loweredTransposedMelodyWithRiser, trapBeatWithFX], 'Pre-Compression Beat', trapFileBpm)

            self.compressAudio(preCompressionFinalBeat, trapBeatFile[:-4]+' FINAL BEAT')
        
        elif self.templateSeed == 3:

            #Tranpose the melody 12 semitones down
            loweredTransposedMelody = self.transposeMelodyAndBpm(transposedMelody, keyTheMelodyShouldBeTurnedInto, keyTheMelodyShouldBeTurnedInto, 'Melody Lowered 12 Semitones', justTranspose=True, setTransposeValue=-12)
            loweredTransposedMelody = self.checkAndChangeVolume(loweredTransposedMelody, volumeRange=(-7,-9))
            loweredTransposedMelody = self.cutAndOrFade(loweredTransposedMelody, trapFileBpm)

            #Tranpose the melody 12 semitones up
            raisedTransposedMelody = self.transposeMelodyAndBpm(transposedMelody, keyTheMelodyShouldBeTurnedInto, keyTheMelodyShouldBeTurnedInto, 'Melody Raised 12 Semitones', justTranspose=True, setTransposeValue=12)
            raisedTransposedMelody = self.checkAndChangeVolume(raisedTransposedMelody, volumeRange=(-7,-9))
            raisedTransposedMelody = self.cutAndOrFade(raisedTransposedMelody, trapFileBpm)

            #Filter the trapbeat
            filteredTrapBeat = self.filterAudio(newTrapBeat, 'Filtered Trap Beat', automate=True, automateType='Exponential')

            #Add riser to melody
            loweredTransposedMelodyWithRiser = self.addFX(loweredTransposedMelody, sound='Riser', position='Back')

            #Make and export clip with melody and beat playing
            raisedMelodyAndTrapBeat = self.mergeAudioFiles([raisedTransposedMelody, newTrapBeat], 'Melody Raised 12 Semitones + Trap Beat')

            #Melody with crash at the beginning and riser at the end
            transposedMelodyWithFX = self.addFX(transposedMelody, sound='Crash', position='Front')
            transposedMelodyWithFX = self.addFX(transposedMelodyWithFX, sound='Riser', position='Back')

            #Trap beat with crash at the beginning
            trapBeatWithFX = self.addFX(newTrapBeat, sound='Crash', position='Front')

            #Concatenate clips in a particular order to make the beat structure (export this file)
            preCompressionFinalBeat = self.beatStructure([filteredTrapBeat, transposedMelodyWithFX, transposedMelodyAndTrapBeat, loweredTransposedMelodyWithRiser, transposedMelodyAndTrapBeat, raisedMelodyAndTrapBeat, loweredTransposedMelodyWithRiser, trapBeatWithFX], 'Pre-Compression Beat', trapFileBpm)

            self.compressAudio(preCompressionFinalBeat, trapBeatFile[:-4]+' FINAL BEAT')

        elif self.templateSeed == 4:

            #Tranpose the melody 12 semitones up
            raisedTransposedMelody = self.transposeMelodyAndBpm(transposedMelody, keyTheMelodyShouldBeTurnedInto, keyTheMelodyShouldBeTurnedInto, 'Melody Raised 12 Semitones', justTranspose=True, setTransposeValue=12)
            raisedTransposedMelody = self.checkAndChangeVolume(raisedTransposedMelody, volumeRange=(-7,-9))
            raisedTransposedMelody = self.cutAndOrFade(raisedTransposedMelody, trapFileBpm)

            #Tranpose the melody 12 semitones down
            loweredTransposedMelody = self.transposeMelodyAndBpm(transposedMelody, keyTheMelodyShouldBeTurnedInto, keyTheMelodyShouldBeTurnedInto, 'Melody Lowered 12 Semitones', justTranspose=True, setTransposeValue=-12)
            loweredTransposedMelody = self.checkAndChangeVolume(loweredTransposedMelody, volumeRange=(-7,-9))
            loweredTransposedMelody = self.cutAndOrFade(loweredTransposedMelody, trapFileBpm)

            #Raised melody with trap beat
            raisedMelodyAndTrapBeat = self.mergeAudioFiles([raisedTransposedMelody, newTrapBeat], 'Raised Melody + Trap Beat')

            #Add reverb to melody
            transposedMelodyWithReverb = self.addReverb(transposedMelody, dry_level=0.3)

            #Add FX to reverbed melody
            transposedMelodyWithReverbWithFX = self.addFX(transposedMelodyWithReverb, sound='Riser', position='Back')
            transposedMelodyWithReverbWithFX = self.checkAndChangeVolume(transposedMelodyWithReverbWithFX, volumeRange=(-7,-9))

            #Trap beat with crash at the beginning
            trapBeatWithFX = self.addFX(newTrapBeat, sound='Crash', position='Front')

            #Concatenate clips in a particular order to make the beat structure (export this file)
            preCompressionFinalBeat = self.beatStructure([transposedMelodyWithReverbWithFX, transposedMelodyAndTrapBeat, raisedMelodyAndTrapBeat, transposedMelodyWithReverbWithFX, transposedMelodyAndTrapBeat, raisedMelodyAndTrapBeat, loweredTransposedMelody, trapBeatWithFX], 'Pre-Compression Beat', trapFileBpm)

            self.compressAudio(preCompressionFinalBeat, trapBeatFile[:-4]+' FINAL BEAT')

        #Removed the used melody
        print('\nRemoved Melody : '+melody+'\n')
        remove(melody)

        nameAdd = 0
        while(1):
            try:
                if nameAdd == 0:
                    #Put the files in a zip file
                    chdir(self.finalBeatsFolder)
                    make_archive(trapBeatFile[:-4]+' FINAL BEAT', 'zip', self.outputFolder)

                    #Move final beat and used melody to separate directories
                    chdir(self.outputFolder)
                    move(trapBeatFile[:-4]+' FINAL BEAT.wav', self.finalBeatsFolder)
                else:
                    chdir(self.finalBeatsFolder)
                    make_archive(trapBeatFile[:-4]+' '+str(nameAdd)+' FINAL BEAT', 'zip', self.outputFolder)
                    
                    chdir(self.outputFolder)
                    rename(trapBeatFile[:-4]+' '+str(nameAdd-1)+' FINAL BEAT.wav', trapBeatFile[:-4]+' '+str(nameAdd)+'FINAL BEAT.wav')
                    move(trapBeatFile[:-4]+' '+str(nameAdd)+' FINAL BEAT.wav', self.finalBeatsFolder)
                break
            except Exception:
                nameAdd = nameAdd+1

        #Remove all the by-product files
        chdir(self.outputFolder)
        for file in listdir(self.outputFolder):
            remove(file)

        #Removed the used melody
        print('\nRemoved Melody : '+melody+'\n')
        # remove(melody)

        #Return the used melody
        return self.outputFolder+trapBeatFile[:-4]+' FINAL BEAT.wav', trapBeatFile[:-4]+' FINAL BEAT.wav', self.outputFolder+trapBeatFile[:-4]+' FINAL BEAT.zip', trapBeatFile[:-4]+' FINAL BEAT.zip'

    def mergeAudioFiles(self, files, name):
        
        audioClipFiles = []
        for file in files:
            audioClipFiles.append(AudioFileClip(file))
        
        CompositeAudioClip(audioClipFiles).write_audiofile(self.outputFolder+name+'.wav', fps=44100, codec='pcm_s32le')

        return (self.outputFolder+name+'.wav')

    def beatStructure(self, files, name, bpm):
        
        beatsPerEightBars = 32

        fullLength = ((beatsPerEightBars*len(files))/int(bpm))*60*1000

        beatFile = AudioSegment.silent(duration=fullLength)

        counter = 0
        for file in files:
            soundFile = AudioSegment.from_wav(file)
            if len(soundFile) < fullLength/len(files):
                soundFile += AudioSegment.silent(duration=fullLength/len(files)-len(soundFile))
            elif len(soundFile) > fullLength/len(files):
                soundFile = soundFile[:fullLength/len(files)]
            
            beatFile = beatFile.overlay(soundFile, position=(fullLength/len(files))*counter)
            counter+=1
        
        beatFile.export(self.outputFolder+name+'.wav', 'wav')

        return (self.outputFolder+name+'.wav')

    def compressAudio(self, file, name):

        playback_processor = self.engine.make_playback_processor("playback", self.loadAudioFile(file))

        soft_clipper = self.engine.make_plugin_processor("my_soft_clipper", self.pluginFolder+self.pathConjoiner+'Initial Clipper.dll')
        soft_clipper.set_parameter(0, 1.0) #Threshold
        soft_clipper.set_parameter(1, 0.5) #Input gain
        soft_clipper.set_parameter(2, 0.0) #Positive saturation
        soft_clipper.set_parameter(3, 0.0) #Negative saturation
        soft_clipper.set_parameter(4, 0.0) #Saturate (0.0==False, 1.0==True)
        
        graph = [
            (playback_processor, []),
            (soft_clipper, ["playback"])
        ]

        #Make the final audio
        self.exportGraphAsWav(graph, file, name)

        #Return the new file
        return (self.outputFolder+name+'.wav')
    
    def filterAudio(self, file, name, automate=False, automateType='Linear'):

        playback_processor = self.engine.make_playback_processor("song", self.loadAudioFile(file))

        filter_processor = self.engine.make_filter_processor("the_filter", "low")

        filter_processor.mode = 'low'

        if automate == True:
            freq = self.createAutomationSlope(file, automateType)
            filter_processor.set_automation("freq", freq)

        graph = [
            (playback_processor, []),
            (filter_processor, ["song"])
        ]

        self.exportGraphAsWav(graph, file, name)

        #Return the new file
        return (self.outputFolder+name+'.wav')

    def createAutomationSlope(self, file, slopeType):

        num_samples = AudioSegment.from_wav(file).duration_seconds * self.sampleRate
        a = np.linspace(0, 1, num=int(num_samples), endpoint=True)
        base = np.e
        b = np.power(base, a)

        if slopeType == 'Exponential':
            c = (b-1)/(5*base-1)
        if slopeType == 'Linear':
            c = a

        return 200. + (20000-200.)*c

    def checkAndChangeVolume(self, file, wantedVolume=False, volumeRange=False):

        #Get peak of passed file
        peak = self.getPeak(file)
        print(file[file.rfind(self.pathConjoiner)+1:-4]+"'s Old Peak : "+str(peak))

        #If user set a specific db to be set to, set the min and max to that loudness
        
        if volumeRange == False:
            maxVolume = wantedVolume
            minVolume = wantedVolume
        else:
            maxVolume, minVolume = volumeRange
        
        #Sometimes comes out as negative 0 (doesnt mean/do anything but still i want it positive)
        if peak == -0.0:
            peak = 0.0

        #Subtract/add the difference to get the audio's peak within the desired range
        if peak > maxVolume:
            audioFile = AudioSegment.from_wav(file)
            audioFile = audioFile - (peak-maxVolume)
            audioFile.export(file, format='wav')
        elif peak < minVolume:
            audioFile = AudioSegment.from_wav(file)
            audioFile = audioFile - (peak-minVolume)
            audioFile.export(file, format='wav')

        #Get the new audio peak 
        peak = self.getPeak(file)
        print(file[file.rfind(self.pathConjoiner)+1:-4]+"'s New Peak : "+str(peak)+' (new peak may not be exactly what was specified)\n')
        
        #Return the file. It's the same as the one that was passed.
        return file
    
    def cutAndOrFade(self, file, bpm, fade=False, fadeNumber=128, fadeType='Both'):
        
        #Get the file
        pydubFile = AudioSegment.from_wav(file)
        
        #Trim the file to make sure it doesnt trail past or stop short of 8 bars
        if pydubFile.duration_seconds > ((32/int(bpm))*60):
            pydubFile = pydubFile[:((32/int(bpm))*60)*1000]
        elif pydubFile.duration_seconds < ((32/int(bpm))*60):
            difference = ((32/int(bpm))*60)*1000 - pydubFile.duration_seconds*1000
            pydubFile = pydubFile+AudioSegment.silent(duration=difference)

        #Fade the audio if specified
        if fade == True:
            if fadeType=='Both':
                pydubFile = pydubFile.fade_in(round((pydubFile.duration_seconds*1000)/fadeNumber)).fade_out(round((pydubFile.duration_seconds*1000)/fadeNumber))
            if fadeType=='In':
                pydubFile = pydubFile.fade_in(round((pydubFile.duration_seconds*1000)/fadeNumber))
            if fadeType=='Out':
                pydubFile = pydubFile.fade_out(round((pydubFile.duration_seconds*1000)/fadeNumber))
        
        #Export and return the file
        pydubFile.export(file, format="wav")
        return file

    def getPeak(self, file):
        loudness_stats = get_loudness(file)
        peak = loudness_stats.get('True Peak').get('Peak')
        return peak
    
    def addFX(self, file1, sound, position):
        
        #Choose whether FX will be a crash or riser
        if sound == 'Riser':
            risers = listdir(self.risersFolder)
            chosenRiser = risers[randint(0, len(risers)-1)]
            file2 = self.risersFolder+chosenRiser
        elif sound == 'Crash':
            crashes = listdir(self.crashesFolder)
            chosenCrash = crashes[randint(0, len(crashes)-1)]
            file2 = self.crashesFolder+chosenCrash
        
        #Set the files to be used
        base = AudioSegment.from_wav(file1)
        layered = AudioSegment.from_wav(file2)

        #Choose the position of the FX
        if position == 'Back':
            overlay = base.overlay(layered, position=(base.duration_seconds*1000-layered.duration_seconds*1000))
        if position == 'Front':
            overlay = base.overlay(layered, position=0)
        
        #Export sound
        overlay.export(file1[:-4]+' with '+sound+'.wav', format="wav")

        #Add fx sound to the output folder
        copy(file2, self.outputFolder)

        #Return the edited sound
        return file1[:-4]+' with '+sound+'.wav'
    
    def addReverb(self, file, room_size=0.5, damping=0.5, wet_level=0.33, dry_level=0.4, width=1.):
        playback_processor = self.engine.make_playback_processor("playback", self.loadAudioFile(file))

        reverb_processor = self.engine.make_reverb_processor("my_reverb", room_size, damping, wet_level, dry_level, width)
        reverb_processor.room_size = room_size
        reverb_processor.damping = damping
        reverb_processor.wet_level = wet_level
        reverb_processor.dry_level = dry_level
        reverb_processor.width = width

        graph = [
            (playback_processor, []),
            (reverb_processor, ["playback"])
        ]

        self.exportGraphAsWav(graph, file, file[file.rfind(self.pathConjoiner):][:-4]+' with Reverb')

        return (file[:-4]+' with Reverb.wav')