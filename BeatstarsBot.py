from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from os import path
from random import randint
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
from webdriver_manager.chrome import ChromeDriverManager
from imap_tools import MailBox


class BeatstarsBot:
    def __init__(self, username, password, beatLocation, stemZipLocation, imageLocation, beatTitle, beatDescription, beatTags, beatGenres, beatMoods, beatKey, beatBPM):

        #Find file location
        fileLocation = path.abspath(__file__)

        #Path conjoiner is dependant on OS
        if fileLocation.rfind('/') >= 0:
            self.pathConjoiner = '/'

            #Set webdriver configurations
            options = Options()
            options.headless = True
            driver = webdriver.Chrome("/usr/bin/chromedriver", options=options)

        else:
            self.pathConjoiner = '\\'

            #Set webdriver configurations
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        #Get main directory
        instance = fileLocation.rfind(self.pathConjoiner)
        fileLocation = fileLocation[0:instance+1]
        self.fileLocation = fileLocation
        self.emailCreds = fileLocation+'email_creds.txt'

        #Set variables
        self.username = username
        self.password = password
        self.beatLocation = beatLocation
        self.stemZipLocation = stemZipLocation
        self.imageLocation = imageLocation
        self.beatTitle = beatTitle
        self.beatDescription = beatDescription
        self.beatTags = beatTags
        self.beatGenres = beatGenres
        self.beatMoods = beatMoods
        self.beatBPM = beatBPM
        self.driver = driver
        self.errorScreenshotsFolder = fileLocation+'Error Screenshots'+self.pathConjoiner
        self.emailCode = fileLocation+'email_code.txt'
        self.action = ActionChains(self.driver)

        #Translate key to beatstars key ID
        beatstarsIDs = {'Am' : 2, 'A' : 3, 'A#m' : 4, 'A#' : 5, 'Bm' : 8, 'B' : 9, 'Cm' : 11, 'C' : 12, 'C#m' : 13, 'C#' : 14, 'Dm' : 17, 'D' : 18, 'D#m' : 19, 'D#' : 20, 'Em' : 23, 'E' : 24, 'Fm' : 25, 'F' : 26, 'F#m' : 27, 'F#' : 28, 'Gm' : 30, 'G' : 31, 'G#m' : 32, 'G#' : 33}
        self.beatKeyID = beatstarsIDs[beatKey]

    def accessWebsite(self):

        #Go to website
        self.driver.get('https://studio.beatstars.com/content/tracks/uploaded')

    def login(self):

        #Check and see if already logged in
        try:
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, 'input-username')))
            oldLoginPage = True
            print("    Logging in.... (old login page)")
        except TimeoutException:
            try:
                WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, 'oath-email')))
                print("    Logging in.... (new login page)")
                oldLoginPage = False
            except TimeoutException:
                print("    Already logged in")
                return
    
        #Input username, password, and click sign in
        if oldLoginPage == True:
            WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.ID, 'input-username')))[1].send_keys(self.username)
            self.superSleep()
            WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.ID, 'input-password')))[1].send_keys(self.password)
            self.superSleep()
            WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'action-element')))[0].click()
            self.superSleep()
            self.fillAndCheckEmailCode()
    
        else:
            WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.ID, 'oath-email'))).send_keys(self.username)
            self.superSleep()
            WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'action-element')))[0].click()
            self.superSleep()
            WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.ID, 'userPassword'))).send_keys(self.password)
            self.superSleep()
            WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'action-element')))[1].click()
            self.fillAndCheckEmailCode()
        
        #Sometimes redirected to a page-not-found
        if 'page-not-found' in str(self.driver.current_url):
            WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'wrapper-button')))[0].click()
            WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'option-action-mat-menu')))[0].click()
            self.driver.switch_to.window(self.driver.window_handles[1])
            try:
                WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'action-link')))[0].click()
            except TimeoutException:
                WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, "//*[text() = 'Go to Beatstars Studio.']"))).click()
            if 'content/tracks/' not in str(self.driver.current_url):
                WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'menu-name')))[0].click()
                WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'ng-star-inserted')))[9].click()
            if len(self.driver.window_handles) > 1:
                self.driver.switch_to.window(self.driver.window_handles[0])
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])

    def getPastCode(self):

        creds = open(self.emailCreds, 'r').readlines()
        username = creds[0].strip()
        password = creds[1].strip()

        with MailBox('imap.gmail.com').login(username, password) as mailbox:
            while(1):
                for msg in mailbox.fetch('TEXT "Beatstars Verification Code"', reverse=True, limit=1):
                    open(self.emailCode, 'w').write(msg.subject[-4:].strip())

    def getCode(self):

        pastCode = open(self.emailCode, 'r').read()
        creds = open(self.emailCreds, 'r').readlines()
        username = creds[0].strip()
        password = creds[1].strip()

        with MailBox('imap.gmail.com').login(username, password) as mailbox:
            while(1):
                sleep(1)
                for msg in mailbox.fetch('TEXT "Beatstars Verification Code"', reverse=True, limit=1):
                    if pastCode == msg.subject[-4:].strip():
                        print("New code not received yet. Still waiting....")
                    else:
                        open(self.emailCode, 'w').write(msg.subject[-4:].strip())
                        return msg.subject[-4:].strip()

    def makeNewTrack(self):

        #Click the add tracks button
        currentWebsite = str(self.driver.current_url)
        try:
            WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'action-element')))[0].click()
        except StaleElementReferenceException:
            WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'action-element')))[0].click()
        self.superSleep()

        #Wait until website changes
        while(str(self.driver.current_url) == currentWebsite):
            sleep(0.5)

        #Sometimes redirected to the wrong page
        if 'www.beatstars.com/tracks' in str(self.driver.current_url):
            try:
                WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'action-link')))[0].click()
            except TimeoutException:
                WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, "//*[text() = 'Go to Beatstars Studio.']"))).click()
            if 'content/tracks/' not in str(self.driver.current_url):
                WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'menu-name')))[0].click()
                WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'ng-star-inserted')))[9].click()
            self.superSleep()

            #Click the add tracks button
            currentWebsite = str(self.driver.current_url)
            WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'action-element')))[0].click()

        #Check tab situation
        while(currentWebsite == str(self.driver.current_url)):
            sleep(0.5)
        sleep(3)
        if len(self.driver.window_handles) > 1:
            self.driver.switch_to.window(self.driver.window_handles[1])
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])

    def uploadWav(self):

        #Click wav upload button
        print('    Uploading untagged wav....')
        print('    Uploading tagged mp3....')
        self.driver.execute_script('arguments[0].click();', WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'action-element')))[1])
        self.superSleep()

        #Upload the wav file
        try:
            dropFiles = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'uppy-DragDrop-input')))
            dropFiles.send_keys(self.beatLocation)
        except StaleElementReferenceException:
            dropFiles = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'uppy-DragDrop-input')))
            dropFiles.send_keys(self.beatLocation)
        self.superSleep()
        
        #Wait until the mp3 play button is enabled, meaning the upload is finished
        while(1):
            try:
                playButton = WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'action-element')))[2]
                if playButton.is_enabled() == True:
                    print('    Uploaded untagged wav.')
                    print('    Uploaded tagged mp3.')
                    break
            except StaleElementReferenceException:
                playButton = WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'action-element')))[2]
        
    def uploadZip(self):

        #Click upload track stems button
        print('    Uploading track stems....')
        self.driver.execute_script('arguments[0].click();', WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'action-element')))[2])

        #Upload the zip file
        try:
            dropFiles = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'uppy-DragDrop-input')))
            dropFiles.send_keys(self.stemZipLocation)
        except StaleElementReferenceException:
            dropFiles = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'uppy-DragDrop-input')))
            dropFiles.send_keys(self.stemZipLocation)
        self.superSleep()
        
        #Wait until replace button is showing for zip
        while(1):
            try:
                theButton = WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'vb-btn-additional-primary-text-m')))[2]
                if theButton.is_enabled() == True:
                    if 'Replace' in theButton.text:
                        print('    Uploaded track stems.')
                        self.superSleep()
                        break
            except StaleElementReferenceException as e:
                theButton = WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'vb-btn-additional-primary-text-m')))[2]

        #Go to next step
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//bs-square-button[@data-qa='button_upload_next']"))).click()
        self.superSleep()
        
    def uploadImage(self):

        #Upload the image
        print('    Uploading image....')
        self.driver.execute_script('arguments[0].click();', WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'action-element')))[0])
        self.superSleep()
        self.driver.execute_script('arguments[0].click();', WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'mat-menu-item')))[0])
        self.superSleep()
        try:
            uploadImage = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'uppy-DragDrop-input')))
            uploadImage.send_keys(self.imageLocation)
        except StaleElementReferenceException:
            uploadImage = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'uppy-DragDrop-input')))
            uploadImage.send_keys(self.imageLocation)
        self.superSleep()
        self.driver.execute_script('arguments[0].click();', WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'action-element')))[8])
        self.superSleep()
        print('    Image uploaded.')

    def uploadBasicInfo(self, dealForTitle, private=False):

        #Upload title
        print('    Uploading title....')
        try:
            titleBox = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.ID, 'title')))
            titleBox.clear()
            titleBox.send_keys(self.beatTitle+' '+dealForTitle)
        except StaleElementReferenceException:
            titleBox = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.ID, 'title')))
            titleBox.clear()
            titleBox.send_keys(self.beatTitle+' '+dealForTitle)
        self.superSleep()
        print('    Title uploaded.')

        #Upload description
        print('    Uploading description....')
        try:
            descBox = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, '//textarea[@placeholder="Description"]')))
            descBox.clear()
            descBox.send_keys(self.beatDescription)
        except StaleElementReferenceException:
            descBox = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, '//textarea[@placeholder="Description"]')))
            descBox.clear()
            descBox.send_keys(self.beatDescription)
        self.superSleep()
        print('    Description uploaded.')

        if private == True:
            print('    This is a private upload.')
            WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'mat-radio-container')))[0].click()

        #Go to next step
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//bs-square-button[@data-qa='button_upload_next']"))).click()
        self.superSleep()
        
    def uploadMetadata(self):
        
        #Remove all pre-set details
        print("    Removing pre-set details....")
        try:
            removeButtons = WebDriverWait(self.driver, 5).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'vb-icon-close-s-silent-solid')))
            for button in removeButtons:
                while(1):
                    self.driver.execute_script('arguments[0].click();', button)
                    self.superSleep()
                    break
        except TimeoutException:
            pass
        except StaleElementReferenceException:
            removeButtons = WebDriverWait(self.driver, 5).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'mat-chip-remove')))
            for button in removeButtons:
                while(1):
                    self.driver.execute_script('arguments[0].click();', button)
                    self.superSleep()
                    break
        print("    Pre-set details removed.")

        #Upload tags
        print("    Setting beat tags....")
        try:
            tagBox = WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'mat-chip-input')))[0]
            tagBox.send_keys(str(self.beatTags[0])+','+str(self.beatTags[1])+','+str(self.beatTags[2])+',')
        except StaleElementReferenceException:
            tagBox = WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'mat-chip-input')))[0]
            tagBox.send_keys(str(self.beatTags[0])+','+str(self.beatTags[1])+','+str(self.beatTags[2])+',')
        self.superSleep()
        print("    Beat tags set.")

        # ###### GENRE AND MOOD SELECTION IS NOT FUNCTIONING PROPERLY ######
        #
        # #Select genres
        # print("    Selecting genres....")
        # for genre in self.beatGenres:
        #     try:
        #         genreBox = WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'mat-chip-input')))[0]
        #         genreBox.send_keys(genre)
        #     except StaleElementReferenceException:
        #         genreBox = WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'mat-chip-input')))[0]
        #         genreBox.send_keys(genre)
        #     self.superSleep()
        #     try:
        #         self.driver.execute_script('arguments[0].click();', genreBox)
        #         self.action.send_keys(Keys.ARROW_DOWN).perform()
        #         self.action.send_keys(Keys.ENTER).perform()
        #     except StaleElementReferenceException:
        #         self.driver.execute_script('arguments[0].click();', genreBox)
        #         self.action.send_keys(Keys.ARROW_DOWN).perform()
        #         self.action.send_keys(Keys.ENTER).perform()
        #     self.superSleep()
        #     try:
        #         addButton = WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'add-button')))[0]
        #         self.driver.execute_script('arguments[0].click();', addButton)
        #     except StaleElementReferenceException:
        #         addButton = WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'add-button')))[0]
        #         self.driver.execute_script('arguments[0].click();', addButton)
        #     self.superSleep()
        # print('    Genres selected.')

        # #Select moods
        # print("    Selecting mood....")
        # for mood in self.beatMoods:
        #     try:
        #         moodBox = WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'mat-input-element')))[1]
        #         moodBox.send_keys(mood)
        #     except StaleElementReferenceException:
        #         moodBox = WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'mat-input-element')))[1]
        #         moodBox.send_keys(mood)
        #     self.superSleep()
        #     try:
        #         self.driver.execute_script('arguments[0].click();', moodBox)
        #         self.action.send_keys(Keys.ARROW_DOWN).perform()
        #         self.action.send_keys(Keys.ENTER).perform()
        #     except StaleElementReferenceException:
        #         self.driver.execute_script('arguments[0].click();', moodBox)
        #         self.action.send_keys(Keys.ARROW_DOWN).perform()
        #         self.action.send_keys(Keys.ENTER).perform()
        #     self.superSleep()
        #     try:
        #         addButton = WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'add-button')))[1]
        #         self.driver.execute_script('arguments[0].click();', addButton)
        #     except StaleElementReferenceException:
        #         addButton = WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'add-button')))[1]
        #         self.driver.execute_script('arguments[0].click();', addButton)
        #     self.superSleep()
        # print('    Moods selected')

        #Input Key
        print('    Selecting key....')
        try:
            selectKey = Select(WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'ng-valid')))[8])
            self.superSleep()
            selectKey.select_by_index(self.beatKeyID)
        except StaleElementReferenceException:
            selectKey = Select(WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'ng-valid')))[8])
            self.superSleep()
            selectKey.select_by_index(self.beatKeyID)
        self.superSleep()
        print('    Key selected.')

        #Input BPM
        print('    Selecting BPM....')
        try:
            bpmBox = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, "//input[@max='999.99']")))
            bpmBox.clear()
            bpmBox.send_keys(str(self.beatBPM))
        except StaleElementReferenceException:
            bpmBox = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, "//input[@max='999.99']")))
            bpmBox.clear()
            bpmBox.send_keys(str(self.beatBPM))
        self.superSleep()
        print('    BPM selected.')

        #Go to next step
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//bs-square-button[@data-qa='button_upload_next']"))).click()
        self.superSleep()

    def activateLeases(self):
        
        #Find all leases and their sections
        print("    Activating leases....")

        #Enable all leases
        for license in range(4):
            try:
                toggleStatus = 'false'
                self.driver.execute_script('arguments[0].click();', WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'mat-slide-toggle-bar')))[license])
                while(toggleStatus == 'false'):
                    toggleStatus = WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "mat-slide-toggle-input")))[license].get_attribute('aria-checked')
                self.superSleep()
            except StaleElementReferenceException:
                toggleStatus = 'false'
                self.driver.execute_script('arguments[0].click();', WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'mat-slide-toggle-bar')))[license])
                while(toggleStatus == 'false'):
                    toggleStatus = WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "mat-slide-toggle-input")))[license].get_attribute('aria-checked')
                self.superSleep()

        #Go to next step
        print('    Leases activated.')
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//bs-square-button[@data-qa='button_upload_next']"))).click()
        self.superSleep()
    
    def publishBeat(self):

        #Check 3rd party loops checkbox
        print('    Publishing beat....')
        try:
            checkbox = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'mat-checkbox-layout')))
            checkbox.click()
        except StaleElementReferenceException:
            checkbox = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'mat-checkbox-layout')))
            checkbox.click()
        self.superSleep()         

        #Publish beat  
        WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'action-element')))[3].click()

    def fillAndCheckEmailCode(self):

        #Check if emailed pin is needed. If timeoutexception occurs, email pin is not needed
        try:
            codePrompt = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'subtitle')))
            if codePrompt.text == 'Please enter your confirmation code':
                print('    Confirmation code being asked for.')
            else:
                print('    Confirmation code NOT being asked for.')
                return             
        except TimeoutException:
            print('    Confirmation code NOT being asked for.')
            return
        else:
            print("    Getting code....")
            self.getPastCode()
            code = self.getCode()
            print("    Inputting code....")
            WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'ng-pristine')))[1].send_keys(code[0])
            WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'ng-pristine')))[2].send_keys(code[1])
            WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'ng-pristine')))[3].send_keys(code[2])
            WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'ng-pristine')))[4].send_keys(code[3])
            print('    Code inputted.')

    def recover(self):
        WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Go to Beatstars Studio')]"))).click()
        WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'menu-option')))[0].click()
        WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'ng-star-inserted')))[9].click()

    def superSleep(self):
        sleep(randint(5,10)*(randint(80000,120000)/100000)/randint(2,4))

    def savePicture(self, fileName):
        self.driver.get_screenshot_as_file(self.errorScreenshotsFolder+fileName+'.png')

# FOR TESTING FOR TESTING FOR TESTING FOR TESTING FOR TESTING FOR TESTING FOR TESTING FOR TESTING 
# uploadBot = BeatstarsBot('USERNAME', 'PASSWORD', r'C:\Users\samlb\Documents\INSTRUMENTATOR\Final Beats\A#m - 120 BPM FINAL BEAT.wav', r'C:\Users\samlb\Documents\INSTRUMENTATOR\Final Beats\A#m - 120 BPM FINAL BEAT.zip', r'C:\Users\samlb\Documents\INSTRUMENTATOR\Beatstars\Images\c55567cfca8a15c8162299d7b0a574d7.jpg', 'Example Title', 'Example Description', ['test1', 'test2', 'test3'], ['Trap', 'Freestyle', 'Mumble'], ['Angry', 'Energetic', 'Enraged', 'Evil', 'Intense'], 'A#m', 120)
# status = False
# while(status ==  False):
#     try:
#         print('\n-----------------------------------------------\n')
#         uploadBot.accessWebsite()
#         uploadBot.login()
#         uploadBot.makeNewTrack()
#         uploadBot.uploadWav()
#         uploadBot.uploadZip()
#         uploadBot.uploadImage()
#         uploadBot.uploadBasicInfo()
#         uploadBot.uploadMetadata()
#         uploadBot.activateLeases()
#         status = uploadBot.publishBeat()
#         print('\n-----------------------------------------------\n')
#     except Exception:
#         print("Error in Beatstars Bot. Waiting 1 minute and restarting.")
#         print(traceback.format_exc())
#         sleep(60)